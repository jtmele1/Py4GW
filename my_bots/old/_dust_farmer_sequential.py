# region imports
from bot_routines import *
from datetime import datetime
# endregion

# region classes
class BotVariables:
    bot_started  = False
    do_setup     = True
    handle_inv   = False
    
    class Timers:
        total     = Timer()
        lap       = Timer()
        lap_times = []

    class Loot:
        coins    = True
        log_list = ['gold',929,441]

    class GUI:
        window_module = ImGui.WindowModule('Dust Farmer',window_name='Curtain Dust Farm',window_pos=(234,802),
                                           window_flags=PyImGui.WindowFlags.AlwaysAutoResize)
        window_pos:    tuple[float,float] = (0,0)
        window_size:   tuple[float,float] = (0,0)
        settings_pos:  tuple[float,float] = (0,0)
        settings_size: tuple[float,float] = (0,0)

        class Stats:
            status        = [datetime.now().strftime('%H:%M:%S'),'waiting for input']
            runs          = 0
            fails         = 0
            avg_time      = 0
            dust          = 0
            dust_per_hour = 0
            starting_dust = Inventory.GetModelCount(929)
            total_dust    = Inventory.GetModelCount(929)
            gold_coins    = 0
            remains       = 0

        class Opts:
            show_settings   = False
            condense_tables = False
            color_rows      = True
            show_all        = False

            class Rows:
                runs       = True
                fails      = True
                pace       = True
                lap_time   = False
                total_time = True
                dust       = True
                dust_hr    = False
                start_dust = False
                total_dust = False
                coins      = False
                remains    = True

                def GetRows(self) -> list:
                    return [self.runs, self.fails, 
                            self.pace, self.lap_time, self.total_time,
                            self.dust,self.dust_hr,self.start_dust,self.total_dust,
                            self.coins,self.remains]
            
            rows = Rows()

        stats = Stats()
        opts = Opts()
                
    timers = Timers()
    loot   = Loot()
    gui    = GUI()

class Path:
    zone   = [(-5096, 16560),(-5200, 16000)]
    rezone = [(-5124, 16439)]
    merch  = [(-5034, 19329)]
    farm   = [(-6854, 14613),(-7761, 12286),(-6228, 7567),(-4783, 6108),
              (-2103, 3318),(2872, 273),(6008, -1207),(7653, -2127),
              (7348, -3619),(10026, -6060),(12097, -7507),(12769, -4257),
              (12857, 364),(12519, 1257),(10434, 1086)]
    
class Maps:
    toa     = 138
    curtain = 18

class Build:
    # template
    template = 'OgCjkirMrSmXfbDYqifXsX7X9gA'
    # weapon slots
    scythe = 1
    staff  = 2
    # skills
    ss  = 1
    vos = 2
    cv  = 3
    dm  = 4
    mv  = 5
    mr = 6
    ia = 7
    ea  = 8

    class Effects:
        ss  = 1510
        vos = 1759
        sf  = 1498
        ea  = 1485
        da  = 1043
        mv  = 1762
        cv  = 1515
        mr  = 1516
# endregion

# region globals
bot_vars       = BotVariables()
thread_manager = MultiThreading(timeout = 5)
sq             = SynchronousRoutines()
# endregion

# region helper functions
def StartBot():
    global bot_vars

    thread_manager.stop_all_threads()
    thread_manager.add_thread('SynchronousLogic', SynchronousLogic)
    thread_manager.start_watchdog('SynchronousLogic')
    bot_vars.bot_started = True
    bot_vars.timers.total.Start()

    Log('Starting script.')

def StopBot():
    global bot_vars, action_queue
    thread_manager.stop_all_threads()
    action_queue.clear()
    bot_vars.bot_started = False
    bot_vars.timers.total.Pause()
    bot_vars.timers.lap.Stop()

    Log('Stopping script.')

def ToggleDebug():
  global debug
  debug = not debug

def CheckRequirements():
    global bot_vars

    error = False
    error_msgs = []

    # check attributes (for runes)
    attribute_checks = {'Scythe Mastery' : 9,
                        'Earth Prayers'  : 16,
                        'Mysticism'      : 11}
    for attribute in Agent.GetAttributes(Player.GetAgentID()):
        if attribute.GetName() in attribute_checks:
            if attribute_checks[attribute.GetName()] != attribute.level:
                error_msgs.append(f'\tAttribute "{attribute.GetName()}" differs from requirement of {attribute_checks[attribute.GetName()]}.')
                error = True

    # check skills
    for i in range(1,9):
        skill_instance = PySkill.Skill(SkillBar.GetSkillIDBySlot(i))
        if skill_instance.id.id == 0:
            error_msgs.append(f'\tSkill slot [{i}] is empty.')
            error = True

    # display errors
    if error:
        Log('Requirments check failed.', msg_type = 'Error')
        for msg in error_msgs:
            Log(msg, msg_type = 'Error')
    else:
        Log('Requirments check passed.', msg_type = 'Success')

def SetStatus(status):
    global bot_vars
    bot_vars.gui.stats.status = [datetime.now().strftime('%H:%M:%S'),status]
    Log(status)

def LogLap():
    global bot_vars

    if Agent.IsDead(Player.GetAgentID()):
        bot_vars.gui.stats.fails += 1
        return

    bot_vars.gui.stats.runs += 1
    lap_time = bot_vars.timers.lap.GetElapsedTime()
    bot_vars.timers.lap_times.append(lap_time)
    bot_vars.timers.lap.Stop()
    bot_vars.gui.stats.avg_time = int(sum(bot_vars.timers.lap_times)/bot_vars.gui.stats.runs)

    Log(f'Lap completed in {FormatTime(lap_time,mask='mm:ss')} s', msg_type = 'Notice')
# endregion

# region item functions
def GetSellList():
    banned_ids = [921,929,933,948,2989,2992,22751]
    bags_to_check = ItemArray.CreateBagList(1,2,3,4)
    item_array = ItemArray.GetItemArray(bags_to_check)
    item_array = ItemArray.Filter.ByCondition(item_array, lambda item_id: Item.GetModelID(item_id) not in banned_ids)
    item_array = ItemArray.Filter.ByCondition(item_array, lambda item_id: Item.Properties.GetValue(item_id) > 0)
    return item_array

def GetLootList():
    agent_array = AgentArray.GetItemArray()

    valid_model_ids = [929, 441] # dust, remains
    if bot_vars.loot.coins: valid_model_ids.append(2511)

    item_array = AgentArray.Filter.ByCondition(agent_array, lambda agent_id: Item.GetModelID(Agent.GetItemAgent(agent_id).item_id) in valid_model_ids)
    item_array = AgentArray.Sort.ByDistance(item_array,Player.GetXY())

    return item_array

def CatalogLoot(inv_log):
    global bot_vars

    curr_inv = SynchronousRoutines.Items.LogInventory(bot_vars.loot.log_list)
    new_inv  = {key: curr_inv[key] - inv_log[key] for key in set(inv_log) & set(curr_inv)}

    bot_vars.gui.stats.gold_coins += new_inv['gold']
    bot_vars.gui.stats.dust       += new_inv[929]
    bot_vars.gui.stats.remains    += new_inv[441]

    if not bot_vars.handle_inv:
        bot_vars.gui.stats.dust_per_hour = int(bot_vars.gui.stats.dust*3600000/bot_vars.timers.total.GetElapsedTime())
    bot_vars.gui.stats.total_dust = Inventory.GetModelCount(929)

    Log('Loot from current lap:',             msg_type = 'Notice')
    Log(f' -  Gold coins: {new_inv['gold']}', msg_type = 'Notice')
    Log(f' -  Dust: {new_inv[929]}',          msg_type = 'Notice')
    Log(f' -  Remains: {new_inv[441]}',       msg_type = 'Notice')
# endregion

# region combat functions
def InDangerZone():
    if Agent.IsDead(Player.GetAgentID()): return
    if Agent.GetHealth(Player.GetAgentID()) < 0.7: return

def TargetsInRange(range = 1000, model_ids = None):
    enemy_array = AgentArray.GetEnemyArray()
    enemy_array = AgentArray.Filter.ByAttribute(enemy_array, 'IsAlive')
    if model_ids:
        if not isinstance(model_ids, list):
            model_ids = [model_ids]
        enemy_array = AgentArray.Filter.ByCondition(enemy_array, lambda agent_id: Agent.GetPlayerNumber(agent_id) in model_ids)
    enemy_array = AgentArray.Filter.ByDistance(enemy_array, Player.GetXY(), range)
    return enemy_array

def FindAloe(range = 1200):
    enemy_array = TargetsInRange(range, model_ids = [1731])
    enemy_array = AgentArray.Sort.ByDistance(enemy_array, Player.GetXY())
    if enemy_array:
        return enemy_array[0]

    return False

def Run():
    for skill in [Build.ea, Build.dm]:
        if not sq.Skills.HasEffect(skill) and sq.Skills.IsRecharged(skill):
            sq.Skills.CastSkill(skill)

    if Agent.GetHealth(Player.GetAgentID()) < .95:
        if not sq.Skills.HasEffect(Build.mr) and sq.Skills.IsRecharged(Build.mr):
            sq.Skills.CastSkill(Build.mr)

    if len(TargetsInRange(800, model_ids = [1729])) >= 2:
        action_queue.add_action(Keystroke.PressAndRelease,Key.S.value)
        sleep(.1)

def WaitForSettle():
    SetStatus('Waiting for enemies.')
    timer = Timer()
    timer.Start()
    while True:
        if InDangerZone():          return
        if timer.HasElapsed(10000): return

        # wait for foes to ball
        enemy_array = TargetsInRange(800, model_ids = [1729])
        enemy_array = AgentArray.Sort.ByDistance(enemy_array, Player.GetXY(), descending = True)
        if not enemy_array:
            return
        
        if Utils.Distance(Player.GetXY(),Agent.GetXY(enemy_array[0])) <= Range.Adjacent.value:
            return
        
        # move to aloe if one exists
        aloe = TargetsInRange(1000, model_ids = [1731])
        if aloe:
            x, y = Agent.GetXY(aloe[0])
            if Utils.Distance(Player.GetXY(), (x, y)) > Range.Adjacent.value:
                if not Agent.IsMoving(Player.GetAgentID()):
                    action_queue.add_action(Player.Move, x, y)

        # maintain mystic regen and mystic vigor
        for skill in [Build.ea, Build.ia, Build.mr, Build.mv, Build.ss, Build.vos]:
            if not sq.Skills.HasEffect(skill) and sq.Skills.IsRecharged(skill):
                sq.Skills.CastSkill(skill)
                continue

        sleep(.5)

def Kill():
    SetStatus('Killing enemies.')
    sq.Skills.ChangeWeaponSet(Build.scythe, 'Scythe')
    # kill remaining foes
    while True:
        if Agent.IsDead(Player.GetAgentID()):
            return

        # check for remaming enemies
        if not TargetsInRange(800, model_ids = [1729]):
            return

        # maintain mystic regen , mystic vigor, conviction, and vos
        for skill in [Build.ea, Build.ia, Build.mr, Build.mv, Build.ss, Build.vos]:
            if not sq.Skills.HasEffect(skill) and sq.Skills.IsRecharged(skill):
                sq.Skills.CastSkill(skill)
                continue
        
        # select target
        target_id = Player.GetTargetID()
        if target_id == 0 or Agent.GetAllegiance(target_id)[0] != 3 or Agent.IsDead(target_id):
            sq.Agents.TargetNearestEnemy()

        # cast chilling victory
        if sq.Skills.HasEnoughAdrenaline(Build.cv):
            sq.Skills.CastSkill(Build.cv)

        # attack
        if not Agent.IsAttacking(Player.GetAgentID()):
            sq.Agents.Interact()

        sleep(1)

def Farm():
    Run()
    if TargetsInRange(800, model_ids = [1729]):
        WaitForSettle()
        Kill()
        SetStatus('Looting.')
        sq.Items.Loot(GetLootList())
        sq.Skills.ChangeWeaponSet(Build.staff)
        SetStatus('Continuing farm.')
# endregion

# region synchronous functions
def SynchronousLogic():
    global bot_vars

    while True:
        if not bot_vars.bot_started:
            sleep(1)
            continue

        # setup routine
        if (bot_vars.do_setup or Map.GetMapID() != Maps.toa) and not bot_vars.handle_inv:
            SetStatus('Setting up.')
            bot_vars.do_setup = False
            sq.Maps.Travel(Maps.toa)
            sq.Skills.LoadSkillBar(Build.template)
            CheckRequirements()
            sq.Maps.SetMode(0)
            sq.Move.Zone(Path.zone, Maps.curtain)
            sq.Move.Zone(Path.rezone, Maps.toa)

        # inventory management
        if Inventory.GetModelCount(441) >= 50 or bot_vars.handle_inv:
            SetStatus('Handling inventory.')
            sq.Items.RequestInvNames()
            sq.Move.FollowPath(Path.merch)
            sq.Agents.TargetNearestNPC()
            sq.Agents.Interact(frame_alias = 'Merchant Window')
            inv_log = sq.Items.LogInventory(bot_vars.loot.log_list)
            sq.Items.ProcessInventory(sell_func=GetSellList)
            CatalogLoot(inv_log)
            if bot_vars.handle_inv:
                bot_vars.bot_started = False
                thread_manager.stop_all_threads()
                return
            
        # farm routine
        SetStatus('Leaving ToA.')
        bot_vars.timers.lap.Start()
        sq.Skills.ChangeWeaponSet(Build.staff)
        sq.Move.Zone(Path.zone, Maps.curtain)
        inv_log = sq.Items.LogInventory(bot_vars.loot.log_list)
        SetStatus('Starting farm.')
        sq.Move.FollowPath(Path.farm, do_func = Farm, extra_status = '"Farm"')
        LogLap()
        CatalogLoot(inv_log)
        SetStatus('Resetting.')
        sq.Maps.ResignAndReturn(Maps.toa)
# endregion

# region draw
def Draw():
    global bot_vars, debug, action_queue

    def MakeTable(*columns, colors = None):
        num_cols = len(columns)
        num_rows = len(columns[0])

        if PyImGui.begin_table('Info', num_cols,   PyImGui.TableFlags.Borders |
                                                   PyImGui.TableFlags.RowBg   |
                                                   PyImGui.TableFlags.SizingStretchSame):
            for row in range(num_rows):
                PyImGui.table_next_row()
                for col in range(num_cols):
                    PyImGui.table_next_column()
                    if colors:
                        PyImGui.text_colored(str(columns[col][row]), colors[row])
                    else:
                        PyImGui.text(str(columns[col][row]))
            PyImGui.end_table()

    def FormatItemStack(count):
        return f'{count} ({round(count/250,1)})'

    def DebugFn():
        Log('running debug function', msg_type='Debug')

    def CreateRunButton():
        window_width = 250
        button_width = (window_width-20)

        if bot_vars.bot_started:
            if PyImGui.button('\uf04d', button_width, 25):
                StopBot()
        else:
            if PyImGui.button('\uf04b', button_width, 25):
                StartBot()

    def CreateStateLog():
        PyImGui.text_colored(f'[{bot_vars.gui.stats.status[0]}]', (.48, .68, 1, 1))
        PyImGui.same_line(0.0,-1.0)
        PyImGui.text(f'{bot_vars.gui.stats.status[1]}')

    def CreateTables():
        colors = {
            'runs'    : [   0,   .7,    0, 1],
            'fails'   : [   1,  .25,  .23, 1],
            'time'    : [  .9,   .9,   .9, 1],
            'dust'    : [  .9,   .9,   .9, 1],
            'remains' : [  .9,   .9,   .9, 1],
            'coins'   : [   1,  .75,    0, 1],   
        }

        columns = [
            'Runs',
            'Fails',
            'Average Pace',
            'Lap Time',
            'Total Time',
            'Dust',
            'Dust/Hour',
            'Starting Dust',
            'Total Dust',
            'Gold Coins',
            'Remains'
        ]

        values = [
            bot_vars.gui.stats.runs,
            bot_vars.gui.stats.fails,
            FormatTime(bot_vars.gui.stats.avg_time,mask='mm:ss'),
            bot_vars.timers.lap.FormatElapsedTime("hh:mm:ss"),
            bot_vars.timers.total.FormatElapsedTime("hh:mm:ss"),
            FormatItemStack(bot_vars.gui.stats.dust),
            FormatItemStack(round(bot_vars.gui.stats.dust_per_hour)),
            FormatItemStack(bot_vars.gui.stats.starting_dust),
            FormatItemStack(bot_vars.gui.stats.total_dust),
            bot_vars.gui.stats.gold_coins,
            bot_vars.gui.stats.remains
        ]

        colors = [
            colors['runs'],
            colors['fails'],
            colors['time'],
            colors['time'],
            colors['time'],
            colors['dust'],
            colors['dust'],
            colors['dust'],
            colors['dust'],
            colors['coins'],
            colors['remains'],
        ]

        table_nums = [1,1,2,2,2,3,3,3,3,4,4]

        filter = bot_vars.gui.opts.rows.GetRows()

        columns    = [item for i, item in enumerate(columns)    if filter[i]] if not bot_vars.gui.opts.show_all else columns
        values     = [item for i, item in enumerate(values)     if filter[i]] if not bot_vars.gui.opts.show_all else values
        colors     = [item for i, item in enumerate(colors)     if filter[i]] if not bot_vars.gui.opts.show_all else colors
        table_nums = [item for i, item in enumerate(table_nums) if filter[i]] if not bot_vars.gui.opts.show_all else table_nums

        if bot_vars.gui.opts.condense_tables:
            MakeTable(columns,values,colors=colors if bot_vars.gui.opts.color_rows else None)
        else:
            tables = []
            for num in list(set(table_nums)):
                table = {'columns':[],'values':[],'colors':[]}
                for i,table_num in enumerate(table_nums):
                    if table_num == num:
                        table['columns'].append(columns[i])
                        table['values'].append(values[i])
                        table['colors'].append(colors[i])
                tables.append(table)

            for table in tables:
                MakeTable(table['columns'],table['values'],colors = table['colors'] if bot_vars.gui.opts.color_rows else None)

    def CreateSettings():
        global debug
        # general
        if PyImGui.tree_node('General'):
            if PyImGui.checkbox('Debug Mode', debug) != debug:
                ToggleDebug()

            if PyImGui.button('Process Inventory',PyImGui.get_window_size()[0]-60):
                thread_manager.stop_all_threads()
                thread_manager.add_thread('SynchronousLogic', SynchronousLogic)
                thread_manager.start_watchdog('SynchronousLogic')
                bot_vars.handle_inv = True
                bot_vars.bot_started = True

            if PyImGui.button('Open Storage', PyImGui.get_window_size()[0]-60):
                if not Inventory.IsStorageOpen():
                    Inventory.OpenXunlaiWindow()

            if debug:
                if PyImGui.button('Run Debug Function', PyImGui.get_window_size()[0]-60):
                    DebugFn()

            PyImGui.tree_pop()

        # loot
        if PyImGui.tree_node('Loot'):
            bot_vars.loot.coins        = PyImGui.checkbox('Gold Coins',        bot_vars.loot.coins)
            PyImGui.tree_pop()

        # gui
        if PyImGui.tree_node('User Interface  '):
            bot_vars.gui.opts.condense_tables = PyImGui.checkbox('Condense Tables', bot_vars.gui.opts.condense_tables)
            bot_vars.gui.opts.color_rows      = PyImGui.checkbox('Color Rows',      bot_vars.gui.opts.color_rows)
            bot_vars.gui.opts.show_all        = PyImGui.checkbox('Show All',        bot_vars.gui.opts.show_all)
            PyImGui.separator()
            bot_vars.gui.opts.rows.lap_time   = PyImGui.checkbox('Lap Time',        bot_vars.gui.opts.rows.lap_time)
            bot_vars.gui.opts.rows.dust_hr    = PyImGui.checkbox('Dust per Hour',   bot_vars.gui.opts.rows.dust_hr)
            bot_vars.gui.opts.rows.start_dust = PyImGui.checkbox('Starting Dust',   bot_vars.gui.opts.rows.start_dust)
            bot_vars.gui.opts.rows.total_dust = PyImGui.checkbox('Total Dust',      bot_vars.gui.opts.rows.total_dust)
            bot_vars.gui.opts.rows.coins      = PyImGui.checkbox('Gold Coins',      bot_vars.gui.opts.rows.coins)

            bot_vars.gui.opts.rows.remains    = PyImGui.checkbox('Remains',         bot_vars.gui.opts.rows.remains)
            PyImGui.tree_pop()

        # general
        if PyImGui.tree_node('Description'):
            PyImGui.text('This bot uses a Dervish to farm')
            PyImGui.text('dust in The Black Curtain. It will')
            PyImGui.text('loot dust, remains, and coins.')
            PyImGui.text('At 50 remains,it will salvage them.')
            PyImGui.text('Development was done using')
            PyImGui.text('the requirements below.')
            PyImGui.tree_pop()

        # build
        if PyImGui.tree_node('Requirements  '):
            PyImGui.text('Map:')
            PyImGui.text('     Temple of the Ages')
            PyImGui.text('Build:')
            PyImGui.text('     Sand Shards')
            PyImGui.text('     Vos of Strength')
            PyImGui.text('     Staggering Force')
            PyImGui.text('     Eremite\'s Attack')
            PyImGui.text('     Dash')
            PyImGui.text('     Mystuc Vigor')
            PyImGui.text('     Armor of Sanctity')
            PyImGui.text('     Mystic Regeneration')
            PyImGui.text('Weapons:')
            PyImGui.text('     Slot 1 - Zealous +15%^Ench Scythe of Enchanting')
            PyImGui.text('     Slot 1 - Any Staff of Enchanting')
            PyImGui.text('Armor:')
            PyImGui.text('     x5 Windwalker Insignias')
            PyImGui.text('     +4 Earth Prayers')
            PyImGui.text('     +1 Scythe Mastery')
            PyImGui.text('     +1 Mysticism')
            PyImGui.text('     x2 Runes of Attunement')
            PyImGui.tree_pop()

    def Run():
        if bot_vars.gui.window_module.first_run:
            PyImGui.set_next_window_size(bot_vars.gui.window_module.window_size[0], bot_vars.gui.window_module.window_size[1])     
            PyImGui.set_next_window_pos(bot_vars.gui.window_module.window_pos[0], bot_vars.gui.window_module.window_pos[1])
            bot_vars.gui.window_module.first_run = False

            PyImGui.push_style_var(ImGui.ImGuiStyleVar.WindowBorderSize,0.0)
            PyImGui.push_style_var(ImGui.ImGuiStyleVar.WindowRounding,0.0)
            PyImGui.push_style_var(ImGui.ImGuiStyleVar.FrameRounding,0.0)
            
            PyImGui.push_style_color(PyImGui.ImGuiCol.FrameBg,        (.2,.2,.2,1))
            PyImGui.push_style_color(PyImGui.ImGuiCol.FrameBgHovered, (.3,.3,.3,1))
            PyImGui.push_style_color(PyImGui.ImGuiCol.FrameBgActive,  (.4,.4,.4,1))
            PyImGui.push_style_color(PyImGui.ImGuiCol.CheckMark,      (.9,.9,.9,1))

            PyImGui.push_style_color(PyImGui.ImGuiCol.WindowBg,         (0.0, 0.0, 0.0, 0.7))
            PyImGui.push_style_color(PyImGui.ImGuiCol.TitleBg,          (0.0, 0.0, 0.0, 0.7))
            PyImGui.push_style_color(PyImGui.ImGuiCol.TitleBgActive,    (0.0, 0.0, 0.0, 0.7))
            PyImGui.push_style_color(PyImGui.ImGuiCol.TitleBgCollapsed, (0.0, 0.0, 0.0, 0.7))

        try:
            PyImGui.push_style_color(PyImGui.ImGuiCol.Button,        (.2,.2,.2,1))
            PyImGui.push_style_color(PyImGui.ImGuiCol.ButtonHovered, (.3,.3,.3,1))
            PyImGui.push_style_color(PyImGui.ImGuiCol.ButtonActive,  (.4,.4,.4,1))

            if PyImGui.begin(bot_vars.gui.window_module.window_name, bot_vars.gui.window_module.window_flags):
                bot_vars.gui.window_pos  = PyImGui.get_window_pos()
                bot_vars.gui.window_size = PyImGui.get_window_size()

                CreateRunButton()
                CreateStateLog()
                CreateTables()
                if PyImGui.tree_node('Settings'):
                    CreateSettings()
                    PyImGui.tree_pop()
            PyImGui.end()

            PyImGui.pop_style_color(3)
        except Exception as e:
            current_function = inspect.currentframe().f_code.co_name # type: ignore
            Py4GW.Console.Log('BOT', f'Error in {current_function}: {str(e)}', Py4GW.Console.MessageType.Error)
            raise

    Run()
# endregion

# region main
def main():
    global bot_vars, action_queue

    try:
        if bot_vars.bot_started:
            thread_manager.update_all_keepalives()

        if not Map.IsMapReady() or not Party.IsPartyLoaded(): return

        Draw()

        if not action_queue.is_empty():
            action_queue.ProcessQueue()
        
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