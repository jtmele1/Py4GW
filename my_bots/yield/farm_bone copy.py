# region imports
from Py4GWCoreLib import *
# endregion

# region classes
class BotVariables:
    bot_started = False
    do_setup    = True
    handle_inv  = False

    class FarmItem:
        name     = ''
        model_id = 0
        color    = [.9, .9, .9, 1]

        def Reset(self):
            self.name     = ''
            self.model_id = 0
            self.color    = [.9, .9, .9, 1]

    class Loot:
        pickup_list = {}
        ignore_list = {}
        dont_sell_list = [# materials
                          ModelID.Bone,
                          ModelID.Pile_Of_Glittering_Dust,
                          ModelID.Iron_Ingot,
                          ModelID.Feather,
                          ModelID.Plant_Fiber,
                          # rare materials
                          ModelID.Glob_Of_Ectoplasm,
                          ModelID.Obsidian_Shard,
                          ModelID.Ruby,
                          ModelID.Sapphire,
                          # misc
                          ModelID.Identification_Kit,
                          ModelID.Salvage_Kit,
                          ModelID.Lockpick]

        def Reset(self):
            self.pickup_list = {}
            self.ignore_list = {}
            self.dont_sell_list = []

    class Timers:
        total     = Timer()
        lap       = Timer()
        lap_times = []

        def Reset(self):
            self.total.Stop()
            self.lap.Stop()
            self.lap_times = []

    class Stats:
        status          = [datetime.now().strftime('%H:%M:%S'),'Waiting for input...']
        runs            = 0
        fails           = 0
        pace            = 0
        farmed          = 0
        farmed_per_hour = 0
        starting_farmed = 0
        total_farmed    = 0

        def Reset(self):
            self.status          = [datetime.now().strftime('%H:%M:%S'),'Waiting for input...']
            self.runs            = 0
            self.fails           = 0
            self.pace            = 0
            self.farmed          = 0
            self.farmed_per_hour = 0
            self.starting_farmed = 0
            self.total_farmed    = 0

    class GUI:
        window_module = ImGui.WindowModule('Farmer',window_pos=(234,668),window_flags=PyImGui.WindowFlags.AlwaysAutoResize)
        window_width  = 250
        window_name   = ''
        
        class Logging:
            player = False
            move   = False
            skills = False
            agents = False
            maps   = False
            items  = False
            all    = True

            def Reset(self):
                self.player = False
                self.move   = False
                self.skills = False
                self.agents = False
                self.maps   = False
                self.items  = False
                self.all    = True

        class Opts:
            condense_tables = False
            color_rows      = True
            show_all        = True

            def Reset(self):
                self.condense_tables = False
                self.color_rows      = True
                self.show_all        = True
        
        class Rows:
            runs            = True
            fails           = True
            success         = False
            pace            = True
            lap_time        = False
            total_time      = True
            farmed          = True
            farmed_per_hour = False
            starting_farmed = False
            total_farmed    = False

            def Reset(self):
                self.runs            = True
                self.fails           = True
                self.success         = False
                self.pace            = True
                self.lap_time        = False
                self.total_time      = True
                self.farmed          = True
                self.farmed_per_hour = False
                self.starting_farmed = False
                self.total_farmed    = False

            def GetRows(self):
                return [
                    self.runs,
                    self.fails,
                    self.success,
                    self.pace,
                    self.lap_time,
                    self.total_time,
                    self.farmed,
                    self.farmed_per_hour,
                    self.starting_farmed,
                    self.total_farmed
                ]
            
        log = Logging()
        opts = Opts()
        rows = Rows()

        def Reset(self):
            self.window_module.first_run = True
            self.log.Reset()
            self.opts.Reset()
            self.rows.Reset()
    
    farm_item = FarmItem()
    loot      = Loot()
    timers    = Timers()
    stats     = Stats()
    gui       = GUI()

    def Reset(self):
        self.bot_started = False
        self.do_setup    = True
        self.handle_inv  = False
        self.timers.Reset()
        self.stats.Reset()
        self.gui.Reset()

class Path:
    npc    = [(-19085.0, 17960.0)]
    rezone = [(-19665.0, -8045.0)]
    prep   = [(-16623.0, -8989.0)]
    kill   = [(-15525.0, -8923.0), (-15737.0,-9093.0)]

class Maps:
    starting = 648
    dungeon  = 560

class Build:
    # template
    template = 'OgCjkqqLrSYiihdftXjhOXhXxlA'
    # weapon slots
    scythe = 1
    staff  = 2
    # skills
    soms = 2200
    pf   = 2146
    ga   = 2013
    vos  = 1517
    cv   = 2147
    ri   = 1486
    vop  = 1505
    mb   = 2417
    iau  = 2356

    class Effects:
        vos = 1517
# endregion

# region globals
initialized                  = False
bot_vars                     = BotVariables()
bot_vars.gui.window_name     = 'CoF Bone Farm'
bot_vars.farm_item.name      = 'Bones'
bot_vars.farm_item.model_id  = ModelID.Bone
bot_vars.farm_item.color     = [.89, .85, .79, 1]
bot_vars.loot.pickup_list    = {ModelID.Bone                    : ('Bones'            , True),
                                ModelID.Pile_Of_Glittering_Dust : ('Dust'             , False),
                                ModelID.Gold_Coins              : ('Gold Coins'       , False),
                                ModelID.Lockpick                : ('Lockpicks'        , False),
                                24353                           : ('Diessa Chalices'  , False),
                                ModelID.Golden_Rin_Relic        : ('Golden Rin Relics', False),
                                'salvageables'                  : ('Salvageables'     , True)}
# endregion

def Log(message, title = 'Log', msg_type = 'Info'):
    py4gw_msg_type = Py4GW.Console.MessageType.Info
    if   msg_type == 'Debug':       py4gw_msg_type = Py4GW.Console.MessageType.Debug
    elif msg_type == 'Error':       py4gw_msg_type = Py4GW.Console.MessageType.Error
    elif msg_type == 'Info':        py4gw_msg_type = Py4GW.Console.MessageType.Info
    elif msg_type == 'Notice':      py4gw_msg_type = Py4GW.Console.MessageType.Notice
    elif msg_type == 'Performance': py4gw_msg_type = Py4GW.Console.MessageType.Performance
    elif msg_type == 'Success':     py4gw_msg_type = Py4GW.Console.MessageType.Success
    elif msg_type == 'Warning':     py4gw_msg_type = Py4GW.Console.MessageType.Warning
    Py4GW.Console.Log(title, str(message), py4gw_msg_type)

# region combat functions
def GetAftercast(skill_id, min_aftercast = 200):
    activation = Skill.Data.GetActivation(skill_id)
    aftercast = Skill.Data.GetAftercast(skill_id)    
    total = int(max(activation*1000 + aftercast*1000,200))

    yield from Routines.Yield.wait(max(min_aftercast, total))

def HandleStuck(pos):
    Log('Player is stuck.')
    yield True

def UseVoS():
    global bot_vars 
    
    player_id = GLOBAL_CACHE.Player.GetAgentID()
    energy =  GLOBAL_CACHE.Agent.GetEnergy(player_id) * GLOBAL_CACHE.Agent.GetMaxEnergy(player_id)

    skills = [Build.pf, Build.ga, Build.vos]
    if Routines.Checks.Skills.IsSkillIDReady(skills[0]) and Routines.Checks.Skills.IsSkillIDReady(skills[1]) and Routines.Checks.Skills.IsSkillIDReady(skills[2]) and energy >= 15:
        for skill in skills:
            if Routines.Yield.Skills.CastSkillID(skill):
                yield from GetAftercast(skill)
        yield True
    yield False

def CheckVoS():
    global bot_vars 

    player_id = GLOBAL_CACHE.Player.GetAgentID()

    if not GLOBAL_CACHE.Effects.EffectExists(player_id, Build.Effects.vos):
        skills = [Build.pf, Build.ga, Build.vos]
        for skill in skills:
            if Routines.Yield.Skills.CastSkillID(skill):
                yield from GetAftercast(skill)
        yield True
    yield False

def WaitForSettle():
    timer = Timer()
    timer.Start()

    while True:
        player_id = GLOBAL_CACHE.Player.GetAgentID()
        if GLOBAL_CACHE.Agent.IsDead(player_id): break
        if GLOBAL_CACHE.Agent.GetHealth(player_id) < 0.5: break
        if timer.HasElapsed(6000): break

        enemy_array = GLOBAL_CACHE.AgentArray.GetEnemyArray()
        enemy_array = AgentArray.Filter.ByAttribute(enemy_array, 'IsAlive')
        enemy_array = AgentArray.Filter.ByDistance(enemy_array, Player.GetXY(), 200)

        if len(enemy_array) >= 3: break
        
        if (yield from UseVoS()): continue
        if (yield from CheckVoS()): continue

        if Routines.Yield.Skills.CastSkillSlot(Build.soms):
            yield from GetAftercast(Build.soms)

        yield from Routines.Yield.wait(100)

def Kill():
    while True:
        yield from Routines.Yield.wait(200)

        player_id = GLOBAL_CACHE.Player.GetAgentID()

        if GLOBAL_CACHE.Agent.IsDead(player_id): 
            break

        # check for remaming enemies
        enemy_array = GLOBAL_CACHE.AgentArray.GetEnemyArray()
        enemy_array = AgentArray.Filter.ByAttribute(enemy_array, 'IsAlive')
        enemy_array = AgentArray.Filter.ByDistance(enemy_array, GLOBAL_CACHE.Player.GetXY(), 600)
        if not enemy_array or (len(enemy_array) < 2 and enemy_array[0] and GLOBAL_CACHE.Agent.GetHealth(enemy_array[0]) > 0.4):
            break

        # maintain vos
        if (yield from UseVoS()):                                               continue
        if (yield from CheckVoS()):                                             continue
        if GLOBAL_CACHE.Effects.GetEffectTimeRemaining(player_id, 1517) < 1500: continue
        if not Routines.Checks.Skills.CanCast():                                continue

        # maintain signet of mystic speed
        if not GLOBAL_CACHE.Effects.EffectExists(player_id, Build.soms):
            if Routines.Yield.Skills.CastSkillID(Build.soms):
                yield from GetAftercast(Build.soms)
            continue

        # select target
        target_id = GLOBAL_CACHE.Player.GetTargetID()
        if target_id == 0 or GLOBAL_CACHE.Agent.GetAllegiance(target_id)[0] != 3 or GLOBAL_CACHE.Agent.IsDead(target_id):

            enemy_array = GLOBAL_CACHE.AgentArray.GetEnemyArray()
            enemy_array = AgentArray.Filter.ByAttribute(enemy_array,'IsAlive')
            enemy_array = AgentArray.Sort.ByDistance(enemy_array,(-15706,-9035))

            enemy_array = AgentArray.Filter.ByDistance(enemy_array,(-15706,-9035), 600)
            close_array = AgentArray.Filter.ByDistance(enemy_array,(-15706,-9035), 100)
            new_target = 0

            if Utils.Distance(GLOBAL_CACHE.Agent.GetXY(target_id),(-15706,-9035)) > 100 and close_array and close_array[0]:
                new_target = close_array[0]
            elif enemy_array and enemy_array[0]:
                new_target = enemy_array[0]

            if new_target and not GLOBAL_CACHE.Agent.IsSpirit(new_target):
                yield from Routines.Yield.Agents.ChangeTarget(new_target)
                continue

        # attack
        target_id = GLOBAL_CACHE.Player.GetTargetID()
        if not GLOBAL_CACHE.Agent.IsAttacking(player_id) and target_id:
            yield from Routines.Yield.Agents.InteractAgent(target_id)
            continue
        
        # cast crippling victory and reap impurities
        for skill in [Build.cv, Build.ri]:
            if Routines.Yield.Skills.CastSkillID(skill):
                yield from GetAftercast(skill, 1000)
                break
# endregion

# region sequential functions
def BotLogic():
    global bot_vars

    while True:
        if not bot_vars.bot_started:
            yield from Routines.Yield.wait(1)
            continue

        # setup routine
        if (bot_vars.do_setup or Map.GetMapID() != Maps.starting) and not bot_vars.handle_inv:
            Log(bot_vars, 'Setting up.')
            bot_vars.do_setup = False
            yield from Routines.Yield.Map.TravelToOutpost(Maps.starting)
            yield from Routines.Yield.Skills.LoadSkillbar(Build.template)
            yield from Routines.Yield.Movement.FollowPath(Path.npc) # type: ignore
            yield from Routines.Yield.Agents.TargetNearestNPC()
            yield from Routines.Yield.Player.InteractTarget()
            while not UIManager.IsNPCDialogVisible():
                yield from Routines.Yield.wait(100)
            UIManager.ClickDialogButton(2)
            yield from Routines.Yield.wait(500)
            UIManager.ClickDialogButton(1)
            yield from Routines.Yield.wait(500)
            yield from Routines.Yield.Map.WaitforMapLoad(Maps.dungeon)
            yield from Routines.Yield.Movement.FollowPath(Path.rezone)
            yield from Routines.Yield.Map.WaitforMapLoad(Maps.starting)

        # inventory management
        if GLOBAL_CACHE.Inventory.GetFreeSlotCount() <= 5 or bot_vars.handle_inv:
            Log(bot_vars, 'Handling inventory.')
            yield from Routines.Yield.Movement.FollowPath(Path.npc)
            yield from Routines.Yield.Agents.TargetNearestNPC()
            yield from Routines.Yield.Player.InteractTarget()
            while not UIManager.IsNPCDialogVisible():
                yield from Routines.Yield.wait(100)
            UIManager.ClickDialogButton(3)

            yield from bot_funcs.Items.ProcessInventory(bot_vars.loot.dont_sell_list)
            if bot_vars.handle_inv:
                bot_vars.bot_started = False
                return
            
        # farm routine
        Log(bot_vars, 'Entering dungeon.')
        bot_vars.timers.lap.Start()

        yield from Routines.Yield.


        yield from bot_funcs.Skills.ChangeWeaponSet(Build.staff)
        yield from bot_funcs.Agents.TargetNearestNPC()
        yield from bot_funcs.Agents.Interact(frame_alias = 'NPC Dialog')
        yield from bot_funcs.Player.ClickUIOptionFrame(3856160816, [2,0,0,1], 1)
        yield from bot_funcs.Player.ClickUIOptionFrame(3856160816, [2,0,0,1], 0)
        yield from bot_funcs.Maps.WaitForArrival(Maps.dungeon)
        yield from bot_funcs.Move.FollowPath(Path.prep)
        Log(bot_vars, 'Prepping skills.')
        yield from wait(3)
        yield from bot_funcs.Skills.CastSkill([Build.vop, Build.mb, Build.ga, Build.vos])
        yield from bot_funcs.Move.FollowPath(Path.kill, rand = 15, stuck_func = HandleStuck, stuck_time = 2000)
        Log(bot_vars, 'Waiting for enemies.')
        yield from WaitForSettle()
        yield from bot_funcs.Skills.ChangeWeaponSet(Build.scythe, 'Scythe')
        Log(bot_vars, 'Killing enemies.')
        yield from Kill()
        Log(bot_vars, 'Looting items.')
        inv_log = bot_funcs.Items.LogInventory(bot_vars.loot.pickup_list.keys())
        yield from bot_funcs.Items.Loot(bot_vars.loot.pickup_list.keys())
        LogLap(bot_vars, inv_log)
        yield from bot_funcs.Maps.ResignAndReturn(Maps.starting)
        Log(bot_vars, 'Resetting farm.')
# endregion

# region draw
def Draw(bot_vars, SyncFc):
    global bot_vars

    def SetWindowStyle():
        PyImGui.push_style_var(ImGui.ImGuiStyleVar.WindowBorderSize,0)
        PyImGui.push_style_var(ImGui.ImGuiStyleVar.WindowRounding,  0)
        PyImGui.push_style_var(ImGui.ImGuiStyleVar.FrameRounding,   0)

        PyImGui.push_style_color(PyImGui.ImGuiCol.FrameBg,        (1, 1, 1, 0.00))
        PyImGui.push_style_color(PyImGui.ImGuiCol.FrameBgHovered, (1, 1, 1, 0.15))
        PyImGui.push_style_color(PyImGui.ImGuiCol.FrameBgActive,  (1, 1, 1, 0.30))

        PyImGui.push_style_color(PyImGui.ImGuiCol.HeaderHovered,  (1, 1, 1, 0.15))
        PyImGui.push_style_color(PyImGui.ImGuiCol.HeaderActive,   (1, 1, 1, 0.30))

        PyImGui.push_style_color(PyImGui.ImGuiCol.Button,        (1, 1, 1, 0.00))
        PyImGui.push_style_color(PyImGui.ImGuiCol.ButtonHovered, (1, 1, 1, 0.15))
        PyImGui.push_style_color(PyImGui.ImGuiCol.ButtonActive,  (1, 1, 1, 0.30))

        PyImGui.push_style_color(PyImGui.ImGuiCol.WindowBg,         (0, 0, 0, 0.7))
        PyImGui.push_style_color(PyImGui.ImGuiCol.TitleBg,          (0, 0, 0, 0.7))
        PyImGui.push_style_color(PyImGui.ImGuiCol.TitleBgActive,    (0, 0, 0, 0.7))
        PyImGui.push_style_color(PyImGui.ImGuiCol.TitleBgCollapsed, (0, 0, 0, 0.7))

        PyImGui.push_style_color(PyImGui.ImGuiCol.TableBorderStrong, (.35, .35,.35, 1))
        PyImGui.push_style_color(PyImGui.ImGuiCol.TableBorderLight,  (.35, .35,.35, 1))
        PyImGui.push_style_color(PyImGui.ImGuiCol.Border,            (.35, .35,.35, 1))
        PyImGui.push_style_color(PyImGui.ImGuiCol.BorderShadow,      (.35, .35,.35, 0))
        PyImGui.push_style_color(PyImGui.ImGuiCol.Text,              (.75, .75,.75, 1))
        PyImGui.push_style_color(PyImGui.ImGuiCol.CheckMark,         (.75, .75,.75, 1))

    def PopWindowStyle():
        PyImGui.pop_style_var(4)
        PyImGui.pop_style_color(11)

    def MakeTable(*columns, colors = None):
        num_cols = len(columns)
        num_rows = len(columns[0])

        if PyImGui.begin_table('Info', num_cols, PyImGui.TableFlags.Borders |
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

    def CreateRunButton():
        button_width = (bot_vars.gui.window_width-20)

        if bot_vars.bot_started:
            if PyImGui.button('\uf04d', button_width, 25):
                GLOBAL_CACHE.Coroutines.clear()
                bot_vars.bot_started = False
                bot_vars.timers.total.Pause()
                bot_vars.timers.lap.Stop()

                Log('Stopping script.')
        else:
            if PyImGui.button('\uf04b', button_width, 25):
                GLOBAL_CACHE.Coroutines.clear()
                GLOBAL_CACHE.Coroutines.append(BotLogic())
                bot_vars.bot_started = True
                bot_vars.timers.total.Start()

                Log('Starting script.')

    def CreateStateLog():
        PyImGui.text_colored(f'[{bot_vars.stats.status[0]}]', (.48, .68, 1, 1))
        PyImGui.same_line(0.0,-1.0)
        PyImGui.text(f'{bot_vars.stats.status[1]}')

    def CreateTables():
        colors = {
            'runs'     : [   0,   .7,    0, 1],
            'fails'    : [   1,  .25,  .23, 1],
            'time'     : [ .75,  .75,  .75, 1],
            'farmed'   : bot_vars.farm_item.color,
        }

        columns = [
            'Runs',
            'Fails',
            'Success Rate (%)',
            'Average Pace',
            'Lap Time',
            'Total Time',
            bot_vars.farm_item.name,
            f'{bot_vars.farm_item.name}/Hour',
            f'Starting {bot_vars.farm_item.name}',
            f'Total {bot_vars.farm_item.name}'
        ]

        total_runs = bot_vars.stats.runs + bot_vars.stats.fails
        values = [
            bot_vars.stats.runs,
            bot_vars.stats.fails,
            round(100*bot_vars.stats.runs/total_runs,1) if total_runs != 0 else 0,
            FormatTime(bot_vars.stats.pace,mask='mm:ss'),
            bot_vars.timers.lap.FormatElapsedTime("hh:mm:ss"),
            bot_vars.timers.total.FormatElapsedTime("hh:mm:ss"),
            FormatItemStack(bot_vars.stats.farmed),
            FormatItemStack(round(bot_vars.stats.farmed_per_hour)),
            FormatItemStack(bot_vars.stats.starting_farmed),
            FormatItemStack(bot_vars.stats.total_farmed)
        ]

        colors = [
            colors['runs'],
            colors['fails'],
            colors['time'],
            colors['time'],
            colors['time'],
            colors['time'],
            colors['farmed'],
            colors['farmed'],
            colors['farmed'],
            colors['farmed'],
        ]

        table_nums = [1,1,1,2,2,2,3,3,3,3]

        filter = bot_vars.gui.rows.GetRows()

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
        # general
        if PyImGui.button('Process Inventory',PyImGui.get_window_size()[0]-40):
            coroutines.clear()
            coroutines.append(SyncFc())
            bot_vars.handle_inv = True
            bot_vars.bot_started = True

        if PyImGui.button('Open Storage', PyImGui.get_window_size()[0]-40):
            if not Inventory.IsStorageOpen():
                Inventory.OpenXunlaiWindow()

        # gui
        if PyImGui.tree_node('User Interface'):
            bot_vars.gui.opts.condense_tables  = PyImGui.checkbox('Condense Tables',    bot_vars.gui.opts.condense_tables)
            bot_vars.gui.opts.color_rows       = PyImGui.checkbox('Color Rows',         bot_vars.gui.opts.color_rows)
            bot_vars.gui.opts.show_all         = PyImGui.checkbox('Show All',           bot_vars.gui.opts.show_all)
            PyImGui.separator()
            bot_vars.gui.rows.success         = PyImGui.checkbox('Success Rate',                        bot_vars.gui.rows.success)
            bot_vars.gui.rows.lap_time        = PyImGui.checkbox('Lap Time',                            bot_vars.gui.rows.lap_time)
            bot_vars.gui.rows.farmed_per_hour = PyImGui.checkbox(f'{bot_vars.farm_item.name} per Hour', bot_vars.gui.rows.farmed_per_hour)
            bot_vars.gui.rows.starting_farmed = PyImGui.checkbox(f'Starting {bot_vars.farm_item.name}', bot_vars.gui.rows.starting_farmed)
            bot_vars.gui.rows.total_farmed    = PyImGui.checkbox(f'Total {bot_vars.farm_item.name}',    bot_vars.gui.rows.total_farmed)
            PyImGui.tree_pop()

    if bot_vars.gui.window_module.first_run:
        bot_vars.gui.window_module.first_run = False
        bot_vars.stats.starting_farmed = Inventory.GetModelCount(bot_vars.farm_item.model_id)
        bot_vars.stats.total_farmed    = Inventory.GetModelCount(bot_vars.farm_item.model_id)

        PyImGui.set_next_window_pos(bot_vars.gui.window_module.window_pos[0], bot_vars.gui.window_module.window_pos[1])

    try:
        SetWindowStyle()
        if PyImGui.begin(bot_vars.gui.window_name, bot_vars.gui.window_module.window_flags):
            PyImGui.push_style_var(ImGui.ImGuiStyleVar.FrameBorderSize, 1)
            
            CreateRunButton()
            CreateStateLog()
            CreateTables()
            if PyImGui.tree_node('Settings'):
                CreateSettings()
                PyImGui.tree_pop()
        PyImGui.end()
        PopWindowStyle()
    except Exception as e:
        current_function = inspect.currentframe().f_code.co_name # type: ignore
        Py4GW.Console.Log('BOT', f'Error in {current_function}: {str(e)}', Py4GW.Console.MessageType.Error)
        raise
# endregion

# region main
def main():
    global bot_vars, initialized

    try:
        if not Map.IsMapReady() or not Party.IsPartyLoaded():
            return

        Draw()

        for coroutine in GLOBAL_CACHE.Coroutines[:]:
            try:
                next(coroutine)
            except StopIteration:
                GLOBAL_CACHE.Coroutines.remove(coroutine)
        
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