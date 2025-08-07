# region imports
from _bot_routines import *
# endregion

# region globals
initialized = False
bot_funcs   = BotRoutines()
# endregion

# region classes
class Path:
    bounty = [(13458, -20803)]
    exit   = [( 15400,-20400),( 15850,-20550)]
    
class Maps:
    bjora = 482
    jaga  = 546
# endregion

# region bot logic
def BotLogic():
    while True:
        if Map.GetMapID() == Maps.jaga:
            Log('Grabbing bounty.')
            yield from bot_funcs.Move.FollowPath(Path.bounty)
            yield from bot_funcs.Agents.ChangeTarget(AgentArray.GetNPCMinipetArray()[0])
            yield from bot_funcs.Agents.Interact(frame_alias = "NPC Dialog")
            yield from bot_funcs.Player.ClickUIOptionFrame(3856160816, [2,0,0,1], 0)
            current_points = Player.GetTitle(TitleID.Norn).current_points
            Log('Waiting for kill.')
            while True:
                if Agent.IsDead(Party.GetPartyLeaderID()):
                    Log('Leader died. Rezoning.')
                    yield from bot_funcs.Move.Zone(Path.exit, Maps.bjora)
                    break
            
                if Map.GetFoesKilled() > 5:
                    gained_points = Player.GetTitle(TitleID.Norn).current_points - current_points
                    Log(f'Enemies killed. Gained {gained_points} Norn points.')
                    yield from bot_funcs.Maps.WaitForArrival(Maps.bjora)
                    break
                yield from wait(1)

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