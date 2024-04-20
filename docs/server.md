# Server Module for Linguflex

The Server module for Linguflex creates a HTTPS Webserver on Port 443 and a Websocket SSL Server on Port 8001.

> **Note**: *Serving Elevenlabs TTS currently doesn't work. Serving RVC postprocessed chunks currently result in slightly higher pitched voice.*

## Contents

- [Functionality](#functionality)
- [Installation](#installation)
- [Configuration](#configuration)

## Functionality

- **Webserver access**: Offers voice access to Linguflex from webbrowsers within the local network.

## Installation

### Open ports 443 and 8001 for local network TCP communication on your Firewall (443 should be open already)

To open firewall settings for a specific port in Windows, follow these steps:

1. Type "Firewall" in the taskbar search box and select "Windows Defender Firewall".
2. Click on "Advanced settings".
3. In the left panel, click on "Inbound Rules".
4. Click on "New Rule..." in the right panel.
5. Select "Port" and click "Next".
6. Choose the protocol (usually TCP for servers) and enter "8000" for "Specific local ports".
7. Choose "Allow the connection" and click "Next".
8. Select the appropriate profiles (usually "Private" for home networks).
9. Name the rule (e.g., "Port 443 for Python Server") and click "Finish".

Repeat for Inbound and Outbound Rules for ports 8000 and 8001.

### Installation of OpenSSL
1. **Install OpenSSL** if it is not already installed on your server. Use the appropriate command for your operating system:
   - For Ubuntu/Debian-based Linux:
     ```bash
     sudo apt-get install openssl
     ```
   - For RedHat/Fedora-based Linux:
     ```bash
     sudo yum install openssl
     ```
   - For macOS:
     ```bash
     brew install openssl
     ```
   - For Windows, download it from [OpenSSL's official website](https://www.openssl.org/).

### Creating SSL Certificates
2. **Create a PFX Certificate File:**
   - Generate a new SSL certificate and key, then export them to a PFX file (`mycertificate.pfx`). Adjust the command with your server's IP and your details:
     ```bash
     openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -days 365
     openssl pkcs12 -export -out mycertificate.pfx -inkey key.pem -in cert.pem
     ```
   - You can replace `mycertificate` with any preferred file name.

3. **Generate PEM Files from PFX:**
   - Extract the certificate:
     ```bash
     openssl pkcs12 -in mycertificate.pfx -clcerts -nokeys -out mycertificate.pem
     ```
   - Extract the private key:
     ```bash
     openssl pkcs12 -in mycertificate.pfx -nocerts -nodes -out mycertificate-key.pem
     ```

### Configuring Your Server
4. **Reference the PEM files in your server configuration:**
   - Add the paths to the `mycertificate.pem` and `mycertificate-key.pem` files in your server's `settings.yaml` file. 

### Update Client-Side Configuration
5. **Modify the Client JavaScript to Connect via SSL:**
   - Open the file `static/tts.js`.
   - Change the line containing the socket address to use the IP address of your server:
     ```javascript
     let socket_address = "wss://YOUR_SERVER_IP:8001";
     ```
   - Replace `YOUR_SERVER_IP` with the actual IP address your server is running on.

### Documentation for Users
6. **Provide this documentation to users who need to install the certificate on their client devices (e.g., phones).**
   - They should install the `mycertificate.pfx` on their devices to trust the SSL connection.

## Configuration

- You can change the ports linguflex is running on by changing port_ssl and port_websocket in the settings.yaml (remember to also adjust static/tts.js)