# region imports
from _bot_routines import *
# endregion

# region globals
initialized              = False
bot_funcs                = BotRoutines()
bot_vars                 = BotVariables()
bot_vars.gui.window_name = 'LDoA Hamnet Farm'

# endregion

# region classes
class Path:
    zone   = [(-19085, 17960)]
    rezone = [(-19665, -8045)]
    kill   = [(-15525, -8923), (-15737,-9093)]

class Maps:
    foibles = 165
    folly   = 560

class Build:
    # template
    template = 'OgATYDclzQx+m2AAAAAAAAA'
    # skills
    ps = 1
    tu = 2
# endregion

# region combat functions
def Kill():
    while True:
        yield from wait(.2)

        if Agent.GetHealth(Player.GetAgentID()) < 0.3: 
            break

        # check for enemies
        enemy_array = AgentArray.GetEnemyArray()
        enemy_array = AgentArray.Filter.ByAttribute(enemy_array, 'IsAlive')
        enemy_array = AgentArray.Filter.ByCondition(enemy_array, lambda agent_id: Agent.GetLevel(agent_id) > 5)

        if not enemy_array:
            break

        # select target
        if not Player.GetTargetID():
            bot_funcs.Agents.TargetNearestEnemy()
            continue

        # attack
        if not Agent.IsAttacking(Player.GetAgentID()) and Player.GetTargetID():
            yield from bot_funcs.Agents.Interact()
            continue
        
        # cast power shot
        if bot_funcs.Skills.IsRecharged(Build.ps) and bot_funcs.Skills.GetEnergy() > 15:
            bot_funcs.Skills.CastSkill(Build.ps, min_aftercast = 1000)
            continue

        # cast troll unguent
        if bot_funcs.Skills.IsRecharged(Build.tu) and Agent.GetHealth(Player.GetAgentID()) < 0.9:
            bot_funcs.Skills.CastSkill(Build.tu, min_aftercast = 1000)
            continue
# endregion

# region sequential functions
def BotLogic():
    global bot_vars

    while True:
        if not bot_vars.bot_started:
            yield from wait(1)
            continue

        # setup routine
        if (bot_vars.do_setup or Map.GetMapID() != Maps.foibles):
            SetStatus(bot_vars, 'Setting up.')
            bot_vars.do_setup = False
            yield from bot_funcs.Maps.Travel(Maps.foibles)
            yield from bot_funcs.Skills.LoadSkillBar(Build.template)
            yield from bot_funcs.Move.Zone(Path.zone, Maps.folly)
            yield from bot_funcs.Move.Zone(Path.rezone, Maps.foibles)
            
        # farm routine
        SetStatus(bot_vars, 'Leaving Foible\'s.')
        bot_vars.timers.lap.Start()
        yield from bot_funcs.Move.Zone(Path.zone, Maps.folly)
        SetStatus(bot_vars, 'Moving to enemies.')
        yield from bot_funcs.Move.FollowPath(Path.kill)
        SetStatus(bot_vars, 'Waiting for enemies.')
        yield from Kill()
        SetStatus(bot_vars, 'Looting items.')
        inv_log = bot_funcs.Items.LogInventory(bot_vars.loot.pickup_list.keys())
        LogLap(bot_vars, inv_log)
        yield from bot_funcs.Maps.ResignAndReturn(Maps.foibles)
        SetStatus(bot_vars, 'Resetting farm.')
# endregion

# region main
def main():
    global bot_vars, initialized

    try:
        if not initialized:
            bot_vars.Reset()
            initialized = True

        if not Map.IsMapReady() or not Party.IsPartyLoaded():
            return

        Draw(bot_vars, BotLogic)

        for coroutine in coroutines[:]:
            try:
                next(coroutine)
            except StopIteration:
                coroutines.remove(coroutine)
        
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