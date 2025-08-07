# region imports
from _bot_routines import *
# endregion

# region globals
initialized                  = False
bot_funcs                    = BotRoutines()
bot_vars                     = BotVariables()
bot_vars.gui.window_name     = 'Curtain Dust Farm'
bot_vars.farm_item.name      = 'Dust'
bot_vars.farm_item.model_id  = ModelID.Pile_Of_Glittering_Dust
bot_vars.farm_item.color     = [.89, .85, .79, 1]
bot_vars.loot.pickup_list    = {ModelID.Pile_Of_Glittering_Dust : ('Dust'    , True),
                                ModelID.Shadowy_Remnant         : ('Remnants', True)}
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
    zone   = [(-5096, 16560),(-5200, 16000)]
    rezone = [(-5124, 16439)]
    merch  = [(-5034, 19329)]
    farm   = [(-6854, 14613),(-7761, 12286),(-6228, 7567),(-4783, 6108),
              (-2103, 3318),(2872, 273),(6008, -1207),(7653, -2127),
              (7348, -3619),(10026, -6060),(12097, -7507),(12769, -4257),
              (12857, 364),(12519, 1257),(10434, 1086)]
    
class Maps:
    toa     = 138
    curtain = 18

class Build:
    # template
    template = 'OgCjkirMrSmXfbDYqifXsX7X9gA'
    # weapon slots
    scythe = 1
    staff  = 2
    # skills
    ss  = 1
    vos = 2
    cv  = 3
    dm  = 4
    mv  = 5
    mr  = 6
    ia  = 7
    ea  = 8
# endregion

# region combat functions
def InDangerZone():
    if Agent.IsDead(Player.GetAgentID()): return
    if Agent.GetHealth(Player.GetAgentID()) < 0.7: return

def TargetsInRange(range = 1000, model_ids = None):
    enemy_array = AgentArray.GetEnemyArray()
    enemy_array = AgentArray.Filter.ByAttribute(enemy_array, 'IsAlive')
    if model_ids:
        if not isinstance(model_ids, list):
            model_ids = [model_ids]
        enemy_array = AgentArray.Filter.ByCondition(enemy_array, lambda agent_id: Agent.GetPlayerNumber(agent_id) in model_ids)
    enemy_array = AgentArray.Filter.ByDistance(enemy_array, Player.GetXY(), range)
    return enemy_array

def FindAloe(range = 1200):
    enemy_array = TargetsInRange(range, model_ids = [1731])
    enemy_array = AgentArray.Sort.ByDistance(enemy_array, Player.GetXY())
    if enemy_array:
        return enemy_array[0]

    return False

def Run():
    for skill in [Build.ea, Build.dm]:
        if not bot_funcs.Skills.HasEffect(skill) and bot_funcs.Skills.IsRecharged(skill):
            yield from bot_funcs.Skills.CastSkill(skill)

    if Agent.GetHealth(Player.GetAgentID()) < .95:
        if not bot_funcs.Skills.HasEffect(Build.mr) and bot_funcs.Skills.IsRecharged(Build.mr):
            yield from bot_funcs.Skills.CastSkill(Build.mr)

    if len(TargetsInRange(800, model_ids = [1729])) >= 2:
        Keystroke.PressAndRelease(Key.S.value)
        yield from wait(.1)

def WaitForSettle():
    global bot_vars

    SetStatus(bot_vars, 'Waiting for enemies.')
    timer = Timer()
    timer.Start()
    while True:
        if InDangerZone():          return
        if timer.HasElapsed(10000): return

        # wait for foes to ball
        enemy_array = TargetsInRange(800, model_ids = [1729])
        enemy_array = AgentArray.Sort.ByDistance(enemy_array, Player.GetXY(), descending = True)
        if not enemy_array:
            return
        
        if Utils.Distance(Player.GetXY(),Agent.GetXY(enemy_array[0])) <= Range.Adjacent.value:
            return
        
        # move to aloe if one exists
        aloe = TargetsInRange(1000, model_ids = [1731])
        if aloe:
            x, y = Agent.GetXY(aloe[0])
            if Utils.Distance(Player.GetXY(), (x, y)) > Range.Adjacent.value:
                if not Agent.IsMoving(Player.GetAgentID()):
                    yield from bot_funcs.Move.FollowPath((x, y), stuck_func = lambda: True, stuck_time = 1500)

        # maintain mystic regen and mystic vigor
        for skill in [Build.ea, Build.ia, Build.mr, Build.mv, Build.ss, Build.vos]:
            if not bot_funcs.Skills.HasEffect(skill) and bot_funcs.Skills.IsRecharged(skill):
                yield from bot_funcs.Skills.CastSkill(skill)
                continue

        yield from wait(.5)

def Kill():
    global bot_vars

    SetStatus(bot_vars, 'Killing enemies.')
    yield from bot_funcs.Skills.ChangeWeaponSet(Build.scythe, 'Scythe')
    # kill remaining foes
    while True:
        if Agent.IsDead(Player.GetAgentID()):
            return

        # check for remaming enemies
        if not TargetsInRange(800, model_ids = [1729]):
            return

        # maintain mystic regen , mystic vigor, conviction, and vos
        for skill in [Build.ea, Build.ia, Build.mr, Build.mv, Build.ss, Build.vos]:
            if not bot_funcs.Skills.HasEffect(skill) and bot_funcs.Skills.IsRecharged(skill):
                yield from bot_funcs.Skills.CastSkill(skill)
                break
        
        # select target
        target_id = Player.GetTargetID()
        if target_id == 0 or Agent.GetAllegiance(target_id)[0] != 3 or Agent.IsDead(target_id):
            yield from bot_funcs.Agents.TargetNearestEnemy()

        # cast chilling victory
        if bot_funcs.Skills.HasEnoughAdrenaline(Build.cv):
            yield from bot_funcs.Skills.CastSkill(Build.cv)

        # attack
        if not Agent.IsAttacking(Player.GetAgentID()):
            yield from bot_funcs.Agents.Interact()

        yield from wait(1)

def Farm():
    global bot_vars

    yield from Run()
    if TargetsInRange(800, model_ids = [1729]):
        yield from WaitForSettle()
        yield from Kill()
        SetStatus(bot_vars, 'Looting.')
        yield from bot_funcs.Items.Loot(bot_vars.loot.pickup_list.keys())
        yield from bot_funcs.Skills.ChangeWeaponSet(Build.staff)
        SetStatus(bot_vars, 'Continuing farm.')
# endregion

# region synchronous functions
def BotLogic():
    global bot_vars

    while True:
        if not bot_vars.bot_started:
            yield from wait(1)
            continue

        # setup routine
        if (bot_vars.do_setup or Map.GetMapID() != Maps.toa) and not bot_vars.handle_inv:
            SetStatus(bot_vars, 'Setting up.')
            bot_vars.do_setup = False
            yield from bot_funcs.Maps.Travel(Maps.toa)
            yield from bot_funcs.Skills.LoadSkillBar(Build.template)
            bot_funcs.Skills.CheckRequirements({'Scythe Mastery' : 9, 'Earth Prayers' : 16, 'Mysticism' : 11})
            yield from bot_funcs.Maps.SetMode(0)
            yield from bot_funcs.Move.Zone(Path.zone, Maps.curtain)
            yield from bot_funcs.Move.Zone(Path.rezone, Maps.toa)

        # inventory management
        if Inventory.GetModelCount(441) >= 50 or bot_vars.handle_inv:
            SetStatus(bot_vars, 'Handling inventory.')
            yield from bot_funcs.Items.RequestInvNames()
            yield from bot_funcs.Move.FollowPath(Path.merch)
            yield from bot_funcs.Agents.TargetNearestNPC()
            yield from bot_funcs.Agents.Interact(frame_alias = 'Merchant Window')
            inv_log = bot_funcs.Items.LogInventory(bot_vars.loot.pickup_list.keys())
            yield from bot_funcs.Items.ProcessInventory(bot_vars.loot.dont_sell_list)
            LogLoot(bot_vars, inv_log)
            if bot_vars.handle_inv:
                bot_vars.bot_started = False
                return
            
        # farm routine
        SetStatus(bot_vars, 'Leaving ToA.')
        bot_vars.timers.lap.Start()
        yield from bot_funcs.Skills.ChangeWeaponSet(Build.staff)
        yield from bot_funcs.Move.Zone(Path.zone, Maps.curtain)
        inv_log = bot_funcs.Items.LogInventory(bot_vars.loot.pickup_list.keys())
        SetStatus(bot_vars, 'Starting farm.')
        yield from bot_funcs.Move.FollowPath(Path.farm, do_func = Farm, extra_status = '"Farm"')
        LogLap(bot_vars, inv_log)
        SetStatus(bot_vars, 'Resetting.')
        yield from bot_funcs.Maps.ResignAndReturn(Maps.toa)
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