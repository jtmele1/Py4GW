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
        log_list = ['gold',933,835]

    class GUI:
        window_module = ImGui.WindowModule('Feather Farmer',window_name='Jaya Feather Farm',window_pos=(234,802),
                                           window_flags=PyImGui.WindowFlags.AlwaysAutoResize)
        window_pos:    tuple[float,float] = (0,0)
        window_size:   tuple[float,float] = (0,0)
        settings_pos:  tuple[float,float] = (0,0)
        settings_size: tuple[float,float] = (0,0)

        class Stats:
            status            = [datetime.now().strftime('%H:%M:%S'),'waiting for input']
            runs              = 0
            fails             = 0
            avg_time          = 0
            feathers          = 0
            feathers_per_hour = 0
            starting_feathers = Inventory.GetModelCount(933)
            total_feathers    = Inventory.GetModelCount(933)
            gold_coins        = 0
            lockpicks         = 0
            crests            = 0

        class Opts:
            show_settings   = False
            condense_tables = False
            color_rows      = True
            show_all        = False

            class Rows:
                runs           = True
                fails          = True
                pace           = True
                lap_time       = False
                total_time     = True
                feathers       = True
                feathers_hr    = False
                start_feathers = False
                total_feathers = False
                coins          = False
                picks          = False
                crests         = True

                def GetRows(self) -> list:
                    return [self.runs, self.fails, 
                            self.pace, self.lap_time, self.total_time,
                            self.feathers,self.feathers_hr,self.start_feathers,self.total_feathers,
                            self.coins,self.picks,self.crests]
            
            rows = Rows()

        stats = Stats()
        opts = Opts()
                
    timers = Timers()
    loot   = Loot()
    gui    = GUI()

class Path:
    zone   = [(16800, 17550)]
    zone1  = [(18127, 11740),(19196, 13149),(17288, 17243),(16800, 17550)]
    zone2  = [(20556, 11582),(19196, 13149),(17288, 17243),(16800, 17550)]
    zone3  = [(17912, 13531),(19196, 13149),(17288, 17243),(16800, 17550)]
    rezone = [(10924, -13325)]
    merch  = [(17180, 12325)]
    farm   = [(8759, -12485),(7737, -10285),(3964, -9693),(1606, -6805),(-114, -4725),
              (-1536, -1686),(586, -76),(-1556, 2786),(-2229, -815),(-5247, -3290),
              (-6994, -2273),(-5042, -6638),(-11040, -8577),(-10232, -3820)]
    
class Maps:
    seitung = 250
    jaya    = 196

class Build:
    # template
    template = 'OgejkmrMbOm3vt2t5OBF3rX2LA'
    # weapon slots
    scythe = 1
    staff  = 2
    # skills
    ss  = 1
    vos = 2
    sf  = 3
    ea  = 4
    da  = 5
    hof = 6
    aos = 7
    mr  = 8

    class Effects:
        ss  = 1510
        vos = 1759
        sf  = 1498
        ea  = 1485
        da  = 1043
        mv  = 1762
        aos = 1515
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
    attribute_checks = {'Scythe Mastery' : 10,
                        'Earth Prayers'  : 16,
                        'Mysticism'      : 10}
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

    valid_model_ids = [933, 835] # feathers, crests
    if bot_vars.loot.coins:    valid_model_ids.append(2511)

    item_array = AgentArray.Filter.ByCondition(agent_array, lambda agent_id: Item.GetModelID(Agent.GetItemAgent(agent_id).item_id) in valid_model_ids)
    item_array = AgentArray.Sort.ByDistance(item_array,Player.GetXY())

    return item_array

def CatalogLoot(inv_log):
    global bot_vars

    curr_inv = SynchronousRoutines.Items.LogInventory(bot_vars.loot.log_list)
    new_inv  = {key: curr_inv[key] - inv_log[key] for key in set(inv_log) & set(curr_inv)}

    bot_vars.gui.stats.gold_coins += new_inv['gold']
    bot_vars.gui.stats.feathers   += new_inv[933]
    bot_vars.gui.stats.crests     += new_inv[835]

    bot_vars.gui.stats.feathers_per_hour = int(bot_vars.gui.stats.feathers*3600000/bot_vars.timers.total.GetElapsedTime())
    bot_vars.gui.stats.total_feathers = Inventory.GetModelCount(933)

    Log('Loot from current lap:',             msg_type = 'Notice')
    Log(f' -  Gold coins: {new_inv['gold']}', msg_type = 'Notice')
    Log(f' -  Feathers: {new_inv[933]}',      msg_type = 'Notice')
    Log(f' -  Crests: {new_inv[835]}',        msg_type = 'Notice')
# endregion

# region combat functions
def ChoosePath():
    global bot_vars

    pos = Player.GetXY()
    if   Utils.Distance(pos,(18383,11202))  < 750: return Path.zone1
    elif Utils.Distance(pos,(18786, 9415))  < 750: return Path.zone2
    elif Utils.Distance(pos,(16669, 11862)) < 750: return Path.zone3
    return Path.zone1[1:]

def Run():
    if sq.Skills.IsRecharged(Build.da):
        sq.Skills.CastSkill(Build.da)
        sleep(.1)

def WaitForSettle():
    SetStatus('Waiting for enemies.')
    timer = Timer()
    timer.Start()
    while True:
        if Agent.IsDead(Player.GetAgentID()):          return
        if Agent.GetHealth(Player.GetAgentID()) < 0.4: return
        if timer.HasElapsed(15000):                    return

        # wait for foes to ball
        enemy_array = AgentArray.GetEnemyArray()
        enemy_array = AgentArray.Filter.ByAttribute(enemy_array, 'IsAlive')
        enemy_array = AgentArray.Filter.ByCondition(enemy_array, lambda agent_id: Agent.GetPlayerNumber(agent_id) in [3944,3946,3948])
        enemy_array = AgentArray.Filter.ByDistance(enemy_array, Player.GetXY(), 800)
        enemy_array = AgentArray.Sort.ByDistance(enemy_array, Player.GetXY(), descending = True)
        if not enemy_array: return
        
        if Utils.Distance(Player.GetXY(),Agent.GetXY(enemy_array[0])) <= Range.Adjacent.value:
            return

        # maintain mystic regen and mystic vigor
        for skill in [Build.mr, Build.ss]:
            if not sq.Skills.HasEffect(skill) and sq.Skills.IsRecharged(skill):
                sq.Skills.CastSkill(skill)

        # use armor of sanctity
        if not sq.Skills.HasEffect(Build.aos) and sq.Skills.IsRecharged(Build.aos) and Agent.GetHealth(Player.GetAgentID()) < 0.75:
            sq.Skills.CastSkill(Build.aos)

        sleep(.5)

def Kill():
    SetStatus('Killing enemies.')
    # ensure enough energy for spike
    while sq.Skills.GetEnergy() < 30:
        sleep(.5)
    # prep enchantments
    for skill in [Build.ss, Build.vos, Build.sf]:
        while not sq.Skills.HasEffect(skill):
            sq.Skills.CastSkill(skill)
            sleep(.1)
    # spike
    sq.Skills.ChangeWeaponSet(Build.scythe, 'Scythe')
    sq.Agents.TargetNearestEnemy()
    sq.Skills.CastSkill(Build.ea)
    # kill remaining foes
    while True:
        sleep(1)

        if Agent.IsDead(Player.GetAgentID()):
            return

        # check for remaming enemies
        enemy_array = AgentArray.GetEnemyArray()
        enemy_array = AgentArray.Filter.ByAttribute(enemy_array, 'IsAlive')
        enemy_array = AgentArray.Filter.ByCondition(enemy_array, lambda agent_id: Agent.GetPlayerNumber(agent_id) in [3944,3946,3948])
        enemy_array = AgentArray.Filter.ByDistance(enemy_array, Player.GetXY(), 600)
        if not enemy_array:
            return

        # maintain mystic regen and vos
        for skill in [Build.mr, Build.vos]:
            if not sq.Skills.HasEffect(skill) and sq.Skills.IsRecharged(skill):
                sq.Skills.CastSkill(skill)
                continue

        # use armor of sanctity
        if not sq.Skills.HasEffect(Build.aos) and sq.Skills.IsRecharged(Build.aos) and Agent.GetHealth(Player.GetAgentID()) < 0.75:
            sq.Skills.CastSkill(Build.aos)

        # use heart of fury
        if sq.Skills.HasEnoughAdrenaline(Build.hof):
            sq.Skills.CastSkill(Build.hof)
        
        # select target
        target_id = Player.GetTargetID()
        if target_id == 0 or Agent.GetAllegiance(target_id)[0] != 3 or Agent.IsDead(target_id):
            sq.Agents.TargetNearestEnemy()

        # attack
        if not Agent.IsAttacking(Player.GetAgentID()):
            sq.Agents.Interact()

def Farm():
    Run()
    enemy_array = AgentArray.GetEnemyArray()
    enemy_array = AgentArray.Filter.ByAttribute(enemy_array, 'IsAlive')
    enemy_array = AgentArray.Filter.ByCondition(enemy_array, lambda agent_id: Agent.GetPlayerNumber(agent_id) in [3944,3946,3948])
    enemy_array = AgentArray.Filter.ByDistance(enemy_array, Player.GetXY(), 800)
    if enemy_array:
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
        if (bot_vars.do_setup or Map.GetMapID() != Maps.seitung) and not bot_vars.handle_inv:
            SetStatus('Setting up.')
            bot_vars.do_setup = False
            sq.Maps.Travel(Maps.seitung)
            sq.Skills.LoadSkillBar(Build.template)
            CheckRequirements()
            sq.Maps.SetMode(0)
            sq.Move.Zone(ChoosePath(), Maps.jaya)
            sq.Move.Zone(Path.rezone, Maps.seitung)

        # inventory management
        if Inventory.GetModelCount(835) >= 50 or bot_vars.handle_inv:
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
        SetStatus('Leaving Jaya.')
        bot_vars.timers.lap.Start()
        sq.Skills.ChangeWeaponSet(Build.staff)
        sq.Move.Zone(Path.zone, Maps.jaya)
        inv_log = sq.Items.LogInventory(bot_vars.loot.log_list)
        SetStatus('Starting farm.')
        sq.Move.FollowPath(Path.farm, do_func = Farm, extra_status = '"Farm"')
        LogLap()
        CatalogLoot(inv_log)
        SetStatus('Resetting.')
        sq.Maps.ResignAndReturn(Maps.seitung)
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
            'runs'     : [   0,   .7,    0, 1],
            'fails'    : [   1,  .25,  .23, 1],
            'time'     : [  .9,   .9,   .9, 1],
            'feathers' : [  .9,   .9,   .9, 1],
            'crests'   : [  .9,   .9,   .9, 1],
            'coins'    : [   1,  .75,    0, 1],   
        }

        columns = [
            'Runs',
            'Fails',
            'Average Pace',
            'Lap Time',
            'Total Time',
            'Feathers',
            'Feathers/Hour',
            'Starting Feathers',
            'Total Feathers',
            'Gold Coins',
            'Crests'
        ]

        values = [
            bot_vars.gui.stats.runs,
            bot_vars.gui.stats.fails,
            FormatTime(bot_vars.gui.stats.avg_time,mask='mm:ss'),
            bot_vars.timers.lap.FormatElapsedTime("hh:mm:ss"),
            bot_vars.timers.total.FormatElapsedTime("hh:mm:ss"),
            FormatItemStack(bot_vars.gui.stats.feathers),
            FormatItemStack(round(bot_vars.gui.stats.feathers_per_hour)),
            FormatItemStack(bot_vars.gui.stats.starting_feathers),
            FormatItemStack(bot_vars.gui.stats.total_feathers),
            bot_vars.gui.stats.gold_coins,
            bot_vars.gui.stats.crests
        ]

        colors = [
            colors['runs'],
            colors['fails'],
            colors['time'],
            colors['time'],
            colors['time'],
            colors['feathers'],
            colors['feathers'],
            colors['feathers'],
            colors['feathers'],
            colors['coins'],
            colors['crests'],
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
            bot_vars.gui.opts.condense_tables     = PyImGui.checkbox('Condense Tables',    bot_vars.gui.opts.condense_tables)
            bot_vars.gui.opts.color_rows          = PyImGui.checkbox('Color Rows',         bot_vars.gui.opts.color_rows)
            bot_vars.gui.opts.show_all            = PyImGui.checkbox('Show All',           bot_vars.gui.opts.show_all)
            PyImGui.separator()
            bot_vars.gui.opts.rows.lap_time       = PyImGui.checkbox('Lap Time',           bot_vars.gui.opts.rows.lap_time)
            bot_vars.gui.opts.rows.feathers_hr    = PyImGui.checkbox('Feathers per Hour',  bot_vars.gui.opts.rows.feathers_hr)
            bot_vars.gui.opts.rows.start_feathers = PyImGui.checkbox('Starting Feathers',  bot_vars.gui.opts.rows.start_feathers)
            bot_vars.gui.opts.rows.total_feathers = PyImGui.checkbox('Total Feathers',     bot_vars.gui.opts.rows.total_feathers)
            bot_vars.gui.opts.rows.coins          = PyImGui.checkbox('Gold Coins',         bot_vars.gui.opts.rows.coins)
            bot_vars.gui.opts.rows.picks          = PyImGui.checkbox('Lockpicks',          bot_vars.gui.opts.rows.picks)
            bot_vars.gui.opts.rows.crests         = PyImGui.checkbox('Crests',             bot_vars.gui.opts.rows.crests)
            PyImGui.tree_pop()

        # general
        if PyImGui.tree_node('Description'):
            PyImGui.text('This bot uses a Dervish to farm')
            PyImGui.text('feathers in Jaya Bluffs. It will')
            PyImGui.text('loot feathers, crests, and coins.')
            PyImGui.text('At 50 crests,it will salvage them.')
            PyImGui.text('Development was done using')
            PyImGui.text('the requirements below.')
            PyImGui.tree_pop()

        # build
        if PyImGui.tree_node('Requirements  '):
            PyImGui.text('Map:')
            PyImGui.text('     Seitung Harbor')
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