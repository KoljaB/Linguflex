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

    def validate_if_app_was_opened(self, tool):
        """
        Checks if the specified application is running.
        Returns True if the application is running, False otherwise.
        
        Args:
            tool (str): The name of the tool to check from get_available_apps()
            
        Returns:
            bool: True if the application is running, False otherwise
        """
        system = platform.system().lower()
        
        # Map tool names to their process names on different platforms
        process_names = {
            'windows': {
                'calculator': 'CalculatorApp.exe',
                'text_editor': 'notepad.exe',
                'file_manager': 'explorer.exe',
                'terminal': 'cmd.exe',
                'browser': 'chrome.exe,firefox.exe,msedge.exe,iexplore.exe',
                'system_monitor': 'taskmgr.exe',
                'paint': 'mspaint.exe'
            },
            'darwin': {  # macOS
                'calculator': 'Calculator',
                'text_editor': 'TextEdit',
                'file_manager': 'Finder',
                'terminal': 'Terminal',
                'browser': 'Safari,Google Chrome,Firefox',
                'system_monitor': 'Activity Monitor',
                'paint': 'Preview'
            },
            'linux': {
                'calculator': 'gnome-calculator,kcalc,xcalc',
                'text_editor': 'gedit',
                'file_manager': 'nautilus',
                'terminal': 'gnome-terminal',
                'browser': 'chrome,firefox,chromium',
                'system_monitor': 'gnome-system-monitor',
                'paint': 'gimp'
            }
        }
        
        if tool not in self.get_available_apps():
            raise ValueError(f"Tool '{tool}' is not in the list of available apps")
            
        try:
            if system == 'windows':
                # Use tasklist to get running processes
                output = subprocess.check_output('tasklist /FO CSV /NH', shell=True).decode()
                running_processes = [line.split(',')[0].strip('"').lower() for line in output.splitlines()]
                
                # Check against possible process names
                process_list = process_names['windows'][tool].split(',')
                return any(proc.lower() in running_processes for proc in process_list)
                
            elif system == 'darwin':  # macOS
                # Use ps command to check running processes
                cmd = ["ps", "-A", "-o", "comm="]
                output = subprocess.check_output(cmd).decode()
                running_processes = [p.strip().lower() for p in output.splitlines()]
                
                # Check against possible process names
                process_list = process_names['darwin'][tool].split(',')
                return any(any(proc.lower() in p for p in running_processes) for proc in process_list)
                
            elif system == 'linux':
                # Use ps command to check running processes
                cmd = ["ps", "-A", "-o", "comm="]
                output = subprocess.check_output(cmd).decode()
                running_processes = [p.strip().lower() for p in output.splitlines()]
                
                # Check against possible process names
                process_list = process_names['linux'][tool].split(',')
                return any(proc.lower() in running_processes for proc in process_list)
                
            else:
                raise OSError("Unsupported operating system")
                
        except subprocess.CalledProcessError as e:
            print(f"Error checking process: {e}")
            return False
        except Exception as e:
            print(f"Unexpected error while checking process: {e}")
            return False

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
