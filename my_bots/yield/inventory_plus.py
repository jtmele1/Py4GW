# region imports
from Py4GWCoreLib import * # type: ignore
# endregion

class BotVariables:
    inventory_frame_hash = 291586130
    parent_frame_id      = 0
    current_window       = 0

    class ID:
        whites  = True
        blues   = True
        purples = True
        golds   = True
        checkbox_states: Dict[int, bool] = {}
        item_id = 0
        fsm     = FSM('ID')

    class Salvage:
        whites  = True
        blues   = True
        purples = True
        golds   = True
        checkbox_states: Dict[int, bool] = {}
        item_id = 0
        fsm     = FSM('Salv')

    class Colors:
        text = {
            'White'  : Utils.RGBToColor(255, 255, 255, 255),
            'Blue'   : Utils.RGBToColor(  0, 170, 255, 255),
            'Purple' : Utils.RGBToColor(110,  65, 200, 255),
            'Gold'   : Utils.RGBToColor(225, 150,   0, 255),
            'Green'  : Utils.RGBToColor( 25, 200,   0, 255)
        }
        frame = {
            'White'  : Utils.RGBToColor(255, 255, 255, 125),
            'Blue'   : Utils.RGBToColor(  0, 170, 255, 125),
            'Purple' : Utils.RGBToColor(110,  65, 200, 125),
            'Gold'   : Utils.RGBToColor(225, 150,   0, 125),
            'Green'  : Utils.RGBToColor( 25, 200,   0, 125),
            'Ignore' : Utils.RGBToColor( 26,  26,  26, 200)
        }
        fill = {
            'White'  : Utils.RGBToColor(255, 255, 255, 50),
            'Blue'   : Utils.RGBToColor(  0, 170, 255, 50),
            'Purple' : Utils.RGBToColor(110,  65, 200, 50),
            'Gold'   : Utils.RGBToColor(225, 150,   0, 50),
            'Green'  : Utils.RGBToColor( 25, 200,   0, 50),
            'Ignore' : Utils.RGBToColor( 26,  26,  26, 200)
        }

    id     = ID()
    salv   = Salvage()
    colors = Colors()

bot_vars = BotVariables()

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

def Draw():
    global bot_vars

    def ToggleWindow(window):
        bot_vars.current_window = window if bot_vars.current_window != window else 0

    def OpenStorage():
        if not Inventory.IsStorageOpen():
                Inventory.OpenXunlaiWindow()

    def DrawMenuBar(left, top):
        flags = (PyImGui.WindowFlags.NoCollapse        | 
                 PyImGui.WindowFlags.NoTitleBar        |
                 PyImGui.WindowFlags.NoScrollbar       |
                 PyImGui.WindowFlags.NoScrollWithMouse |
                 PyImGui.WindowFlags.NoResize          |
                 PyImGui.WindowFlags.NoBackground)
        
        PyImGui.set_next_window_pos(left + 350, top - 5)
        PyImGui.set_next_window_size(278, 25)
        PyImGui.push_style_color(PyImGui.ImGuiCol.Button,        (.2,.2,.2,0))
        PyImGui.push_style_color(PyImGui.ImGuiCol.ButtonHovered, (.3,.3,.3,1))
        PyImGui.push_style_color(PyImGui.ImGuiCol.ButtonActive,  (.4,.4,.4,1))

        if PyImGui.begin('Menu Bar',True, flags):
            if PyImGui.button('Identify', 60, 22): ToggleWindow(1)
            PyImGui.same_line(76,-1.0)
            if PyImGui.button('Salvage',  60, 22): ToggleWindow(2)
            PyImGui.same_line(142,-1.0)
            if PyImGui.button('Settings', 60, 22): ToggleWindow(3)
            PyImGui.same_line(208,-1.0)
            if PyImGui.button('Storage',  60, 22): OpenStorage()
        PyImGui.end()

        PyImGui.pop_style_color(3)

    def DrawIDMenu(top, right, flags):
        PyImGui.set_next_window_pos(right - 5, top - 1)
        
        if PyImGui.begin('ID Menu',True, flags):
            PyImGui.push_style_color(PyImGui.ImGuiCol.Text,      Utils.ColorToTuple(bot_vars.colors.text['White']))
            PyImGui.push_style_color(PyImGui.ImGuiCol.CheckMark, Utils.ColorToTuple(bot_vars.colors.text['White']))
            bot_vars.id.whites  = PyImGui.checkbox('Whites',  bot_vars.id.whites)
            PyImGui.push_style_color(PyImGui.ImGuiCol.Text,      Utils.ColorToTuple(bot_vars.colors.text['Blue']))
            PyImGui.push_style_color(PyImGui.ImGuiCol.CheckMark, Utils.ColorToTuple(bot_vars.colors.text['Blue']))
            bot_vars.id.blues   = PyImGui.checkbox('Blues',   bot_vars.id.blues)
            PyImGui.push_style_color(PyImGui.ImGuiCol.Text,      Utils.ColorToTuple(bot_vars.colors.text['Purple']))
            PyImGui.push_style_color(PyImGui.ImGuiCol.CheckMark, Utils.ColorToTuple(bot_vars.colors.text['Purple']))
            bot_vars.id.purples = PyImGui.checkbox('Purples', bot_vars.id.purples)
            PyImGui.push_style_color(PyImGui.ImGuiCol.Text,      Utils.ColorToTuple(bot_vars.colors.text['Gold']))
            PyImGui.push_style_color(PyImGui.ImGuiCol.CheckMark, Utils.ColorToTuple(bot_vars.colors.text['Gold']))
            bot_vars.id.golds   = PyImGui.checkbox('Golds',   bot_vars.id.golds)
            PyImGui.pop_style_color(8)
            
            if PyImGui.button('Select All', 80, 22):
                 bot_vars.id.whites  = True
                 bot_vars.id.blues   = True
                 bot_vars.id.purples = True
                 bot_vars.id.golds   = True

            PyImGui.separator()

            if PyImGui.button('Identify', 80, 22):
                ...

        PyImGui.end()

    def DrawSalvageMenu(top, right, flags):
        PyImGui.set_next_window_pos(right - 5, top - 1)
        
        if PyImGui.begin('Salvage Menu',True, flags):
            PyImGui.push_style_color(PyImGui.ImGuiCol.Text,      Utils.ColorToTuple(bot_vars.colors.text['White']))
            PyImGui.push_style_color(PyImGui.ImGuiCol.CheckMark, Utils.ColorToTuple(bot_vars.colors.text['White']))
            bot_vars.salv.whites  = PyImGui.checkbox('Whites',  bot_vars.salv.whites)
            PyImGui.push_style_color(PyImGui.ImGuiCol.Text,      Utils.ColorToTuple(bot_vars.colors.text['Blue']))
            PyImGui.push_style_color(PyImGui.ImGuiCol.CheckMark, Utils.ColorToTuple(bot_vars.colors.text['Blue']))
            bot_vars.salv.blues   = PyImGui.checkbox('Blues',   bot_vars.salv.blues)
            PyImGui.push_style_color(PyImGui.ImGuiCol.Text,      Utils.ColorToTuple(bot_vars.colors.text['Purple']))
            PyImGui.push_style_color(PyImGui.ImGuiCol.CheckMark, Utils.ColorToTuple(bot_vars.colors.text['Purple']))
            bot_vars.salv.purples = PyImGui.checkbox('Purples', bot_vars.salv.purples)
            PyImGui.push_style_color(PyImGui.ImGuiCol.Text,      Utils.ColorToTuple(bot_vars.colors.text['Gold']))
            PyImGui.push_style_color(PyImGui.ImGuiCol.CheckMark, Utils.ColorToTuple(bot_vars.colors.text['Gold']))
            bot_vars.salv.golds   = PyImGui.checkbox('Golds',   bot_vars.salv.golds)
            PyImGui.pop_style_color(8)
            
            if PyImGui.button('Select All', 80, 22):
                 bot_vars.salv.whites  = True
                 bot_vars.salv.blues   = True
                 bot_vars.salv.purples = True
                 bot_vars.salv.golds   = True

            PyImGui.separator()

            if PyImGui.button('Salvage', 80, 22):
                ...

        PyImGui.end()

    def DrawSettingsMenu(top, right, flags):
        ...

    def StyleMenus(push):
        if push:
            PyImGui.push_style_color(PyImGui.ImGuiCol.Button,         (.2,.2,.2,1))
            PyImGui.push_style_color(PyImGui.ImGuiCol.ButtonHovered,  (.3,.3,.3,1))
            PyImGui.push_style_color(PyImGui.ImGuiCol.ButtonActive,   (.4,.4,.4,1))
            PyImGui.push_style_color(PyImGui.ImGuiCol.FrameBg,        (.2,.2,.2,1))
            PyImGui.push_style_color(PyImGui.ImGuiCol.FrameBgHovered, (.3, .3, .3, 1))
            PyImGui.push_style_color(PyImGui.ImGuiCol.FrameBgActive,  (.4, .4, .4, 1))
            PyImGui.push_style_var(ImGui.ImGuiStyleVar.WindowBorderSize,0.0)
            PyImGui.push_style_var(ImGui.ImGuiStyleVar.WindowRounding,0.0)
        else:
            PyImGui.pop_style_color(6)
            PyImGui.pop_style_var(2)
     
    left, top, right, _ = UIManager.GetFrameCoords(bot_vars.parent_frame_id) 

    DrawMenuBar(left, top)

    flags = (PyImGui.WindowFlags.NoCollapse       | 
             PyImGui.WindowFlags.NoTitleBar       |
             PyImGui.WindowFlags.NoScrollbar      |
             PyImGui.WindowFlags.AlwaysAutoResize |
             PyImGui.WindowFlags.NoScrollWithMouse)
    StyleMenus(1)
    if   bot_vars.current_window == 1: DrawIDMenu(      top, right, flags)
    elif bot_vars.current_window == 2: DrawSalvageMenu( top, right, flags)
    elif bot_vars.current_window == 3: DrawSettingsMenu(top, right, flags)
    StyleMenus(0)
    
# region main
def main():
    global bot_vars

    try:
        # only run when everything is loaded
        if not Map.IsMapReady() or not Party.IsPartyLoaded(): return

        bot_vars.parent_frame_id = UIManager.GetFrameIDByHash(bot_vars.inventory_frame_hash)
        if bot_vars.parent_frame_id == 0: return

        # draw gui
        Draw()

    except ImportError as e:
        Py4GW.Console.Log('BOT', f'ImportError encountered: {str(e)}', Py4GW.Console.MessageType.Error)
        Py4GW.Console.Log('BOT', f'Stack trace: {traceback.format_exc()}', Py4GW.Console.MessageType.Error)
    except ValueError as e:
        Py4GW.Console.Log('BOT', f'ValueError encountered: {str(e)}', Py4GW.Console.MessageType.Error)
        Py4GW.Console.Log('BOT', f'Stack trace: {traceback.format_exc()}', Py4GW.Console.MessageType.Error)
    except TypeError as e:
        Py4GW.Console.Log('BOT', f'TypeError encountered: {str(e)}', Py4GW.Console.MessageType.Error)
        Py4GW.Console.Log('BOT', f'Stack trace: {traceback.format_exc()}', Py4GW.Console.MessageType.Error)
    except Exception as e:
        Py4GW.Console.Log('BOT', f'Unexpected error encountered: {str(e)}', Py4GW.Console.MessageType.Error)
        Py4GW.Console.Log('BOT', f'Stack trace: {traceback.format_exc()}', Py4GW.Console.MessageType.Error)
    finally:
        pass

if __name__ == '__main__':
    main()
# endregion