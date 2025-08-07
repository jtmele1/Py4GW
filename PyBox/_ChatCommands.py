# region imports
from Py4GWCoreLib import *
import _Utils
import ctypes
# endregion

user32 = ctypes.WinDLL("user32", use_last_error=True)

def is_key_pressed(vk_code):
    value = user32.GetAsyncKeyState(vk_code) & 0x8000
    is_value_not_zero = value != 0
    if is_value_not_zero:
        return True
    return None

class Variables:
    icon              = IconsFontAwesome5.ICON_USER_FRIENDS
    can_show_button   = True
    is_showing_button = True
    is_showing        = False
    is_snappable      = False
    offset_x          = 0
    offset_y          = 0
    pos_x             = 500
    pos_y             = 500

    focus_set = False
    waiting_for_ready = False
    ready_for_input = False
    string = ''
    timer = Timer()
    timer.Start()

vars = Variables()

def floating_input_text(label, value, x, y, width=120, height=24, color: Color = Color(181, 181, 181, 255)):
    global vars

    # Set the position and size of the floating input
    PyImGui.set_next_window_pos(x, y)
    PyImGui.set_next_window_size(width, height)

    flags = (
        PyImGui.WindowFlags.NoCollapse |
        PyImGui.WindowFlags.NoTitleBar |
        PyImGui.WindowFlags.NoScrollbar |
        PyImGui.WindowFlags.NoScrollWithMouse |
        PyImGui.WindowFlags.AlwaysAutoResize
    )

    PyImGui.push_style_var2(ImGui.ImGuiStyleVar.WindowPadding, 0.0, 0.0)
    PyImGui.push_style_var(ImGui.ImGuiStyleVar.WindowRounding, 0.0)
    PyImGui.push_style_var2(ImGui.ImGuiStyleVar.FramePadding, 3, 3)
    PyImGui.push_style_color(PyImGui.ImGuiCol.Border, color.to_tuple_normalized())

    new_value = value
    if PyImGui.begin(f"##invisible_window_input_{label}", flags):
        PyImGui.push_style_color(PyImGui.ImGuiCol.FrameBg, (0, 0, 0, 1))
        PyImGui.push_style_color(PyImGui.ImGuiCol.FrameBgHovered, (0, 0, 0, 1))
        PyImGui.push_style_color(PyImGui.ImGuiCol.FrameBgActive, (0, 0, 0, 1))
        if not vars.focus_set:
            PyImGui.set_keyboard_focus_here(0)
            focus_set = True

        ImGui.push_font('Regular', 12)
        new_value = PyImGui.input_text(f"##floating_input_text_{label}", value)
        ImGui.pop_font()

        PyImGui.pop_style_color(3)
    PyImGui.end()

    PyImGui.pop_style_var(3)
    PyImGui.pop_style_color(1)
    return new_value

def GetChannelString():
    if UIManager.FrameExists(UIManager.GetChildFrameID(2527393984, [0])):
        return('!')
    elif UIManager.FrameExists(UIManager.GetChildFrameID(2527393984, [1])):
        return('%')
    elif UIManager.FrameExists(UIManager.GetChildFrameID(2527393984, [2])):
        return('@')
    elif UIManager.FrameExists(UIManager.GetChildFrameID(2527393984, [3])):
        return('#')
    elif UIManager.FrameExists(UIManager.GetChildFrameID(2527393984, [4])):
        return('$')
    elif UIManager.FrameExists(UIManager.GetChildFrameID(2527393984, [5])):
        return('"')

def Draw():
    global vars

    if GLOBAL_CACHE.Player.IsTyping():


        vars.string = floating_input_text("123", vars.string, 56, 1313, 580, 17)

        if is_key_pressed(13):
            vars.waiting_for_ready = True

            if vars.ready_for_input:
                vars.waiting_for_ready = False
                vars.ready_for_input = False
                Player.SendChat(GetChannelString(), vars.string)
                vars.string = ''
                UIManager.Keypress(Key.Enter.value, UIManager.GetChildFrameID(2527393984, [3]))


        if vars.waiting_for_ready and not is_key_pressed(13):
            vars.ready_for_input = True
            
    else:
        vars.focus_set = False

def Update():
    global vars
    
    Draw()


        