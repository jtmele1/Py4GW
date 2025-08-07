# region imports
from bot_routines import *
# endregion

# region globals
sq                           = SynchronousRoutines()
thread_manager               = MultiThreading(timeout = 5)
bot_vars                     = BotVariables()
bot_vars.gui.window_name     = 'Jaya Feather Farm'
bot_vars.gui.window_width    = 250
bot_vars.farm_item.name      = 'Feathers'
bot_vars.farm_item.model_id  = ModelID.Feather
bot_vars.farm_item.color     = [.9, .9, .9, 1]
bot_vars.loot.pickup_list    = {'Feathers'   : ModelID.Feather,
                                'Crests'     : ModelID.Feathered_Crest,
                                'Gold Coins' : 2511}
bot_vars.loot.dont_sell_list = [ModelID.Bone,
                                ModelID.Pile_Of_Glittering_Dust,
                                ModelID.Iron_Ingot,
                                ModelID.Feather,
                                ModelID.Identification_Kit,
                                ModelID.Salvage_Kit,
                                ModelID.Lockpick]
# endregion

# region classes
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
    global bot_vars

    SetStatus(bot_vars, 'Waiting for enemies.')
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
    global bot_vars

    SetStatus(bot_vars, 'Killing enemies.')
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
                break

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
    global bot_vars
    Run()
    enemy_array = AgentArray.GetEnemyArray()
    enemy_array = AgentArray.Filter.ByAttribute(enemy_array, 'IsAlive')
    enemy_array = AgentArray.Filter.ByCondition(enemy_array, lambda agent_id: Agent.GetPlayerNumber(agent_id) in [3944,3946,3948])
    enemy_array = AgentArray.Filter.ByDistance(enemy_array, Player.GetXY(), 800)
    if enemy_array:
        WaitForSettle()
        Kill()
        SetStatus(bot_vars, 'Looting.')
        sq.Items.Loot(bot_vars.loot.pickup_list.values())
        sq.Skills.ChangeWeaponSet(Build.staff)
        SetStatus(bot_vars, 'Continuing farm.')
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
            SetStatus(bot_vars, 'Setting up.')
            bot_vars.do_setup = False
            sq.Maps.Travel(Maps.seitung)
            sq.Skills.LoadSkillBar(Build.template)
            sq.Skills.CheckRequirements({'Scythe Mastery' : 10, 'Earth Prayers' : 16, 'Mysticism' : 10})
            sq.Maps.SetMode(0)
            sq.Move.Zone(ChoosePath(), Maps.jaya)
            sq.Move.Zone(Path.rezone, Maps.seitung)

        # inventory management
        if Inventory.GetModelCount(835) >= 50 or bot_vars.handle_inv:
            SetStatus(bot_vars, 'Handling inventory.')
            sq.Items.RequestInvNames()
            sq.Move.FollowPath(Path.merch)
            sq.Agents.TargetNearestNPC()
            sq.Agents.Interact(frame_alias = 'Merchant Window')
            inv_log = sq.Items.LogInventory(bot_vars.loot.pickup_list.values())
            sq.Items.ProcessInventory(bot_vars.loot.dont_sell_list)
            CatalogLoot(bot_vars, inv_log)
            if bot_vars.handle_inv:
                bot_vars.bot_started = False
                thread_manager.stop_all_threads()
                return
            
        # farm routine
        SetStatus(bot_vars, 'Leaving Jaya.')
        bot_vars.timers.lap.Start()
        sq.Skills.ChangeWeaponSet(Build.staff)
        sq.Move.Zone(Path.zone, Maps.jaya)
        inv_log = sq.Items.LogInventory(bot_vars.loot.pickup_list.values())
        SetStatus(bot_vars, 'Starting farm.')
        sq.Move.FollowPath(Path.farm, do_func = Farm, extra_status = '"Farm"')
        LogLap(bot_vars)
        CatalogLoot(bot_vars, inv_log)
        SetStatus(bot_vars, 'Resetting farm.')
        sq.Maps.ResignAndReturn(Maps.seitung)
# endregion

# region main
def main():
    global bot_vars, action_queue, thread_manager

    try:
        if bot_vars.bot_started:
            thread_manager.update_all_keepalives()

        if not Map.IsMapReady() or not Party.IsPartyLoaded(): return

        Draw(bot_vars, thread_manager, SynchronousLogic)

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