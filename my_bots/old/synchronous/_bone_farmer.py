# region imports
from bot_routines import *
# endregion

# region globals
sq                           = SynchronousRoutines()
thread_manager               = MultiThreading(timeout = 5)
bot_vars                     = BotVariables()
bot_vars.gui.window_name     = 'CoF Bone Farm'
bot_vars.farm_item.name      = 'Bones'
bot_vars.farm_item.model_id  = ModelID.Bone
bot_vars.farm_item.color     = [.89, .85, .79, 1]
bot_vars.loot.pickup_list    = {'Bones'             : ModelID.Bone,
                                'Dust'              : ModelID.Pile_Of_Glittering_Dust,
                                'Gold Coins'        : ModelID.Gold_Coins, 
                                'Lockpicks'         : ModelID.Lockpick, 
                                'Diessa Chalices'   : 24353, 
                                'Golden Rin Relics' : ModelID.Golden_Rin_Relic,
                                'Salvageables'      : 'salvageables'}
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
    npc    = [(-19085, 17960)]
    rezone = [(-19665, -8045)]
    prep   = [(-16623, -8989)]
    kill   = [(-15525, -8923), (-15737,-9093)]

class Maps:
    starting = 648
    dungeon  = 560

class Build:
    # template
    template = 'OgCjkqqLrSYiihdftXjhOXhXxlA'
    # weapon slots
    scythe = 1
    staff  = 2
    # skills
    soms = 1
    pf   = 2
    ga   = 3
    vos  = 4
    cv   = 5
    ri   = 6
    vop  = 7
    mb   = 8
# endregion

# region combat functions
def HandleStuck():
    Log('Player is stuck.')
    return True

def UseVoS():
    global bot_vars 
    
    if (sq.Skills.IsRecharged(Build.pf) and sq.Skills.IsRecharged(Build.ga) and sq.Skills.IsRecharged(Build.vos) and sq.Skills.GetEnergy() >= 15):
        sq.Skills.CastSkill([Build.pf, Build.ga, Build.vos])
        return True
    return False

def CheckVos():
    global bot_vars 

    if not sq.Skills.HasEffect([Build.vos]) and action_queue.is_empty():
        if sq.Skills.IsRecharged(Build.pf):  sq.Skills.CastSkill(Build.pf)
        if sq.Skills.IsRecharged(Build.ga):  sq.Skills.CastSkill(Build.ga)
        if sq.Skills.IsRecharged(Build.vos): sq.Skills.CastSkill(Build.vos)
        return True
    return False

def WaitForSettle():
    timer = Timer()
    timer.Start()
    while True:
        if Agent.IsDead(Player.GetAgentID()):          return
        if Agent.GetHealth(Player.GetAgentID()) < 0.5: return
        if timer.HasElapsed(6000):                  return

        enemy_array = AgentArray.GetEnemyArray()
        enemy_array = AgentArray.Filter.ByAttribute(enemy_array, 'IsAlive')
        enemy_array = AgentArray.Filter.ByDistance(enemy_array, Player.GetXY(), 200)

        if len(enemy_array) >= 3: return
        
        if UseVoS():   continue
        if CheckVos(): continue

        if sq.Skills.IsRecharged(Build.soms):
            sq.Skills.CastSkill(Build.soms)
            continue

        sleep(.1)

def Kill():
    while True:
        sleep(.2)

        if Agent.IsDead(Player.GetAgentID()): 
            return

        # check for remaming enemies
        enemy_array = AgentArray.GetEnemyArray()
        enemy_array = AgentArray.Filter.ByAttribute(enemy_array, 'IsAlive')
        enemy_array = AgentArray.Filter.ByDistance(enemy_array, Player.GetXY(), 600)
        if not enemy_array or (len(enemy_array) < 2 and enemy_array[0] and Agent.GetHealth(enemy_array[0]) > 0.4):
            return

        # maintain vos
        if UseVoS():                                   continue
        if CheckVos():                                 continue
        if sq.Skills.EffectTimeRemaining(1517) < 1500: continue
        if not sq.Skills.CanCast():                    continue

        # maintain signet of mystic speed
        if not sq.Skills.HasEffect(Build.soms) and sq.Skills.IsRecharged(Build.soms):
            sq.Skills.CastSkill(Build.soms)
            continue

        # select target
        target_id = Player.GetTargetID()
        if target_id == 0 or Agent.GetAllegiance(target_id)[0] != 3 or Agent.IsDead(target_id):

            enemy_array = AgentArray.GetEnemyArray()
            enemy_array = AgentArray.Filter.ByAttribute(enemy_array,'IsAlive')
            enemy_array = AgentArray.Sort.ByDistance(enemy_array,(-15706,-9035))

            enemy_array = AgentArray.Filter.ByDistance(enemy_array,(-15706,-9035), 600)
            close_array = AgentArray.Filter.ByDistance(enemy_array,(-15706,-9035), 100)
            new_target = 0

            if Utils.Distance(Agent.GetXY(target_id),(-15706,-9035)) > 100 and close_array and close_array[0]:
                new_target = close_array[0]
            elif enemy_array and enemy_array[0]:
                new_target = enemy_array[0]

            if new_target and not Agent.IsSpirit(new_target):
                sq.Agents.ChangeTarget(new_target)
                continue

        # attack
        if not Agent.IsAttacking(Player.GetAgentID()) and Player.GetTargetID():
            sq.Agents.Interact()
            continue
        
        # cast crippling victory and reap impurities
        for spell in [Build.cv, Build.ri]:
            if sq.Skills.HasEnoughAdrenaline(spell):
                sq.Skills.CastSkill(spell)
                sleep(1)
                break
# endregion

def EnterDungeon():
    frames = UIManager.GetAllChildFrameIDs(3856160816, [2,0,0,1])
    frames = UIManager.SortFramesByVerticalPosition(frames)
    frame_id = frames[1][0]
    sq.Player.ClickUIFrame(frame_id)

    frames = UIManager.GetAllChildFrameIDs(3856160816, [2,0,0,1])
    frames = UIManager.SortFramesByVerticalPosition(frames)
    frame_id = frames[0][0]
    sq.Player.ClickUIFrame(frame_id)

# region sequential functions
def SynchronousLogic():
    global bot_vars, thread_manager

    while True:
        if not bot_vars.bot_started:
            sleep(1)
            continue

        # setup routine
        if (bot_vars.do_setup or Map.GetMapID() != Maps.starting) and not bot_vars.handle_inv:
            SetStatus(bot_vars, 'Setting up.')
            bot_vars.do_setup = False
            sq.Maps.Travel(Maps.starting)
            sq.Skills.LoadSkillBar(Build.template)
            sq.Skills.CheckRequirements({'Scythe Mastery' : 11, 'Wind Prayers' : 15, 'Mysticism' : 11})
            sq.Maps.SetMode(0)
            sq.Move.FollowPath(Path.npc)
            sq.Agents.TargetNearestNPC()
            sq.Agents.Interact(frame_alias = 'NPC Dialog')
            sq.Player.ClickUIOptionFrame(3856160816, [2,0,0,1], 1)
            sq.Player.ClickUIOptionFrame(3856160816, [2,0,0,1], 0)
            sq.Maps.WaitForArrival(Maps.dungeon)
            sq.Move.Zone(Path.rezone, Maps.starting)

        # inventory management
        if sq.Items.CheckSlots(5) or bot_vars.handle_inv:
            SetStatus(bot_vars, 'Handling inventory.')
            sq.Items.RequestInvNames()
            sq.Move.FollowPath(Path.npc)
            sq.Agents.TargetNearestNPC()
            sq.Agents.Interact(frame_alias = 'NPC Dialog')
            sq.Player.ClickUIOptionFrame(3856160816, [2,0,0,1], 2)
            inv_log = sq.Items.LogInventory([ModelID.Iron_Ingot, *bot_vars.loot.pickup_list.values()])
            sq.Items.ProcessInventory(bot_vars.loot.dont_sell_list)
            CatalogLoot(bot_vars, inv_log)
            if bot_vars.handle_inv:
                bot_vars.bot_started = False
                thread_manager.stop_all_threads()
                return
            
        # farm routine
        SetStatus(bot_vars, 'Entering dungeon.')
        bot_vars.timers.lap.Start()
        sq.Skills.ChangeWeaponSet(Build.staff)
        sq.Agents.TargetNearestNPC()
        sq.Agents.Interact(frame_alias = 'NPC Dialog')
        sq.Player.ClickUIOptionFrame(3856160816, [2,0,0,1], 1)
        sq.Player.ClickUIOptionFrame(3856160816, [2,0,0,1], 0)
        sq.Maps.WaitForArrival(Maps.dungeon)
        sq.Move.FollowPath(Path.prep)
        SetStatus(bot_vars, 'Prepping skills.')
        sleep(3)
        sq.Skills.CastSkill([Build.vop, Build.mb, Build.ga, Build.vos])
        sq.Move.FollowPath(Path.kill, rand = 15, stuck_func = HandleStuck, stuck_time = 2000)
        sq.Agents.RequestEnemyNames()
        WaitForSettle()
        sq.Skills.ChangeWeaponSet(Build.scythe, 'Scythe')
        SetStatus(bot_vars, 'Killing enemies.')
        Kill()
        SetStatus(bot_vars, 'Looting items.')
        sq.Items.RequestLootNames()
        inv_log = sq.Items.LogInventory(bot_vars.loot.pickup_list.values())
        sq.Items.Loot(bot_vars.loot.pickup_list.values())
        LogLap(bot_vars)
        CatalogLoot(bot_vars, inv_log)
        sq.Maps.ResignAndReturn(Maps.starting)
        SetStatus(bot_vars, 'Resetting farm.')
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