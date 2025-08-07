# region imports
from Py4GWCoreLib import *
import PyBox._Utils
# endregion

class Variables:
    icon              = IconsFontAwesome5.ICON_LIST_CHECK
    can_show_button   = True
    is_showing_button = True
    is_showing        = False
    is_snappable      = False
    offset_x          = 0
    offset_y          = 0
    pos_x             = 500
    pos_y             = 500

    map_id = 0
    check_map_id = True
    region_type = 0

    completion_times = ['']*5

    dungeon_map_ids = [
        [570, 571, 676], # catacombs of kathandrax
        [573, 574, 575], # rragar's menagerie
        [560, 567, 568], # cathedral of flames
        [576], # ooze pit
        [635, 636, 637], # darkrime delves
        [630, 631, 632, 633, 634], # frostmaw's burrows
        [628, 629], # sepulchre of dragrimmar
        [617, 618, 619], # raven's point
        [604, 605, 606], # vloxen excavations
        [615, 616], # bogroot growths
        [612, 613, 614], # bloodstone caves
        [581, 582, 583], # shards of orr
        [578, 579, 580], # oola's lab
        [584, 585], # arachni's haunt
        [577], # slaver's exile
        [704], # fronis irontoe's lair
        [701, 781, 782], # secret lair of the snowmen
        [607, 608, 609], # heart of the shiverpeaks
    ]

vars = Variables()

def InMission():
    return GLOBAL_CACHE.Map.IsExplorable() and GLOBAL_CACHE.Map.GetRegionType()[0] == 5

def InDungeon():
    return GLOBAL_CACHE.Map.IsExplorable() and GLOBAL_CACHE.Map.GetRegionType()[0] == 18

def GetLevelCount():
    global vars

    for levels in vars.dungeon_map_ids:
        if GLOBAL_CACHE.Map.GetMapID() in levels:
            return len(levels)
        
    return 0

def Draw():
    global vars

    PyImGui.set_next_window_size(165, -1)
    if PyBox._Utils.BeginWindow('Objectives'):
        PyImGui.push_item_width(157)
        if InMission():
            PyImGui.input_text('##objtext', f'Mission - {vars.completion_times[0]}', PyImGui.InputTextFlags.ReadOnly)
        elif InDungeon():
            for i in range(GetLevelCount()):
                PyImGui.input_text('##objtext', f'Level {i + 1} - {vars.completion_times[i]}', PyImGui.InputTextFlags.ReadOnly)
        else:
            PyImGui.text(f'Enter a Mission/Dungeon\nto view objectives.')
            
        PyImGui.pop_item_width()
        PyImGui.end()

    PyBox._Utils.EndWindow()

def Update():
    global vars

    if Map.IsMapLoading():
        vars.check_map_id = True

    if PyBox._Utils.CanDraw():
        if vars.is_showing:
            Draw()