# region imports
from _bot_routines import *
# endregion

# region globals
initialized                  = False
bot_funcs                    = BotRoutines()
bot_vars                     = BotVariables()
bot_vars.gui.window_name     = 'Vaettir Farm'
bot_vars.farm_item.name      = 'Grog'
bot_vars.farm_item.model_id  = ModelID.Bottle_Of_Grog
bot_vars.farm_item.color     = [.32, .66, .75, 1]
bot_vars.loot.pickup_list    = {ModelID.Glacial_Stone          : ('Glacial Stones', True),
                                ModelID.Bottle_Of_Grog         : ('Grog', True),
                                ModelID.Gold_Coins             : ('Gold Coins'    , False),
                                ModelID.Wayfarer_Mark          : ('Wayfaerer\'s Marks', True),
                                #'salvageables'                 : ('Salvageables'  , True),
                                ModelID.Map_Piece_Bottom_Left  : ('BL Map Piece'  , False),
                                ModelID.Map_Piece_Bottom_Right : ('BR Map Piece'  , False),
                                ModelID.Map_Piece_Top_Left     : ('TL Map Piece'  , False),
                                ModelID.Map_Piece_Top_Right    : ('TR Map Piece'  , False)}
# endregion

# region classes
class Path:
    zone   = [(-24492, 14938),(-26678, 16325)]
    bjora  = [( 15003,-16598),( 15003,-16598),( 12699,-14589),( 11628,-13867),( 10891,-12989),( 10517,-11229),
              ( 10209, -9973),(  9296, -8811),(  7815, -7967),(  6266, -6328),(  4940, -4655),(  3867, -2397),
              (  2279, -1331),(     7, -1072),( -1752, -1209),( -3596, -1671),( -5386, -1526),( -6904,  -283),
              ( -7711,   364),( -9537,  1265),(-11141,   857),(-12730,   371),(-13379,    40),(-14925,  1099),
              (-16183,  2753),(-17803,  4439),(-18852,  5290),(-19250,  5431),(-19968,  5564),(-20404,  5637)]
    left   = [( 12496,-22600),( 11375,-22761),( 10925,-23466),( 10917,-24311),(  9910,-24599),(  8995,-23177),
              (  8307,-23187),(  8213,-22829),(  8307,-23187),(  8213,-22829),(  8740,-22475),(  8880,-21384),
              (  8684,-20833),(  8982,-20576)]
    right  = [( 10584,-20150),(  9976,-18338),( 11316,-18056),( 10392,-17512),( 10114,-16948),( 10729,-16273),
              ( 10810,-15058),( 11120,-15105),( 11670,-15457),( 12604,-15320),( 12476,-16157)]
    block  = [(12920, -17032),(12847, -17136),( 12720,-17222),( 12617,-17273),( 12480,-17304)]
    exit   = [( 15400,-20400),( 15850,-20550)]
    rezone = [(-20404,  5637)]
    
class Maps:
    long  = 650
    bjora = 482
    jaga  = 546

class Build:
    # template
    template = 'OwVUI2h5lPP8Id2BkAiAvpLBTAA'
    # weapon slots
    shield_set = 1
    # skills
    dp  = 1
    sf  = 2
    sod = 3
    wop = 4
    hos = 5
    wd  = 6
    ae  = 7
    ch  = 8

    class Effects:
        sf  = 826
        sod = 1031
        wop = 1028
        ch  = 38

    class IDs:
        wd = 1335
# endregion

# region combat functions
def Run():
    if Agent.GetHealth(Player.GetAgentID()) < .9:
        if not bot_funcs.Skills.HasEffect(Build.sf) and bot_funcs.Skills.IsRecharged(Build.sf):
            yield from bot_funcs.Skills.CastSkill([Build.dp, Build.sf])

    if Agent.GetHealth(Player.GetAgentID()) < .7:
        if not bot_funcs.Skills.HasEffect(Build.sod) and bot_funcs.Skills.IsRecharged(Build.sod):
            yield from bot_funcs.Skills.CastSkill(Build.sod)

    if Agent.GetHealth(Player.GetAgentID()) < .3:
        if bot_funcs.Skills.IsRecharged(Build.hos):
            yield from bot_funcs.Agents.TargetNearestEnemy()
            yield from bot_funcs.Skills.CastSkill(Build.hos)

def StayAlive():
    if not bot_funcs.Skills.CanCast(): return

    if bot_funcs.Skills.EffectTimeRemaining(Build.Effects.sf) <= 5 and bot_funcs.Skills.IsRecharged(Build.sf):
        yield from bot_funcs.Skills.CastSkill([Build.dp, Build.sf])
        return

    for skill in [Build.sod, Build.wop, Build.ch]:
        if bot_funcs.Skills.IsRecharged(skill):
            yield from bot_funcs.Skills.CastSkill(skill)
            return

def HandleStuck(destination: tuple):
    Log('Player is stuck.', msg_type = 'Warning')

    pos = Player.GetXY()
    reference_angle = math.atan2(destination[1] - pos[1], destination[0] - pos[0])

    timer = Timer()
    timer.Start()
    while True:
        # check deadlock
        if timer.HasElapsed(60000):
            Log('Cannot un-stuck - resetting.', msg_type = 'Error')
            if Agent.IsDead(Player.GetAgentID()):
                return True
            while Agent.IsAlive(Player.GetAgentID()):
                yield from wait(1)
        
        # check position
        pos_ = Player.GetXY()
        if Utils.Distance(pos, pos_) > 100:
            Log('Successfully un-stuck!', msg_type = 'Success')
            return False
        
        # skill routine
        yield from StayAlive()

        # HoS attempt
        if bot_funcs.Skills.IsRecharged(Build.hos):
            # select target
            min_angle = 2*math.pi
            agent_id = 0

            enemy_array = AgentArray.GetEnemyArray()
            enemy_array = AgentArray.Filter.ByDistance(enemy_array,Player.GetXY(),Range.Spellcast.value)

            for enemy in enemy_array:
                e_x, e_y = Agent.GetXY(enemy)
                angle = math.fabs(math.pi - math.fabs(reference_angle - (math.atan2(e_y - pos[1], e_x - pos[0]))))
                if angle < min_angle:
                    min_angle = angle
                    agent_id = enemy

            if not agent_id:
                yield from bot_funcs.Agents.TargetNearestEnemy()
            else:
                yield from bot_funcs.Agents.ChangeTarget(agent_id)

            yield from bot_funcs.Skills.CastSkill(Build.hos)

            # update reference angle for next attempt
            reference_angle += math.pi/3

        yield from wait(0.5)

def Aggro():
    enemy_array = AgentArray.GetEnemyArray()
    if not enemy_array:
        return
    
    enemy_array = AgentArray.Sort.ByDistance(enemy_array, Player.GetXY())
    
    if Utils.Distance(Player.GetXY(),Agent.GetXY(enemy_array[0])) >= 1.2*Range.Earshot.value:
        return

    yield from StayAlive()

def WaitForSettle():
    if Agent.IsDead(Player.GetAgentID()):
        return

    timer = Timer()
    timer.Start()
    while not timer.HasElapsed(20000):
        if Agent.IsDead(Player.GetAgentID()):
            return

        enemy_array = AgentArray.GetEnemyArray()
        if not enemy_array:
            break

        adjacent_array   = AgentArray.Filter.ByDistance(enemy_array,Player.GetXY(),Range.Adjacent.value)
        cast_array       = AgentArray.Filter.ByDistance(enemy_array,Player.GetXY(),Range.Spellcast.value)
        
        if len(adjacent_array) == len(cast_array):
            break

        yield from StayAlive()
        yield from wait(.1)

    timer.Reset()
    while not timer.HasElapsed(3000):
        if Agent.IsDead(Player.GetAgentID()):
            return

        yield from StayAlive()
        yield from wait(.1)

def SelectTarget():
    enemy_array = AgentArray.GetEnemyArray()
    enemy_array = AgentArray.Filter.ByCondition(enemy_array, lambda agent_id: Utils.Distance(Player.GetXY(), Agent.GetXY(agent_id)) <= 1.2*Range.Adjacent.value)
    enemy_array = AgentArray.Filter.ByAttribute(enemy_array, 'IsAlive')
    enemy_array = AgentArray.Filter.ByCondition(enemy_array, lambda agent_id: Agent.IsEnchanted(agent_id))
    enemy_array = AgentArray.Filter.ByCondition(enemy_array, lambda agent_id: not Agent.IsHexed(agent_id))
    if not enemy_array: return 0

    return enemy_array[0]

def Kill():
    yield from bot_funcs.Agents.TargetNearestEnemy()

    while bot_funcs.Skills.EffectTimeRemaining(Build.Effects.sf) < 10:
        yield from StayAlive()
        if Agent.IsDead(Player.GetAgentID()):
            return
        yield from wait(0.5)

    yield from bot_funcs.Skills.CastSkill(Build.ae)

    echoed = False
    while True:
        if Agent.IsDead(Player.GetAgentID()):
            return

        enemy_array = AgentArray.GetEnemyArray()
        enemy_array = AgentArray.Filter.ByAttribute(enemy_array, 'IsAlive')
        enemy_array = AgentArray.Filter.ByCondition(enemy_array, lambda agent_id: Utils.Distance(Player.GetXY(), Agent.GetXY(agent_id)) <= 1.2*Range.Area.value)
        if len(enemy_array) < 5:
            break
        
        if echoed:
            yield from StayAlive()

        target_id = Player.GetTargetID()
        if not target_id or Agent.IsHexed(target_id):
            target_id = SelectTarget()
            if not target_id:
                continue

            yield from bot_funcs.Agents.ChangeTarget(target_id)

        if bot_funcs.Skills.IsRecharged(Build.wd):
            yield from bot_funcs.Skills.CastSkill(Build.wd)
            echoed = True
            continue
    
        if PySkill.Skill(SkillBar.GetSkillIDBySlot(Build.ae)).id.id == Build.IDs.wd and bot_funcs.Skills.IsRecharged(Build.ae):
            yield from bot_funcs.Skills.CastSkill(Build.ae)
            continue

        yield from wait(0.2)

    yield from wait(1)
# endregion

# region bot logic
def BotLogic():
    global bot_vars

    while True:
        if not bot_vars.bot_started:
            yield from wait(1)
            continue

        # setup routine
        if (bot_vars.do_setup) and Inventory.GetFreeSlotCount() > 0:
            bot_vars.do_setup = False

            # check map
            if (Map.GetMapID() == Maps.jaga):
                SetStatus(bot_vars, 'Starting from Jaga.')
                yield from bot_funcs.Move.Zone(Path.zone[-1], Maps.bjora)
                yield from bot_funcs.Move.Zone(Path.rezone, Maps.jaga)
            elif (Map.GetMapID() == Maps.bjora):
                SetStatus(bot_vars, 'Starting from Bjora.')
                yield from bot_funcs.Move.Zone(Path.rezone, Maps.jaga)
            else:
                SetStatus(bot_vars, 'Setting up.')
                yield from bot_funcs.Maps.Travel(Maps.long)
                yield from bot_funcs.Skills.LoadSkillBar(Build.template)
                bot_funcs.Skills.CheckRequirements({'Shadow Arts' : 16, 'Domination Magic' : 11, 'Inspiration Magic': 6})
                yield from bot_funcs.Maps.SetMode(1)
                yield from bot_funcs.Skills.ChangeWeaponSet(Build.shield_set)
                SetStatus(bot_vars, 'Leaving Longeyes.')
                yield from bot_funcs.Move.Zone(Path.zone, Maps.bjora)
                SetStatus(bot_vars, 'Traversing Bjora\'s.')
                yield from bot_funcs.Move.Zone(Path.bjora, Maps.jaga, do_func = Run, extra_status = '"Bjora Marches"')
            
        # inventory management
        if bot_funcs.Items.CheckSlots(5) or bot_vars.handle_inv:
            SetStatus(bot_vars, 'Handling inventory.')
            inv_log = bot_funcs.Items.LogInventory([ModelID.Iron_Ingot, *bot_vars.loot.pickup_list.keys()])
            yield from BotRoutines.Items.Identify()
            yield from BotRoutines.Items.Salvage()
            yield from BotRoutines.Items.Sort()
            LogLoot(bot_vars, inv_log, header = 'Loot from inventory management:')
            if bot_vars.handle_inv:
                bot_vars.bot_started = False
                return

        # farm routine
        bot_vars.timers.lap.Start()
        SetStatus(bot_vars, 'Aggroing left ball.')
        yield from bot_funcs.Move.FollowPath(Path.left, do_func = Aggro, stuck_func= HandleStuck, stuck_time = 3000, extra_status = '"Aggroing - Left"', rand = 200)
        SetStatus(bot_vars, 'Waiting for enemies.')
        yield from WaitForSettle()
        SetStatus(bot_vars, 'Aggroing right ball.')
        yield from bot_funcs.Move.FollowPath(Path.right, do_func = Aggro, stuck_func= HandleStuck, stuck_time = 3000, extra_status = '"Aggroing - Right"', rand = 200)
        SetStatus(bot_vars, 'Waiting for enemies.')
        yield from WaitForSettle()
        SetStatus(bot_vars, 'Blocking enemies.')
        yield from bot_funcs.Move.FollowPath(Path.block[:3], do_func = Aggro, stuck_func= HandleStuck, stuck_time = 3000, extra_status = '"Blocking"', rand = 50)
        yield from wait(1)
        yield from bot_funcs.Move.FollowPath(Path.block[3], do_func = Aggro, stuck_func= HandleStuck, stuck_time = 3000, extra_status = '"Blocking"', rand = 20)
        yield from wait(1)
        yield from bot_funcs.Move.FollowPath(Path.block[4], do_func = Aggro, stuck_func= HandleStuck, stuck_time = 3000, extra_status = '"Blocking"', rand = 5)
        SetStatus(bot_vars, 'Killing enemies.')
        yield from Kill()
        inv_log = bot_funcs.Items.LogInventory(bot_vars.loot.pickup_list.keys())
        yield from bot_funcs.Items.Loot(bot_vars.loot.pickup_list.keys())
        LogLap(bot_vars, inv_log)
        SetStatus(bot_vars, 'Resetting.')
        if Party.GetPartySize() == 1:
            while Agent.IsDead(Player.GetAgentID()):
                yield from wait(1)
            if Map.GetMapID() == Maps.bjora:
                yield from bot_funcs.Maps.Travel(Maps.long)
                SetStatus(bot_vars, 'Leaving Longeyes.')
                yield from bot_funcs.Move.Zone(Path.zone, Maps.bjora)
                SetStatus(bot_vars, 'Traversing Bjora\'s.')
                yield from bot_funcs.Move.Zone(Path.bjora, Maps.jaga, do_func = Run, extra_status = '"Bjora Marches"')
            else:
                yield from bot_funcs.Move.Zone(Path.exit, Maps.bjora)
                yield from bot_funcs.Move.Zone(Path.rezone, Maps.jaga)
        else:
            if Agent.IsDead(Player.GetAgentID()):
                yield from bot_funcs.Maps.WaitForArrival(Maps.bjora)
            else:
                yield from bot_funcs.Move.Zone(Path.exit, Maps.bjora)
            yield from bot_funcs.Move.Zone(Path.rezone, Maps.jaga)
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