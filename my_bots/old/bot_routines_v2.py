from Py4GWCoreLib import *
from random import randint

action_queue = ActionQueueNode(150)
debug = True

class BotRoutines:
    global action_queue

    action_timer = Timer()
    action_check = 0

    @staticmethod
    def ActionIsPending():
        global bot_vars
        if BotRoutines.action_check != 0 and BotRoutines.action_timer.GetElapsedTime() > 0:
            if BotRoutines.action_timer.HasElapsed(BotRoutines.action_check):
                BotRoutines.action_check = 0
                BotRoutines.action_timer.Stop()
                return False
        if BotRoutines.action_check == 0 and BotRoutines.action_timer.GetElapsedTime() == 0:
            return False
        return True

    @staticmethod
    def SetPendingAction(time: float = 1000):
        global bot_vars
        BotRoutines.action_check = time
        BotRoutines.action_timer.Reset()
    
    class Player:
        @staticmethod
        def sSendDialog(dialog_id):
            Log(f'Sending DialogID [{hex(dialog_id)}]')
            action_queue.add_action(Player.SendDialog, dialog_id)
            sleep(.5)

        @staticmethod
        def sSendChatCommand(command):
            Log(f'Sending chat command [{command}]')
            action_queue.add_action(Player.SendChatCommand, command)
            sleep(.5)

    class Move:
        @staticmethod
        def sFollowPath(path, do_func = None, stuck_func = None, stuck_time = 3000,
                        exit_func = lambda: False, rand = 50, extra_debug = ''):
            tolerance = 1.1*math.sqrt(rand**2 + rand**2)
            if extra_debug: extra_debug = f'{extra_debug} '
            starting_map_id = Map.GetMapID()
            for idx, (x, y) in enumerate(path):
                Log(f'Traversing {extra_debug}point [{idx + 1}/{len(path)}].')
                    
                rand_x = x + randint(-rand, rand)
                rand_y = y + randint(-rand, rand)

                timer = Timer()
                timer.Start()
                while Utils.Distance(Player.GetXY(), (rand_x, rand_y)) > tolerance:
                    if exit_func():                       return
                    if Agent.IsDead(Player.GetAgentID()): return
                    if Map.IsMapLoading():                return
                    if Map.GetMapID() != starting_map_id: return
                    
                    if callable(do_func):
                        Log('do_func')
                        do_func()
                        timer.Reset()

                    if Agent.IsMoving(Player.GetAgentID()):
                        timer.Reset()
                    else:
                        Log(f'Me: {Player.GetXY()}, Move: {(rand_x, rand_y)}, Dist: {Utils.Distance(Player.GetXY(), (rand_x, rand_y))}, Tol: {tolerance}')
                        action_queue.add_action(Player.Move, rand_x, rand_y)
                        sleep(.2)

                    if timer.HasElapsed(stuck_time):
                        if callable(stuck_func):
                            Log('stuck_func')
                            stuck_func()
                        else:
                            Log('stuck_func')
                            continue
                    
                    sleep(.1)

        @staticmethod
        def sZone(path, map_id):
            Log(f'Zoning to {Map.GetMapName(map_id)} MapID [{map_id}].')

            BotRoutines.Move.sFollowPath(path)
            BotRoutines.Maps.sWaitForArrival(map_id)

        @staticmethod
        def aFollowPath(path_handler,follow_handler):
            return Routines.Movement.FollowPath(path_handler,follow_handler)
        
        @staticmethod
        def aPathFinished(path_handler,follow_handler):
            return Routines.Movement.IsFollowPathFinished(path_handler, follow_handler)
        
    class Maps:
        @staticmethod
        def sSetMode(mode = 0):
            if mode:
                Log(f'Setting Hard Mode.')
                Party.SetHardMode()
            else:
                Log(f'Setting Normal Mode.')
                Party.SetNormalMode()
            sleep(.1)

        @staticmethod
        def sWaitForArrival(map_id):
            while not (Map.IsMapReady() and Map.GetMapID() == map_id and Party.IsPartyLoaded()):
                sleep(.5)
            Log(f'Arrived at {Map.GetMapName(map_id)} - MapID [{map_id}].')
            sleep(2)

        @staticmethod
        def sTravel(map_id):
            if not Map.IsOutpost() or (Map.GetMapID() != map_id):
                Log(f'Travelling to {Map.GetMapName(map_id)} - MapID [{map_id}].')
                action_queue.add_action(Map.Travel, map_id)
                    
                BotRoutines.Maps.sWaitForArrival(map_id)

        @staticmethod
        def sResignAndReturn(map_id):
            BotRoutines.Player.sSendChatCommand('resign')
            while not Party.IsPartyDefeated():
                sleep(.5)
            Log(f'Returning to {Map.GetMapName(map_id)} - MapID [{map_id}].')
            action_queue.add_action(Party.ReturnToOutpost)
            BotRoutines.Maps.sWaitForArrival(map_id)
            sleep(2)

        @staticmethod
        def aTravel(map_id):
            if Map.IsMapReady():
                if not Map.IsOutpost() or (Map.GetMapID() != map_id):
                    Log(f'Travelling to {Map.GetMapName(map_id)} - MapID [{map_id}].')
                    Map.Travel(map_id)
                    return

        @staticmethod
        def aArrived(map_id,):
            if Map.IsMapReady() and Map.GetMapID() == map_id and Party.IsPartyLoaded():
                Log(f'Arrived at {Map.GetMapName(map_id)} - MapID [{map_id}].')
                return True
            return False

    class Agents:



class SynchronousRoutines:



    class Skills:
        @staticmethod
        def LoadSkillBar(template):
            Log(f'Loading skill template [{template}]')
            action_queue.add_action(SkillBar.LoadSkillTemplate,template)
            sleep(.1)

        @staticmethod
        def ChangeWeaponSet(set,weapon_type = None):
            if Agent.IsDead(Player.GetAgentID()): return
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
        def CastSkill(slots, wait_for_aftercast = True):
            if not isinstance(slots, list):
                slots = [slots]

            for slot in slots:
                name = Skill.GetName(SkillBar.GetSkillIDBySlot(slot)).replace('_',' ')
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
                    sleep(SynchronousRoutines.Skills.GetAftercast(slot)/1000)

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
                    return effect.time_remaining
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
            Log(f'Changing target to {SynchronousRoutines.Agents.GetAgentName(agent_id)}AgentID [{agent_id}].')
            action_queue.add_action(Player.ChangeTarget, agent_id)
            while Player.GetTargetID() != agent_id:
                sleep(0.2)

        @staticmethod
        def TargetNearestNPC():
            Log(f'Changing target to nearest NPC.')
            action_queue.add_action(Keystroke.PressAndRelease, Key.V.value)
            sleep(0.2)

        @staticmethod
        def TargetNearestEnemy():
            Log(f'Changing target to nearest enemy.')
            action_queue.add_action(Keystroke.PressAndRelease, Key.C.value)
            sleep(0.2)

        @staticmethod
        def Interact(distance = None, frame_alias = '', timeout = 5000):
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
                filename = r'D:\Games\Guild Wars\Py4GW\my_bots\frame_aliases.json'
                while not int(UIManager.GetFrameIDByCustomLabel(filename = filename,frame_label = frame_alias)):
                    if timer.GetElapsedTime() > timeout:
                        break
                    sleep(.2)

    class Maps:
        

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
                Log(f'Idenfiying {SynchronousRoutines.Items.GetItemName(item_id)}ItemID [{item_id}] in slot [{bag},{slot}].')

                action_queue.add_action(Inventory.IdentifyItem, item_id, kit_id)

                while item_id == Inventory.GetFirstUnidentifiedItem():
                    sleep(.1)

                item_id = Inventory.GetFirstUnidentifiedItem()
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
                Log(f'Salvaging {SynchronousRoutines.Items.GetItemName(item_id)}ItemID [{item_id}] in slot [{bag},{slot}].')

                action_queue.add_action(Inventory.SalvageItem, item_id, kit_id)
                while item_id == Inventory.GetFirstSalvageableItem():
                    sleep(.1)
                    if quantity != Item.Properties.GetQuantity(item_id):
                        break
                    if Item.Rarity.IsPurple(item_id) or Item.Rarity.IsGold(item_id):
                        Log('Handling Salvage UI.')
                        action_queue.add_action(Inventory.AcceptSalvageMaterialsWindow)
                        sleep(.1)

                item_id = Inventory.GetFirstSalvageableItem()
            Log('Salvage loop complete.')

        @staticmethod
        def Sell(sell_list = None):
            if not sell_list:
                return

            item_id = sell_list[0]
            while sell_list:
                bag, slot = Inventory.FindItemBagAndSlot(item_id)
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
                    Log(f'Sorting "{Item.GetName(item_id)}" - ItemID [{item_id}] in slot [{item_bag},{item_slot}] to slot [{sort_bag},{sort_slot}].')
                    action_queue.add_action(Inventory.MoveItem,item_id, sort_bag, sort_slot, Item.Properties.GetQuantity(item_id))
                sort_position += 1
            if continue_sort:
                SynchronousRoutines.Items.Sort(False)
            else:
                Log('Sort loop complete')

        @staticmethod
        def ProcessInventory(sell_func = None):
            if callable(sell_func):
                SynchronousRoutines.Items.Identify()
                SynchronousRoutines.Items.Salvage()
                SynchronousRoutines.Items.Sell(sell_func())
                SynchronousRoutines.Items.Sort()
            else:
                Log('A sell list function is required to process your inventory.', msg_type = 'Notice')

        @staticmethod
        def LogInventory(item_ids = None):
            counts = {}
            if item_ids:
                for item_id in item_ids:
                    if item_id == 'gold':
                        counts[item_id] = Inventory.GetGoldOnCharacter()
                    elif item_id == 'salv':
                        salvageables = ItemArray.GetItemArray(ItemArray.CreateBagList(1,2,3,4))
                        salvageables = ItemArray.Filter.ByCondition(salvageables, lambda item_id: Item.Usage.IsSalvageable(item_id))
                        counts[item_id] = len(salvageables)
                    else:
                        counts[item_id] = Inventory.GetModelCount(item_id)
            return counts

        @staticmethod
        def Loot(loot_list = None):
            if not loot_list:                     return
            if Agent.IsDead(Player.GetAgentID()): return

            agent_id = loot_list[0]
            while loot_list:
                Log(f'Picking up {SynchronousRoutines.Agents.GetAgentName(agent_id)}AgentID [{agent_id}].')

                SynchronousRoutines.Agents.ChangeTarget(agent_id)
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
            Log('Loot loop complete.')

class AsyncRoutines:

    class Agents:
        @staticmethod
        def TargetNearestNPC():
            Log(f'Changing target to nearest NPC.')
            Keystroke.PressAndRelease(Key.V.value)

        @staticmethod
        def TargetNearestEnemy():
            Log(f'Changing target to nearest enemy.')
            Keystroke.PressAndRelease(Key.C.value)

        @staticmethod
        def Interact(distance = None, frame_alias = '', timeout = 5000):
            Log(f'Interacting with target.')
            Keystroke.PressAndRelease(Key.Space.value)

        @staticmethod
        def CheckUIFrame(frame_alias = ''):
            filename = r'D:\Games\Guild Wars\Py4GW\my_bots\frame_aliases.json'
            return bool(int(UIManager.GetFrameIDByCustomLabel(filename = filename,frame_label = frame_alias)))

    class Skills:
        @staticmethod
        def LoadSkillBar(template):
            SkillBar.LoadSkillTemplate(template)

        @staticmethod
        def ChangeWeaponSet(set):
            global bot_vars

            if AsyncRoutines.ActionIsPending(): return

            Log(f'Equipping weapon set [{set}].')

            if   set == 1: Keystroke.PressAndRelease(Key.F1.value)
            elif set == 2: Keystroke.PressAndRelease(Key.F2.value)
            elif set == 3: Keystroke.PressAndRelease(Key.F3.value)
            elif set == 4: Keystroke.PressAndRelease(Key.F4.value)

            AsyncRoutines.SetPendingAction(300)

        @staticmethod
        def CastSkill(slot):
            global bot_vars

            name = Skill.GetName(SkillBar.GetSkillIDBySlot(slot)).replace('_',' ')
            Log(f'Casting "{name}" in slot [{slot}].')

            if   slot == 1: Keystroke.PressAndRelease(Key.One.value)
            elif slot == 2: Keystroke.PressAndRelease(Key.Two.value)
            elif slot == 3: Keystroke.PressAndRelease(Key.Three.value)
            elif slot == 4: Keystroke.PressAndRelease(Key.Four.value)
            elif slot == 5: Keystroke.PressAndRelease(Key.Five.value)
            elif slot == 6: Keystroke.PressAndRelease(Key.Six.value)
            elif slot == 7: Keystroke.PressAndRelease(Key.Seven.value)
            elif slot == 8: Keystroke.PressAndRelease(Key.Eight.value)

            AsyncRoutines.SetPendingAction(AsyncRoutines.Skills.GetAftercast(slot))

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
            return max(activation*1000 + aftercast*1000 + Py4GW.PingHandler().GetCurrentPing() + 50,500)
        
        @staticmethod
        def EffectTimeRemaining(skill_id):
            for effect in Effects.GetEffects(Player.GetAgentID()):
                if effect.skill_id == skill_id:
                    return effect.time_remaining
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

            return AsyncRoutines.Skills.GetEnergyAgentCost(slot) <= energy_points

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

def Log(message, title = 'STATUS', msg_type = 'Info'):
    py4gw_msg_type = Py4GW.Console.MessageType.Debug
    if   msg_type == 'Log':       py4gw_msg_type = Py4GW.Console.MessageType.Debug
    elif msg_type == 'Error':       py4gw_msg_type = Py4GW.Console.MessageType.Error
    elif msg_type == 'Info':        py4gw_msg_type = Py4GW.Console.MessageType.Info
    elif msg_type == 'Notice':      py4gw_msg_type = Py4GW.Console.MessageType.Notice
    elif msg_type == 'Performance': py4gw_msg_type = Py4GW.Console.MessageType.Performance
    elif msg_type == 'Success':     py4gw_msg_type = Py4GW.Console.MessageType.Success
    elif msg_type == 'Warning':     py4gw_msg_type = Py4GW.Console.MessageType.Warning
    Py4GW.Console.Log(title, str(message), py4gw_msg_type)

def Debug(message, title = 'DEBUG', msg_type = 'Log'):
    global debug
    if debug: Log(message, title, msg_type)