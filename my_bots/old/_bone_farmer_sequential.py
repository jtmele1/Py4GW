# region imports
from bot_routines import *
from datetime import datetime
# endregion

# region classes
class Path:
    npc    = [(-19085, 17960)]
    rezone = [(-19665, -8045)]
    prep   = [(-16623, -8989)]
    kill   = [(-15525, -8923), (-15737,-9093)]

class BotVariables:
    bot_started  = False
    do_setup     = True
    handle_inv   = False
    
    class Maps:
        starting = 648
        dungeon  = 560

    class Timers:
        total     = Timer()
        lap       = Timer()
        lap_times = []

    class Opts:
        build_type = 'mb'

    class Loot:
        salvageables = True
        coins        = True
        picks        = True
        dust         = True
        chalices     = True
        relics       = True
        log_list     = ['gold','salv',921,929,22751,24353,24354]

    class GUI:
        window_module = ImGui.WindowModule('Bone Farmer',window_name='CoF Bone Farm',window_pos=(234,802),
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
            bone          = 0
            bone_per_hour = 0
            starting_bone = Inventory.GetModelCount(921)
            total_bone    = Inventory.GetModelCount(921)
            gold_coins    = 0
            lockpicks     = 0
            dust          = 0
            iron          = 0
            chalices      = 0
            relics        = 0

        class Opts:
            show_settings   = False
            condense_tables = False
            color_rows      = True
            show_all        = False

            class Rows:
                runs        = True
                fails       = True
                pace        = True
                lap_time    = False
                total_time  = True
                bones       = True
                bones_hr    = False
                start_bones = False
                total_bones = False
                coins       = False
                picks       = False
                dust        = False
                iron        = False
                chalices    = False
                relics      = False

                def GetRows(self) -> list:
                    return [self.runs, self.fails, 
                            self.pace, self.lap_time, self.total_time,
                            self.bones, self.bones_hr, self.start_bones, self.total_bones,
                            self.coins, self.picks, self.dust, self.iron, self.chalices, self.relics]
            
            rows = Rows()
        
        stats = Stats()
        opts = Opts()
                
    map    = Maps()
    timers = Timers()
    path   = Path()
    opts   = Opts()
    loot   = Loot()
    gui    = GUI()

class Build:
    # template
    @staticmethod
    def GetTemplate(type):
        if type == 'iau':
            return 'OgCjwqpq6SYiihdftXjhOXhX0k'
        elif type == 'mb':
            return 'OgCjkqqLrSYiihdftXjhOXhXxlA'
    # weapon slots
    scythe   = 1
    staff    = 2
    # skills
    soms     = 1
    pf       = 2
    ga       = 3
    vos      = 4
    cv       = 5
    ri       = 6
    vop      = 7
    iau      = 8
    mb       = 8
# endregion

# region globals
bot_vars       = BotVariables()
thread_manager = MultiThreading(timeout = 5)
sq = SynchronousRoutines()
# endregion

# region helper functions
def StartBot():
    global bot_vars

    thread_manager.stop_all_threads()
    thread_manager.add_thread('SequentialLogic', SequentialLogic)
    thread_manager.start_watchdog('SequentialLogic')
    bot_vars.bot_started = True
    bot_vars.timers.total.Start()

    Debug('Starting script.')

def StopBot():
    global bot_vars, action_queue
    thread_manager.stop_all_threads()
    action_queue.clear()
    bot_vars.bot_started = False
    bot_vars.timers.total.Pause()
    bot_vars.timers.lap.Stop()

    Debug('Stopping script.')

def ToggleDebug():
  global debug
  debug = not debug

def CheckRequirements():
    global bot_vars

    error = False
    error_msgs = []

    # check attributes (for runes)
    attribute_checks = {'Scythe Mastery' : 11,
                        'Wind Prayers'   : 15,
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

    valid_model_ids = [921] # bones
    if bot_vars.loot.coins:    valid_model_ids.append(2511)
    if bot_vars.loot.picks:    valid_model_ids.append(22751)
    if bot_vars.loot.dust:     valid_model_ids.append(929)
    if bot_vars.loot.chalices: valid_model_ids.append(24353)
    if bot_vars.loot.relics:   valid_model_ids.append(24354)

    item_array_model = AgentArray.Filter.ByCondition(agent_array, lambda agent_id: Item.GetModelID(Agent.GetItemAgent(agent_id).item_id) in valid_model_ids)

    item_array_salv = []
    if bot_vars.loot.salvageables:
        item_array_salv = AgentArray.Filter.ByCondition(agent_array, lambda agent_id: Item.Usage.IsSalvageable(Agent.GetItemAgent(agent_id).item_id))

    item_array = list(set(item_array_model + item_array_salv))  
    item_array = AgentArray.Sort.ByDistance(item_array,Player.GetXY())

    return item_array

def CatalogLoot(inv_log):
    global bot_vars

    curr_inv = SynchronousRoutines.Items.LogInventory(bot_vars.loot.log_list)
    new_inv  = {key: curr_inv[key] - inv_log[key] for key in set(inv_log) & set(curr_inv)}

    bot_vars.gui.stats.bone       += new_inv[921]
    bot_vars.gui.stats.gold_coins += new_inv['gold']
    bot_vars.gui.stats.lockpicks  += new_inv[22751]
    bot_vars.gui.stats.dust       += new_inv[929]
    bot_vars.gui.stats.chalices   += new_inv[24353]
    bot_vars.gui.stats.relics     += new_inv[24354]

    bot_vars.gui.stats.bone_per_hour = int(bot_vars.gui.stats.bone*3600000/bot_vars.timers.total.GetElapsedTime())
    bot_vars.gui.stats.total_bone = Inventory.GetModelCount(921)

    Log('Loot from current lap:',                   msg_type = 'Notice')
    Log(f' -  Gold coins: {new_inv['gold']}',       msg_type = 'Notice')
    Log(f' -  Lockpicks: {new_inv[22751]}',         msg_type = 'Notice')
    Log(f' -  Diessa Chalices: {new_inv[24353]}',   msg_type = 'Notice')
    Log(f' -  Golden Rin Relics: {new_inv[24354]}', msg_type = 'Notice')
    Log(f' -  Salvageables: {new_inv['salv']}',     msg_type = 'Notice')
    Log(f' -  Bone: {new_inv[921]}',                msg_type = 'Notice')
    Log(f' -  Dust: {new_inv[929]}',                msg_type = 'Notice')
# endregion

# region combat functions
def CheckStuck(timeout = 2000):
    player_id = Player.GetAgentID()
    timer = Timer()
    timer.Start()
    while not Agent.IsMoving(player_id):
        if timer.HasElapsed(timeout):
            Debug('Player is stuck.')
            return True
        
    return False

def UseVoS():
    global bot_vars 
    
    if (sq.Skills.IsRecharged(Build.pf) and sq.Skills.IsRecharged(Build.ga) and sq.Skills.IsRecharged(Build.vos) and sq.Skills.GetEnergy() >= 15):
        sq.Skills.CastSkill([Build.pf, Build.ga, Build.vos])
        return True
    return False

def CheckVos():
    global bot_vars 

    if not sq.Skills.CheckBuffs([Build.vos]) and action_queue.is_empty():
        if sq.Skills.IsRecharged(Build.pf):  sq.Skills.CastSkill(Build.pf)
        if sq.Skills.IsRecharged(Build.ga):  sq.Skills.CastSkill(Build.ga)
        if sq.Skills.IsRecharged(Build.vos): sq.Skills.CastSkill(Build.vos)
        return True
    return False

def WaitForSettle():
    timer = Timer()
    timer.Start()
    while True:
        if Agent.IsDead(Player.GetAgentID()):          return
        if Agent.GetHealth(Player.GetAgentID()) < 0.5: return
        if timer.HasElapsed(6000):                  return

        enemy_array = AgentArray.GetEnemyArray()
        enemy_array = AgentArray.Filter.ByAttribute(enemy_array, 'IsAlive')
        enemy_array = AgentArray.Filter.ByDistance(enemy_array, Player.GetXY(), 200)

        if len(enemy_array) >= 3: return
        
        if UseVoS():   continue
        if CheckVos(): continue

        if sq.Skills.IsRecharged(Build.soms):
            sq.Skills.CastSkill(Build.soms)
            continue

        sleep(.1)

def Kill():
    while True:
        sleep(.2)

        if Agent.IsDead(Player.GetAgentID()): 
            return

        # check for remaming enemies
        enemy_array = AgentArray.GetEnemyArray()
        enemy_array = AgentArray.Filter.ByAttribute(enemy_array, 'IsAlive')
        enemy_array = AgentArray.Filter.ByDistance(enemy_array, Player.GetXY(), 600)
        if not enemy_array or (len(enemy_array) < 2 and enemy_array[0] and Agent.GetHealth(enemy_array[0]) > 0.4):
            return

        # maintain vos
        if UseVoS():                                   continue
        if CheckVos():                                 continue
        if sq.Skills.EffectTimeRemaining(1517) < 1500: continue
        if not sq.Skills.CanCast():                    continue

        # maintain signet of mystic speed
        if not sq.Skills.HasEffect(Build.soms) and sq.Skills.IsRecharged(Build.soms):
            sq.Skills.CastSkill(Build.soms)
            continue
        
        # maintain iau (if equipped)
        if bot_vars.opts.build_type == 'iau' and sq.Skills.IsRecharged(Build.iau):
            sq.Skills.CastSkill(Build.iau)
            continue

        # select target
        target_id = Player.GetTargetID()
        if target_id == 0 or Agent.GetAllegiance(target_id)[0] != 3 or Agent.IsDead(target_id):

            enemy_array = AgentArray.GetEnemyArray()
            enemy_array = AgentArray.Filter.ByAttribute(enemy_array,'IsAlive')
            enemy_array = AgentArray.Sort.ByDistance(enemy_array,(-15706,-9035))

            enemy_array = AgentArray.Filter.ByDistance(enemy_array,(-15706,-9035), 600)
            close_array = AgentArray.Filter.ByDistance(enemy_array,(-15706,-9035), 100)
            new_target = 0

            if Utils.Distance(Agent.GetXY(target_id),(-15706,-9035)) > 100 and close_array and close_array[0]:
                new_target = close_array[0]
            elif enemy_array and enemy_array[0]:
                new_target = enemy_array[0]

            if new_target:
                sq.Agents.ChangeTarget(new_target)
                continue

        # attack
        if not Agent.IsAttacking(Player.GetAgentID()):
            sq.Agents.Interact()
            continue
        
        # cast crippling victory and reap impurities
        for spell in [Build.cv, Build.ri]:
            if sq.Skills.HasEnoughAdrenaline(spell):
                sq.Skills.CastSkill(spell)
                sleep(1)
                continue
# endregion

# region sequential functions
def SequentialLogic():
    global bot_vars

    while True:
        if not bot_vars.bot_started:
            sleep(1)
            continue

        # setup routine
        if (bot_vars.do_setup or Map.GetMapID() != bot_vars.map.starting) and not bot_vars.handle_inv:
            SetStatus('setting up')
            bot_vars.do_setup = False
            sq.Maps.Travel(bot_vars.map.starting)
            sq.Skills.LoadSkillBar(Build.GetTemplate(bot_vars.opts.build_type))
            CheckRequirements()
            sq.Maps.SetMode(0)
            sq.Move.FollowPath(bot_vars.path.npc)
            sq.Agents.TargetNearestNPC()
            sq.Agents.Interact(frame_alias = 'NPC Bounty Dialog')
            sq.Player.SendDialog(0x832105)
            sq.Player.SendDialog(0x88)
            sq.Maps.WaitForArrival(bot_vars.map.dungeon)
            sq.Move.Zone(bot_vars.path.rezone, bot_vars.map.starting)

        # inventory management
        if sq.Items.CheckSlots(5) or bot_vars.handle_inv:
            SetStatus('handling inventory')
            sq.Items.RequestInvNames()
            sq.Move.FollowPath(bot_vars.path.npc)
            sq.Agents.TargetNearestNPC()
            sq.Agents.Interact(frame_alias = 'NPC Bounty Dialog')
            sq.Player.SendDialog(0x7F)
            sq.Items.Identify()
            sq.Items.Salvage()
            sq.Items.RequestInvNames()
            sq.Items.Sell(sell_list = GetSellList())
            if bot_vars.handle_inv:
                bot_vars.bot_started = False
                thread_manager.stop_all_threads()
                return
            
        # farm routine
        SetStatus('entering dungeon')
        bot_vars.timers.lap.Start()
        sq.Skills.ChangeWeaponSet(Build.staff)
        sq.Agents.TargetNearestNPC()
        sq.Agents.Interact(frame_alias = 'NPC Bounty Dialog')
        sq.Player.SendDialog(0x832105)
        sq.Player.SendDialog(0x88)
        sq.Maps.WaitForArrival(bot_vars.map.dungeon)
        SetStatus('prepping')
        sq.Move.FollowPath(bot_vars.path.prep)
        sleep(3)
        sq.Skills.CastSkill([Build.vop, Build.mb, Build.ga, Build.vos])
        sq.Move.FollowPath(bot_vars.path.kill, exit_func = CheckStuck, rand = 15)
        sq.Agents.RequestEnemyNames()
        WaitForSettle()
        sq.Skills.ChangeWeaponSet(Build.scythe, 'Scythe')
        SetStatus('killing')
        Kill()
        SetStatus('looting')
        sq.Items.RequestLootNames()
        inv_log = sq.Items.LogInventory(bot_vars.loot.log_list)
        sq.Items.Loot(loot_list = GetLootList())
        LogLap()
        CatalogLoot(inv_log)
        SetStatus('resetting')
        sq.Maps.ResignAndReturn(bot_vars.map.starting)
# endregion

# region draw
def Draw():
    global bot_vars, debug

    def SetButtonStyle(active):
        if active:
            PyImGui.push_style_color(PyImGui.ImGuiCol.Button,        (.15,.15,.15,1))
            PyImGui.push_style_color(PyImGui.ImGuiCol.ButtonHovered, (.20,.20,.20,1))
            PyImGui.push_style_color(PyImGui.ImGuiCol.ButtonActive,  (.25,.25,.25,1))
        else:
            PyImGui.push_style_color(PyImGui.ImGuiCol.Button,        (.13,.13,.13,1))
            PyImGui.push_style_color(PyImGui.ImGuiCol.ButtonHovered, (.3,.3,.3,1))
            PyImGui.push_style_color(PyImGui.ImGuiCol.ButtonActive,  (.4,.4,.4,1))

    def PopButtonStyle():
        PyImGui.pop_style_color(3)

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
        window_width = 220
        button_width = (window_width-20)

        SetButtonStyle(1)
        if bot_vars.bot_started:
            if PyImGui.button('\uf04d', button_width, 25):
                StopBot()
        else:
            if PyImGui.button('\uf04b', button_width, 25):
                StartBot()
        PopButtonStyle()

    def CreateStateLog():
        PyImGui.text_colored(f'[{bot_vars.gui.stats.status[0]}]', (.48, .68, 1, 1))
        PyImGui.same_line(0.0,-1.0)
        PyImGui.text(f'{bot_vars.gui.stats.status[1]}')

    def CreateTables():
        colors = {
            'runs'     : [   0,   .7,    0, 1],
            'fails'    : [   1,  .25,  .23, 1],
            'time'     : [  .9,   .9,   .9, 1],
            'bones'    : [ .89,  .85,  .79, 1],
            'coins'    : [   1,  .75,    0, 1],
            'picks'    : [  .6,   .6,   .6, 1],
            'dust'     : [.737, .463, .455, 1],
            'iron'     : [.631, .616, .580, 1],
            'chalices' : [.737, .514, .365, 1],
            'relics'   : [.839, .737, .424, 1]
        }

        columns = [
            'Runs',
            'Fails',
            'Average Pace',
            'Lap Time',
            'Total Time',
            'Bones',
            'Bones/Hour',
            'Starting Bones',
            'Total Bones',
            'Gold Coins',
            'Lock Picks',
            'Dust',
            'Iron',
            'Chalices',
            'Relics'
        ]

        values = [
            bot_vars.gui.stats.runs,
            bot_vars.gui.stats.fails,
            FormatTime(bot_vars.gui.stats.avg_time,mask='mm:ss'),
            bot_vars.timers.lap.FormatElapsedTime("hh:mm:ss"),
            bot_vars.timers.total.FormatElapsedTime("hh:mm:ss"),
            FormatItemStack(bot_vars.gui.stats.bone),
            FormatItemStack(round(bot_vars.gui.stats.bone_per_hour)),
            FormatItemStack(bot_vars.gui.stats.starting_bone),
            FormatItemStack(bot_vars.gui.stats.total_bone),
            bot_vars.gui.stats.gold_coins,
            bot_vars.gui.stats.lockpicks,
            FormatItemStack(bot_vars.gui.stats.dust),
            FormatItemStack(bot_vars.gui.stats.iron),
            bot_vars.gui.stats.chalices,
            bot_vars.gui.stats.relics
        ]

        colors = [
            colors['runs'],
            colors['fails'],
            colors['time'],
            colors['time'],
            colors['time'],
            colors['bones'],
            colors['bones'],
            colors['bones'],
            colors['bones'],
            colors['coins'],
            colors['picks'],
            colors['dust'],
            colors['iron'],
            colors['chalices'],
            colors['relics']
        ]

        table_nums = [1,1,2,2,2,3,3,3,3,4,4,4,4,4,4]

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

            SetButtonStyle(1)

            if PyImGui.button('Process Inventory',PyImGui.get_window_size()[0]-60):
                thread_manager.stop_all_threads()
                thread_manager.add_thread('SequentialLogic', SequentialLogic)
                thread_manager.start_watchdog('SequentialLogic')
                bot_vars.handle_inv = True
                bot_vars.bot_started = True

            if PyImGui.button('Open Storage', PyImGui.get_window_size()[0]-60):
                if not Inventory.IsStorageOpen():
                    Inventory.OpenXunlaiWindow()

            if debug:
                if PyImGui.button('Run Debug Function', PyImGui.get_window_size()[0]-60):
                    DebugFn()

            PyImGui.pop_style_color(3)
            
            PyImGui.tree_pop()

        # build
        if PyImGui.tree_node('Build'):
            items = ['iau','mb']
            bot_vars.opts.build_type = items[PyImGui.radio_button("IaU", items.index(bot_vars.opts.build_type), 0)]
            PyImGui.same_line(0.0,-1.0)
            bot_vars.opts.build_type = items[PyImGui.radio_button("Mental Block", items.index(bot_vars.opts.build_type), 1)]
            PyImGui.tree_pop()

        # loot
        if PyImGui.tree_node('Loot'):
            bot_vars.loot.salvageables = PyImGui.checkbox('Salvageables',      bot_vars.loot.salvageables)
            bot_vars.loot.coins        = PyImGui.checkbox('Gold Coins',        bot_vars.loot.coins)
            bot_vars.loot.picks        = PyImGui.checkbox('Lockpicks',         bot_vars.loot.picks)
            bot_vars.loot.dust         = PyImGui.checkbox('Glittering Dust',   bot_vars.loot.dust)
            bot_vars.loot.chalices     = PyImGui.checkbox('Diessa Chalices',   bot_vars.loot.chalices)
            bot_vars.loot.relics       = PyImGui.checkbox('Golden Rin Relics', bot_vars.loot.relics)
            PyImGui.tree_pop()

        # gui
        if PyImGui.tree_node('User Interface  '):
            bot_vars.gui.opts.condense_tables  = PyImGui.checkbox('Condense Tables',    bot_vars.gui.opts.condense_tables)
            bot_vars.gui.opts.color_rows       = PyImGui.checkbox('Color Rows',         bot_vars.gui.opts.color_rows)
            bot_vars.gui.opts.show_all         = PyImGui.checkbox('Show All',           bot_vars.gui.opts.show_all)
            PyImGui.separator()
            bot_vars.gui.opts.rows.lap_time    = PyImGui.checkbox('Lap Time',           bot_vars.gui.opts.rows.lap_time)
            bot_vars.gui.opts.rows.bones_hr    = PyImGui.checkbox('Bones per Hour',     bot_vars.gui.opts.rows.bones_hr)
            bot_vars.gui.opts.rows.start_bones = PyImGui.checkbox('Starting Bones',     bot_vars.gui.opts.rows.start_bones)
            bot_vars.gui.opts.rows.total_bones = PyImGui.checkbox('Total Bones',        bot_vars.gui.opts.rows.total_bones)
            bot_vars.gui.opts.rows.coins       = PyImGui.checkbox('Gold Coins ',        bot_vars.gui.opts.rows.coins)
            bot_vars.gui.opts.rows.picks       = PyImGui.checkbox('Lockpicks ',         bot_vars.gui.opts.rows.picks)
            bot_vars.gui.opts.rows.dust        = PyImGui.checkbox('Glittering Dust ',   bot_vars.gui.opts.rows.dust)
            bot_vars.gui.opts.rows.iron        = PyImGui.checkbox('Iron',               bot_vars.gui.opts.rows.iron)
            bot_vars.gui.opts.rows.chalices    = PyImGui.checkbox('Diessa Chalices ',   bot_vars.gui.opts.rows.chalices)
            bot_vars.gui.opts.rows.relics      = PyImGui.checkbox('Golden Rin Relics ', bot_vars.gui.opts.rows.relics)
            PyImGui.tree_pop()

        # general
        if PyImGui.tree_node('Description'):
            PyImGui.text('This bot uses a Dervish to farm bones at the entrance of')
            PyImGui.text('the Cathedral of Flames dungeon. It will loot bone, dust,')
            PyImGui.text('salvageables, coins, lockpicks, Diessa Chalices, and Golden')
            PyImGui.text('Rin Relics. When the inventory has 5 or lessslots remaining,')
            PyImGui.text('it will ID, salvage, and sell everything besides materials.')
            PyImGui.text('Development was done using the requirements below.')
            PyImGui.tree_pop()

        # build
        if PyImGui.tree_node('Requirements  '):
            PyImGui.text('Map:')
            PyImGui.text('     Doolmore Shrine')
            PyImGui.text('Build:')
            PyImGui.text('     Signet of Mystic Speed')
            PyImGui.text('     Pious Fury')
            PyImGui.text('     Grenth\'s Aura')
            PyImGui.text('     Vow of Silence')
            PyImGui.text('     Crippling Victory')
            PyImGui.text('     Reap Impurities')
            PyImGui.text('     Vow of Piety')
            PyImGui.text('     "I Am Unstoppable!" / Mental Block')
            PyImGui.text('Weapons:')
            PyImGui.text('     Slot 1 - Zealous +15%^Ench Scythe of Enchanting')
            PyImGui.text('     Slot 1 - Any Staff of Enchanting')
            PyImGui.text('Armor:')
            PyImGui.text('     x5 Windwalker Insignias')
            PyImGui.text('     +4 Wind Prayers')
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
            
            PyImGui.push_style_color(PyImGui.ImGuiCol.FrameBg,        (0.15, 0.15, 0.15, 1))
            PyImGui.push_style_color(PyImGui.ImGuiCol.FrameBgHovered, (0.20, 0.20, 0.20, 1))
            PyImGui.push_style_color(PyImGui.ImGuiCol.FrameBgActive,  (0.25, 0.25, 0.25, 1))
            PyImGui.push_style_color(PyImGui.ImGuiCol.CheckMark,      (1.0, 1.0, 1.0, 1.0))

            PyImGui.push_style_color(PyImGui.ImGuiCol.WindowBg,         (0.0, 0.0, 0.0, 0.7))
            PyImGui.push_style_color(PyImGui.ImGuiCol.TitleBg,          (0.0, 0.0, 0.0, 0.7))
            PyImGui.push_style_color(PyImGui.ImGuiCol.TitleBgActive,    (0.0, 0.0, 0.0, 0.7))
            PyImGui.push_style_color(PyImGui.ImGuiCol.TitleBgCollapsed, (0.0, 0.0, 0.0, 0.7))

        try:
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