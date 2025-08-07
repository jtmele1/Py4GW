# region imports
import _bot_routines
import importlib
importlib.reload(_bot_routines)
from _bot_routines import *
# endregion

# region globals
initialized                 = False
bot_funcs                   = BotRoutines()
bot_vars                    = BotVariables()
bot_vars.gui.window_name    = 'CoF Bone Farm'
bot_vars.farm_item.name     = 'Bones'
bot_vars.farm_item.model_id = ModelID.Bone
bot_vars.farm_item.color    = [.89, .85, .79, 1]
bot_vars.loot.pickup_list   = {ModelID.Bone                    : ('Bones'            , True),
                               ModelID.Pile_Of_Glittering_Dust : ('Dust'             , False),
                               ModelID.Gold_Coins              : ('Gold Coins'       , False),
                               ModelID.Lockpick                : ('Lockpicks'        , False),
                               24353                           : ('Diessa Chalices'  , False),
                               ModelID.Golden_Rin_Relic        : ('Golden Rin Relics', False),
                               'salvageables'                  : ('Salvageables'     , True)}
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
def HandleStuck(pos):
    Log('Player is stuck.')
    yield True

def UseVoS():
    global bot_vars 
    
    if (bot_funcs.Skills.IsRecharged(Build.pf) and bot_funcs.Skills.IsRecharged(Build.ga) and bot_funcs.Skills.IsRecharged(Build.vos) and bot_funcs.Skills.GetEnergy() >= 15):
        yield from bot_funcs.Skills.CastSkill([Build.pf, Build.ga, Build.vos])
        yield True
    yield False

def CheckVoS():
    global bot_vars 

    if not bot_funcs.Skills.HasEffect([Build.vos]):
        if bot_funcs.Skills.IsRecharged(Build.pf):
            yield from bot_funcs.Skills.CastSkill(Build.pf)
        if bot_funcs.Skills.IsRecharged(Build.ga):
            yield from bot_funcs.Skills.CastSkill(Build.ga)
        if bot_funcs.Skills.IsRecharged(Build.vos):
            yield from bot_funcs.Skills.CastSkill(Build.vos)
        yield True
    yield False

def WaitForSettle():
    timer = Timer()
    timer.Start()
    while True:
        if Agent.IsDead(Player.GetAgentID()):          break
        if Agent.GetHealth(Player.GetAgentID()) < 0.5: break
        if timer.HasElapsed(6000):                     break

        enemy_array = AgentArray.GetEnemyArray()
        enemy_array = AgentArray.Filter.ByAttribute(enemy_array, 'IsAlive')
        enemy_array = AgentArray.Filter.ByDistance(enemy_array, Player.GetXY(), 200)

        if len(enemy_array) >= 3: break
        
        if (yield from UseVoS()): continue
        if (yield from CheckVoS()): continue

        if bot_funcs.Skills.IsRecharged(Build.soms):
            yield from bot_funcs.Skills.CastSkill(Build.soms)
            continue

        yield from wait(.1)

def Kill():
    while True:
        yield from wait(.2)

        if Agent.IsDead(Player.GetAgentID()): 
            break

        # check for remaming enemies
        enemy_array = AgentArray.GetEnemyArray()
        enemy_array = AgentArray.Filter.ByAttribute(enemy_array, 'IsAlive')
        enemy_array = AgentArray.Filter.ByDistance(enemy_array, Player.GetXY(), 600)
        if not enemy_array or (len(enemy_array) < 2 and enemy_array[0] and Agent.GetHealth(enemy_array[0]) > 0.4):
            break

        # maintain vos
        if (yield from UseVoS()):                      continue
        if (yield from CheckVoS()):                    continue
        if bot_funcs.Skills.EffectTimeRemaining(1517) < 1.5: continue
        if not bot_funcs.Skills.CanCast():                    continue

        # maintain signet of mystic speed
        if not bot_funcs.Skills.HasEffect(Build.soms) and bot_funcs.Skills.IsRecharged(Build.soms):
            yield from bot_funcs.Skills.CastSkill(Build.soms)
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
                yield from bot_funcs.Agents.ChangeTarget(new_target)
                continue

        # attack
        if not Agent.IsAttacking(Player.GetAgentID()) and Player.GetTargetID():
            yield from bot_funcs.Agents.Interact()
            continue
        
        # cast crippling victory and reap impurities
        for spell in [Build.cv, Build.ri]:
            if bot_funcs.Skills.HasEnoughAdrenaline(spell):
                yield from bot_funcs.Skills.CastSkill(spell, min_aftercast = 1000)
                break

    yield from wait(.5)
# endregion

# region sequential functions
def BotLogic():
    global bot_vars

    while True:
        if not bot_vars.bot_started:
            yield from wait(1)
            continue

        # setup routine
        if (bot_vars.do_setup or Map.GetMapID() != Maps.starting) and not bot_vars.handle_inv:
            SetStatus(bot_vars, 'Setting up.')
            bot_vars.do_setup = False
            yield from bot_funcs.Maps.Travel(Maps.starting)
            yield from bot_funcs.Skills.LoadSkillBar(Build.template)
            bot_funcs.Skills.CheckRequirements({'Scythe Mastery' : 11, 'Wind Prayers' : 15, 'Mysticism' : 11})
            yield from bot_funcs.Maps.SetMode(0)
            yield from bot_funcs.Move.FollowPath(Path.npc)
            yield from bot_funcs.Agents.TargetNearestNPC()
            yield from bot_funcs.Agents.Interact(frame_alias = 'NPC Dialog')
            yield from bot_funcs.Player.ClickUIOptionFrame(3856160816, [2,0,0,1], 1)
            yield from bot_funcs.Player.ClickUIOptionFrame(3856160816, [2,0,0,1], 0)
            yield from bot_funcs.Maps.WaitForArrival(Maps.dungeon)
            yield from bot_funcs.Move.Zone(Path.rezone, Maps.starting)

        # inventory management
        if bot_funcs.Items.CheckSlots(5) or bot_vars.handle_inv:
            SetStatus(bot_vars, 'Handling inventory.')
            yield from bot_funcs.Move.FollowPath(Path.npc)
            yield from bot_funcs.Agents.TargetNearestNPC()
            yield from bot_funcs.Agents.Interact(frame_alias = 'NPC Dialog')
            yield from bot_funcs.Player.ClickUIOptionFrame(3856160816, [2,0,0,1], 2)
            inv_log = bot_funcs.Items.LogInventory([ModelID.Iron_Ingot, *bot_vars.loot.pickup_list.keys()])
            yield from bot_funcs.Items.ProcessInventory(bot_vars.loot.dont_sell_list)
            LogLoot(bot_vars, inv_log, header = 'Loot from inventory management:')
            if bot_vars.handle_inv:
                bot_vars.bot_started = False
                return
            
        # farm routine
        SetStatus(bot_vars, 'Entering dungeon.')
        bot_vars.timers.lap.Start()
        yield from bot_funcs.Skills.ChangeWeaponSet(Build.staff)
        yield from bot_funcs.Agents.TargetNearestNPC()
        yield from bot_funcs.Agents.Interact(frame_alias = 'NPC Dialog')
        yield from bot_funcs.Player.ClickUIOptionFrame(3856160816, [2,0,0,1], 1)
        yield from bot_funcs.Player.ClickUIOptionFrame(3856160816, [2,0,0,1], 0)
        yield from bot_funcs.Maps.WaitForArrival(Maps.dungeon)
        yield from bot_funcs.Move.FollowPath(Path.prep)
        SetStatus(bot_vars, 'Prepping skills.')
        yield from wait(3)
        yield from bot_funcs.Skills.CastSkill([Build.vop, Build.mb, Build.ga, Build.vos])
        yield from bot_funcs.Move.FollowPath(Path.kill, rand = 15, stuck_func = HandleStuck, stuck_time = 2000)
        SetStatus(bot_vars, 'Waiting for enemies.')
        yield from WaitForSettle()
        yield from bot_funcs.Skills.ChangeWeaponSet(Build.scythe, 'Scythe')
        SetStatus(bot_vars, 'Killing enemies.')
        yield from Kill()
        SetStatus(bot_vars, 'Looting items.')
        inv_log = bot_funcs.Items.LogInventory(bot_vars.loot.pickup_list.keys())
        yield from bot_funcs.Items.Loot(bot_vars.loot.pickup_list.keys())
        LogLap(bot_vars, inv_log)
        SetStatus(bot_vars, 'Resetting farm.')
        yield from bot_funcs.Maps.ResignAndReturn(Maps.starting)
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