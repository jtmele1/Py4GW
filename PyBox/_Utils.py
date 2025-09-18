# region imports
from Py4GWCoreLib import *
# endregion

class Colors:
    open = (.94, .85, .38, 1)
    on   = (0, 1, 0, 1)
    off  = (1, 0.20, 0.18, 1)

def Debug(message, title = 'DEBUG', msg_type = 'Debug'):
    py4gw_msg_type = Py4GW.Console.MessageType.Debug
    if   msg_type == 'Debug':       py4gw_msg_type = Py4GW.Console.MessageType.Debug
    elif msg_type == 'Error':       py4gw_msg_type = Py4GW.Console.MessageType.Error
    elif msg_type == 'Info':        py4gw_msg_type = Py4GW.Console.MessageType.Info
    elif msg_type == 'Notice':      py4gw_msg_type = Py4GW.Console.MessageType.Notice
    elif msg_type == 'Performance': py4gw_msg_type = Py4GW.Console.MessageType.Performance
    elif msg_type == 'Success':     py4gw_msg_type = Py4GW.Console.MessageType.Success
    elif msg_type == 'Warning':     py4gw_msg_type = Py4GW.Console.MessageType.Warning
    Py4GW.Console.Log(title, str(message), py4gw_msg_type)

def CanDraw():
    return (Map.IsMapReady()        and 
            Party.IsPartyLoaded()   and 
            not Map.IsInCinematic() and 
            not UIManager.IsWorldMapShowing())

def SendInfoChat(msg, color = 'FFFF00'):
    Player.SendFakeChat(ChatChannel.CHANNEL_GROUP, f'<c=#88BBFF>[PyBox]</c> <c=#{color}>{msg}</c>')

def BeginWindow(name, opened = True):
    flags = (PyImGui.WindowFlags.AlwaysAutoResize  |
             PyImGui.WindowFlags.NoScrollWithMouse | 
             PyImGui.WindowFlags.NoSavedSettings)

    PyImGui.push_style_var( ImGui.ImGuiStyleVar.WindowBorderSize, 0)
    PyImGui.push_style_var2(ImGui.ImGuiStyleVar.WindowPadding,    4, 4)
    PyImGui.push_style_var( ImGui.ImGuiStyleVar.WindowRounding,   0)
    PyImGui.push_style_var( ImGui.ImGuiStyleVar.FrameRounding,    0)
    PyImGui.push_style_var( ImGui.ImGuiStyleVar.TabRounding,      0)
    PyImGui.push_style_var2(ImGui.ImGuiStyleVar.ItemSpacing,      4, 4)

    PyImGui.push_style_color(PyImGui.ImGuiCol.SliderGrab,       (.9, .9, .9, 1))
    PyImGui.push_style_color(PyImGui.ImGuiCol.SliderGrabActive, (.9, .9, .9, 1))

    PyImGui.push_style_color(PyImGui.ImGuiCol.Button,        (.5, .5, .5, 0.3))
    PyImGui.push_style_color(PyImGui.ImGuiCol.ButtonHovered, (.5, .5, .5, 0.4))
    PyImGui.push_style_color(PyImGui.ImGuiCol.ButtonActive,  (.5, .5, .5, 0.5))

    PyImGui.push_style_color(PyImGui.ImGuiCol.Header,         (.5, .5, .5, 0.3))
    PyImGui.push_style_color(PyImGui.ImGuiCol.HeaderHovered,  (.5, .5, .5, 0.4))
    PyImGui.push_style_color(PyImGui.ImGuiCol.HeaderActive,   (.5, .5, .5, 0.5))

    PyImGui.push_style_color(PyImGui.ImGuiCol.FrameBg,        (.5, .5, .5, 0.3))
    PyImGui.push_style_color(PyImGui.ImGuiCol.FrameBgHovered, (.5, .5, .5, 0.4))
    PyImGui.push_style_color(PyImGui.ImGuiCol.FrameBgActive,  (.5, .5, .5, 0.5))

    PyImGui.push_style_color(PyImGui.ImGuiCol.WindowBg,         (0, 0, 0, 0.7))
    PyImGui.push_style_color(PyImGui.ImGuiCol.TitleBg,          (0, 0, 0, 0.7))
    PyImGui.push_style_color(PyImGui.ImGuiCol.TitleBgActive,    (0, 0, 0, 0.7))
    PyImGui.push_style_color(PyImGui.ImGuiCol.TitleBgCollapsed, (0, 0, 0, 0.7))

    PyImGui.push_style_color(PyImGui.ImGuiCol.TableBorderStrong, (.5, .5, .5, 0.3))
    PyImGui.push_style_color(PyImGui.ImGuiCol.TableBorderLight,  (.5, .5, .5, 0.3))

    PyImGui.push_style_color(PyImGui.ImGuiCol.Tab,        (.5, .5, .5, 0.3))
    PyImGui.push_style_color(PyImGui.ImGuiCol.TabHovered, (.5, .5, .5, 0.4))
    PyImGui.push_style_color(PyImGui.ImGuiCol.TabActive,  (.5, .5, .5, 0.5))

    PyImGui.push_style_color(PyImGui.ImGuiCol.Border,     (.5, .5, .5, 0.3))

    return PyImGui.begin_with_close(name, opened, flags)

def EndWindow():
    PyImGui.pop_style_var(6)
    PyImGui.pop_style_color(21)

def BeginHeadlessWindow(name):
    flags = (PyImGui.WindowFlags.NoTitleBar        | 
             PyImGui.WindowFlags.NoMove            |
             PyImGui.WindowFlags.NoScrollbar       |
             PyImGui.WindowFlags.NoScrollWithMouse |
             PyImGui.WindowFlags.NoCollapse        |
             PyImGui.WindowFlags.NoSavedSettings)

    PyImGui.push_style_var( ImGui.ImGuiStyleVar.WindowBorderSize, 0)
    PyImGui.push_style_var2(ImGui.ImGuiStyleVar.WindowPadding,    4, 4)
    PyImGui.push_style_var( ImGui.ImGuiStyleVar.WindowRounding,   0)
    PyImGui.push_style_var( ImGui.ImGuiStyleVar.FrameRounding,    0)
    PyImGui.push_style_var2(ImGui.ImGuiStyleVar.ItemSpacing,      4, 4)

    PyImGui.push_style_color(PyImGui.ImGuiCol.Button,        (1, 1, 1, 0.00))
    PyImGui.push_style_color(PyImGui.ImGuiCol.ButtonHovered, (1, 1, 1, 0.15))
    PyImGui.push_style_color(PyImGui.ImGuiCol.ButtonActive,  (1, 1, 1, 0.30))

    PyImGui.push_style_color(PyImGui.ImGuiCol.Text, (.9, .9, .9, 1))

    PyImGui.push_style_color(PyImGui.ImGuiCol.WindowBg,         (0, 0, 0, 0.7))
    PyImGui.push_style_color(PyImGui.ImGuiCol.TitleBg,          (0, 0, 0, 0.7))
    PyImGui.push_style_color(PyImGui.ImGuiCol.TitleBgActive,    (0, 0, 0, 0.7))
    PyImGui.push_style_color(PyImGui.ImGuiCol.TitleBgCollapsed, (0, 0, 0, 0.7))

    return PyImGui.begin(name, flags)

def EndHeadlessWindow():
    PyImGui.pop_style_var(5)
    PyImGui.pop_style_color(8)

def BeginHiddenWindow(name):
    flags = (PyImGui.WindowFlags.NoTitleBar        | 
             PyImGui.WindowFlags.AlwaysAutoResize  |
             PyImGui.WindowFlags.NoMove            |
             PyImGui.WindowFlags.NoScrollbar       |
             PyImGui.WindowFlags.NoBackground      |
             PyImGui.WindowFlags.NoScrollWithMouse |
             PyImGui.WindowFlags.NoCollapse        |
             PyImGui.WindowFlags.NoSavedSettings)

    PyImGui.push_style_var(ImGui.ImGuiStyleVar.WindowBorderSize,0)
    PyImGui.push_style_var2(ImGui.ImGuiStyleVar.WindowPadding,   0, 5)
    PyImGui.push_style_var(ImGui.ImGuiStyleVar.WindowRounding,  0)
    PyImGui.push_style_var(ImGui.ImGuiStyleVar.FrameRounding,   0)

    PyImGui.push_style_color(PyImGui.ImGuiCol.Button,        (1, 1, 1, 0.00))
    PyImGui.push_style_color(PyImGui.ImGuiCol.ButtonHovered, (1, 1, 1, 0.15))
    PyImGui.push_style_color(PyImGui.ImGuiCol.ButtonActive,  (1, 1, 1, 0.30))

    PyImGui.push_style_color(PyImGui.ImGuiCol.Text, (.9, .9, .9, 1))

    PyImGui.push_style_color(PyImGui.ImGuiCol.WindowBg,         (0, 0, 0, 0.7))
    PyImGui.push_style_color(PyImGui.ImGuiCol.TitleBg,          (0, 0, 0, 0.7))
    PyImGui.push_style_color(PyImGui.ImGuiCol.TitleBgActive,    (0, 0, 0, 0.7))
    PyImGui.push_style_color(PyImGui.ImGuiCol.TitleBgCollapsed, (0, 0, 0, 0.7))

    return PyImGui.begin(name, flags)

def EndHiddenWindow():
    PyImGui.pop_style_var(4)
    PyImGui.pop_style_color(8)