from lingu import log, cfg, Logic
import threading
import json
import subprocess
import platform
import webbrowser
import os


class OS_Apps_Logic(Logic):
    def __init__(self):
        super().__init__()

    def get_available_apps(self):
        return [
            'calculator',
            'browser',
            'paint',
            'text_editor',
            'file_manager',
            'terminal',
            'system_monitor'
        ]

    def open_browser(self, url):
        system = platform.system().lower()
        
        if system == 'windows':
            # Try to use the default browser directly
            try:
                os.startfile(url)
            except AttributeError:
                # If os.startfile is not available, fall back to webbrowser
                webbrowser.open(url)
        elif system == 'darwin':  # macOS
            subprocess.Popen(['open', url])
        elif system == 'linux':
            subprocess.Popen(['xdg-open', url])
        else:
            # Fall back to webbrowser for unsupported systems
            webbrowser.open(url)

    def open_os_app(self, tool):
        system = platform.system().lower()
        
        if tool not in self.get_available_apps():
            return f"Tool '{tool}' is not available on this system"

        try:
            if tool == 'calculator':
                return self._open_calculator()
            
            if system == 'windows':
                if tool == 'text_editor':
                    subprocess.Popen('notepad.exe', shell=True)
                elif tool == 'file_manager':
                    subprocess.Popen('explorer.exe', shell=True)
                elif tool == 'terminal':
                    subprocess.Popen('start cmd.exe', shell=True)
                elif tool == 'browser':
                    self.open_browser('http://www.google.com')
                elif tool == 'system_monitor':
                    subprocess.Popen('taskmgr.exe', shell=True)
                elif tool == 'paint':
                    subprocess.Popen('mspaint.exe', shell=True)
            
            elif system == 'darwin':  # macOS
                if tool == 'text_editor':
                    subprocess.Popen(['open', '-a', 'TextEdit'])
                elif tool == 'file_manager':
                    subprocess.Popen(['open', '-a', 'Finder'])
                elif tool == 'terminal':
                    subprocess.Popen(['open', '-a', 'Terminal'])
                elif tool == 'browser':
                    self.open_browser('http://www.google.com')
                elif tool == 'system_monitor':
                    subprocess.Popen(['open', '-a', 'Activity Monitor'])
                elif tool == 'paint':
                    subprocess.Popen(['open', '-a', 'Preview'])
            
            elif system == 'linux':
                if tool == 'text_editor':
                    subprocess.Popen(['gedit'])
                elif tool == 'file_manager':
                    subprocess.Popen(['nautilus'])
                elif tool == 'terminal':
                    subprocess.Popen(['gnome-terminal'])
                elif tool == 'browser':
                    self.open_browser('http://www.google.com')
                elif tool == 'system_monitor':
                    subprocess.Popen(['gnome-system-monitor'])
                elif tool == 'paint':
                    try:
                        subprocess.Popen(['gimp'])
                    except FileNotFoundError:
                        return "GIMP not found. Please install GIMP or another paint program."
            
            else:
                return "Unsupported operating system"
            
            return f"{tool.replace('_', ' ').title()} opened successfully"
        
        except subprocess.CalledProcessError as e:
            return f"Error opening {tool}: {e}"
        except FileNotFoundError as e:
            return f"{tool.replace('_', ' ').title()} application not found: {e}"

    def _open_calculator(self):
        system = platform.system().lower()
        
        try:
            if system == 'windows':
                subprocess.Popen(['calc.exe'])
            elif system == 'darwin':  # macOS
                subprocess.Popen(['open', '-a', 'Calculator'])
            elif system == 'linux':
                linux_calculators = ['gnome-calculator', 'kcalc', 'xcalc']
                for calc in linux_calculators:
                    try:
                        subprocess.Popen([calc])
                        break  # Stop if a calculator is successfully launched
                    except FileNotFoundError:
                        print(f"{calc} not found")
                else:
                    print("No calculator application found")
                    return "No calculator application found on Linux"
            else:
                print('Unsupported operating system')
                return "Unsupported operating system"
            print('Calculator opened successfully')
            return "Calculator app opened"
        except FileNotFoundError as e:
            print(f'Calculator application not found: {e}')
            return f"Calculator application not found: {e}"

logic = OS_Apps_Logic()


# from lingu import log, cfg, Logic
# import threading
# import json
# import subprocess
# import platform
# import webbrowser
# import os


# class OS_Apps_Logic(Logic):
#     def __init__(self):
#         super().__init__()

#     def get_available_apps(self):
#         return [
#             'calculator',
#             'browser',
#             'paint',
#             'text_editor',
#             'file_manager',
#             'terminal',
#             'system_monitor'
#         ]

#     def open_browser(self, url):
#         system = platform.system().lower()
        
#         if system == 'windows':
#             # Try to use the default browser directly
#             try:
#                 os.startfile(url)
#             except AttributeError:
#                 # If os.startfile is not available, fall back to webbrowser
#                 webbrowser.open(url)
#         elif system == 'darwin':  # macOS
#             subprocess.Popen(['open', url])
#         elif system == 'linux':
#             subprocess.Popen(['xdg-open', url])
#         else:
#             # Fall back to webbrowser for unsupported systems
#             webbrowser.open(url)

#     def open_os_app(self, tool):
#         system = platform.system().lower()
        
#         if tool not in self.get_available_apps():
#             return f"Tool '{tool}' is not available on this system"

#         try:
#             if tool == 'calculator':
#                 return self._open_calculator()
            
#             if system == 'windows':
#                 if tool == 'text_editor':
#                     subprocess.Popen('notepad.exe', shell=True)
#                 elif tool == 'file_manager':
#                     subprocess.Popen('explorer.exe', shell=True)
#                 elif tool == 'terminal':
#                     subprocess.Popen('start cmd.exe', shell=True)
#                 elif tool == 'browser':
#                     self.open_browser('http://www.google.com')
#                 elif tool == 'system_monitor':
#                     subprocess.Popen('taskmgr.exe', shell=True)
#                 elif tool == 'paint':
#                     subprocess.Popen('mspaint.exe', shell=True)
            
#             elif system == 'darwin':  # macOS
#                 if tool == 'text_editor':
#                     subprocess.run(['open', '-a', 'TextEdit'], check=True)
#                 elif tool == 'file_manager':
#                     subprocess.run(['open', '-a', 'Finder'], check=True)
#                 elif tool == 'terminal':
#                     subprocess.run(['open', '-a', 'Terminal'], check=True)
#                 elif tool == 'browser':
#                     self.open_browser('http://www.google.com')
#                 elif tool == 'system_monitor':
#                     subprocess.run(['open', '-a', 'Activity Monitor'], check=True)
#                 elif tool == 'paint':
#                     subprocess.run(['open', '-a', 'Preview'], check=True)
            
#             elif system == 'linux':
#                 if tool == 'text_editor':
#                     subprocess.run(['gedit'], check=True)
#                 elif tool == 'file_manager':
#                     subprocess.run(['nautilus'], check=True)
#                 elif tool == 'terminal':
#                     subprocess.run(['gnome-terminal'], check=True)
#                 elif tool == 'browser':
#                     self.open_browser('http://www.google.com')
#                 elif tool == 'system_monitor':
#                     subprocess.run(['gnome-system-monitor'], check=True)
#                 elif tool == 'paint':
#                     try:
#                         subprocess.run(['gimp'], check=True)
#                     except FileNotFoundError:
#                         return "GIMP not found. Please install GIMP or another paint program."
            
#             else:
#                 return "Unsupported operating system"
            
#             return f"{tool.replace('_', ' ').title()} opened successfully"
        
#         except subprocess.CalledProcessError as e:
#             return f"Error opening {tool}: {e}"
#         except FileNotFoundError as e:
#             return f"{tool.replace('_', ' ').title()} application not found: {e}"

#     def _open_calculator(self):
#         system = platform.system().lower()
        
#         try:
#             if system == 'windows':
#                 subprocess.run(['calc.exe'], check=True)
#             elif system == 'darwin':  # macOS
#                 subprocess.run(['open', '-a', 'Calculator'], check=True)
#             elif system == 'linux':
#                 linux_calculators = ['gnome-calculator', 'kcalc', 'xcalc']
#                 for calc in linux_calculators:
#                     try:
#                         subprocess.run([calc], check=True)
#                         break  # Stop if a calculator is successfully launched
#                     except subprocess.CalledProcessError:
#                         print(f"Failed to start {calc}")
#                     except FileNotFoundError:
#                         print(f"{calc} not found")
#                 else:
#                     print("No calculator application found")
#                     return "No calculator application found on Linux"
#             else:
#                 print('Unsupported operating system')
#                 return "Unsupported operating system"
#             print('Calculator opened successfully')
#             return "Calculator app opened"
#         except subprocess.CalledProcessError as e:
#             print(f'Error opening calculator: {e}')
#             return f"Error opening calculator: {e}"
#         except FileNotFoundError as e:
#             print(f'Calculator application not found: {e}')
#             return f"Calculator application not found: {e}"

# logic = OS_Apps_Logic()





# from lingu import log, cfg, Logic
# import subprocess
# import platform
# import webbrowser
# import time
# import psutil
# import os

# class OS_Apps_Logic(Logic):
#     def __init__(self):
#         super().__init__()

#     def get_available_apps(self):
#         return [
#             'calculator',
#             'browser',
#             'paint',
#             'text_editor',
#             'file_manager',
#             'terminal',
#             'system_monitor'
#         ]

#     def open_os_app(self, tool):
#         system = platform.system().lower()
        
#         if tool not in self.get_available_apps():
#             return f"Tool '{tool}' is not available on this system"

#         try:
#             if tool == 'calculator':
#                 return self._open_calculator()
            
#             if system == 'windows':
#                 commands = {
#                     'text_editor': 'notepad.exe',
#                     'file_manager': 'explorer.exe',
#                     'terminal': 'cmd.exe',
#                     'system_monitor': 'taskmgr.exe',
#                     'paint': 'mspaint.exe'
#                 }
#                 if tool in commands:
#                     subprocess.Popen(['start', commands[tool]], shell=True)
#                     return self._check_windows_process(commands[tool])
#                 elif tool == 'browser':
#                     webbrowser.open('http://www.google.com')
#                     return "Browser opened successfully"
            
#             elif system in ['darwin', 'linux']:  # macOS or Linux
#                 commands = {
#                     'darwin': {
#                         'text_editor': 'TextEdit',
#                         'file_manager': 'Finder',
#                         'terminal': 'Terminal',
#                         'system_monitor': 'Activity Monitor',
#                         'paint': 'Preview'
#                     },
#                     'linux': {
#                         'text_editor': 'gedit',
#                         'file_manager': 'nautilus',
#                         'terminal': 'gnome-terminal',
#                         'system_monitor': 'gnome-system-monitor',
#                         'paint': 'gimp'
#                     }
#                 }
#                 if tool in commands[system]:
#                     if system == 'darwin':
#                         subprocess.Popen(['open', '-a', commands[system][tool]])
#                     else:
#                         subprocess.Popen([commands[system][tool]])
#                     return self._check_unix_process(commands[system][tool])
#                 elif tool == 'browser':
#                     webbrowser.open('http://www.google.com')
#                     return "Browser opened successfully"
            
#             else:
#                 return "Unsupported operating system"
            
#         except FileNotFoundError as e:
#             return f"{tool.replace('_', ' ').title()} application not found: {e}"
#         except Exception as e:
#             return f"Error opening {tool}: {e}"

#     def _open_calculator(self):
#         system = platform.system().lower()
        
#         try:
#             if system == 'windows':
#                 subprocess.Popen(['start', 'calc.exe'], shell=True)
#                 return self._check_windows_process('Calculator.exe')
#             elif system == 'darwin':  # macOS
#                 subprocess.Popen(['open', '-a', 'Calculator'])
#                 return self._check_unix_process('Calculator')
#             elif system == 'linux':
#                 linux_calculators = ['gnome-calculator', 'kcalc', 'xcalc']
#                 for calc in linux_calculators:
#                     try:
#                         subprocess.Popen([calc])
#                         result = self._check_unix_process(calc)
#                         if "opened successfully" in result:
#                             return result
#                     except FileNotFoundError:
#                         continue
#                 return "No calculator application found on Linux"
#             else:
#                 return "Unsupported operating system"
#         except Exception as e:
#             return f"Error opening calculator: {e}"

#     def _check_windows_process(self, process_name):
#         import ctypes
#         import ctypes.wintypes

#         psapi = ctypes.WinDLL('Psapi.dll')
#         enum_processes = psapi.EnumProcesses
#         enum_processes.restype = ctypes.wintypes.BOOL
        
#         max_array = ctypes.c_ulong * 4096
#         proc_ids = max_array()
#         cb = ctypes.sizeof(proc_ids)
#         bytes_returned = ctypes.c_ulong()
        
#         enum_processes(ctypes.byref(proc_ids), cb, ctypes.byref(bytes_returned))
#         proc_count = bytes_returned.value // ctypes.sizeof(ctypes.c_ulong())
        
#         for idx in range(proc_count):
#             process_id = proc_ids[idx]
#             h_process = ctypes.windll.kernel32.OpenProcess(0x0400 | 0x0010, False, process_id)
            
#             if h_process:
#                 image_file_name = (ctypes.c_char * 260)()
#                 if psapi.GetProcessImageFileNameA(h_process, image_file_name, 260) > 0:
#                     filename = os.path.basename(image_file_name.value).decode()
#                     if filename.lower() == process_name.lower():
#                         ctypes.windll.kernel32.CloseHandle(h_process)
#                         return f"{process_name} opened successfully"
#                 ctypes.windll.kernel32.CloseHandle(h_process)
        
#         return f"Error: {process_name} failed to start"

#     def _check_unix_process(self, process_name):
#         time.sleep(1)  # Give the process a moment to start
#         for proc in psutil.process_iter(['name']):
#             if process_name.lower() in proc.info['name'].lower():
#                 return f"{process_name} opened successfully"
#         return f"Error: {process_name} failed to start"

# logic = OS_Apps_Logic()

# from lingu import log, cfg, Logic
# import subprocess
# import platform
# import webbrowser
# import time

# class OS_Apps_Logic(Logic):
#     def __init__(self):
#         super().__init__()

#     def get_available_apps(self):
#         return [
#             'calculator',
#             'browser',
#             'paint',
#             'text_editor',
#             'file_manager',
#             'terminal',
#             'system_monitor'
#         ]

#     def open_os_app(self, tool):
#         system = platform.system().lower()
        
#         if tool not in self.get_available_apps():
#             return f"Tool '{tool}' is not available on this system"

#         try:
#             if tool == 'calculator':
#                 return self._open_calculator()
            
#             if system == 'windows':
#                 commands = {
#                     'text_editor': 'notepad.exe',
#                     'file_manager': 'explorer.exe',
#                     'terminal': 'cmd.exe',
#                     'system_monitor': 'taskmgr.exe',
#                     'paint': 'mspaint.exe'
#                 }
#                 if tool in commands:
#                     process = subprocess.Popen(['start', commands[tool]], shell=True)
#                 elif tool == 'browser':
#                     webbrowser.open('http://www.google.com')
#                     return "Browser opened successfully"
            
#             elif system == 'darwin':  # macOS
#                 commands = {
#                     'text_editor': 'TextEdit',
#                     'file_manager': 'Finder',
#                     'terminal': 'Terminal',
#                     'system_monitor': 'Activity Monitor',
#                     'paint': 'Preview'
#                 }
#                 if tool in commands:
#                     process = subprocess.Popen(['open', '-a', commands[tool]])
#                 elif tool == 'browser':
#                     webbrowser.open('http://www.google.com')
#                     return "Browser opened successfully"
            
#             elif system == 'linux':
#                 commands = {
#                     'text_editor': 'gedit',
#                     'file_manager': 'nautilus',
#                     'terminal': 'gnome-terminal',
#                     'system_monitor': 'gnome-system-monitor',
#                     'paint': 'gimp'
#                 }
#                 if tool in commands:
#                     process = subprocess.Popen([commands[tool]])
#                 elif tool == 'browser':
#                     webbrowser.open('http://www.google.com')
#                     return "Browser opened successfully"
            
#             else:
#                 return "Unsupported operating system"
            
#             # Wait a short time to check if the process is still running
#             time.sleep(2)
#             if process.poll() is not None:
#                 return f"Error: {tool.replace('_', ' ').title()} failed to start"
            
#             return f"{tool.replace('_', ' ').title()} opened successfully"
        
#         except FileNotFoundError as e:
#             return f"{tool.replace('_', ' ').title()} application not found: {e}"
#         except Exception as e:
#             return f"Error opening {tool}: {e}"

#     def _open_calculator(self):
#         system = platform.system().lower()
        
#         try:
#             if system == 'windows':
#                 process = subprocess.Popen(['start', 'calc.exe'], shell=True)
#             elif system == 'darwin':  # macOS
#                 process = subprocess.Popen(['open', '-a', 'Calculator'])
#             elif system == 'linux':
#                 linux_calculators = ['gnome-calculator', 'kcalc', 'xcalc']
#                 for calc in linux_calculators:
#                     try:
#                         process = subprocess.Popen([calc])
#                         break
#                     except FileNotFoundError:
#                         continue
#                 else:
#                     return "No calculator application found on Linux"
#             else:
#                 return "Unsupported operating system"
            
#             # Wait a short time to check if the process is still running
#             time.sleep(2)
#             if process.poll() is not None:
#                 return "Error: Calculator failed to start"
            
#             return "Calculator app opened successfully"
#         except Exception as e:
#             return f"Error opening calculator: {e}"

# logic = OS_Apps_Logic()



# from lingu import log, cfg, Logic
# import threading
# import json
# import subprocess
# import platform
# import webbrowser

# class OS_Apps_Logic(Logic):
#     def __init__(self):
#         super().__init__()

#     def get_available_apps(self):
#         return [
#             'calculator',
#             'browser',
#             'paint',
#             'text_editor',
#             'file_manager',
#             'terminal',
#             'system_monitor'
#         ]

#     def open_os_app(self, tool):
#         system = platform.system().lower()
        
#         if tool not in self.get_available_apps():
#             return f"Tool '{tool}' is not available on this system"

#         try:
#             if tool == 'calculator':
#                 return self._open_calculator()
            
#             if system == 'windows':
#                 if tool == 'text_editor':
#                     subprocess.Popen('start notepad.exe', shell=True)
#                 elif tool == 'file_manager':
#                     subprocess.Popen('start explorer.exe', shell=True)
#                 elif tool == 'terminal':
#                     subprocess.Popen('start cmd.exe', shell=True)
#                 elif tool == 'browser':
#                     webbrowser.open('http://www.google.com')
#                 elif tool == 'system_monitor':
#                     subprocess.Popen('start taskmgr.exe', shell=True)
#                 elif tool == 'paint':
#                     subprocess.Popen('start mspaint.exe', shell=True)
            
#             elif system == 'darwin':  # macOS
#                 if tool == 'text_editor':
#                     subprocess.Popen(['open', '-a', 'TextEdit'])
#                 elif tool == 'file_manager':
#                     subprocess.Popen(['open', '-a', 'Finder'])
#                 elif tool == 'terminal':
#                     subprocess.Popen(['open', '-a', 'Terminal'])
#                 elif tool == 'browser':
#                     webbrowser.open('http://www.google.com')
#                 elif tool == 'system_monitor':
#                     subprocess.Popen(['open', '-a', 'Activity Monitor'])
#                 elif tool == 'paint':
#                     subprocess.Popen(['open', '-a', 'Preview'])
            
#             elif system == 'linux':
#                 if tool == 'text_editor':
#                     subprocess.Popen(['gedit'])
#                 elif tool == 'file_manager':
#                     subprocess.Popen(['nautilus'])
#                 elif tool == 'terminal':
#                     subprocess.Popen(['gnome-terminal'])
#                 elif tool == 'browser':
#                     webbrowser.open('http://www.google.com')
#                 elif tool == 'system_monitor':
#                     subprocess.Popen(['gnome-system-monitor'])
#                 elif tool == 'paint':
#                     try:
#                         subprocess.Popen(['gimp'])
#                     except FileNotFoundError:
#                         return "GIMP not found. Please install GIMP or another paint program."
            
#             else:
#                 return "Unsupported operating system"
            
#             return f"{tool.replace('_', ' ').title()} opened successfully"
        
#         except subprocess.CalledProcessError as e:
#             return f"Error opening {tool}: {e}"
#         except FileNotFoundError as e:
#             return f"{tool.replace('_', ' ').title()} application not found: {e}"

#     def _open_calculator(self):
#         system = platform.system().lower()
        
#         try:
#             if system == 'windows':
#                 subprocess.Popen('start calc.exe', shell=True)
#             elif system == 'darwin':  # macOS
#                 subprocess.Popen(['open', '-a', 'Calculator'])
#             elif system == 'linux':
#                 linux_calculators = ['gnome-calculator', 'kcalc', 'xcalc']
#                 for calc in linux_calculators:
#                     try:
#                         subprocess.Popen([calc])
#                         break  # Stop if a calculator is successfully launched
#                     except FileNotFoundError:
#                         continue
#                 else:
#                     return "No calculator application found on Linux"
#             else:
#                 return "Unsupported operating system"
#             return "Calculator app opened"
#         except subprocess.CalledProcessError as e:
#             return f"Error opening calculator: {e}"
#         except FileNotFoundError as e:
#             return f"Calculator application not found: {e}"

# logic = OS_Apps_Logic()


# from lingu import log, cfg, Logic
# import threading
# import json
# import subprocess
# import platform
# import webbrowser


# class OS_Apps_Logic(Logic):
#     def __init__(self):
#         super().__init__()

#     def get_available_apps(self):
#         return [
#             'calculator',
#             'browser',
#             'paint',
#             'text_editor',
#             'file_manager',
#             'terminal',
#             'system_monitor'
#         ]

#     def open_os_app(self, tool):
#         system = platform.system().lower()
        
#         if tool not in self.get_available_apps():
#             return f"Tool '{tool}' is not available on this system"

#         try:
#             if tool == 'calculator':
#                 return self._open_calculator()
            
#             if system == 'windows':
#                 if tool == 'text_editor':
#                     subprocess.run(['notepad.exe'], check=True)
#                 elif tool == 'file_manager':
#                     subprocess.run(['explorer.exe'], check=True)
#                 elif tool == 'terminal':
#                     subprocess.run(['cmd.exe'], check=True)
#                 elif tool == 'browser':
#                     webbrowser.open('http://www.google.com')
#                 elif tool == 'system_monitor':
#                     subprocess.run(['taskmgr.exe'], check=True)
#                 elif tool == 'paint':
#                     subprocess.run(['mspaint.exe'], check=True)
            
#             elif system == 'darwin':  # macOS
#                 if tool == 'text_editor':
#                     subprocess.run(['open', '-a', 'TextEdit'], check=True)
#                 elif tool == 'file_manager':
#                     subprocess.run(['open', '-a', 'Finder'], check=True)
#                 elif tool == 'terminal':
#                     subprocess.run(['open', '-a', 'Terminal'], check=True)
#                 elif tool == 'browser':
#                     webbrowser.open('http://www.google.com')
#                 elif tool == 'system_monitor':
#                     subprocess.run(['open', '-a', 'Activity Monitor'], check=True)
#                 elif tool == 'paint':
#                     subprocess.run(['open', '-a', 'Preview'], check=True)
            
#             elif system == 'linux':
#                 if tool == 'text_editor':
#                     subprocess.run(['gedit'], check=True)
#                 elif tool == 'file_manager':
#                     subprocess.run(['nautilus'], check=True)
#                 elif tool == 'terminal':
#                     subprocess.run(['gnome-terminal'], check=True)
#                 elif tool == 'browser':
#                     webbrowser.open('http://www.google.com')
#                 elif tool == 'system_monitor':
#                     subprocess.run(['gnome-system-monitor'], check=True)
#                 elif tool == 'paint':
#                     try:
#                         subprocess.run(['gimp'], check=True)
#                     except FileNotFoundError:
#                         return "GIMP not found. Please install GIMP or another paint program."
            
#             else:
#                 return "Unsupported operating system"
            
#             return f"{tool.replace('_', ' ').title()} opened successfully"
        
#         except subprocess.CalledProcessError as e:
#             return f"Error opening {tool}: {e}"
#         except FileNotFoundError as e:
#             return f"{tool.replace('_', ' ').title()} application not found: {e}"

#     def _open_calculator(self):
#         system = platform.system().lower()
        
#         try:
#             if system == 'windows':
#                 subprocess.run(['calc.exe'], check=True)
#             elif system == 'darwin':  # macOS
#                 subprocess.run(['open', '-a', 'Calculator'], check=True)
#             elif system == 'linux':
#                 linux_calculators = ['gnome-calculator', 'kcalc', 'xcalc']
#                 for calc in linux_calculators:
#                     try:
#                         subprocess.run([calc], check=True)
#                         break  # Stop if a calculator is successfully launched
#                     except subprocess.CalledProcessError:
#                         print(f"Failed to start {calc}")
#                     except FileNotFoundError:
#                         print(f"{calc} not found")
#                 else:
#                     print("No calculator application found")
#                     return "No calculator application found on Linux"
#             else:
#                 print('Unsupported operating system')
#                 return "Unsupported operating system"
#             print('Calculator opened successfully')
#             return "Calculator app opened"
#         except subprocess.CalledProcessError as e:
#             print(f'Error opening calculator: {e}')
#             return f"Error opening calculator: {e}"
#         except FileNotFoundError as e:
#             print(f'Calculator application not found: {e}')
#             return f"Calculator application not found: {e}"

# logic = OS_Apps_Logic()




# from lingu import log, cfg, Logic
# import threading
# import json
# import subprocess
# import platform
# import webbrowser

# class OS_Apps_Logic(Logic):
#     def __init__(self):
#         super().__init__()

#     def get_available_apps(self):
#         return [
#             'calculator',
#             'browser',
#             'paint',
#             'text_editor',
#             'file_manager',
#             'terminal',
#             'system_monitor'
#         ]

#     def open_os_app(self, tool):
#         system = platform.system().lower()
        
#         if tool not in self.get_available_apps():
#             return f"Tool '{tool}' is not available on this system"

#         try:
#             if tool == 'calculator':
#                 return self._open_calculator()
            
#             if system == 'windows':
#                 if tool == 'text_editor':
#                     subprocess.Popen('start notepad.exe', shell=True)
#                 elif tool == 'file_manager':
#                     subprocess.Popen('start explorer.exe', shell=True)
#                 elif tool == 'terminal':
#                     subprocess.Popen('start cmd.exe', shell=True)
#                 elif tool == 'browser':
#                     webbrowser.open('http://www.google.com')
#                 elif tool == 'system_monitor':
#                     subprocess.Popen('start taskmgr.exe', shell=True)
#                 elif tool == 'paint':
#                     subprocess.Popen('start mspaint.exe', shell=True)
            
#             elif system == 'darwin':  # macOS
#                 if tool == 'text_editor':
#                     subprocess.Popen(['open', '-a', 'TextEdit'])
#                 elif tool == 'file_manager':
#                     subprocess.Popen(['open', '-a', 'Finder'])
#                 elif tool == 'terminal':
#                     subprocess.Popen(['open', '-a', 'Terminal'])
#                 elif tool == 'browser':
#                     webbrowser.open('http://www.google.com')
#                 elif tool == 'system_monitor':
#                     subprocess.Popen(['open', '-a', 'Activity Monitor'])
#                 elif tool == 'paint':
#                     subprocess.Popen(['open', '-a', 'Preview'])
            
#             elif system == 'linux':
#                 if tool == 'text_editor':
#                     subprocess.Popen(['gedit'])
#                 elif tool == 'file_manager':
#                     subprocess.Popen(['nautilus'])
#                 elif tool == 'terminal':
#                     subprocess.Popen(['gnome-terminal'])
#                 elif tool == 'browser':
#                     webbrowser.open('http://www.google.com')
#                 elif tool == 'system_monitor':
#                     subprocess.Popen(['gnome-system-monitor'])
#                 elif tool == 'paint':
#                     try:
#                         subprocess.Popen(['gimp'])
#                     except FileNotFoundError:
#                         return "GIMP not found. Please install GIMP or another paint program."
            
#             else:
#                 return "Unsupported operating system"
            
#             return f"{tool.replace('_', ' ').title()} opened successfully"
        
#         except subprocess.CalledProcessError as e:
#             return f"Error opening {tool}: {e}"
#         except FileNotFoundError as e:
#             return f"{tool.replace('_', ' ').title()} application not found: {e}"

#     def _open_calculator(self):
#         system = platform.system().lower()
        
#         try:
#             if system == 'windows':
#                 subprocess.Popen('start calc.exe', shell=True)
#             elif system == 'darwin':  # macOS
#                 subprocess.Popen(['open', '-a', 'Calculator'])
#             elif system == 'linux':
#                 linux_calculators = ['gnome-calculator', 'kcalc', 'xcalc']
#                 for calc in linux_calculators:
#                     try:
#                         subprocess.Popen([calc])
#                         break  # Stop if a calculator is successfully launched
#                     except FileNotFoundError:
#                         continue
#                 else:
#                     return "No calculator application found on Linux"
#             else:
#                 return "Unsupported operating system"
#             return "Calculator app opened"
#         except subprocess.CalledProcessError as e:
#             return f"Error opening calculator: {e}"
#         except FileNotFoundError as e:
#             return f"Calculator application not found: {e}"

# logic = OS_Apps_Logic()
