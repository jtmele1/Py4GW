# region imports
from Py4GWCoreLib import *
import PyBox._Utils
import ctypes
# endregion

user32 = ctypes.WinDLL("user32", use_last_error=True)

def is_key_pressed(vk_code):
    value = user32.GetAsyncKeyState(vk_code) & 0x8000
    is_value_not_zero = value != 0
    if is_value_not_zero:
        return True
    return None

def char_to_vk(char: str) -> int:
    if len(char) != 1:
        pass
    vk = user32.VkKeyScanW(ord(char))
    if vk == -1:
        pass
    return vk & 0xFF  # The low byte is the VK code

def vk_to_char(vk_code):
    return chr(user32.MapVirtualKeyW(vk_code, 2))

class Hotkey:
    def __init__(self, key, func):
        self.key = key
        self.func = func
        self.instance_type = [0, 1] # 0 for outpost, 1 for explorable
        self.buffer = 200
        self.timer = Timer()
        self.timer.Start()
    
    def Activate(self):
        if self.timer.HasElapsed(self.buffer):
            self.func()
            self.timer.Reset()

def PrintAge():
    Player.SendChatCommand('age')
    time = FormatTime(Map.GetInstanceUptime(), 'mm:ss.ms')
    PyBox._Utils.SendInfoChat(f'Time: {time}')

class Variables:
    hotkeys = [Hotkey(4,  PrintAge)] 

vars = Variables()

def InFocus():
    hwnd = user32.GetForegroundWindow()
    if not hwnd:
        return False

    pid = ctypes.c_ulong()
    user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
    return pid.value == os.getpid()

def Draw():
    global vars

    pass

def Update():
    global vars

    if InFocus():
        for hotkey in vars.hotkeys:
            if is_key_pressed(hotkey.key):
                hotkey.Activate()