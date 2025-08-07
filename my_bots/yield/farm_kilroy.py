# region imports
import _bot_routines
import importlib
importlib.reload(_bot_routines)
from _bot_routines import *
# endregion

# region globals
initialized                  = False
bot_funcs                    = BotRoutines()
bot_vars                     = BotVariables()
bot_vars.gui.window_name     = 'Kilroy XP Farm'
bot_vars.farm_item.name      = 'Level'

# endregion 856

# region classes
class Path:
    zone   = [(14968, -6331)]
    rezone = [(15570, -6586)]
    npc    = [(17186, -4889)]
    farm   = [(-16000, -14175), (-13188, -15924), (-7346, -16483),
              (-4355, -16111),  (-1419, -14337),  (2196, -15638),
              (5031, -15935),   (6161, -15167),   (7425, -15869),
              (10414, -16212),  (12241, -16084)]

class Maps:
    gunnars  = 644
    dungeon  = 704
    norrhart = 548

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

# region routine functions
def TakeQuest():
    SetStatus(bot_vars, 'Taking quest.')
    yield from bot_funcs.Move.FollowPath(Path.npc)
    yield from bot_funcs.Agents.TargetNearestNPC()
    yield from bot_funcs.Agents.Interact(wait_for_frame = True)
    yield from bot_funcs.Player.ClickDialogButton(1)
    yield from bot_funcs.Player.ClickDialogButton(1)

def EnterDungeon():
    bot_vars.timers.lap.Start()
    SetStatus(bot_vars, 'Entering dungeon.')
    yield from bot_funcs.Move.FollowPath(Path.npc)
    yield from bot_funcs.Agents.TargetNearestNPC()
    yield from bot_funcs.Agents.Interact(wait_for_frame = True)
    yield from bot_funcs.Player.ClickDialogButton(1)
    yield from bot_funcs.Maps.WaitForArrival(Maps.dungeon)

def AcceptReward():
    SetStatus(bot_vars, 'Accepting reward.')
    yield from bot_funcs.Move.FollowPath(Path.npc)
    yield from bot_funcs.Agents.TargetNearestNPC()
    yield from bot_funcs.Agents.Interact(wait_for_frame = True)
    yield from bot_funcs.Player.ClickDialogButton(1)
    yield from bot_funcs.Move.Zone(Path.zone, Maps.norrhart)
    yield from bot_funcs.Move.Zone(Path.rezone, Maps.gunnars)
    LogLap(bot_vars)
    yield from TakeQuest()
    yield from EnterDungeon()

def HandleQuest():
    has_quest = False
    for quest in Quest.GetQuestLog():
        if quest.quest_id == 856:
            has_quest = True
            break
    
    if not has_quest:
        yield from TakeQuest()

    if not Quest.GetQuestData(856).is_completed:
        yield from EnterDungeon()

    if Quest.GetQuestData(856).is_completed:
        yield from AcceptReward()

def Kill():
    global bot_vars

    # kill foes
    while True:
        yield from wait(0.5)
        if Agent.IsDead(Player.GetAgentID()):
            break

        # check for knockout
        if bot_funcs.Skills.IsRecharged(8):
            while Agent.GetEnergy(Player.GetAgentID()) < 1:
                yield from bot_funcs.Skills.CastSkill(8, min_aftercast = 50)

        # check for remaming enemies
        enemy_array = AgentArray.GetEnemyArray()
        enemy_array = AgentArray.Filter.ByAttribute(enemy_array, 'IsAlive')
        enemy_array = AgentArray.Filter.ByDistance(enemy_array, Player.GetXY(), 1200)
        if not enemy_array:
            break

        yield from bot_funcs.Skills.CastSkill(1)

        target_id = Player.GetTargetID()
        if not target_id or Agent.IsDead(target_id) or Agent.GetHealth(target_id) <= 0:
            yield from bot_funcs.Agents.TargetNearestEnemy()
        else:
            for skill in range(6, 1, -1):
                if not bot_funcs.Skills.CanCast():                  break
                if not bot_funcs.Skills.IsRecharged(skill):         continue
                if not bot_funcs.Skills.HasEnoughAdrenaline(skill): continue
                if not bot_funcs.Skills.HasEnoughEnergy(skill):     continue
                yield from bot_funcs.Skills.CastSkill(skill)
                break
# endregion

# region synchronous functions
def SynchronousLogic():
    global bot_vars

    while True:
        if not bot_vars.bot_started:
            yield from wait(1)
            continue

        # setup
        if (bot_vars.do_setup or Map.GetMapID() != Maps.gunnars):
            SetStatus(bot_vars, 'Setting up.')
            bot_vars.do_setup = False
            yield from bot_funcs.Maps.Travel(Maps.gunnars)
            yield from bot_funcs.Maps.SetMode(0)
            
        # handle quest
        yield from HandleQuest()

        # farm routine
        SetStatus(bot_vars, 'Starting farm.')
        yield from bot_funcs.Move.FollowPath(Path.farm, do_func = Kill, rand = 100)
        SetStatus(bot_vars, 'Resetting farm.')
        yield from wait(2)
        yield from bot_funcs.Maps.Travel(Maps.gunnars)
# endregion

# region main
def main():
    global bot_vars, initialized

    try:
        if not initialized:
            bot_vars.Reset()
            initialized = True

        if not Map.IsMapReady() or not Party.IsPartyLoaded(): return

        Draw(bot_vars, SynchronousLogic)

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