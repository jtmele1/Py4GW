# region imports
from Py4GWCoreLib import *
import PyBox._Utils
# endregion

class Variables:
    timer = Timer()
    timer.Start()

vars = Variables()

def FormatTimer(time_ms, mask="hh:mm:ss.ms"):
    """Get the formatted elapsed time string based on the mask provided."""
    ms = int(time_ms)
    seconds = ms // 1000
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60

    # Apply the mask
    formatted_time = mask
    if "hh" in mask:
        formatted_time = formatted_time.replace("hh", f"{hours:02}")
    if "mm" in mask:
        formatted_time = formatted_time.replace("mm", f"{minutes:02}")
    if "ss" in mask:
        formatted_time = formatted_time.replace("ss", f"{secs:02}")

    return formatted_time

def Draw():
    global vars

    # health
    target_id = GLOBAL_CACHE.Player.GetTargetID()
    if target_id: 
        if GLOBAL_CACHE.Agent.IsLiving(target_id):
            health = math.ceil(GLOBAL_CACHE.Agent.GetHealth(target_id)*100)

            PyImGui.set_next_window_pos(1301,14)
            ImGui.push_font("Regular", 24)
            if PyBox._Utils.BeginHiddenWindow('HealthWidget1'):
                PyImGui.text_colored(f'{health:0} %', (0,0,0,1))
                PyImGui.end()
            PyBox._Utils.EndHiddenWindow()

            PyImGui.set_next_window_pos(1300,13)
            if PyBox._Utils.BeginHiddenWindow('HealthWidget2'):
                PyImGui.text(f'{health:0} %')
                PyImGui.end()
            PyBox._Utils.EndHiddenWindow()
            ImGui.pop_font()

    # timer
    player_time = vars.timer.GetElapsedTime()
    instance_time = GLOBAL_CACHE.Map.GetInstanceUptime()

    mask = 'mm:ss'
    if instance_time > 60*60*1000:
        mask = 'hh:mm:ss'

    player_time = FormatTimer(vars.timer.GetElapsedTime(), mask = mask)
    instance_time = FormatTimer(GLOBAL_CACHE.Map.GetInstanceUptime(), mask = mask)

    PyImGui.set_next_window_pos(1285 + 65, 1360) # 242,896
    ImGui.push_font("Regular", 40)
    if PyBox._Utils.BeginHiddenWindow('TimerWidget1'):
        PyImGui.text_colored(f'{player_time}\n{instance_time}', (0,0,0,1))
        PyImGui.end()
    PyBox._Utils.EndHiddenWindow()

    PyImGui.set_next_window_pos(1283 + 65, 1358) # 240,894
    if PyBox._Utils.BeginHiddenWindow('TimerWidget2'):
        PyImGui.text(f'{player_time}\n{instance_time}')
    PyBox._Utils.EndHiddenWindow()
    ImGui.pop_font()

def Update():
    global vars

    if Map.IsMapLoading():
        vars.timer.Stop()

    if GLOBAL_CACHE.Map.IsInCinematic():
            GLOBAL_CACHE.Map.SkipCinematic()

    if PyBox._Utils.CanDraw():
        if vars.timer.IsStopped():
            vars.timer.Reset()
        Draw()
        
        # if GLOBAL_CACHE.Party.IsPartyDefeated():
        #     GLOBAL_CACHE.Party.ReturnToOutpost()