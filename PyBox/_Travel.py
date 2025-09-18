# region imports
from Py4GWCoreLib import *
import PyBox._Utils
# endregion

class Variables:
    # required for all modules
    icon              = IconsFontAwesome5.ICON_MAP_MARKED_ALT
    can_show_button   = True
    is_showing_button = True
    is_showing        = False
    is_snappable      = False
    offset_x          = 0
    offset_y          = 0
    first_run         = True

    # module specific
    selected_district = 'Current District'
    selected_outpost = 'Travel To...'

    districts_dict = {
        'Current District'   : 0,
        'International'      : 1,
        'American - English' : 2,
        'Europe - English'   : 3,
        'Europe - French'    : 4,
        'Europe - German'    : 5,
        'Europe - Italian'   : 6,
        'Europe - Spanish'   : 7,
        'Europe - Polish'    : 8,
        'Europe - Russian'   : 9,
        'Asia - Korean'      : 10,
        'Asia - Chinese'     : 11,
        'Asia - Japanese'    : 12
    }

    district_list = list(districts_dict.keys())

    outposts = list(outposts.values())
    outposts.append('Travel To...')
    outposts.sort()

vars = Variables()

def Draw():
    global vars, config

    PyImGui.set_next_window_pos(233, 835) # 292

    if PyBox._Utils.BeginWindow('Travel', vars.is_showing):
        if Map.GetContinent()[0] == 1: # presearing
            common = [
                ('Ascalon City'        , 148),
                ('Ashford Abbey'       , 164),
                ('Foible\'s Fair'      , 165),
                ('Fort Ranik'          , 166),
                ('The Barradin Estate' , 163)
            ]

            for name, map_id in common:
                if PyImGui.button(f'{name}##travel', 150):
                    vars.is_showing = False
                    GLOBAL_CACHE.Map.Travel(map_id)

        else:
            PyImGui.push_item_width(344)
            vars.selected_district = vars.district_list[PyImGui.combo(f'##Shapetravel_district',  vars.districts_dict[vars.selected_district],  vars.district_list)]
            vars.selected_outpost  = vars.outposts[PyImGui.combo(f'##Shapetravel_map',        vars.outposts.index(vars.selected_outpost),   vars.outposts)]
            PyImGui.pop_item_width()

            if vars.selected_outpost != 'Travel To...':
                vars.is_showing = False
                GLOBAL_CACHE.Map.TravelToDistrict(outpost_name_to_id[vars.selected_outpost], vars.districts_dict[vars.selected_district])
                vars.selected_outpost = 'Travel To...'
                vars.selected_district = 'Current District'

            common = [
                ('Kamadan, Jewel of Istan'   , 449),
                ('Gate of Anguish'           , 474),
                ('Embark Beach'              , 857),
                ('Great Temple of Balthazar' , 248)
            ]

            newline = False
            for name, map_id in common:
                if PyImGui.button(f'{name}##travel', 170):
                    vars.is_showing = False
                    GLOBAL_CACHE.Map.TravelToDistrict(map_id, vars.districts_dict[vars.selected_district])
                if newline:
                    newline = False
                else:
                    PyImGui.same_line(0, -1)
                    newline = True

        PyImGui.end()

    PyBox._Utils.EndWindow()

def Update():
    global vars, config

    if PyBox._Utils.CanDraw() and vars.is_showing:
        Draw()