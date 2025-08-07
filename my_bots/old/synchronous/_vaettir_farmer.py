# region imports
from bot_routines import *
# endregion

# region globals
sq                           = SynchronousRoutines()
thread_manager               = MultiThreading(timeout = 5)
bot_vars                     = BotVariables()
bot_vars.gui.window_name     = 'Vaettir Farm'
bot_vars.farm_item.name      = 'Stones'
bot_vars.farm_item.model_id  = ModelID.Glacial_Stone
bot_vars.farm_item.color     = [.89, .85, .79, 1]
bot_vars.loot.pickup_list    = {'Glacial Stones' : ModelID.Glacial_Stone}
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
    zone   = [(-24492, 14938),(-26678, 16325)]
    bjora =  [( 15003,-16598),( 15003,-16598),( 12699,-14589),( 11628,-13867),( 10891,-12989),( 10517,-11229),
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
    exit   = [( 13970,-18920),( 15400,-20400),( 15850,-20550)]
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
        if not sq.Skills.HasEffect(Build.sf) and sq.Skills.IsRecharged(Build.sf):
            sq.Skills.CastSkill([Build.dp, Build.sf])

    if Agent.GetHealth(Player.GetAgentID()) < .7:
        if not sq.Skills.HasEffect(Build.sod) and sq.Skills.IsRecharged(Build.sod):
            sq.Skills.CastSkill(Build.sod)

def StayAlive(use_on_recharge = True):
    if not sq.Skills.CanCast(): return

    if sq.Skills.EffectTimeRemaining(Build.Effects.sf) <= 4 and sq.Skills.IsRecharged(Build.sf):
        sq.Skills.CastSkill([Build.dp, Build.sf])

    for skill in [Build.sod, Build.wop, Build.ch]:
        if sq.Skills.IsRecharged(skill):
            sq.Skills.CastSkill(skill)

def HandleStuck():
    enemy_array = AgentArray.GetEnemyArray()
    enemy_array = AgentArray.Filter.ByDistance(enemy_array,Player.GetXY(),Range.Spellcast.value)

    if not enemy_array:
        return True

    min_angle = math.pi
    agent_id = 0

    p_x, p_y = Player.GetXY()
    for enemy in enemy_array:
        e_x, e_y = Agent.GetXY(enemy)
        angle = math.fabs(math.pi - (math.atan2(e_y - p_y, e_x - p_x) - Agent.GetRotationAngle(Player.GetAgentID())))
        if angle < min_angle:
            min_angle = angle
            agent_id = enemy

    if not agent_id:
        sq.Agents.TargetNearestEnemy()
    else:
        sq.Agents.ChangeTarget(agent_id)

    if sq.Skills.IsRecharged(Build.hos):
        sq.Skills.CastSkill(Build.hos)
    return False

def Aggro():
    enemy_array = AgentArray.GetEnemyArray()
    if not enemy_array:
        return
    
    enemy_array = AgentArray.Sort.ByDistance(enemy_array, Player.GetXY())
    
    if Utils.Distance(Player.GetXY(),Agent.GetXY(enemy_array[0])) >= 1.2*Range.Earshot.value:
        return

    StayAlive()

def WaitForSettle():
    global bot_vars

    if Agent.IsDead(Player.GetAgentID()):
        return

    SetStatus(bot_vars, 'Waiting for enemies.')
    timer = Timer()
    timer.Start()
    while True:
        if timer.HasElapsed(20000): return
        if Agent.IsDead(Player.GetAgentID()):
            return

        enemy_array = AgentArray.GetEnemyArray()
        if not enemy_array:
            break

        enemy_array = AgentArray.Filter.ByDistance(enemy_array,Player.GetXY(),Range.Spellcast.value)
        enemy_array = AgentArray.Sort.ByDistance(enemy_array, Player.GetXY(), descending = True)
        
        if Utils.Distance(Player.GetXY(),Agent.GetXY(enemy_array[0])) <= Range.Adjacent.value:
            break

        StayAlive()
        sleep(.5)

    timer.Reset()
    while True:
        if timer.HasElapsed(3000): return
        if Agent.IsDead(Player.GetAgentID()):
            return

        StayAlive()
        sleep(.5)

def SelectTarget():
    enemy_array = AgentArray.GetEnemyArray()
    enemy_array = AgentArray.Filter.ByCondition(enemy_array, lambda agent_id: Utils.Distance(Player.GetXY(), Agent.GetXY(agent_id)) <= 1.2*Range.Adjacent.value)
    enemy_array = AgentArray.Filter.ByCondition(enemy_array, lambda agent_id: Agent.IsAlive(agent_id))
    enemy_array = AgentArray.Filter.ByCondition(enemy_array, lambda agent_id: Agent.GetHealth(agent_id) > 0)
    enemy_array = AgentArray.Filter.ByCondition(enemy_array, lambda agent_id:not Agent.IsHexed(agent_id))
    if not enemy_array: return 0

    return enemy_array[0]

def Kill():
    global bot_vars

    SetStatus(bot_vars, 'Killing enemies.')

    while sq.Skills.EffectTimeRemaining(Build.Effects.sf) < 10:
        StayAlive()
        if Agent.IsDead(Player.GetAgentID()):
            return
        sleep(0.5)

    sq.Skills.CastSkill(Build.ae)

    echoed = False
    while True:
        if Agent.IsDead(Player.GetAgentID()):
            return

        enemy_array = AgentArray.GetEnemyArray()
        enemy_array = AgentArray.Filter.ByCondition(enemy_array, lambda agent_id: Utils.Distance(Player.GetXY(), Agent.GetXY(agent_id)) <= 1.2*Range.Area.value)
        enemy_array = AgentArray.Filter.ByCondition(enemy_array, lambda agent_id: Agent.IsAlive(agent_id))
        enemy_array = AgentArray.Filter.ByCondition(enemy_array, lambda agent_id: Agent.GetHealth(agent_id) > 0)
        if not enemy_array:
            break
        
        if echoed:
            StayAlive()

        if Agent.IsHexed(Player.GetTargetID()):
            target_id = SelectTarget()
            if not target_id:
                continue

            sq.Agents.ChangeTarget(target_id)

        if sq.Skills.IsRecharged(Build.wd):
            sq.Skills.CastSkill(Build.wd)
            echoed = True
            continue
    
        if PySkill.Skill(SkillBar.GetSkillIDBySlot(Build.ae)).id.id == Build.IDs.wd and sq.Skills.IsRecharged(Build.ae):
            sq.Skills.CastSkill(Build.ae)
            continue

        sleep(0.2)

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
        if (bot_vars.do_setup) and Inventory.GetFreeSlotCount() > 0:
            SetStatus(bot_vars, 'Setting up.')
            bot_vars.do_setup = False
            sq.Maps.Travel(Maps.long)
            sq.Skills.LoadSkillBar(Build.template)
            sq.Skills.CheckRequirements({'Shadow Arts' : 16, 'Domination Magic' : 11, 'Inspiration Magic': 6})
            sq.Maps.SetMode(1)
            sq.Skills.ChangeWeaponSet(Build.shield_set)
            SetStatus(bot_vars, 'Leaving Longeyes.')
            sq.Move.Zone(Path.zone, Maps.bjora)
            sq.Move.Zone(Path.bjora, Maps.jaga, do_func = Run, extra_status = '"Bjora Marches"')
            
        # farm routine
        bot_vars.timers.lap.Start()
        SetStatus(bot_vars, 'Aggroing left ball.')
        sq.Move.FollowPath(Path.left, do_func = Aggro, stuck_func= HandleStuck, stuck_time = 3000, extra_status = '"Aggroing - Left"', rand = 200)
        WaitForSettle()
        SetStatus(bot_vars, 'Aggroing right ball.')
        sq.Move.FollowPath(Path.right, do_func = Aggro, stuck_func= HandleStuck, stuck_time = 3000, extra_status = '"Aggroing - Right"', rand = 200)
        WaitForSettle()
        SetStatus(bot_vars, 'Blocking enemies.')
        sq.Move.FollowPath(Path.block[:3], do_func = Aggro, stuck_func= HandleStuck, stuck_time = 3000, extra_status = '"Blocking"', rand = 20)
        sleep(1)
        sq.Move.FollowPath(Path.block[3], do_func = Aggro, extra_status = '"Blocking"', rand = 20)
        sleep(1)
        sq.Move.FollowPath(Path.block[4], do_func = Aggro, extra_status = '"Blocking"', rand = 5)
        Kill()
        inv_log = sq.Items.LogInventory(bot_vars.loot.pickup_list.values())
        sq.Items.Loot(bot_vars.loot.pickup_list.values())
        LogLap(bot_vars)
        while Agent.IsDead(Player.GetAgentID()):
            sleep(1)
        CatalogLoot(bot_vars, inv_log)
        SetStatus(bot_vars, 'Resetting.')
        sq.Move.Zone(Path.exit, Maps.bjora)
        sq.Move.Zone(Path.rezone, Maps.jaga)
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