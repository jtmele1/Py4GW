# region imports
from Py4GWCoreLib import *
import PyBox._Utils
from os import path
# endregion

class PCon:
    def __init__(self, name, model_id, skill_id, active):
        self.name     = name
        self.model_id = model_id
        self.skill_id = skill_id
        self.count    = 0
        self.active   = active
        self.timer    = Timer()

        self.timer.Start()

def LoadConfig(ini):
    essense    = PCon('Essence_of_Celerity'   , ModelID.Essence_Of_Celerity    , 2522, ini.read_bool('pcons', 'essence'    , False))
    grail      = PCon('Grail_of_Might'        , ModelID.Grail_Of_Might         , 2521, ini.read_bool('pcons', 'grail'      , False))
    armor      = PCon('Armor_of_Salvation'    , ModelID.Armor_Of_Salvation     , 2520, ini.read_bool('pcons', 'armor'      , False))
    red_rock   = PCon('Red_Rock_Candy'        , ModelID.Red_Rock_Candy         , 2973, ini.read_bool('pcons', 'red_rock'   , False))
    blue_rock  = PCon('Blue_Rock_Candy'       , ModelID.Blue_Rock_Candy        , 2971, ini.read_bool('pcons', 'blue_rock'  , False))
    green_rock = PCon('Green_Rock_Candy'      , ModelID.Green_Rock_Candy       , 2972, ini.read_bool('pcons', 'green_rock' , False))
    cupcake    = PCon('Birthday_Cupcake'      , ModelID.Birthday_Cupcake       , 1945, ini.read_bool('pcons', 'cupcake'    , False))
    apple      = PCon('Candy_Apple'           , ModelID.Candy_Apple            , 2605, ini.read_bool('pcons', 'apple'      , False))
    corn       = PCon('Candy_Corn'            , ModelID.Candy_Corn             , 2604, ini.read_bool('pcons', 'corn'       , False))
    pie        = PCon('Slice_of_Pumpkin_Pie'  , ModelID.Slice_Of_Pumpkin_Pie   , 2649, ini.read_bool('pcons', 'pie'        , False))
    egg        = PCon('Golden_Egg'            , ModelID.Golden_Egg             , 1934, ini.read_bool('pcons', 'egg'        , False))
    war_sup    = PCon('War_Supplies'          , ModelID.War_Supplies           , 3174, ini.read_bool('pcons', 'war_sup'    , False))
    kabob      = PCon('Drake_Kabob'           , ModelID.Drake_Kabob            , 1680, ini.read_bool('pcons', 'kabob'      , False))
    soup       = PCon('Bowl_of_Skalefin_Soup' , ModelID.Bowl_Of_Skalefin_Soup  , 1681, ini.read_bool('pcons', 'soup'       , False))
    salad      = PCon('Pahnai_Salad'          , ModelID.Pahnai_Salad           , 1682, ini.read_bool('pcons', 'salad'      , False))
    alc        = PCon('Dwarven_Ale'           , ModelID.Dwarven_Ale            , 0   , ini.read_bool('pcons', 'alc'        , False))
    lunar      = PCon('Lunar_Fortune'         , ModelID.Lunar_Fortune_2018_Dog , 1926, ini.read_bool('pcons', 'lunar'      , False))
    speed      = PCon('Sugary_Blue_Drink'     , ModelID.Sugary_Blue_Drink      , 0   , ini.read_bool('pcons', 'speed'      , False))

    pcons = [
        essense, grail, armor, red_rock, blue_rock, green_rock, cupcake, apple,
        corn, pie, egg, war_sup, kabob, soup, salad, alc, lunar, speed
    ]

    return pcons

def SaveConfig(ini, config):
    ini.write_key(f'pcons', 'essence'    , str(config[0].active))
    ini.write_key(f'pcons', 'grail'      , str(config[1].active))
    ini.write_key(f'pcons', 'armor'      , str(config[2].active))
    ini.write_key(f'pcons', 'red_rock'   , str(config[3].active))
    ini.write_key(f'pcons', 'blue_rock'  , str(config[4].active))
    ini.write_key(f'pcons', 'green_rock' , str(config[5].active))
    ini.write_key(f'pcons', 'egg'        , str(config[6].active))
    ini.write_key(f'pcons', 'apple'      , str(config[7].active))
    ini.write_key(f'pcons', 'corn'       , str(config[8].active))
    ini.write_key(f'pcons', 'cupcake'    , str(config[9].active))
    ini.write_key(f'pcons', 'pie'        , str(config[10].active))
    ini.write_key(f'pcons', 'war_sup'    , str(config[11].active))
    ini.write_key(f'pcons', 'alc'        , str(config[12].active))
    ini.write_key(f'pcons', 'lunar'      , str(config[13].active))
    ini.write_key(f'pcons', 'speed'      , str(config[14].active))
    ini.write_key(f'pcons', 'kabob'      , str(config[15].active))
    ini.write_key(f'pcons', 'soup'       , str(config[16].active))
    ini.write_key(f'pcons', 'salad'      , str(config[17].active))

class Variables:
    # required for all modules
    ini = IniHandler(os.path.join(os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)))), "PyBox.ini"))
    icon              = IconsFontAwesome5.ICON_BIRTHDAY_CAKE
    can_show_button   = True
    is_showing_button = True
    is_showing        = False
    is_snappable      = False
    offset_x          = 0
    offset_y          = 0
    pos_x             = ini.read_int('pcons', 'x', 500)
    pos_y             = ini.read_int('pcons', 'y', 500)
    first_run         = True

    enabled = False
    image_path = r'D:\Games\Guild Wars\Py4GW\PyBox\pcons'
    config = LoadConfig(ini)

vars = Variables()

def Draw():
    global vars

    PyImGui.set_next_window_pos(233, 807) # 412

    if PyBox._Utils.BeginWindow('Consumables', vars.is_showing):
        text = 'Disabled'
        color = PyBox._Utils.Colors.off

        if vars.enabled: 
            text = 'Enabled'
            color = PyBox._Utils.Colors.on
            
        PyImGui.push_style_color(PyImGui.ImGuiCol.Text, color)
        if PyImGui.button(f'{text}##pcons', 224, 22):
            vars.enabled = not vars.enabled
        PyImGui.pop_style_color(1)

        count = 1
        for pcon in vars.config:
            
            PyImGui.push_style_var2(ImGui.ImGuiStyleVar.FramePadding, 2, 2)
            if pcon.active:
                PyImGui.push_style_color(PyImGui.ImGuiCol.Button,        (0, 0.7, 0, 0.5))
                PyImGui.push_style_color(PyImGui.ImGuiCol.ButtonHovered, (0, 0.7, 0, 0.6))
                PyImGui.push_style_color(PyImGui.ImGuiCol.ButtonActive,  (0, 0.7, 0, 0.7))
            else:
                PyImGui.push_style_color(PyImGui.ImGuiCol.Button,        (.5, .5, .5, 0.3))
                PyImGui.push_style_color(PyImGui.ImGuiCol.ButtonHovered, (.5, .5, .5, 0.4))
                PyImGui.push_style_color(PyImGui.ImGuiCol.ButtonActive,  (.5, .5, .5, 0.5))

            if ImGui.ImageButton(f'##{pcon.name}pcons', path.join(vars.image_path, f'{pcon.name}.png'), 30, 30):
                pcon.active = not pcon.active
                SaveConfig(vars.ini, vars.config)

            PyImGui.same_line(4 + 38*(count-1), -1)
            if pcon.count > 50:
                PyImGui.text_colored(str(pcon.count), (1,0.8,0,1))
            elif pcon.count > 10:
                PyImGui.text_colored(str(pcon.count), (1,0.35,0,1))
            else:
                PyImGui.text_colored(str(pcon.count), (1,0,0,1))
            
            PyImGui.pop_style_var(1)
            PyImGui.pop_style_color(3)

            if count < 6:
                PyImGui.same_line(4 + 38*(count), -1)
            else:
                count = 0
            count += 1
            
        PyImGui.end()

    PyBox._Utils.EndWindow()

def Update():
    global vars

    if vars.is_showing and PyBox._Utils.CanDraw():
        Draw()

    if not Map.IsMapReady() or not Party.IsPartyLoaded():
        return

    for pcon in vars.config:
        pcon.count = GLOBAL_CACHE.Inventory.GetModelCount(pcon.model_id)

    if vars.enabled and Map.IsExplorable():
        player_id = GLOBAL_CACHE.Player.GetAgentID()
        for pcon in vars.config:
            if pcon.active and pcon.count >= 1 and pcon.timer.HasElapsed(500) and not GLOBAL_CACHE.Effects.EffectExists(player_id, pcon.skill_id):
                item_id = GLOBAL_CACHE.Inventory.GetFirstModelID(pcon.model_id)
                GLOBAL_CACHE.Inventory.UseItem(item_id)
                pcon.timer.Reset()