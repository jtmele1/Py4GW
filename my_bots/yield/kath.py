# region imports
from Py4GWCoreLib import *
import _bot_routines
import importlib 
importlib.reload(_bot_routines)
from _bot_routines import *
# endregion

# region globals
initialized              = False
bot_funcs                = BotRoutines()
bot_vars                 = BotVariables()
bot_vars.gui.window_name = 'Kathandrax Runner'
# endregion

# region classes
class Path:
    lvl1      = [(18018.15, -18110.99),
                 (18090.47,-13629.70),
                 (16467.34,-11775.57),
                 (17001.40,-9018.28),
                 (15475.53,-7503.77),
                 (12357.95,-8971.77),
                 (10706.84,-6124.61),
                 (8484.29,-4318.46),
                 (6985.80,32.63),
                 (4719.98,2777.21)] # tight   3747.00 2744.00 target loc
    lvl2      = [(14690.12, -958.41),
                 (13067.56,-795.03),
                 (10068.56,-1029.61),
                 (10941.11,-2893.57),
                 (10018.60,-6056.97),
                 (8371.82,-8533.96),
                 (4865.58,-10246.96),
                 (3032.42,-11571.11),
                 (1115.19,-11240.37)]  # target -25.40,  -11176.63
    lvl3_key  = [(-14390.21, 10646.68)]
    lvl3_boss = [(-14390.21, 10646.68)]

class Maps:
    lvl1 = 570
    lvl2 = 571
    lvl3 = 676

class Build:
    # template
    template = 'OwBS85OTHQ6M0kri7iIQ4OdO'
    # skills
    shroud = 1
    sf     = 2
    iau    = 3
    gdw    = 4
    evas   = 5
    hos    = 6
    dc     = 7
    re     = 8

    class Effects:
        shroud = 1031
        sf     = 826
        iau    = 2356
        gdw    = 2219
        re     = 925
# endregion

# region combat functions
def WaitForCons():
    while not bot_funcs.Skills.EffectTimeRemaining(2522):
        yield from wait(0.1)

def PickUpKey():
    yield from bot_funcs.Items.Loot([25410])

def MaintainSF():
    if bot_funcs.Skills.EffectTimeRemaining(Build.Effects.shroud) < 10:
        yield from bot_funcs.Skills.CastSkill(Build.shroud)

    if bot_funcs.Skills.EffectTimeRemaining(Build.Effects.sf) < 4:
        yield from bot_funcs.Skills.CastSkill(Build.sf)

    if bot_funcs.Skills.EffectTimeRemaining(Build.Effects.sf) < 8:
        yield from bot_funcs.Skills.CastSkill(Build.iau)

def KillBoss(type):
    enemy_array = AgentArray.GetEnemyArray()
    enemy_array = AgentArray.Filter.ByAttribute(enemy_array, 'IsAlive')
    
    match type:
        case 'wurm':
            yield from bot_funcs.Agents.TargetNearestEnemyToCoords(3747, 2744)
            yield from bot_funcs.Skills.CastSkill(Build.dc)
        case 'regent':
            enemy_array = AgentArray.Filter.ByCondition(enemy_array, lambda agent_id: Agent.GetPlayerNumber(agent_id) == 6907)
            if enemy_array and enemy_array[0]:
                Player.ChangeTarget(enemy_array[0])
                yield from bot_funcs.Skills.CastSkill(Build.dc)
        case 'djinn':
            enemy_array = AgentArray.Filter.ByCondition(enemy_array, lambda agent_id: Agent.GetPlayerNumber(agent_id) == 6813)
            if enemy_array and enemy_array[0]:
                Player.ChangeTarget(enemy_array[0])
                yield from bot_funcs.Skills.CastSkill(Build.dc)
        case 'ilsundur':
            yield from bot_funcs.Agents.TargetNearestEnemy()

    yield from bot_funcs.Skills.ChangeWeaponSet(1)

    while True:
        if Agent.IsDead(Player.GetAgentID()):
            return
        
        yield from MaintainSF()

        target_id = Player.GetTargetID()

        # check for target death
        if not target_id:
            break

        # cast evas
        if bot_funcs.Skills.IsRecharged(Build.evas):
            yield from bot_funcs.Skills.CastSkill(Build.evas)
            continue

        # attack
        if not Agent.IsAttacking(Player.GetAgentID()) and target_id:
            yield from bot_funcs.Agents.Interact()
            continue

        yield from wait(0.2)

    yield from bot_funcs.Skills.ChangeWeaponSet(2)
# end region

# region bot logic
def BotLogic():
    while True:
        # Curse of the Nornbear
        match Map.GetMapID():
            # Curse of the Nornbear
            case Maps.lvl1:
                yield from bot_funcs.Skills.ChangeWeaponSet(2)
                yield from WaitForCons()
                yield from bot_funcs.Move.FollowPath(Path.lvl1[:-1], do_func = MaintainSF, rand = 200)
                yield from bot_funcs.Move.FollowPath(Path.lvl1[-1],  do_func = MaintainSF, rand = 10)
                yield from KillBoss('wurm')
                yield from PickUpKey()
                while Map.GetMapID() == Maps.lvl1:
                    yield from wait(1)
                bot_funcs.Maps.WaitForArrival(Maps.lvl2)
            case Maps.lvl2:
                yield from bot_funcs.Skills.ChangeWeaponSet(2)
                yield from WaitForCons()
                yield from bot_funcs.Move.FollowPath(Path.lvl2, do_func = MaintainSF, rand = 200)
                yield from KillBoss('regent')
                yield from PickUpKey()
                while Map.GetMapID() == Maps.lvl2:
                    yield from wait(1)
                bot_funcs.Maps.WaitForArrival(Maps.lvl3)
            

        yield from wait(1)
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