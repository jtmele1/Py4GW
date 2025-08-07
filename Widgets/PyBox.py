# region imports
import sys
import importlib
from Py4GWCoreLib import *

window_module = ImGui.WindowModule('Py4GW', window_name = 'Py4GW', window_flags = PyImGui.WindowFlags.AlwaysAutoResize)

module_names = ['_PCons', '_Objectives', '_Reroll', '_Hotkeys', '_Builds', '_Travel','_Info', '_Messaging', '_Titles', '_Materials',
                '_Bonds', '_Compass', '_Inventory', '_Misc', '_Party', '_Skillbar', '_EnvUpkeep', '_Utils']

for module_name in module_names:
    try:
        del sys.modules[f'PyBox.{module_name}']
    except Exception as e:
        print(f"Error unloading module {module_name}: {e}")

modules = {}
for name in module_names:
    try:
        module = importlib.import_module(f'PyBox.{name}')
        modules[name] = module
    except ImportError as e:
        print(f"Could not import module '{name}': {e}")
# endregion

class Variables:
    show_settings = False

vars = Variables()

def DrawWidgetWindow():
    global vars, modules

    frame_id = UIManager.GetFrameIDByHash(291586130)
    if not frame_id:
        return
    
    left, top, right, bottom = UIManager.GetFrameCoords(frame_id)

    PyImGui.set_next_window_pos(left + 408, top - 3) # 438, 408


    widget_modules = ['_PCons', '_Builds', '_Reroll', '_Titles', '_Travel', '_Materials', '_Info']
    if modules['_Utils'].BeginHiddenWindow('ToggleButtons'):
        for module in widget_modules:
            if not hasattr(modules[module], 'vars'):
                continue

            if modules[module].vars.is_showing:
                PyImGui.push_style_color(PyImGui.ImGuiCol.Text, modules['_Utils'].Colors.open)
            else:
                if hasattr(modules[module].vars, 'enabled'):
                    if modules[module].vars.enabled:
                        PyImGui.push_style_color(PyImGui.ImGuiCol.Text, modules['_Utils'].Colors.on)
                    else:
                        PyImGui.push_style_color(PyImGui.ImGuiCol.Text, modules['_Utils'].Colors.off)
                else:
                    PyImGui.push_style_color(PyImGui.ImGuiCol.Text, (.9, .9, .9, 1))

            if PyImGui.button(f'{modules[module].vars.icon}##widgets'):
                modules[module].vars.is_showing = not modules[module].vars.is_showing
                for module_ in widget_modules:
                    if module_ == module:
                        continue
                    modules[module_].vars.is_showing = False

            PyImGui.pop_style_color(1)
            PyImGui.same_line(0, 0)

        # if vars.show_settings:
        #     PyImGui.push_style_color(PyImGui.ImGuiCol.Text, modules['_Utils'].Colors.open)
        # else:
        #     PyImGui.push_style_color(PyImGui.ImGuiCol.Text, (.9, .9, .9, 1))

        # if PyImGui.button(f'{IconsFontAwesome5.ICON_GEAR}##widgets'):
        #     vars.show_settings = not vars.show_settings

        PyImGui.end()

    modules['_Utils'].EndHiddenWindow()

def DrawSettings():
    global window_module

    if modules['_Utils'].BeginWindow('PyBox'):
        PyImGui.indent(1)
        for module in modules:
            if hasattr(modules[module], 'DrawConfig'):
                modules[module].DrawConfig()
        PyImGui.unindent(1)
        PyImGui.end()
    
    modules['_Utils'].EndWindow() 

def configure():
    pass

# region main
def main():
    global modules, vars
    try:
        if modules['_Utils'].CanDraw():
            DrawWidgetWindow()

            if vars.show_settings:
                DrawSettings()
            
        for module in modules:
            if hasattr(modules[module], 'Update'):
                modules[module].Update()

    except ImportError as e:
        Py4GW.Console.Log('PyBox', f'ImportError encountered: {str(e)}', Py4GW.Console.MessageType.Error)
        Py4GW.Console.Log('PyBox', f'Stack trace: {traceback.format_exc()}', Py4GW.Console.MessageType.Error)
    except ValueError as e:
        Py4GW.Console.Log('PyBox', f'ValueError encountered: {str(e)}', Py4GW.Console.MessageType.Error)
        Py4GW.Console.Log('PyBox', f'Stack trace: {traceback.format_exc()}', Py4GW.Console.MessageType.Error)
    except TypeError as e:
        Py4GW.Console.Log('PyBox', f'TypeError encountered: {str(e)}', Py4GW.Console.MessageType.Error)
        Py4GW.Console.Log('PyBox', f'Stack trace: {traceback.format_exc()}', Py4GW.Console.MessageType.Error)
    except Exception as e:
        Py4GW.Console.Log('PyBox', f'Unexpected error encountered: {str(e)}', Py4GW.Console.MessageType.Error)
        Py4GW.Console.Log('PyBox', f'Stack trace: {traceback.format_exc()}', Py4GW.Console.MessageType.Error)
    finally:
        pass

if __name__ == '__main__':
    main()
# endregion