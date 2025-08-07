# region imports
from bot_routines import *
# endregion

# region globals
sq                           = SynchronousRoutines()
thread_manager               = MultiThreading(timeout = 5)
bot_vars                     = BotVariables()
bot_vars.gui.window_name     = 'Drazach Fiber Farm'
bot_vars.farm_item.name      = 'Fiber'
bot_vars.farm_item.model_id  = ModelID.Plant_Fiber
bot_vars.farm_item.color     = [.89, .85, .79, 1]
bot_vars.loot.pickup_list    = {'Gold Coins' : ModelID.Gold_Coins, 
                                'Lockpicks'  : ModelID.Lockpick,
                                'Fiber'      : ModelID.Plant_Fiber,
                                'Roots'      : ModelID.Dragon_Root,
                                'Rubies'     : ModelID.Ruby}
bot_vars.loot.dont_sell_list = [ModelID.Bone,
                                ModelID.Pile_Of_Glittering_Dust,
                                ModelID.Iron_Ingot,
                                ModelID.Feather,
                                ModelID.Plant_Fiber,
                                ModelID.Ruby,
                                ModelID.Identification_Kit,
                                ModelID.Salvage_Kit,
                                ModelID.Lockpick]
# endregion

# region classes
class Path:
    zone   = [(-11125, -23457)]
    rezone = [(-11376, 20383)]
    merch  = [(-10652, -20586)]
    aggro  = [(-8172, 18404),(-6669, 17233),(-5429, 15821),(-6252, 17643)]
    kill   = [(-6091, 17962),(-6341, 18158)]
    
class Maps:
    sas = 349
    dt  = 195

class Build:
    # template
    template = 'OwJSg5PT8I6MHQ/a3lPH4OCH'
    # weapon slots
    sword = 1
    # skills
    dp  = 1 # deadly paradox
    sf  = 2 # shadow form
    sod = 3 # shroud of distress
    ns  = 4 # natural stride
    ds  = 5 # dwarven stability
    w   = 6 # winnowing
    dc  = 7 # death's charge
    wd  = 8 # whirling defence
# endregion

# region combat functions
def Run():
    agent_array = AgentArray.GetEnemyArray()
    agent_array = AgentArray.Filter.ByDistance(agent_array, Player.GetXY(), 900)

    if agent_array and sq.Skills.IsRecharged(Build.sf):
        sq.Skills.CastSkill([Build.dp, Build.sf])

    if sq.Skills.HasEffect(Build.sf) and not sq.Skills.HasEffect(Build.ns):
        sq.Skills.CastSkill(Build.ns)

def TargetsInRange(range = 1000.0, model_ids = None):
    enemy_array = AgentArray.GetEnemyArray()
    enemy_array = AgentArray.Filter.ByAttribute(enemy_array, 'IsAlive')
    if model_ids:
        if not isinstance(model_ids, list):
            model_ids = [model_ids]
        enemy_array = AgentArray.Filter.ByCondition(enemy_array, lambda agent_id: Agent.GetPlayerNumber(agent_id) in model_ids)
    enemy_array = AgentArray.Filter.ByDistance(enemy_array, Player.GetXY(), range)
    return enemy_array

def Prep():
    sq.Skills.CastSkill([Build.sod, Build.ds])
    sleep(.5)
    sq.Skills.CastSkill(Build.ns)

def Kill():
    sq.Skills.CastSkill(Build.w)
    while not sq.Skills.IsRecharged(Build.sf) or not sq.Skills.IsRecharged(Build.ds):
        if Agent.IsDead(Player.GetAgentID()):
            return
        sleep(.5)
    sq.Skills.CastSkill([Build.sf, Build.ds])
    
    agent_array = AgentArray.GetEnemyArray()
    agent_array = AgentArray.Sort.ByDistance(agent_array, (-5832,16688))
    if len(agent_array) > 0:
        Player.ChangeTarget(agent_array[0])
        sleep(.5)

    sq.Skills.CastSkill(Build.dc)
    while sq.Skills.IsRecharged(Build.dc):
        if Agent.IsDead(Player.GetAgentID()):
            return
        sleep(.1)
    sq.Skills.CastSkill(Build.wd)

    while TargetsInRange(Range.Adjacent.value, 3722):
        if Agent.IsDead(Player.GetAgentID()):
            return
        sleep(1)
# endregion

# region synchronous functions
def SynchronousLogic():
    global bot_vars

    while True:
        if not bot_vars.bot_started:
            sleep(1)
            continue

        # setup routine
        if (bot_vars.do_setup or Map.GetMapID() != Maps.sas) and not bot_vars.handle_inv:
            SetStatus(bot_vars, 'Setting up.')
            bot_vars.do_setup = False
            sq.Maps.Travel(Maps.sas)
            sq.Skills.LoadSkillBar(Build.template)
            sq.Skills.CheckRequirements({'Shadow Arts' : 16, 'Wilderness Survival' : 12})
            sq.Maps.SetMode(1)
            sq.Move.Zone(Path.zone, Maps.dt)
            sq.Move.Zone(Path.rezone, Maps.sas)

        # inventory management
        if Inventory.GetModelCount(ModelID.Dragon_Root) >= 50 or bot_vars.handle_inv:
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
        SetStatus(bot_vars, 'Leaving outpost.')
        bot_vars.timers.lap.Start()
        sq.Move.Zone(Path.zone, Maps.dt)
        SetStatus(bot_vars, 'Aggroing enemies.')
        Prep()
        sq.Move.FollowPath(Path.aggro, rand = 15, do_func = Run)
        sleep(1)
        sq.Move.FollowPath([Path.kill[0]], rand = 5)
        sleep(1)
        sq.Move.FollowPath([Path.kill[1]], rand = 5)
        SetStatus(bot_vars, 'Killing enemies.')
        Kill()
        SetStatus(bot_vars, 'Looting items.')
        inv_log = sq.Items.LogInventory(bot_vars.loot.pickup_list.values())
        sq.Items.Loot(bot_vars.loot.pickup_list.values())
        LogLap(bot_vars)
        CatalogLoot(bot_vars, inv_log)
        SetStatus(bot_vars, 'Resetting farm.')
        sq.Maps.ResignAndReturn(Maps.sas)
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