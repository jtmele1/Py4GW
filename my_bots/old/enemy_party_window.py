import csv
import inspect
from Py4GWCoreLib import *

class BotVariables():
    current_agents  = []
    requested_names = []
    overlay         = Overlay()
    ini             = IniHandler('enemy_party_window.ini')

    class Filters:
        sorting      = 'No Preference'
        enchantments = 'No Preference'
        conditions   = 'No Preference'
        hexes        = 'No Preference'
        health       = 'No Preference'
        
    class Timers:
        throttle = Timer()
        ini      = Timer()

        throttle.Start()
        ini.Start()

        class Checks:
            throttle = 200
            ini      = 1000

        checks = Checks()

    class GUI:
        main_module = ImGui.WindowModule('Enemy Party', window_name='Enemy Party', window_size=(150, 208),
                                         window_flags=PyImGui.WindowFlags.AlwaysAutoResize)
        initialized = False
        pos_x = 900
        pos_y = 600
        overlay_x = 1200
        overlay_y = 600
        height = 20
        width = 250
        rows  = 15
        button_ys = []
    
    filters = Filters()
    timers  = Timers()
    gui     = GUI()

bot_vars = BotVariables()

def Debug(message, title = 'DEBUG', msg_type = 'Debug'):
    if msg_type == 'Debug':         py4gw_msg_type = Py4GW.Console.MessageType.Debug
    elif msg_type == 'Error':       py4gw_msg_type = Py4GW.Console.MessageType.Error
    elif msg_type == 'Info':        py4gw_msg_type = Py4GW.Console.MessageType.Info
    elif msg_type == 'Notice':      py4gw_msg_type = Py4GW.Console.MessageType.Notice
    elif msg_type == 'Performance': py4gw_msg_type = Py4GW.Console.MessageType.Performance
    elif msg_type == 'Success':     py4gw_msg_type = Py4GW.Console.MessageType.Success
    elif msg_type == 'Warning':     py4gw_msg_type = Py4GW.Console.MessageType.Warning
    Py4GW.Console.Log(title, str(message), py4gw_msg_type)

def LoadSettings():
    global bot_vars

    bot_vars.gui.pos_x            = bot_vars.ini.read_int('ui'     , 'pos_x'       , 900)
    bot_vars.gui.pos_y            = bot_vars.ini.read_int('ui'     , 'pos_y'       , 600)
    bot_vars.gui.overlay_x        = bot_vars.ini.read_int('ui'     , 'overlay_x'   , 1400)
    bot_vars.gui.overlay_y        = bot_vars.ini.read_int('ui'     , 'overlay_y'   , 600)
    bot_vars.gui.height           = bot_vars.ini.read_int('ui'     , 'height'      , 20)
    bot_vars.gui.width            = bot_vars.ini.read_int('ui'     , 'width'       , 250)
    bot_vars.gui.rows             = bot_vars.ini.read_int('ui'     , 'rows'        , 15)
    bot_vars.filters.sorting      = bot_vars.ini.read_key('filters', 'sorting'     , 'No Preference')
    bot_vars.filters.enchantments = bot_vars.ini.read_key('filters', 'enchantments', 'No Preference')
    bot_vars.filters.conditions   = bot_vars.ini.read_key('filters', 'conditions'  , 'No Preference')
    bot_vars.filters.hexes        = bot_vars.ini.read_key('filters', 'hexes'       , 'No Preference')
    bot_vars.filters.health       = bot_vars.ini.read_key('filters', 'health'      , 'No Preference')

def SaveSettings():
    global bot_vars

    settings = configparser.ConfigParser()

    settings['ui'] = {
        'pos_x'          : bot_vars.gui.pos_x,
        'pos_y'          : bot_vars.gui.pos_y,
        'overlay_x'      : bot_vars.gui.overlay_x,
        'overlay_y'      : bot_vars.gui.overlay_y,
        'height'         : bot_vars.gui.height,
        'width'          : bot_vars.gui.width,
        'rows'           : bot_vars.gui.rows,
    }
    settings['filters'] = {
        'sorting'      : bot_vars.filters.sorting,
        'enchantments' : bot_vars.filters.enchantments,
        'conditions'   : bot_vars.filters.conditions,
        'hexes'        : bot_vars.filters.hexes,
        'health'       : bot_vars.filters.health
    }

    bot_vars.ini.save(settings)

def GetAgentArray():
    global bot_vars

    agent_array = AgentArray.GetEnemyArray()
    agent_array = AgentArray.Filter.ByAttribute(agent_array, 'IsAlive')

    # sorting
    if bot_vars.filters.sorting == 'By Distance': agent_array = AgentArray.Sort.ByDistance(agent_array, Player.GetXY())
    if bot_vars.filters.sorting == 'By Health': agent_array = AgentArray.Sort.ByHealth(agent_array)

    # filtering
    if bot_vars.filters.enchantments == 'Is Enchanted'      : agent_array = AgentArray.Filter.ByAttribute(agent_array, 'IsEnchanted')
    if bot_vars.filters.enchantments == 'Is Not Enchanted'  : agent_array = AgentArray.Filter.ByAttribute(agent_array, 'IsEnchanted',   negate = True)
    if bot_vars.filters.conditions   == 'Is Conditoned'     : agent_array = AgentArray.Filter.ByAttribute(agent_array, 'IsConditioned')
    if bot_vars.filters.conditions   == 'Is Not Conditoned' : agent_array = AgentArray.Filter.ByAttribute(agent_array, 'IsConditioned', negate = True)
    if bot_vars.filters.hexes        == 'Is Hexed'          : agent_array = AgentArray.Filter.ByAttribute(agent_array, 'IsHexed')
    if bot_vars.filters.hexes        == 'Is Not Hexed'      : agent_array = AgentArray.Filter.ByAttribute(agent_array, 'IsHexed',       negate = True)


    bot_vars.current_agents = agent_array

def DrawOverlay():
    global bot_vars

    def CustomQuad(pos_x,pos_y,size_x,size_y,color, filled = True):
        if filled:
            bot_vars.overlay.DrawQuadFilled(pos_x,          pos_y,
                                            pos_x + size_x, pos_y,
                                            pos_x + size_x, pos_y + size_y,
                                            pos_x,          pos_y + size_y,
                                            color = color)
        else:
            size_x -= 1
            size_y -= 1
            bot_vars.overlay.DrawLine(pos_x,          pos_y,          pos_x + size_x, pos_y,          color=color, thickness=1)
            bot_vars.overlay.DrawLine(pos_x,          pos_y + size_y, pos_x + size_x, pos_y + size_y, color=color, thickness=1)
            bot_vars.overlay.DrawLine(pos_x,          pos_y,          pos_x,          pos_y + size_y, color=color, thickness=1)
            bot_vars.overlay.DrawLine(pos_x + size_x, pos_y,          pos_x + size_x, pos_y + size_y+1, color=color, thickness=1)

            # bot_vars.overlay.DrawQuad(pos_x,            pos_y,
            #                           pos_x + size_x-1, pos_y,
            #                           pos_x + size_x-1, pos_y + size_y-1,
            #                           pos_x,            pos_y + size_y-1,
            #                           color = color,    thickness = 1)

    # load ini settings
    if not bot_vars.gui.initialized:
        LoadSettings()
        bot_vars.gui.initialized = True

    # periodically save ini settings
    if bot_vars.timers.ini.HasElapsed(bot_vars.timers.checks.ini):
        bot_vars.timers.ini.Reset()
        SaveSettings()

    # settings
    x = bot_vars.gui.overlay_x
    y = bot_vars.gui.overlay_y
    border = 3
    bar_height = bot_vars.gui.height
    width = bot_vars.gui.width
    num_agents = min(len(bot_vars.current_agents), bot_vars.gui.rows)
    height = num_agents*(bar_height + border) + border
    target_id = Player.GetTargetID()

    # begin drawing
    bot_vars.overlay.BeginDraw()
    # draw background
    CustomQuad(x,     y,
               width, height + 15,
               Utils.RGBToColor(0,0,0,200))
    # draw title
    bot_vars.overlay.DrawText(x + width/2, y + 3,
                                  'Enemy Party')

    # draw health bars
    for i,agent in enumerate(bot_vars.current_agents):
        # limit targets
        if i >= bot_vars.gui.rows: return

        # draw bar
        x_bar = x + border
        y_bar = y + i*(bar_height + border) + border + 15
        CustomQuad(x_bar, y_bar, int(Agent.GetHealth(agent)*(width - 2*border)), bar_height, Utils.RGBToColor(255,0,0,255))

        # check for hover and click    
        mouse_pos = bot_vars.overlay.GetMouseCoords()
        if (mouse_pos[0] >= x + border and 
            mouse_pos[0] <= x + border + width - 2*border and 
            mouse_pos[1] >= y + i*(bar_height + border) + border + 15 and 
            mouse_pos[1] <= y + i*(bar_height + border) + border + 15 + bar_height):

            CustomQuad(x_bar, y_bar, int(Agent.GetHealth(agent)*(width - 2*border)), bar_height, Utils.RGBToColor(255,255,0,255), filled=False)

            if bot_vars.overlay.IsMouseClicked():
                Player.ChangeTarget(agent)

        # highlight target
        text_color = Utils.RGBToColor(255,255,255,255)
        if target_id == agent:
            text_color = Utils.RGBToColor(255,255,0,255)

        # draw names
        if agent in bot_vars.requested_names and Agent.IsNameReady(agent):
            name = f'{Agent.GetName(agent)} [{agent}]'
        else:
            if agent not in bot_vars.requested_names:
                Agent.RequestName(agent)
                bot_vars.requested_names.append(agent)
            name = str(agent)

        bot_vars.overlay.DrawText(x + border + 3, y + i*(bar_height + border) + border + 3 + 15,
                                  name, centered = False, color = text_color)
        
        # draw statuses
        tri_width = 16
        x_offset = x_bar + width - 2*border - tri_width - 2
        if Agent.IsEnchanted(agent):
            CustomQuad(x_offset, y_bar+2, 16, 16, Utils.RGBToColor(228,254,109,255))
            CustomQuad(x_offset, y_bar+2, 16, 16, Utils.RGBToColor(0,0,0,255), filled=False)
            x_offset -= tri_width + 2
        if Agent.IsConditioned(agent):
            CustomQuad(x_offset, y_bar+2, 16, 16, Utils.RGBToColor(141,102,76,255))
            CustomQuad(x_offset, y_bar+2, 16, 16, Utils.RGBToColor(0,0,0,255), filled=False)
            x_offset -= tri_width + 2
        if Agent.IsHexed(agent):
            CustomQuad(x_offset, y_bar+2, 16, 16, Utils.RGBToColor(225,94,233,255))
            CustomQuad(x_offset, y_bar+2, 16, 16, Utils.RGBToColor(0,0,0,255), filled=False)
    # end drawing
    bot_vars.overlay.EndDraw()

def configure():
    global bot_vars

    try:
        if bot_vars.gui.main_module.first_run:  
            LoadSettings()
            PyImGui.set_next_window_pos(bot_vars.gui.pos_x, bot_vars.gui.pos_y)
            bot_vars.gui.main_module.first_run = False
            
        if PyImGui.begin(bot_vars.gui.main_module.window_name, bot_vars.gui.main_module.window_flags):
            bot_vars.gui.pos_x = PyImGui.get_window_pos()[0]
            bot_vars.gui.pos_y = PyImGui.get_window_pos()[1]

            # ui
            bot_vars.gui.overlay_x = PyImGui.slider_int('X Pos', bot_vars.gui.overlay_x, 0, 2500)
            bot_vars.gui.overlay_y = PyImGui.slider_int('Y Pos', bot_vars.gui.overlay_y, 0, 1000)

            bot_vars.gui.width  = PyImGui.slider_int('Bar Width', bot_vars.gui.width, 150, 500)
            bot_vars.gui.height = PyImGui.slider_int('Bar Height', bot_vars.gui.height, 10, 40)
            bot_vars.gui.rows   = PyImGui.input_int('Max Targets', bot_vars.gui.rows)

            PyImGui.separator()
            
            # filters
            items = ['No Preference','By Distance', 'By Health']
            bot_vars.filters.sorting = items[PyImGui.combo('Sorting', items.index(bot_vars.filters.sorting), items)]
                
            items = ['No Preference', 'Is Enchanted', 'Is Not Enchanted']
            bot_vars.filters.enchantments = items[PyImGui.combo('Enchantments', items.index(bot_vars.filters.enchantments), items)]

            items = ['No Preference', 'Is Conditoned', 'Is Not Conditoned']
            bot_vars.filters.conditions = items[PyImGui.combo('Conditions', items.index(bot_vars.filters.conditions), items)]
            
            items = ['No Preference', 'Is Hexed', 'Is Not Hexed']
            bot_vars.filters.hexes = items[PyImGui.combo('Hexes', items.index(bot_vars.filters.hexes), items)]

            items = ['No Preference', '< 50 %', '< 75 %', '< 90 %']
            bot_vars.filters.health = items[PyImGui.combo('Health', items.index(bot_vars.filters.health), items)]

            PyImGui.pop_style_color(8)
            PyImGui.end()

    except Exception as e:
        current_function = inspect.currentframe().f_code.co_name
        Py4GW.Console.Log(bot_vars.gui.main_module.window_name, f'Error in {current_function}: {str(e)}', Py4GW.Console.MessageType.Error)
        raise

def main():
    global bot_vars

    try:
        # reset agent names when zoning
        if Map.IsMapLoading():
            bot_vars.requested_names = []


        # show overlay when data is loaded
        if Map.IsMapReady() and Party.IsPartyLoaded():
            configure()
            if Map.IsExplorable():
                DrawOverlay()

            # throttle script calls
            ping = Py4GW.PingHandler().GetCurrentPing() + 50
            if bot_vars.timers.throttle.HasElapsed(max(ping,bot_vars.timers.checks.throttle)):
                bot_vars.timers.throttle.Reset()
                GetAgentArray()

    except ImportError as e:
        Py4GW.Console.Log(bot_vars.gui.main_module.window_name, f'ImportError encountered: {str(e)}', Py4GW.Console.MessageType.Error)
        Py4GW.Console.Log(bot_vars.gui.main_module.window_name, f'Stack trace: {traceback.format_exc()}', Py4GW.Console.MessageType.Error)
    except ValueError as e:
        Py4GW.Console.Log(bot_vars.gui.main_module.window_name, f'ValueError encountered: {str(e)}', Py4GW.Console.MessageType.Error)
        Py4GW.Console.Log(bot_vars.gui.main_module.window_name, f'Stack trace: {traceback.format_exc()}', Py4GW.Console.MessageType.Error)
    except TypeError as e:
        Py4GW.Console.Log(bot_vars.gui.main_module.window_name, f'TypeError encountered: {str(e)}', Py4GW.Console.MessageType.Error)
        Py4GW.Console.Log(bot_vars.gui.main_module.window_name, f'Stack trace: {traceback.format_exc()}', Py4GW.Console.MessageType.Error)
    except Exception as e:
        Py4GW.Console.Log(bot_vars.gui.main_module.window_name, f'Unexpected error encountered: {str(e)}', Py4GW.Console.MessageType.Error)
        Py4GW.Console.Log(bot_vars.gui.main_module.window_name, f'Stack trace: {traceback.format_exc()}', Py4GW.Console.MessageType.Error)
    finally:
        pass

if __name__ == '__main__':
    main()