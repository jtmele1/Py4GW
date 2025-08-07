from Py4GWCoreLib import *
from random import randint
from datetime import datetime

action_queue = ActionQueueNode(150)

def Log(message, title = 'STATUS', msg_type = 'Info'):
    py4gw_msg_type = Py4GW.Console.MessageType.Info
    if   msg_type == 'Debug':       py4gw_msg_type = Py4GW.Console.MessageType.Debug
    elif msg_type == 'Error':       py4gw_msg_type = Py4GW.Console.MessageType.Error
    elif msg_type == 'Info':        py4gw_msg_type = Py4GW.Console.MessageType.Info
    elif msg_type == 'Notice':      py4gw_msg_type = Py4GW.Console.MessageType.Notice
    elif msg_type == 'Performance': py4gw_msg_type = Py4GW.Console.MessageType.Performance
    elif msg_type == 'Success':     py4gw_msg_type = Py4GW.Console.MessageType.Success
    elif msg_type == 'Warning':     py4gw_msg_type = Py4GW.Console.MessageType.Warning
    Py4GW.Console.Log(title, str(message), py4gw_msg_type)

def Debug(message, title = 'DEBUG', msg_type = 'Debug'):
    Log(message, title, msg_type)

class SynchronousRoutines:
    global action_queue

    log_player = False
    log_move   = False
    log_skills = False
    log_agents = False
    log_maps   = False
    log_items  = False
    log_all    = True

    class Player:
        @staticmethod
        def SendDialog(dialog_id):
            if SynchronousRoutines.log_player or SynchronousRoutines.log_all:
                Log(f'Sending DialogID [{hex(dialog_id)}]')
            action_queue.add_action(Player.SendDialog, dialog_id)
            sleep(.5)

        @staticmethod
        def SendChatCommand(command):
            if SynchronousRoutines.log_player or SynchronousRoutines.log_all:
                Log(f'Sending chat command [{command}]')
            action_queue.add_action(Player.SendChatCommand, command)
            sleep(.5)

        @staticmethod
        def ClickUIOptionFrame(hash, offset_ids, option):
            frames = UIManager.GetAllChildFrameIDs(hash, offset_ids)
            frames = UIManager.SortFramesByVerticalPosition(frames)
            if frames:
                frame_id = frames[option][0]
                SynchronousRoutines.Player.ClickUIFrame(frame_id)

        @staticmethod
        def ClickUIFrame(frame_id):
            if SynchronousRoutines.log_player or SynchronousRoutines.log_all:
                Log(f'Clicking FrameID [{frame_id}]')
            action_queue.add_action(UIManager.FrameClick, frame_id)
            sleep(.5)

    class Move:
        @staticmethod
        def FollowPath(path, do_func = None, stuck_func = None, stuck_time = 3000,
                       exit_func = lambda: False, rand = 50, extra_status = ''):
            if not isinstance(path, list): path = [path]
            if extra_status: extra_status = f'{extra_status} '
            tolerance = 1.1*math.sqrt(rand**2 + rand**2)
            starting_map_id = Map.GetMapID()

            for idx, (x, y) in enumerate(path):
                if SynchronousRoutines.log_move or SynchronousRoutines.log_all:
                    Log(f'Traversing {extra_status}point [{idx + 1}/{len(path)}].')
                    
                timer = Timer()
                timer.Start()
                while True:
                    rand_x = x + randint(-rand, rand)
                    rand_y = y + randint(-rand, rand)

                    if exit_func():                       return
                    if Agent.IsDead(Player.GetAgentID()): return
                    if Map.IsMapLoading():                return
                    if Map.GetMapID() != starting_map_id: return

                    if Utils.Distance(Player.GetXY(), (rand_x, rand_y)) <= tolerance:
                        break

                    if callable(do_func):
                        do_func()

                    if Agent.IsMoving(Player.GetAgentID()) or Agent.IsCasting(Player.GetAgentID()):
                        timer.Reset()
                    else:
                        action_queue.add_action(Player.Move, rand_x, rand_y)
                        sleep(.5)

                    if timer.HasElapsed(stuck_time) and callable(stuck_func):
                        if stuck_func():
                            return
                        timer.Reset()
                    
                    sleep(.1)

        @staticmethod
        def Zone(path, map_id, do_func = None, stuck_func = None, stuck_time = 3000,
                 exit_func = lambda: False, rand = 50, extra_status = ''):
            if SynchronousRoutines.log_move or SynchronousRoutines.log_all:
                Log(f'Zoning to {Map.GetMapName(map_id)} - MapID [{map_id}].')

            SynchronousRoutines.Move.FollowPath(path, do_func, stuck_func, stuck_time, exit_func, rand, extra_status)
            if Agent.IsDead(Player.GetAgentID()): return
            SynchronousRoutines.Maps.WaitForArrival(map_id)

    class Skills:
        @staticmethod
        def CheckRequirements(attribute_checks):
            error = False
            error_msgs = []

            # check attributes (for runes)
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

        @staticmethod
        def LoadSkillBar(template):
            if SynchronousRoutines.log_skills or SynchronousRoutines.log_all:
                Log(f'Loading skill template [{template}]')
            action_queue.add_action(SkillBar.LoadSkillTemplate,template)
            sleep(.1)

        @staticmethod
        def ChangeWeaponSet(set,weapon_type = None):
            if Agent.IsDead(Player.GetAgentID()): return
            if SynchronousRoutines.log_skills or SynchronousRoutines.log_all:
                Log(f'Equipping weapon set [{set}].')

            key = None
            if   set == 1: key = Key.F1.value
            elif set == 2: key = Key.F2.value
            elif set == 3: key = Key.F3.value
            elif set == 4: key = Key.F4.value

            while not Agent.GetWeaponType(Player.GetAgentID())[1] == weapon_type:
                action_queue.add_action(Keystroke.PressAndRelease, key)
                sleep(.5)
                if not weapon_type:
                    break

        @staticmethod
        def CastSkill(slots, wait_for_aftercast = True, min_aftercast = 200):
            if not isinstance(slots, list):
                slots = [slots]

            for slot in slots:
                name = Skill.GetName(SkillBar.GetSkillIDBySlot(slot)).replace('_',' ')
                if SynchronousRoutines.log_skills or SynchronousRoutines.log_all:
                    Log(f'Casting "{name}" - Slot [{slot}].')

                key = None
                if   slot == 1: key = Key.One.value
                elif slot == 2: key = Key.Two.value
                elif slot == 3: key = Key.Three.value
                elif slot == 4: key = Key.Four.value
                elif slot == 5: key = Key.Five.value
                elif slot == 6: key = Key.Six.value
                elif slot == 7: key = Key.Seven.value
                elif slot == 8: key = Key.Eight.value

                action_queue.add_action(Keystroke.PressAndRelease, key)

                if wait_for_aftercast:
                    sleep(max(min_aftercast/1000, SynchronousRoutines.Skills.GetAftercast(slot)/1000))

        @staticmethod
        def IsRecharged(slot):
            skill = SkillBar.GetSkillData(slot)
            recharge = skill.recharge
            return recharge == 0
        
        @staticmethod
        def GetAftercast(slot):
            skill_id = SkillBar.GetSkillIDBySlot(slot)

            activation = Skill.Data.GetActivation(skill_id)
            aftercast = Skill.Data.GetAftercast(skill_id)    
            return max(activation*1000 + aftercast*1000,200)
        
        @staticmethod
        def EffectTimeRemaining(skill_id):
            for effect in Effects.GetEffects(Player.GetAgentID()):
                if effect.skill_id == skill_id:
                    return effect.time_remaining/1000
            return 0
        
        @staticmethod
        def CanCast():
            player_agent_id = Player.GetAgentID()

            if (Agent.IsCasting(player_agent_id) 
                or Agent.GetCastingSkill(player_agent_id) != 0
                or Agent.IsKnockedDown(player_agent_id)
                or Agent.IsDead(player_agent_id)
                or SkillBar.GetCasting() != 0):
                return False
            return True

        @staticmethod
        def GetEnergyAgentCost(slot):
            skill_id = SkillBar.GetSkillIDBySlot(slot)
            cost = Skill.skill_instance(skill_id).energy_cost

            if cost == 11:
                cost = 15    # True cost is 15
            elif cost == 12:
                cost = 25    # True cost is 25

            cost = max(0, cost)
            return cost

        @staticmethod
        def GetEnergy():
            player_agent_id = Player.GetAgentID()
            energy = Agent.GetEnergy(player_agent_id)
            max_energy = Agent.GetMaxEnergy(player_agent_id)
            energy_points = int(energy * max_energy)

            return energy_points

        @staticmethod
        def HasEnoughEnergy(slot):
            player_agent_id = Player.GetAgentID()
            energy = Agent.GetEnergy(player_agent_id)
            max_energy = Agent.GetMaxEnergy(player_agent_id)
            energy_points = int(energy * max_energy)

            return SynchronousRoutines.Skills.GetEnergyAgentCost(slot) <= energy_points
        
        @staticmethod
        def HasEnoughAdrenaline(slot):
            skill_id = SkillBar.GetSkillIDBySlot(slot)

            return SkillBar.GetSkillData(slot).adrenaline_a >= Skill.Data.GetAdrenaline(skill_id)
        
        @staticmethod
        def HasEffect(slots):
            if not isinstance(slots, list):
                slots = [slots]

            for slot in slots:
                skill_id = SkillBar.GetSkillIDBySlot(slot)
                if not Effects.EffectExists(Player.GetAgentID(), skill_id):
                    return False
            return True

    class Agents:
        @staticmethod
        def GetAgentName(agent_id):
            if Agent.IsNameReady(agent_id):
                return f'"{Agent.GetName(agent_id)}" - '
            return ''

        @staticmethod
        def RequestEnemyNames():
            agent_array = AgentArray.GetEnemyArray()
            for agent_id in agent_array:
                Agent.RequestName(agent_id)
            sleep(0.5)

        @staticmethod
        def ChangeTarget(agent_id):
            if SynchronousRoutines.log_agents or SynchronousRoutines.log_all:
                Log(f'Changing target to {SynchronousRoutines.Agents.GetAgentName(agent_id)}AgentID [{agent_id}].')
            action_queue.add_action(Player.ChangeTarget, agent_id)
            sleep(0.2)

        @staticmethod
        def TargetNearestNPC():
            if SynchronousRoutines.log_agents or SynchronousRoutines.log_all:
                Log(f'Changing target to nearest NPC.')
            action_queue.add_action(Keystroke.PressAndRelease, Key.V.value)
            sleep(0.2)

        @staticmethod
        def TargetNearestEnemy():
            if SynchronousRoutines.log_agents or SynchronousRoutines.log_all:
                Log(f'Changing target to nearest enemy.')
            action_queue.add_action(Keystroke.PressAndRelease, Key.C.value)
            sleep(0.2)

        @staticmethod
        def Interact(distance = None, frame_alias = '', timeout = 5000):
            if SynchronousRoutines.log_agents or SynchronousRoutines.log_all:
                Log(f'Interacting with target.')
            action_queue.add_action(Keystroke.PressAndRelease, Key.Space.value)

            timer = Timer()
            timer.Start()
            # wait for player to reach target
            if distance:
                while Utils.Distance(Player.GetXY(),Agent.GetXY(Player.GetTargetID())) > distance:
                    if timer.GetElapsedTime() > timeout:
                        break
                    sleep(.2)
            # wait for window to open
            elif frame_alias != '':
                filename = r'D:\Games\Guild Wars\Py4GW\my_bots\synchronous\frame_aliases.json'
                while not int(UIManager.GetFrameIDByCustomLabel(filename = filename,frame_label = frame_alias)):
                    if timer.GetElapsedTime() > timeout:
                        break
                    sleep(.2)

    class Maps:
        @staticmethod
        def SetMode(mode = 0):
            if mode:
                if SynchronousRoutines.log_maps or SynchronousRoutines.log_all:
                    Log(f'Setting Hard Mode.')
                action_queue.add_action(Party.SetHardMode)
            else:
                if SynchronousRoutines.log_maps or SynchronousRoutines.log_all:
                    Log(f'Setting Normal Mode.')
                action_queue.add_action(Party.SetNormalMode)
            
            sleep(.1)

        @staticmethod
        def EnterChallenge():
            action_queue.add_action(Map.EnterChallenge)
            sleep(.1)

        @staticmethod
        def WaitForArrival(map_id):
            while not (Map.IsMapReady() and Map.GetMapID() == map_id and Party.IsPartyLoaded()):
                sleep(.5)
            if SynchronousRoutines.log_maps or SynchronousRoutines.log_all:
                Log(f'Arrived at {Map.GetMapName(map_id)} - MapID [{map_id}].')
            sleep(2)

        @staticmethod
        def Travel(map_id):
            if not Map.IsOutpost() or (Map.GetMapID() != map_id):
                if SynchronousRoutines.log_maps or SynchronousRoutines.log_all:
                    Log(f'Travelling to {Map.GetMapName(map_id)} - MapID [{map_id}].')
                action_queue.add_action(Map.Travel, map_id)
                    
                SynchronousRoutines.Maps.WaitForArrival(map_id)

        @staticmethod
        def ResignAndReturn(map_id):
            SynchronousRoutines.Player.SendChatCommand('resign')
            while not Party.IsPartyDefeated():
                sleep(.5)
            if SynchronousRoutines.log_maps or SynchronousRoutines.log_all:
                Log(f'Returning to {Map.GetMapName(map_id)} - MapID [{map_id}].')
            action_queue.add_action(Party.ReturnToOutpost)
            SynchronousRoutines.Maps.WaitForArrival(map_id)
            sleep(2)

    class Items:
        @staticmethod
        def GetItemName(item_id):
            if Item.IsNameReady(item_id):
                return f'"{Item.GetName(item_id)}" - '
            return ''

        @staticmethod
        def RequestInvNames():
            bags_to_check = ItemArray.CreateBagList(1,2,3,4)
            for item in ItemArray.GetItemArray(bags_to_check):
                Item.RequestName(item)
            sleep(1)

        @staticmethod
        def RequestLootNames():
            agent_array = AgentArray.GetItemArray()
            for agent_id in agent_array:
                Agent.RequestName(agent_id)
            sleep(0.5)

        @staticmethod
        def CheckSlots(empty_slots):
            return Inventory.GetFreeSlotCount() <= empty_slots

        @staticmethod
        def BuyItem(model_id):
            item_array = Trading.Merchant.GetOfferedItems()
            for item_id in item_array:
                if Item.GetModelID(item_id) == model_id:
                    value = Item.Properties.GetValue(item_id) * 2
                    if SynchronousRoutines.log_items or SynchronousRoutines.log_all:
                        Log(f'Buying ItemID [{item_id}] for [{value}] gold.')
                    action_queue.add_action(Trading.Merchant.BuyItem, item_id, value)
                    break

            while not Item.GetItemIdFromModelID(model_id):
                sleep(.1)

        @staticmethod
        def Identify():
            item_id = Inventory.GetFirstUnidentifiedItem()
            while item_id != 0:
                kit_id = Inventory.GetFirstIDKit()
                if not kit_id:
                    SynchronousRoutines.Items.BuyItem(2989)
                    continue
                
                bag, slot = Inventory.FindItemBagAndSlot(item_id)
                if SynchronousRoutines.log_items or SynchronousRoutines.log_all:
                    Log(f'Idenfiying {SynchronousRoutines.Items.GetItemName(item_id)}ItemID [{item_id}] in slot [{bag},{slot}].')

                action_queue.add_action(Inventory.IdentifyItem, item_id, kit_id)

                while item_id == Inventory.GetFirstUnidentifiedItem():
                    sleep(.1)

                item_id = Inventory.GetFirstUnidentifiedItem()
            if SynchronousRoutines.log_items or SynchronousRoutines.log_all:
                Log('Identify loop complete.')

        @staticmethod
        def Salvage():
            item_id = Inventory.GetFirstSalvageableItem()
            while item_id != 0:
                kit_id = Inventory.GetFirstSalvageKit()
                if not kit_id:
                    SynchronousRoutines.Items.BuyItem(2992)
                    continue
                
                quantity = Item.Properties.GetQuantity(item_id)
                bag, slot = Inventory.FindItemBagAndSlot(item_id)
                if SynchronousRoutines.log_items or SynchronousRoutines.log_all:
                    Log(f'Salvaging {SynchronousRoutines.Items.GetItemName(item_id)}ItemID [{item_id}] in slot [{bag},{slot}].')

                action_queue.add_action(Inventory.SalvageItem, item_id, kit_id)
                while item_id == Inventory.GetFirstSalvageableItem():
                    sleep(.1)
                    if quantity != Item.Properties.GetQuantity(item_id):
                        break
                    if Item.Rarity.IsPurple(item_id) or Item.Rarity.IsGold(item_id):
                        if SynchronousRoutines.log_items or SynchronousRoutines.log_all:
                            Log('Handling Salvage UI.')
                        action_queue.add_action(Inventory.AcceptSalvageMaterialsWindow)
                        sleep(.1)

                item_id = Inventory.GetFirstSalvageableItem()
            if SynchronousRoutines.log_items or SynchronousRoutines.log_all:
                Log('Salvage loop complete.')

        @staticmethod
        def GetSellList(dont_sell_list):
            item_array = ItemArray.GetItemArray(ItemArray.CreateBagList(1,2,3,4))
            item_array = ItemArray.Filter.ByCondition(item_array, lambda item_id: Item.GetModelID(item_id) not in dont_sell_list)
            item_array = ItemArray.Filter.ByCondition(item_array, lambda item_id: Item.Properties.GetValue(item_id) > 0)
            return item_array

        @staticmethod
        def Sell(dont_sell_list = None):
            if not dont_sell_list:
                return
            
            sell_list = SynchronousRoutines.Items.GetSellList(dont_sell_list)
            if not sell_list:
                return

            item_id = sell_list[0]
            while sell_list:
                bag, slot = Inventory.FindItemBagAndSlot(item_id)
                if SynchronousRoutines.log_items or SynchronousRoutines.log_all:
                    Log(f'Selling {SynchronousRoutines.Items.GetItemName(item_id)}ItemID [{item_id}] in slot [{bag},{slot}].')

                if not bag:
                    sell_list = sell_list[1:]
                    if sell_list:
                        item_id = sell_list[0]
                    continue

                quantity = Item.Properties.GetQuantity(item_id)
                value = Item.Properties.GetValue(item_id)
                cost = quantity * value
                action_queue.add_action(Trading.Merchant.SellItem, item_id, cost)

                while item_id in ItemArray.GetItemArray(ItemArray.CreateBagList(1, 2, 3, 4)):
                    sleep(.1)

                sell_list = sell_list[1:]
                if sell_list:
                    item_id = sell_list[0]
            if SynchronousRoutines.log_items or SynchronousRoutines.log_all:
                Log('Sell loop complete.')

        @staticmethod
        def Sort(continue_sort = True):
            sort_algo = [('type_id' , 29),  # kits
                         ('type_id' , 18),  # 
                         ('type_id' , 9),   # 
                         ('type_id' , 30),  # 
                         ('model_id', 921), # bone
                         ('model_id', 929), # dust
                         ('model_id', 933), # feathers
                         ('model_id', 948)] # iron
            
            bags_to_check = ItemArray.CreateBagList(1,2,3,4)
            item_array = ItemArray.GetItemArray(bags_to_check)
            sort_list = []
            for sorting_type in sort_algo:
                if sorting_type[0] == 'type_id':
                    items = ItemArray.Filter.ByCondition(item_array, lambda item_id: Item.GetItemType(item_id)[0] == sorting_type[1])
                    sort_list.extend(items)
                elif sorting_type[0] == 'model_id':
                    items = ItemArray.Filter.ByCondition(item_array, lambda item_id: Item.GetModelID(item_id) == sorting_type[1])
                    sort_list.extend(items)
            sort_position = 0

            for item_id in sort_list:
                if sort_position > 34:
                    sort_bag = 4
                    sort_slot = sort_position - 30
                elif sort_position > 24:
                    sort_bag = 3
                    sort_slot = sort_position - 25
                elif sort_position > 19:
                    sort_bag = 2
                    sort_slot = sort_position - 20
                else:
                    sort_bag = 1
                    sort_slot = sort_position

                item_bag, item_slot = Inventory.FindItemBagAndSlot(item_id)
                if item_bag != sort_bag or item_slot != sort_slot:
                    if SynchronousRoutines.log_items or SynchronousRoutines.log_all:
                        Log(f'Sorting "{Item.GetName(item_id)}" - ItemID [{item_id}] in slot [{item_bag},{item_slot}] to slot [{sort_bag},{sort_slot}].')
                    action_queue.add_action(Inventory.MoveItem,item_id, sort_bag, sort_slot, Item.Properties.GetQuantity(item_id))
                    sleep(.15)
                sort_position += 1
            if continue_sort:
                SynchronousRoutines.Items.Sort(False)
            else:
                if SynchronousRoutines.log_items or SynchronousRoutines.log_all:
                    Log('Sort loop complete')

        @staticmethod
        def ProcessInventory(dont_sell_list = None):
            if dont_sell_list:
                SynchronousRoutines.Items.Identify()
                SynchronousRoutines.Items.Salvage()
                SynchronousRoutines.Items.Sell(dont_sell_list)
                SynchronousRoutines.Items.Sort()
            else:
                Log('A sell list is required to process your inventory.', msg_type = 'Notice')

        @staticmethod
        def LogInventory(item_ids = None):
            counts = {}
            if item_ids:
                for item_id in item_ids:
                    if item_id == 2511: # gold coins
                        counts[item_id] = Inventory.GetGoldOnCharacter()
                    elif item_id == 'salvageables':
                        salvageables = ItemArray.GetItemArray(ItemArray.CreateBagList(1,2,3,4))
                        salvageables = ItemArray.Filter.ByCondition(salvageables, lambda item_id: Item.Usage.IsSalvageable(item_id))
                        counts[item_id] = len(salvageables)
                    else:
                        counts[item_id] = Inventory.GetModelCount(item_id)
            return counts

        @staticmethod
        def GetLootList(model_ids):
            agent_array = AgentArray.GetItemArray()

            valid_model_ids = []
            for value in model_ids:
                if isinstance(value, int):
                    valid_model_ids.append(value)

            item_array_model = AgentArray.Filter.ByCondition(agent_array, lambda agent_id: Item.GetModelID(Agent.GetItemAgent(agent_id).item_id) in valid_model_ids)

            item_array_salv = []
            if 'salvageables' in model_ids:
                item_array_salv = AgentArray.Filter.ByCondition(agent_array, lambda agent_id: Item.Usage.IsSalvageable(Agent.GetItemAgent(agent_id).item_id))

            item_array = list(set(item_array_model + item_array_salv))  
            item_array = AgentArray.Sort.ByDistance(item_array,Player.GetXY())

            return item_array

        @staticmethod
        def Loot(loot_list = None):
            loot_list = SynchronousRoutines.Items.GetLootList(loot_list)
            if not loot_list:                     return
            if Agent.IsDead(Player.GetAgentID()): return

            agent_id = loot_list[0]
            while loot_list:
                SynchronousRoutines.Agents.ChangeTarget(agent_id)
                if SynchronousRoutines.log_items or SynchronousRoutines.log_all:
                    Log(f'Picking up {SynchronousRoutines.Agents.GetAgentName(agent_id)}AgentID [{agent_id}].')
                action_queue.add_action(Keystroke.PressAndRelease, Key.Space.value)
                timer = Timer()
                timer.Start()
                while timer.GetElapsedTime() < 5000:
                    sleep(.5)
                    if not Agent.IsValid(agent_id):
                        break
                    
                loot_list = loot_list[1:]
                if loot_list:
                    agent_id = loot_list[0]
            if SynchronousRoutines.log_items or SynchronousRoutines.log_all:
                Log('Loot loop complete.')

class BotVariables:
    bot_started = False
    do_setup    = True
    handle_inv  = False

    class FarmItem:
        name     = ''
        model_id = 0
        color    = [.9, .9, .9, 1]

    class Loot:
        pickup_list = {}
        ignore_list = {}
        dont_sell_list = []

    class Timers:
        total     = Timer()
        lap       = Timer()
        lap_times = []

    class Stats:
        status          = [datetime.now().strftime('%H:%M:%S'),'waiting for input']
        runs            = 0
        fails           = 0
        pace            = 0
        farmed          = 0
        farmed_per_hour = 0
        starting_farmed = 0
        total_farmed    = 0

    class GUI:
        window_module = ImGui.WindowModule('Farmer',window_pos=(234,802),window_flags=PyImGui.WindowFlags.AlwaysAutoResize)
        window_width  = 220
        window_name   = ''
        
        class Opts:
            condense_tables = False
            color_rows      = True
            show_all        = True
        
        class Rows:
            runs            = True
            fails           = True
            pace            = True
            lap_time        = False
            total_time      = True
            farmed          = True
            farmed_per_hour = False
            starting_farmed = False
            total_farmed    = False

            def GetRows(self):
                return [
                    self.runs,
                    self.fails,
                    self.pace,
                    self.lap_time,
                    self.total_time,
                    self.farmed,
                    self.farmed_per_hour,
                    self.starting_farmed,
                    self.total_farmed
                ]
            
        opts = Opts()
        rows = Rows()
    
    farm_item = FarmItem()
    loot      = Loot()
    timers    = Timers()
    stats     = Stats()
    gui       = GUI()

def SetStatus(bot_vars, status):
    bot_vars.stats.status = [datetime.now().strftime('%H:%M:%S'),status]
    Log(status)

def LogLap(bot_vars):
    if Agent.IsDead(Player.GetAgentID()):
        bot_vars.stats.fails += 1
        return

    bot_vars.stats.runs += 1
    lap_time = bot_vars.timers.lap.GetElapsedTime()
    bot_vars.timers.lap_times.append(lap_time)
    bot_vars.timers.lap.Stop()
    bot_vars.stats.pace = int(sum(bot_vars.timers.lap_times)/bot_vars.stats.runs)

    Log(f'Lap completed in {FormatTime(lap_time,mask='mm:ss')} s.', msg_type = 'Notice')

def CatalogLoot(bot_vars, inv_log):
    def GetKeyFromValue(value):
        for key, val in bot_vars.loot.pickup_list.items():
            if val == value:
                return key
        return ''

    keys = inv_log.keys()

    curr_inv = SynchronousRoutines.Items.LogInventory(keys)
    new_inv  = {key: curr_inv[key] - inv_log[key] for key in set(inv_log) & set(curr_inv)}

    bot_vars.stats.farmed += new_inv[bot_vars.farm_item.model_id]
    bot_vars.stats.farmed_per_hour = int(bot_vars.stats.farmed*3600000/bot_vars.timers.total.GetElapsedTime())
    bot_vars.stats.total_farmed = Inventory.GetModelCount(bot_vars.farm_item.model_id)

    Log('Loot from current lap:', msg_type = 'Notice')
    for key in keys:
        Log(f'  -   {GetKeyFromValue(key)}: {new_inv[key]}', msg_type = 'Notice')

def Draw(bot_vars, thread_manager, SyncFc):
    def SetWindowStyle():
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

    def PopWindowStyle():
        PyImGui.pop_style_var(3)
        PyImGui.pop_style_color(8)

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

    def CreateRunButton():
        button_width = (bot_vars.gui.window_width-20)

        SetButtonStyle(1)
        if bot_vars.bot_started:
            if PyImGui.button('\uf04d', button_width, 25):
                thread_manager.stop_all_threads()
                action_queue.clear()
                bot_vars.bot_started = False
                bot_vars.timers.total.Pause()
                bot_vars.timers.lap.Stop()

                Log('Stopping script.')
        else:
            if PyImGui.button('\uf04b', button_width, 25):
                thread_manager.stop_all_threads()
                thread_manager.add_thread('SynchronousLogic', SyncFc)
                thread_manager.start_watchdog('SynchronousLogic')
                bot_vars.bot_started = True
                bot_vars.timers.total.Start()

                Log('Starting script.')
        PopButtonStyle()

    def CreateStateLog():
        PyImGui.text_colored(f'[{bot_vars.stats.status[0]}]', (.48, .68, 1, 1))
        PyImGui.same_line(0.0,-1.0)
        PyImGui.text(f'{bot_vars.stats.status[1]}')

    def CreateTables():
        colors = {
            'runs'     : [   0,   .7,    0, 1],
            'fails'    : [   1,  .25,  .23, 1],
            'time'     : [  .9,   .9,   .9, 1],
            'farmed'   : bot_vars.farm_item.color,
        }

        columns = [
            'Runs',
            'Fails',
            'Average Pace',
            'Lap Time',
            'Total Time',
            bot_vars.farm_item.name,
            f'{bot_vars.farm_item.name}/Hour',
            f'Starting {bot_vars.farm_item.name}',
            f'Total {bot_vars.farm_item.name}'
        ]

        values = [
            bot_vars.stats.runs,
            bot_vars.stats.fails,
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
            colors['farmed'],
            colors['farmed'],
            colors['farmed'],
            colors['farmed'],
        ]

        table_nums = [1,1,2,2,2,3,3,3,3]

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
        SetButtonStyle(1)

        if PyImGui.button('Process Inventory',PyImGui.get_window_size()[0]-60):
            thread_manager.stop_all_threads()
            thread_manager.add_thread('SynchronousLogic', SyncFc)
            thread_manager.start_watchdog('SynchronousLogic')
            bot_vars.handle_inv = True
            bot_vars.bot_started = True

        if PyImGui.button('Open Storage', PyImGui.get_window_size()[0]-60):
            if not Inventory.IsStorageOpen():
                Inventory.OpenXunlaiWindow()

        PyImGui.pop_style_color(3)

        # gui
        if PyImGui.tree_node('User Interface  '):
            bot_vars.gui.opts.condense_tables  = PyImGui.checkbox('Condense Tables',    bot_vars.gui.opts.condense_tables)
            bot_vars.gui.opts.color_rows       = PyImGui.checkbox('Color Rows',         bot_vars.gui.opts.color_rows)
            bot_vars.gui.opts.show_all         = PyImGui.checkbox('Show All',           bot_vars.gui.opts.show_all)
            PyImGui.separator()
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