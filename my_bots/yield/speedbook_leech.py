# region imports
from _bot_routines import *
# endregion

# region globals
initialized = False
bot_funcs   = BotRoutines()
# endregion

# region classes
class Path:
    die = [(8143, 21618), (5214, 22656)]
    
class Maps:
    sif  = 643
    cotn = 653
    atc  = 0
    atfh = 0
# endregion

# region combat functions
def CoTN_Kill():
    while not Map.IsInCinematic():
        yield from wait (.5)

        if not Agent.IsValid(Player.GetTargetID()):
            continue

    
    yield from wait (2)
# endregion

# region bot logic
def BotLogic():
    while True:
        # Curse of the Nornbear
        match Map.GetMapID():
            # Curse of the Nornbear
            case Maps.sif:
                Log('Loading CoTN skillbar.')
                bot_funcs.Skills.LoadSkillBar('OwVj0tf6oOOMG2BLOr/IgEBBAA')
                while Map.IsOutpost():
                    yield from wait(1)
            case Maps.cotn:
                # setup
                yield from bot_funcs.Player.SendChatCommand('resign')
                Log('Dying.')
                yield from bot_funcs.Move.FollowPath(Path.die)
                while Agent.IsAlive(Player.GetAgentID()):
                    yield from wait(1)
                Log('Waiting for resurrect.')
                while Agent.IsDead(Player.GetAgentID()):
                    yield from wait(1)
                # kill
                Log('Killing Nornbear.')
                yield from bot_funcs.Agents.TargetNearestEnemy()
                yield from CoTN_Kill()
                yield from bot_funcs.Maps.SkipCinematic()
                bot_funcs.Maps.WaitForArrival(Maps.sif)

            

        yield from wait(1)
# endregion

# region main
def main():
    global initialized
    try:
        if not initialized:
            coroutines.clear()
            coroutines.append(BotLogic())
            initialized = True

        if not Map.IsMapReady() or not Party.IsPartyLoaded():
            return

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