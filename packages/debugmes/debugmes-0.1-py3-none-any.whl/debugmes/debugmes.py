from colorama import Fore, init, Style
from datetime import datetime

init(autoreset=True)

def _get_time():
    return f"[{datetime.now().strftime('%H:%M:%S')}]"

def info(message):
    print(f"{_get_time()} {Fore.CYAN}[INFO] - {message}")

def success(message):
    print(f"{_get_time()} {Fore.GREEN}[SUCCESS] - {message}")

def warning(message):
    print(f"{_get_time()} {Fore.YELLOW}[WARNING] - {message}")

def error(message):
    print(f"{_get_time()} {Fore.RED}[ERROR] - {message}")

def critical(message):
    print(f"{_get_time()} {Fore.RED}{Style.BRIGHT}[CRITICAL] - {message}")

def debug(message):
    print(f"{_get_time()} {Fore.MAGENTA}[DEBUG] - {message}")
