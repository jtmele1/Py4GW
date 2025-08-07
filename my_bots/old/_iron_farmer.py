# region imports
from Py4GWCoreLib import *
from random import randint
from datetime import datetime
# endregion

# region classes
class Path:
    lever = [(-738, 11728)]
    jump  = [(-626, 11413)]
    kill  = [(-473, 11265)]
    merch = [(-163, 16000),(-1910, 14777)]

class GUIStats:
    total_timer   = Timer()
    lap_timer     = Timer()
    lap_times     = []
    avg_time      = 0
    runs          = 0
    fails         = 0
    iron          = 0 # 948
    starting_iron = 0
    current_iron  = 0
    iron_per_drop = 0
    gold_coins    = 0 # 2511
    salvageables  = 0
    inv_sorting   = {}
    status        = 'waiting for input'
    time          = datetime.now().strftime('%H:%M:%S')

class BotVariabless:
    starting_map  = 32
    bot_started   = False
    window_module = ImGui.WindowModule('Iron Farmer', window_name='Iron Farmer', window_size=(220, 310), # 184, 214, 310
                                       window_pos=(300,600), window_flags=PyImGui.WindowFlags.AlwaysAutoResize)
    gui_stats     = GUIStats()

class FSMVariables:
    fsm        = FSM('Irom Farmer')
    path       = {'lever' : Routines.Movement.PathHandler(Path.lever),
                  'jump'  : Routines.Movement.PathHandler(Path.jump),
                  'kill'  : Routines.Movement.PathHandler(Path.kill),
                  'merch' : Routines.Movement.PathHandler(Path.merch)}
    move       = Routines.Movement.FollowXY()
    exact_move = Routines.Movement.FollowXY(tolerance=5)
    do_setup   = True
    # timers
    action_timer_check = 0
    action_timer  = Timer()
    settle_timer  = Timer()
    sf_timer      = Timer()
    # inventory
    item_id       = 0
    item_quantity = 0
    empty_slots   = 3

class Build:
    # template
    template = 'Ogej8xrMrMHQdGPiAuevu83AGA'
    # weapon slots
    scythe   = 1
    staff    = 2
    # skills
    sod      = 1
    sf       = 2
    dp       = 3
    wop      = 4
    aos      = 5
    aot      = 6
    ms       = 7
    vd       = 8

class Combat:
    debug = False

    def LoadSkillBar(template):
        SkillBar.LoadSkillTemplate(template)
        if Combat.debug:
            Debug(f'Loading skillbar template [{template}]')

    def ChangeWeaponSet(set):
        if set == 1:
            Keystroke.PressAndRelease(Key.F1.value)
        elif set == 2:
            Keystroke.PressAndRelease(Key.F2.value)
        elif set == 3:
            Keystroke.PressAndRelease(Key.F3.value)
        elif set == 4:
            Keystroke.PressAndRelease(Key.F4.value)
        if Combat.debug:
            Debug(f'Changing to weapon set [{set}]')

    def CastSkill(skill_slot, target_agent_id=0):
        SkillBar.UseSkill(skill_slot, target_agent_id)
        if Combat.debug:
            Debug(f'Casting skill [{skill_slot}]')

    def CanCast():
        player_agent_id = Player.GetAgentID()

        if (Agent.IsCasting(player_agent_id) 
            or Agent.GetCastingSkill(player_agent_id) != 0
            or Agent.IsKnockedDown(player_agent_id)
            or Agent.IsDead(player_agent_id)
            or SkillBar.GetCasting() != 0):
            return False
        return True

    def GetEnergyAgentCost(skill_slot):
        skill_id = SkillBar.GetSkillIDBySlot(skill_slot)
        cost = Skill.skill_instance(skill_id).energy_cost

        if cost == 11:
            cost = 15    # True cost is 15
        elif cost == 12:
            cost = 25    # True cost is 25

        cost = max(0, cost)
        return cost

    def HasEnoughAdrenaline(skill_slot):
        skill_id = SkillBar.GetSkillIDBySlot(skill_slot)

        return SkillBar.GetSkillData(skill_slot).adrenaline_a >= Skill.Data.GetAdrenaline(skill_id)

    def GetEnergy():
        player_agent_id = Player.GetAgentID()
        energy = Agent.GetEnergy(player_agent_id)
        max_energy = Agent.GetMaxEnergy(player_agent_id)
        energy_points = int(energy * max_energy)

        return energy_points

    def HasEnoughEnergy(skill_slot):
        player_agent_id = Player.GetAgentID()
        energy = Agent.GetEnergy(player_agent_id)
        max_energy = Agent.GetMaxEnergy(player_agent_id)
        energy_points = int(energy * max_energy)

        return Combat.GetEnergyAgentCost(skill_slot, player_agent_id) <= energy_points
    
    def IsRecharged(skill_slot):
        skill = SkillBar.GetSkillData(skill_slot)
        recharge = skill.recharge
        return recharge == 0
    
    def HasBuff(agent_id, skill_slot):
        skill_id = SkillBar.GetSkillIDBySlot(skill_slot)

        if Effects.BuffExists(agent_id, skill_id) or Effects.EffectExists(agent_id, skill_id):
            return True
        return False
    
    def GetAftercast(skill_slot):
        skill_id = SkillBar.GetSkillIDBySlot(skill_slot)

        activation = Skill.Data.GetActivation(skill_id)
        aftercast = Skill.Data.GetAftercast(skill_id)    
        return max(activation*1000 + aftercast*1000 + 50,500)

class Loot:
    debug = False

    def FilterLoot(item_array):
        return item_array

    def PickUp():
        global fsm_vars
        
        if ActionIsPending(): return

        item_array = Loot.FilterLoot(AgentArray.GetItemArray())
        if len(item_array) == 0:
            return

        item = item_array[0]

        if fsm_vars.item_id != item:
            fsm_vars.item_id = item
        
        current_target = Player.GetTargetID()
        
        if current_target != fsm_vars.item_id:
            Player.ChangeTarget(fsm_vars.item_id)
            SetPendingAction(randint(100,150))
            if Loot.debug:
                Debug(f'Changing target to item ID [{fsm_vars.item_id}]')
            return
        
        Keystroke.PressAndRelease(Key.Space.value)
        SetPendingAction(randint(400,700))
        if Loot.debug:
            Debug(f'Picking up item ID [{fsm_vars.item_id}]')

    def Loop():
        global area_distance, bot_vars
        global pick_up_item_timer

        if Agent.IsDead(Player.GetAgentID()):
            return True

        item_array = Loot.FilterLoot(AgentArray.GetItemArray())

        if (len(item_array) == 0):
            if Loot.debug:
                Debug('Loot loop complete')
            return True
        return False

class Merchant:
    debug = False

    def Buy(model_id):
        item_array = Trading.Merchant.GetOfferedItems()
        for item in item_array:
            if Item.GetModelID(item) == model_id:
                value = Item.Properties.GetValue(item) * 2
                Trading.Merchant.BuyItem(item,value)
                SetPendingAction(randint(750,1250))
                if Merchant.debug:
                    Debug(f'Buying ItemID [{item}] for [{value}] gold')
                break

    def Check():
        if ActionIsPending():
            return False
        fsm_vars.fsm.jump_to_state_by_name('IDing items')
    
class ProcessInventory:
    debug = True

    def CheckSlots():
        global fsm_vars
        if Inventory.GetFreeSlotCount() > fsm_vars.empty_slots:
            fsm_vars.fsm.jump_to_state_by_name('starting mission')

    def IDItem():
        global fsm_vars

        if ActionIsPending(): return

        id_kit_id = Inventory.GetFirstIDKit()
        if id_kit_id == 0:
            fsm_vars.fsm.jump_to_state_by_name('buying ID kit')
            return
    
        unid_item_id = Inventory.GetFirstUnidentifiedItem()
        if unid_item_id == 0:
            fsm_vars.fsm.jump_to_state_by_name('salvaging items')
            return

        fsm_vars.item_id = unid_item_id
        PyInventory.PyInventory().IdentifyItem(id_kit_id, unid_item_id)
        SetPendingAction(randint(750,1250))
        if ProcessInventory.debug:
            bag, slot = Inventory.FindItemBagAndSlot(unid_item_id)
            Debug(f'Idenfiying item ID [{unid_item_id}] in slot [{bag},{slot}]')

    def IDLoop():
        global fsm_vars
        if Inventory.GetFirstUnidentifiedItem() == 0:
            fsm_vars.fsm.jump_to_state_by_name('salvaging items')
            if ProcessInventory.debug:
                Debug(f'Idenfiy loop complete')
        else:
            fsm_vars.fsm.jump_to_state_by_name('IDing items')

    def SalvageItem():
        global fsm_vars
        salvage_kit_id = Inventory.GetFirstSalvageKit()
        if salvage_kit_id == 0:
            fsm_vars.fsm.jump_to_state_by_name('buying salvage kit')
            return
    
        salvage_item_id = Inventory.GetFirstSalvageableItem()
        if salvage_item_id == 0:
            fsm_vars.fsm.jump_to_state_by_name('selling items')
            return

        fsm_vars.item_id = salvage_item_id
        fsm_vars.item_quantity = Item.Properties.GetQuantity(salvage_item_id)
        PyInventory.PyInventory().Salvage(salvage_kit_id, salvage_item_id)
        SetPendingAction(randint(750,1250))
        if ProcessInventory.debug:
            bag, slot = Inventory.FindItemBagAndSlot(salvage_item_id)
            Debug(f'Salvaging item ID [{salvage_item_id}] in slot [{bag},{slot}]')

    def SalvageHandlePrompt():
        global fsm_vars
        if ActionIsPending(): return False
        if Item.Rarity.IsWhite(fsm_vars.item_id) or Item.Rarity.IsBlue(fsm_vars.item_id):
            return True
        else:
            Keystroke.PressAndRelease(Key.Y.value)
            PyInventory.PyInventory().HandleSalvageUI()
            SetPendingAction(randint(750,1250))
            if ProcessInventory.debug:
                Debug('Accepting salvage prompt')
        return True
    
    def SalvageCheck():
        global fsm_vars
        if ActionIsPending(): return False
        salvage_item_id = Inventory.GetFirstSalvageableItem()
        quantity = Item.Properties.GetQuantity(salvage_item_id)
        if fsm_vars.item_id != salvage_item_id or salvage_item_id == 0 or fsm_vars.item_quantity != quantity:
            return True
        return False
    
    def SalvageFinish():
        PyInventory.PyInventory().FinishSalvage()

    def SalvageLoop():
        global fsm_vars
        if Inventory.GetFirstSalvageableItem() == 0:
            bot_vars.gui_stats.current_iron = Inventory.GetModelCount(948)
            bot_vars.gui_stats.iron = bot_vars.gui_stats.current_iron - bot_vars.gui_stats.starting_iron
            fsm_vars.fsm.jump_to_state_by_name('selling items')
            if ProcessInventory.debug:
                Debug(f'Salvage loop complete')
        else:
            fsm_vars.fsm.jump_to_state_by_name('salvaging items')

    def GetSellList():
        banned_ids = [921,929,933,948,2989,2992,22751]
        bags_to_check = ItemArray.CreateBagList(1,2,3,4)
        item_array = ItemArray.GetItemArray(bags_to_check)
        item_array = ItemArray.Filter.ByCondition(item_array, lambda item_id: Item.GetModelID(item_id) not in banned_ids)
        item_array = ItemArray.Filter.ByCondition(item_array, lambda item_id: Item.Properties.GetValue(item_id) > 0)
        return item_array

    def SellItem():
        if ActionIsPending(): return False

        items_to_sell = ProcessInventory.GetSellList()

        if len(items_to_sell) > 0:
            item_id = items_to_sell[0]
            quantity = Item.Properties.GetQuantity(item_id)
            value = Item.Properties.GetValue(item_id)
            cost = quantity * value
            Trading.Merchant.SellItem(item_id, cost)
            SetPendingAction(randint(300,600))
            if ProcessInventory.debug:
                bag, slot = Inventory.FindItemBagAndSlot(item_id)
                Debug(f'Selling item ID [{item_id}] in slot [{bag},{slot}]')
        else:
            fsm_vars.fsm.jump_to_state_by_name('starting mission')

    def SellLoop():
        global fsm_vars

        items_to_sell = ProcessInventory.GetSellList()

        if len(items_to_sell) > 0:
            fsm_vars.fsm.jump_to_state_by_name('selling items')
        else:
            fsm_vars.fsm.jump_to_state_by_name('calculating item sort')
            if ProcessInventory.debug:
                Debug(f'Sell loop complete')
                
    def SortCalculate():
        global bot_vars
        sort_algo = [('type_id'  , 29),  # kits
                        ('type_id'  , 18),  # 
                        ('type_id'  , 9),   # 
                        ('type_id'  , 30),  # 
                        ('model_id' , 921), #
                        ('model_id' , 929), #
                        ('model_id' , 933), #
                        ('model_id' , 948)] # iron

        bags_to_check = ItemArray.CreateBagList(1,2,3,4)
        item_array = ItemArray.GetItemArray(bags_to_check)
        bot_vars.gui_stats.inv_sorting['type_item_list'] = []
        for sorting_type in sort_algo:
            if sorting_type[0] == 'type_id':
                items = ItemArray.Filter.ByCondition(item_array, lambda item_id: Item.GetItemType(item_id)[0] == sorting_type[1])
                bot_vars.gui_stats.inv_sorting['type_item_list'].extend(items)
            elif sorting_type[0] == 'model_id':
                items = ItemArray.Filter.ByCondition(item_array, lambda item_id: Item.GetModelID(item_id) == sorting_type[1])
                bot_vars.gui_stats.inv_sorting['type_item_list'].extend(items)
        bot_vars.gui_stats.inv_sorting['current_sort_position'] = 0
        fsm_vars.fsm.jump_to_state_by_name('sorting items')
            
    def SortItem():
        global bot_vars

        if ActionIsPending(): return False

        if not bot_vars.gui_stats.inv_sorting['type_item_list']:
            return
        item_id = bot_vars.gui_stats.inv_sorting['type_item_list'][0]

        if bot_vars.gui_stats.inv_sorting['current_sort_position'] > 34:
            sort_bag = 4
            sort_slot = bot_vars.gui_stats.inv_sorting['current_sort_position'] - 30
        elif bot_vars.gui_stats.inv_sorting['current_sort_position'] > 24:
            sort_bag = 3
            sort_slot = bot_vars.gui_stats.inv_sorting['current_sort_position'] - 25
        elif bot_vars.gui_stats.inv_sorting['current_sort_position'] > 19:
            sort_bag = 2
            sort_slot = bot_vars.gui_stats.inv_sorting['current_sort_position'] - 20
        else:
            sort_bag = 1
            sort_slot = bot_vars.gui_stats.inv_sorting['current_sort_position']

        item_bag, item_slot = Inventory.FindItemBagAndSlot(item_id)
        if item_bag != sort_bag or item_slot != sort_slot:
            Inventory.MoveItem(item_id, sort_bag, sort_slot, Item.Properties.GetQuantity(item_id))
            SetPendingAction(randint(300,500))
            if ProcessInventory.debug:
                Debug(f'Sorting item ID [{item_id}] in slot [{item_bag},{item_slot}] to slot [{sort_bag},{sort_slot}]')

        bot_vars.gui_stats.inv_sorting['type_item_list'] = bot_vars.gui_stats.inv_sorting['type_item_list'][1:]
        bot_vars.gui_stats.inv_sorting['current_sort_position'] += 1
        
        return

    def SortLoop():
        global bot_vars, fsm_vars

        if bot_vars.gui_stats.inv_sorting['type_item_list']:
            fsm_vars.fsm.jump_to_state_by_name('sorting items')
        else:
            fsm_vars.fsm.jump_to_state_by_name('starting mission')
            if ProcessInventory.debug:
                Debug(f'Sort loop complete')
# endregion

# region globals
bot_vars = BotVariabless()
fsm_vars = FSMVariables()
# endregion

# region helper functions
def Debug(message = ''):
    Py4GW.Console.Log('DEBUG', str(message), Py4GW.Console.MessageType.Info)

def StartBot():
    global bot_vars, fsm_vars
    bot_vars.bot_started = True
    bot_vars.gui_stats.total_timer.Start()
    ResetVariables()

def StopBot():
    global bot_vars
    bot_vars.bot_started = False
    bot_vars.gui_stats.total_timer.Pause()
    bot_vars.gui_stats.lap_timer.Stop()

def ActionIsPending():
    global fsm_vars
    if fsm_vars.action_timer_check != 0 and fsm_vars.action_timer.GetElapsedTime() > 0:
        if fsm_vars.action_timer.HasElapsed(fsm_vars.action_timer_check):
            fsm_vars.action_timer_check = 0
            fsm_vars.action_timer.Stop()
            return False
    if fsm_vars.action_timer_check == 0 and fsm_vars.action_timer.GetElapsedTime() == 0:
        return False
    return True

def SetPendingAction(time=1000):
    global fsm_vars
    fsm_vars.action_timer_check = time
    fsm_vars.action_timer.Reset()

def Travel(outpost_id):
    if Map.IsMapReady():
        if not Map.IsOutpost() or (Map.GetMapID() != outpost_id):
            Map.Travel(outpost_id)
            return

def Arrived(outpost_id):
    if Map.IsMapReady() and Map.GetMapID() == outpost_id and Map.IsOutpost() and Party.IsPartyLoaded():
        return True
    return False

def FollowPath(path_handler,follow_handler):
    return Routines.Movement.FollowPath(path_handler,follow_handler)

def PathFinished(path_handler,follow_handler):
    return Routines.Movement.IsFollowPathFinished(path_handler, follow_handler)

def ResetVariables():
    global fsm_vars

    fsm_vars.path['lever'].reset()
    fsm_vars.path['jump'].reset()
    fsm_vars.path['kill'].reset()
    fsm_vars.path['merch'].reset()
    fsm_vars.move.reset()
    fsm_vars.exact_move.reset()
    fsm_vars.fsm.reset()
    fsm_vars.action_timer_check = 0
    fsm_vars.action_timer.Stop()
    fsm_vars.settle_timer.Stop()
    fsm_vars.sf_timer.Stop()
# endregion

# region farming functions
def DoSetup():
    global bot_vars, fsm_vars
    if fsm_vars.do_setup:
        fsm_vars.do_setup = False
        bot_vars.gui_stats.starting_iron = Inventory.GetModelCount(948)
        bot_vars.gui_stats.current_iron = Inventory.GetModelCount(948)
    else:
        fsm_vars.fsm.jump_to_state_by_name('equipping staff')

def EnterMission():
    global bot_vars

    bot_vars.gui_stats.lap_timer.Start()
    Map.EnterChallenge()

def PrepSkills():
    if not Combat.CanCast(): return
    if ActionIsPending():    return
    

    for spell in [Build.sod, Build.wop]:
        if Combat.IsRecharged(spell):
            Combat.CastSkill(spell)
            SetPendingAction(Combat.GetAftercast(spell))
            return

def PullLever():
    gadget_array = AgentArray.GetGadgetArray()
    for agent_id in gadget_array:
        if Agent.GetGadgetID(agent_id) == 1671:
            Player.Interact(agent_id)

def JumpDown():
    Combat.CastSkill(Build.vd)
    SetPendingAction(Combat.GetAftercast(Build.vd))

def UseSF():
    global fsm_vars 
    
    if (Combat.IsRecharged(Build.dp) and Combat.IsRecharged(Build.sf) and Combat.CanCast() and Combat.GetEnergy() >= 20):
        Combat.CastSkill(Build.sf)
        fsm_vars.sf_timer.Start()
        return True

    if fsm_vars.sf_timer.IsRunning() and fsm_vars.sf_timer.HasElapsed(925):
        Combat.CastSkill(Build.dp)
        fsm_vars.sf_timer.Stop()
        return True

def WaitRotation():
    if ActionIsPending():       return
    if UseSF():                 return

def KillRotation():
    global fsm_vars
    if ActionIsPending():             return
    if UseSF():                       return
    if fsm_vars.sf_timer.IsRunning(): return

    if Combat.CanCast():
        # maintain shroud, way of perf, armor of sanctity, aura of thorns
        for spell in [Build.sod, Build.wop, Build.aos, Build.aot]:
            if Combat.GetEnergy() >= 20 and Combat.IsRecharged(spell):
                Combat.CastSkill(spell)
                SetPendingAction(Combat.GetAftercast(spell))
                return
        
        # cast mystic sandstorm
        if Combat.HasEnoughAdrenaline(Build.ms):
            Combat.CastSkill(Build.ms)
            SetPendingAction(Combat.GetAftercast(Build.ms))
            return
        
        # cast vipers defense
        enemy_array = AgentArray.GetEnemyArray()
        enemy_array = AgentArray.Filter.ByAttribute(enemy_array,'IsAlive')
        enemy_array = AgentArray.Filter.ByDistance(enemy_array,(-389,11407),100)
        if Combat.GetEnergy() >= 20 and Combat.IsRecharged(Build.vd) and len(enemy_array) > 0:
            Combat.CastSkill(Build.vd, enemy_array[0])
            SetPendingAction(Combat.GetAftercast(Build.ms))
            return

        # attack
        if not Agent.IsAttacking(Player.GetAgentID()):
            # target
            target_id = Player.GetTargetID()
            if target_id == 0 or Agent.GetAllegiance(target_id)[0] != 3 or Agent.IsDead(target_id) or Utils.Distance(Agent.GetXY(target_id),Player.GetXY()) > 400:
                enemy_array = AgentArray.GetEnemyArray()
                enemy_array = AgentArray.Filter.ByAttribute(enemy_array,'IsAlive')
                enemy_array = AgentArray.Filter.ByDistance(enemy_array,(-412,11356),400)
                if len(enemy_array) > 0 :
                    Player.ChangeTarget(enemy_array[0])
                    Debug(f'changing to target ID [{enemy_array[0]}]')
                    SetPendingAction(100)
                    return

            Player.Interact(Player.GetTargetID())
            Debug(f'attacking target ID [{Player.GetTargetID()}]')
            SetPendingAction(400)
            return

def HandleSkillbar():
    if Map.IsMapReady() and not Map.IsMapLoading() and Map.IsExplorable() and Party.IsPartyLoaded():
        if fsm_vars.fsm.get_current_step_name() == 'waiting for enemies':
            WaitRotation()
        elif fsm_vars.fsm.get_current_step_name() == 'killing enemies':
            KillRotation()

def WaitForSettle(far_range,close_range,timeout = 10000):
    global fsm_vars 

    if Agent.IsDead(Player.GetAgentID()):
        return True
    
    if not fsm_vars.settle_timer.IsRunning():
        fsm_vars.settle_timer.Start()

    if fsm_vars.settle_timer.HasElapsed(timeout):
        return True

    player_x, player_y = Player.GetXY()

    enemy_array = AgentArray.GetEnemyArray()
    enemy_array = AgentArray.Filter.ByAttribute(enemy_array, 'IsAlive')
    close_array = AgentArray.Filter.ByDistance(enemy_array, (player_x, player_y), close_range)
    far_array   = AgentArray.Filter.ByDistance(enemy_array, (player_x, player_y), far_range)

    if len(close_array) > 2 and len(close_array) == len(far_array):
        fsm_vars.settle_timer.Reset()
        fsm_vars.settle_timer.Stop()
        return True

    return False

def WaitForKill():
    global bot_vars

    if Agent.IsDead(Player.GetAgentID()):
        bot_vars.gui_stats.fails += 1
        return True

    player_x, player_y = Player.GetXY()

    enemy_array       = AgentArray.GetEnemyArray()
    enemy_array       = AgentArray.Filter.ByAttribute(enemy_array, 'IsAlive')
    melee_range_array = AgentArray.Filter.ByDistance(enemy_array, (player_x, player_y), 250)

    if len(melee_range_array) < 2:
        bot_vars.gui_stats.runs += 1
        lap_time = bot_vars.gui_stats.lap_timer.GetElapsedTime()
        bot_vars.gui_stats.lap_times.append(lap_time)
        bot_vars.gui_stats.lap_timer.Stop()
        bot_vars.gui_stats.avg_time = sum(bot_vars.gui_stats.lap_times)/bot_vars.gui_stats.runs
        return True

    return False
# endregion

# region fsm config
fsm_main_states = {
    # setup
    'travelling to outpost' : dict(execute_fn=lambda:Travel(bot_vars.starting_map),transition_delay_ms=1000,exit_condition=lambda:Arrived(bot_vars.starting_map)),
    'setting up'            : dict(execute_fn=lambda:DoSetup(),transition_delay_ms=100),
    'loading skillbar'      : dict(execute_fn=lambda:Combat.LoadSkillBar(Build.template),transition_delay_ms=1000), 
    'setting hard mode'     : dict(execute_fn=lambda:Party.SetHardMode(),transition_delay_ms=1000),
    'equipping staff'       : dict(execute_fn=lambda:Combat.ChangeWeaponSet(Build.staff),transition_delay_ms=1000),
    # inventory
    'checking inventory'    : dict(execute_fn=lambda:ProcessInventory.CheckSlots()),
    'going to merchant'     : dict(execute_fn=lambda:FollowPath(fsm_vars.path['merch'],fsm_vars.move),exit_condition=lambda:PathFinished(fsm_vars.path['merch'],fsm_vars.move),run_once=False),
    'targetting merchant'   : dict(execute_fn=lambda:Keystroke.PressAndRelease(Key.V.value),transition_delay_ms=200),
    'talking tom merchant'  : dict(execute_fn=lambda:Player.Interact(Player.GetTargetID())),
    'IDing items'           : dict(execute_fn=lambda:ProcessInventory.IDItem(),run_once=False,exit_condition=lambda: ProcessInventory.IDLoop()),
    'salvaging items'       : dict(execute_fn=lambda:ProcessInventory.SalvageItem(),exit_condition=lambda:ProcessInventory.SalvageHandlePrompt()),
    'checking salvage'      : dict(exit_condition=lambda:ProcessInventory.SalvageCheck()),
    'finishing salvage'     : dict(execute_fn=lambda:ProcessInventory.SalvageFinish()),
    'handling salvage loop' : dict(execute_fn=lambda:ProcessInventory.SalvageLoop()),
    'selling items'         : dict(execute_fn=lambda:ProcessInventory.SellItem(),run_once=False,exit_condition=lambda:ProcessInventory.SellLoop()),
    'calculating item sort' : dict(execute_fn=lambda:ProcessInventory.SortCalculate()),
    'sorting items'         : dict(execute_fn=lambda:ProcessInventory.SortItem(),run_once=False,exit_condition=lambda:ProcessInventory.SortLoop()),
    'buying ID kit'         : dict(execute_fn=lambda:Merchant.Buy(2989),exit_condition=lambda:Merchant.Check()),
    'buying salvage kit'    : dict(execute_fn=lambda:Merchant.Buy(2992),exit_condition=lambda:Merchant.Check()),
    # farm loop
    'starting mission'      : dict(execute_fn=lambda:EnterMission(),transition_delay_ms=500),
    'entering mission'      : dict(execute_fn=lambda:Keystroke.PressAndRelease(Key.Y.value),exit_condition=lambda:Routines.Transition.IsExplorableLoaded()),
    'going to lever'        : dict(execute_fn=lambda:FollowPath(fsm_vars.path['lever'],fsm_vars.move),exit_condition=lambda:PathFinished(fsm_vars.path['lever'],fsm_vars.move),run_once=False),
    'prepping skills'       : dict(execute_fn=lambda:PrepSkills(),exit_condition=lambda:Combat.HasBuff(Player.GetAgentID(),Build.sod) and Combat.HasBuff(Player.GetAgentID(),Build.wop),run_once=False),
    'targetting mage'       : dict(execute_fn=lambda:Keystroke.PressAndRelease(Key.V.value),transition_delay_ms=200),
    'pulling lever'         : dict(execute_fn=lambda:PullLever(),transition_delay_ms=1000),
    'going to jump spot'    : dict(execute_fn=lambda:FollowPath(fsm_vars.path['jump'],fsm_vars.exact_move),exit_condition=lambda:PathFinished(fsm_vars.path['jump'],fsm_vars.exact_move),run_once=False),
    'jumping off mage'      : dict(execute_fn=lambda:Combat.CastSkill(Build.vd),exit_condition=lambda:not Combat.IsRecharged(Build.vd),transition_delay_ms=250),
    'going to kill spot'    : dict(execute_fn=lambda:FollowPath(fsm_vars.path['kill'],fsm_vars.exact_move),exit_condition=lambda:PathFinished(fsm_vars.path['kill'],fsm_vars.exact_move),run_once=False),
    'waiting for enemies'   : dict(exit_condition=lambda:WaitForSettle(400,200)),
    'equipping scythe'      : dict(execute_fn=lambda:Combat.ChangeWeaponSet(Build.scythe),exit_condition=lambda:Agent.GetWeaponType(Player.GetAgentID())[1]=='Scythe'),
    'killing enemies'       : dict(exit_condition=lambda:WaitForKill()),
    'looting items'         : dict(execute_fn=lambda: Loot.PickUp(),run_once=False,exit_condition=lambda: Loot.Loop()),
    # reset
    'resetting farm loop'   : dict(execute_fn=lambda:ResetVariables(),transition_delay_ms=1000)
}
for state, kwargs in fsm_main_states.items():
    fsm_vars.fsm.AddState(state,**kwargs)
# endregion

# region main
def DrawWindow():
    global bot_vars, fsm_vars

    def make_table(*columns, colors = None):
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
        
    def log_state():
        if bot_vars.gui_stats.status != fsm_vars.fsm.get_current_step_name():
            if "FSM not started or finished" not in fsm_vars.fsm.get_current_step_name():
                bot_vars.gui_stats.time = datetime.now().strftime('%H:%M:%S')
                bot_vars.gui_stats.status = fsm_vars.fsm.get_current_step_name()

        PyImGui.text_colored(f'[{bot_vars.gui_stats.time}]', [.48, .68, 1, 1])
        PyImGui.same_line(0.0,-1.0)
        PyImGui.text(f'{bot_vars.gui_stats.status}')

    try:
        if bot_vars.window_module.first_run:
            PyImGui.set_next_window_size(bot_vars.window_module.window_size[0], bot_vars.window_module.window_size[1])     
            PyImGui.set_next_window_pos(bot_vars.window_module.window_pos[0], bot_vars.window_module.window_pos[1])
            bot_vars.window_module.first_run = False

        if PyImGui.begin(bot_vars.window_module.window_name, bot_vars.window_module.window_flags):

            PyImGui.push_style_color(PyImGui.ImGuiCol.Button,        (.2,.2,.2,1))
            PyImGui.push_style_color(PyImGui.ImGuiCol.ButtonHovered, (.3,.3,.3,1))
            if bot_vars.bot_started:
                if PyImGui.button('Stop', 200):
                    #ResetEnvironment()
                    StopBot()
            else:
                if PyImGui.button('Start', 200):
                    #ResetEnvironment()
                    StartBot()

            # if PyImGui.button('Test', 200):
            #     Debug(Agent.GetAlliegance(Player.GetTargetID()))
                # fsm_vars.fsm.jump_to_state_by_name('calculating item sort')
                # bot_vars.bot_started = True

            PyImGui.pop_style_color(2)

            log_state()

            table_runs  = {'stats'  : ['Runs','Fails','Average Pace','Total Time', 'Iron (Stacks)'],
                           'values' : [bot_vars.gui_stats.runs,
                                       bot_vars.gui_stats.fails,
                                       FormatTime(bot_vars.gui_stats.avg_time,mask='mm:ss'),
                                       bot_vars.gui_stats.total_timer.FormatElapsedTime("hh:mm:ss"),
                                       f'{bot_vars.gui_stats.iron} ({round(bot_vars.gui_stats.iron/250,1)})',],
                           'colors' : [[0, .7, 0, 1],[1, .25, .23, 1],[.9,.9,.9,1],[.9,.9,.9,1],[.631, .616, .580, 1]]}
            
            make_table(table_runs['stats'],table_runs['values'],colors = table_runs['colors'])

            # PyImGui.push_style_color(PyImGui.ImGuiCol.Header,        (.2,.2,.2,1))
            # PyImGui.push_style_color(PyImGui.ImGuiCol.HeaderActive,  (.2,.2,.2,1))
            # PyImGui.push_style_color(PyImGui.ImGuiCol.HeaderHovered, (.3,.3,.3,1))
            # if PyImGui.collapsing_header('More'):
            #     table_runs  = {'stats'  : ['Starting Iron','Current Iron','Gold Coins','Salvageables', 'Iron per Drop'],
            #                    'values' : [f'{bot_vars.gui_stats.starting_iron} ({round(bot_vars.gui_stats.starting_iron/250,1)})',
            #                                f'{bot_vars.gui_stats.current_iron} ({round(bot_vars.gui_stats.current_iron/250,1)})',
            #                                bot_vars.gui_stats.gold_coins,
            #                                bot_vars.gui_stats.salvageables,
            #                                bot_vars.gui_stats.iron_per_drop],
            #                    'colors' : [[.631, .616, .580, 1],[.631, .616, .580, 1],[.898,.722,.043,1],[.9,.9,.9,1],[.631, .616, .580, 1]]}
            
            #     make_table(table_runs['stats'],table_runs['values'],colors = table_runs['colors'])
            # PyImGui.pop_style_color(3)

        PyImGui.end()

    except Exception as e:
        current_function = inspect.currentframe().f_code.co_name
        Py4GW.Console.Log('BOT', f'Error in {current_function}: {str(e)}', Py4GW.Console.MessageType.Error)
        raise

def main():
    global bot_vars, fsm_vars

    try:
        # draw gui
        if Party.IsPartyLoaded():
            DrawWindow()

        # execute script
        if bot_vars.bot_started:
            if fsm_vars.fsm.is_finished():
                ResetVariables()
            else:
                fsm_vars.fsm.update()
                HandleSkillbar()

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