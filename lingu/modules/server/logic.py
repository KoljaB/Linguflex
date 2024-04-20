from fastapi.responses import StreamingResponse, HTMLResponse, FileResponse
from fastapi import FastAPI, Query, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from scipy.signal import resample
from lingu import log, cfg, Logic
from queue import Queue
import numpy as np
import websockets
import threading
import ipaddress
import requests
import asyncio
import uvicorn
import socket
import wave
import json
import time
import ssl
import io

host = cfg("server", "host")
ssl_certfile = cfg("server", "ssl_certfile")
ssl_keyfile = cfg("server", "ssl_keyfile")
port_ssl = cfg("server", "port_ssl")
port_websocket = cfg("server", "port_websocket")

ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
ssl_context.load_cert_chain(ssl_certfile, ssl_keyfile)
ssl_context.options |= ssl.OP_NO_SSLv2 | ssl.OP_NO_SSLv3 | ssl.OP_NO_TLSv1 | ssl.OP_NO_TLSv1_1
ssl_context.set_ciphers("HIGH:!aNULL:!eNULL:!EXPORT:!DES:!RC4:!MD5:!PSK:!SRP")

tts_lock = threading.Lock()
speaking_lock = threading.Lock()
audiochunk_generator_lock = threading.Lock()
play_text_to_speech_semaphore = threading.Semaphore(1)
current_speaking = {}


class WebserverLogic(Logic):
    """
    Logic class for letting external programs operate linguflex.
    """
    def __init__(self):
        super().__init__() 
        self.loop = asyncio.get_event_loop()
        self.audio_queue = Queue()
        self.client_websocket = None

        self.add_listener(
            "user_text", "listen",
            self.realtime_usertext)
        self.add_listener(
            "assistant_text", "brain",
            self.realtime_assistanttext)
        self.add_listener(
            "user_text_complete", "listen",
            self.final_usertext)
        self.add_listener(
            "audio_stream_start", "speech",
            self.audio_stream_ready)
        self.add_listener(
            "audio_stream_stop", "speech",
            self.audio_stream_stop)
        self.add_listener(
            "audio_chunk", "speech",
            self.audio_chunk)
        self.add_listener(
            "rvc_audio_chunk", "speech",
            self.rvc_audio_chunk)
        self.add_listener(
            "module_clicked", "server",
            self.disconnect_client)

    def disconnect_client(self):
        # Disconnect Websockets
        if self.client_websocket:
            asyncio.run_coroutine_threadsafe(
                self.client_websocket.close(),
                self.loop
            )

            self.client_websocket = None
            print("Websocket connection closed.")
            self.trigger("client_disconnected")
        self.state.set_text("")
        self.state.set_active(False)

    async def send_to_client(self, message):
        if self.client_websocket:
            await self.client_websocket.send(message)

    def realtime_usertext(self, text):
        if not self.client_websocket:
            return
        try:
            asyncio.run_coroutine_threadsafe(
                self.send_to_client(
                    json.dumps({
                        'type': 'realtime_user',
                        'text': text
                    })),
                self.loop
            )
            # print(f"\r{text}", flush=True, end='')
        except Exception as e:
            print(f"Error in realtime_text_detected: {e}")

    def realtime_assistanttext(self, text):
        if not self.client_websocket:
            return
        try:
            asyncio.run_coroutine_threadsafe(
                self.send_to_client(
                    json.dumps({
                        'type': 'realtime_assistant',
                        'text': text
                    })),
                self.loop
            )
            # print(f"\r{text}", flush=True, end='')
        except Exception as e:
            print(f"Error in realtime_text_detected: {e}")

    def final_usertext(self, full_sentence):
        if not self.client_websocket:
            return
        try:
            asyncio.run_coroutine_threadsafe(
                self.send_to_client(
                    json.dumps({
                        'type': 'final_usertext',
                        'text': full_sentence
                    })),
                self.loop
            )
            # print(f"\rSentence: {full_sentence}")        
        except Exception as e:
            print(f"Error in final_text_detected: {e}")

    def audio_stream_ready(self):
        self.audio_chunks_available = True
        # (self.stream_info, self.engine_name) = data
        # (audio_format, num_channels, sample_rate) = self.stream_info

        if not self.client_websocket:
            return
        # print(f"Audio stream ready: {self.stream_info}")
        try:
            asyncio.run_coroutine_threadsafe(
                self.send_to_client(
                    json.dumps({
                        'type': 'audio_stream_ready',
                        'text': ''
                    })),
                self.loop
            )
        except Exception as e:
            print(f"Error in audio_stream_ready: {e}")

    def audio_stream_stop(self):
        self.audio_chunks_available = False

    def audio_chunk(self, chunk):
        self.rvc_chunk = False
        self.audio_queue.put(chunk)

    def rvc_audio_chunk(self, chunk):
        self.rvc_chunk = True
        self.audio_queue.put(chunk)

    async def listen_server_worker(self, websocket, path):

        # Extract the IP address from the WebSocket connection
        client_ip = websocket.remote_address[0]
        print(f"Client connected from {client_ip}")
        self.state.set_text(f"{client_ip}")

        def decode_and_resample(
                audio_data,
                original_sample_rate,
                target_sample_rate):
            """
            We need to resample from client microphone sample rate to 16 kHz.
            Otherwise Whisper, WebRTCVad and Silero VAD won't work.
            """

            # Decode 16-bit PCM data to numpy array
            audio_np = np.frombuffer(audio_data, dtype=np.int16)

            # Calculate the number of samples after resampling
            num_original_samples = len(audio_np)
            num_target_samples = int(num_original_samples
                                     * target_sample_rate /
                                     original_sample_rate)

            # Resample the audio
            resampled_audio = resample(audio_np, num_target_samples)

            return resampled_audio.astype(np.int16).tobytes()

        self.client_websocket = websocket
        self.trigger("client_connected")
        self.state.set_active(True)

        async for message in websocket:
            metadata_length = int.from_bytes(message[:4], byteorder='little')
            metadata_json = message[4:4+metadata_length].decode('utf-8')
            metadata = json.loads(metadata_json)
            sample_rate = metadata['sampleRate']
            chunk = message[4+metadata_length:]
            resampled_chunk = decode_and_resample(chunk, sample_rate, 16000)

            self.trigger("client_chunk_received", resampled_chunk)

    def float32_to_int16(self, float_audio):
        # Clip to the range -1.0 to 1.0 to avoid overflow when converting
        float_audio = np.clip(float_audio, -1.0, 1.0)
        # Scale float32 range (-1.0, 1.0) to int16 range (-32768, 32767)
        int16_audio = np.int16(float_audio * 32767)
        return int16_audio.tobytes()

    def init_websocket_server(self):
        asyncio.set_event_loop(self.loop)
        print(f"Starting websocket server on port {port_websocket}")
        start_server = websockets.serve(
            self.listen_server_worker,
            "0.0.0.0",
            port_websocket,
            ssl=ssl_context
        )
        self.loop.run_until_complete(start_server)
        self.loop.run_forever()

    # def init_wav_writer(self):
    #     self.wav_file = wave.open('output.wav', 'wb')
    #     self.wav_file.setnchannels(1)
    #     self.wav_file.setsampwidth(2)  # 4 bytes for float32
    #     self.wav_file.setframerate(48000)
    #     self.wav_file.setcomptype('NONE', 'Not Compressed')

    def init(self):
        log.inf("  [server] Starting Linguflex 2.0 Webserver...")
        self.rvc_chunk = False
        self.stream_info = None
        self.engine_name = None
        self.audio_chunks_available = False
        self.chunk_counter = 0

        self.thread = threading.Thread(target=self.init_websocket_server)
        self.thread.start()

        origins = [
            "http://localhost",
            f"http://localhost:{port_ssl}",
            "http://127.0.0.1",
            f"http://127.0.0.1:{port_ssl}",
            "https://localhost",
            f"https://localhost:{port_ssl}",
            "https://linguflex",
            f"https://linguflex:{port_ssl}",
            "https://127.0.0.1",
            f"https://127.0.0.1:{port_ssl}",
        ]

        def extract_hostrange(host_ip):
            # Split the IP address into segments
            segments = host_ip.split('.')
            # Reconstruct the hostrange by joining the first three segments and adding a dot at the end
            hostrange = '.'.join(segments[:3]) + '.'
            return hostrange

        def get_correct_ip():
            ip_prefix = extract_hostrange(cfg("server", "host"))

            # Get all available network interfaces and their associated IP addresses
            hostnames = socket.getaddrinfo(socket.gethostname(), None)
            for host in hostnames:
                ip = host[4][0]
                if ip.startswith(ip_prefix):  # Specify the IP range you are interested in
                    return ip
            return None

        # Get the appropriate local IP address of the machine running the server
        local_ip = get_correct_ip()
        if local_ip is None:
            raise Exception("No appropriate local IP address found.")

        # Calculate the subnet based on the network prefix length
        network_prefix_length = 24  # Assuming a common subnet mask of /24
        subnet = ipaddress.IPv4Network(f"{local_ip}/{network_prefix_length}", strict=False)

        # Initialize the origins list
        origins = []

        # Add the subnet and the local IP addresses to the origins list
        origins += [f"http://{ip}" for ip in subnet.hosts()]
        origins += [
            f"http://{local_ip}",
            f"https://{local_ip}",
            f"http://{socket.gethostname()}",
            f"https://{socket.gethostname()}",
        ]

        # Optionally, specify a specific port if needed (assuming PORT is defined)
        origins += [f"http://{ip}:{port_ssl}" for ip in subnet.hosts()]
        origins += [
            f"https://{local_ip}:{port_ssl}",
            f"http://{socket.gethostname()}:{port_ssl}",
            f"https://{socket.gethostname()}:{port_ssl}",
        ]

        # Log the IP address and port of the FastAPI server
        print(f"FastAPI server running at http://{local_ip}:{port_ssl}")

        app = FastAPI()
        app.mount("/static", StaticFiles(directory="static"), name="static")
        app.add_middleware(
            CORSMiddleware,
            allow_origins=origins,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

        csp = {
            "default-src": "'self'",
            "script-src": "'self' https://cdn.socket.io",
            "style-src": "'self' 'unsafe-inline'",
            "img-src": "'self' data:",
            "font-src": "'self' data:",
            "media-src": "'self' blob:",
            "connect-src": f"'self' wss://localhost:8001 wss://linguflex:8001 wss://{local_ip}:8001"
        }        
        csp_string = "; ".join(f"{key} {value}" for key, value in csp.items())

        BROWSER_IDENTIFIERS = [
            "mozilla",
            "chrome",
            "safari",
            "firefox",
            "edge",
            "opera",
            "msie",
            "trident"
        ]

        def is_browser_request(request):
            user_agent = request.headers.get('user-agent', '').lower()
            is_browser = any(
                browser_id in user_agent for browser_id in BROWSER_IDENTIFIERS)
            return is_browser

        def is_currently_speaking(text):
            with speaking_lock:
                return current_speaking.get(text, False)

        def set_speaking(text, status):
            with speaking_lock:
                current_speaking[text] = status

        def play_text_to_speech():
            try:
                log.inf(f"  [server] client requested audio stream")
                while self.audio_chunks_available:
                    time.sleep(0.1)

                self.audio_queue.put(None)

                # Wait until the self.audio_queue is empty
                while not self.audio_queue.empty():
                    time.sleep(0.1)
            finally:
                print("Done speaking")
                set_speaking("", False)

        def create_wave_header_for_engine():
            # _, _, sample_rate = engine.get_stream_info()

            if self.rvc_chunk:
                sample_rate = 40000
            else:
                _, _, sample_rate = self.stream_info

            num_channels = 1
            sample_width = 2
            frame_rate = sample_rate

            wav_header = io.BytesIO()
            with wave.open(wav_header, 'wb') as wav_file:
                wav_file.setnchannels(num_channels)
                wav_file.setsampwidth(sample_width)
                wav_file.setframerate(frame_rate)
                wav_file.setcomptype('NONE', 'Not Compressed')

            wav_header.seek(0)
            wave_header_bytes = wav_header.read()
            wav_header.close()

            # Create a new BytesIO with the correct MIME type for Firefox
            final_wave_header = io.BytesIO()
            final_wave_header.write(wave_header_bytes)
            final_wave_header.seek(0)

            return final_wave_header.getvalue()

        def audio_chunk_generator(send_wave_headers):
            with audiochunk_generator_lock:
                first_chunk = False
                try:
                    while True:
                        chunk = self.audio_queue.get()
                        if chunk is None:
                            log.dbg("Terminating stream")
                            break
                        if not first_chunk:
                            if send_wave_headers and not self.engine_name == "elevenlabs":
                                log.dbg("Sending wave header")
                                # yield create_wave_header_for_engine()
                            first_chunk = True
                            # self.init_wav_writer()  # Initialize WAV file on first chunk
                        self.chunk_counter += 1
                        # print(f"Sending chunk {self.chunk_counter}")
                        # # log.dbg("Sending chunk")
                        # int16_chunk = self.float32_to_int16(
                        #     np.frombuffer(chunk, dtype=np.float32))
                        # self.wav_file.writeframes(int16_chunk)
                        yield chunk
                except Exception as e:
                    log.err(f"Error during streaming: {str(e)}")
                # finally:
                #     if first_chunk:
                #         self.wav_file.close()  # Ensure file is closed at the end                    


        @app.middleware("http")
        async def add_security_headers(request: Request, call_next):
            response = await call_next(request)
            response.headers['Content-Security-Policy'] = csp_string
            return response

        @app.get("/favicon.ico")
        async def favicon():
            return FileResponse('static/favicon.ico')

        @app.get("/tts")
        def tts(request: Request):
            with tts_lock:
                browser_request = is_browser_request(request)

                if play_text_to_speech_semaphore.acquire(blocking=False):
                    try:
                        if not is_currently_speaking(""):
                            print("Speaking...")
                            set_speaking("", True)

                            threading.Thread(
                                target=play_text_to_speech,
                                args=(),
                                daemon=True).start()
                    finally:
                        play_text_to_speech_semaphore.release()

                if is_currently_speaking(""):
                    log.dbg(f"Currently speaking")
                    return StreamingResponse(
                        audio_chunk_generator(browser_request),
                        media_type="application/octet-stream"
                    )
                else:
                    print("Service unavailable, returning 503.")
                    raise HTTPException(
                        status_code=503,
                        detail="Service unavailable, currently processing another request. Please try again shortly.",
                        headers={"Retry-After": "10"}
                    )

        @app.post("/disconnect")
        async def async_disconnect_client():
            self.disconnect_client()
            return {"message": "Disconnected successfully"}

        @app.get("/")
        def root_page():
            # Get the WebSocket address dynamically
            # ws_address = f"wss://{local_ip}:{port_websocket}"

            content = f"""
            <!DOCTYPE html>
            <html>
                <head>
                    <title>Linguflex 2.0</title>
                    <meta charset="UTF-8">
                    <script src="https://cdn.socket.io/4.0.0/socket.io.min.js"></script>
                    <style>
                        body {{
                            font-family: Arial, sans-serif;
                            font-size: 20px;
                            background-color: #333;
                            color: #fff;
                            margin: 0;
                            padding: 0;
                        }}
                        h2 {{
                            color: #009CAD;
                            text-align: center;
                            font-size: 48px;
                        }}
                        #container {{
                            width: 100%;
                            margin: 50px auto;
                            background-color: #444;
                            border-radius: 10px;
                            padding: 20px;
                            box-shadow: 0 0 20px rgba(0, 0, 0, 0.3);
                        }}
                        label {{
                            font-weight: bold;
                             font-size: 18px;
                        }}
                        select, textarea {{
                            width: 100%;
                            padding: 10px;
                            margin: 10px 0;
                            border: 1px solid #ccc;
                            border-radius: 5px;
                            box-sizing: border-box;
                            font-size: 20px;
                        }}
                        button {{
                            display: block;
                            width: 100%;
                            padding: 15px;
                            background-color: #007bff;
                            border: none;
                            border-radius: 5px;
                            color: #fff;
                            font-size: 20px;
                            cursor: pointer;
                            transition: background-color 0.3s;
                        }}
                        button:hover {{
                            background-color: #0056b3;
                        }}
                        .text-display {{
                            white-space: pre-wrap;
                            font-size: 20px;
                        }}
                        .user_realtimetext {{
                            background-color: #222;
                            text-align: center;
                            display: block;
                            color: #009CAD;
                            font-size: 24px;
                        }}
                        .assistant_realtimetext {{
                            font-style: italic;
                            text-align: right;
                            display: block;
                            color: #DDD;
                            font-weight: bold;
                            font-size: 24px;
                        }}
                        .user_finaltext {{
                            background-color: #222;
                            text-align: left;
                            display: block;
                            color: #009CAD;
                            font-weight: bold;
                            font-size: 24px;
                        }}
                        .assistant_finaltext {{
                            font-style: italic;
                            text-align: right;
                            display: block;
                            color: #DDD;
                            font-weight: bold;
                            font-size: 24px;
                        }}
                    </style>
                </head>
                <body>
                    <div id="container">
                        <h2>Linguflex 2.0</h2>
                        <div id="textDisplay" style="max-width: 800px; margin: auto;">
                        </div>
                    </div>
                    <script src="/static/tts.js"></script>
                </body>
            </html>
            """
            return HTMLResponse(content=content)

        def run_server():
            uvicorn.run(
                app,
                host="0.0.0.0",
                port=port_ssl,
                ssl_certfile=ssl_certfile,
                ssl_keyfile=ssl_keyfile
            )

        # Run the server in a separate thread
        self.thread = threading.Thread(target=run_server)
        self.thread.start()

        self.ready()


logic = WebserverLogic()
