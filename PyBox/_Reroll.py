# region imports
from Py4GWCoreLib import *
import PyBox._Utils
# endregion

class Variables:
    icon              = IconsFontAwesome5.ICON_USER_FRIENDS
    is_showing        = False

    profession_row_colors = {
        1:  ColorPalette.GetColor('gw_warrior'),
        2:  ColorPalette.GetColor('gw_ranger'),
        3:  ColorPalette.GetColor('gw_monk'),
        4:  ColorPalette.GetColor('gw_necromancer'),
        5:  ColorPalette.GetColor('gw_mesmer'),
        6:  ColorPalette.GetColor('gw_elementalist'),
        7:  ColorPalette.GetColor('gw_assassin'),
        8:  ColorPalette.GetColor('gw_ritualist'),
        9:  ColorPalette.GetColor('gw_paragon'),
        10: ColorPalette.GetColor('gw_dervish'),
    }

    characters = []
    image_path = r'D:\Games\Guild Wars\Py4GW\PyBox\professions'

vars = Variables()

class Character:
    def __init__(self, name, profession, level, icon):
        self.name = name
        self.profession = profession
        self.level = level
        self.icon = icon

def GetCharacters():
    global vars

    characters = Player.GetLoginCharacters()
    for character in characters:
        if Player.GetName() == character.player_name:
            continue
        primary = character.primary
        vars.characters.append(Character(character.player_name, primary, character.level, rf'{vars.image_path}\{primary}.png'))

def InCharacterSelect():
    if not GLOBAL_CACHE.Player.InCharacterSelectScreen():
        return False
    pregame = GLOBAL_CACHE.Player.GetPreGameContext()
    return pregame is not None and pregame.chars is not None

def Reroll(char_name):
    GLOBAL_CACHE.Player.LogoutToCharacterSelect()
    while not InCharacterSelect():
        yield from Routines.Yield.wait(100)

    frame_id = UIManager.GetChildFrameID(828467986,[0])
    pregame = GLOBAL_CACHE.Player.GetPreGameContext()
    character_idx = pregame.chars.index(char_name)
    UIManager.TestMouseAction(frame_id, 7, character_idx)
    yield from Routines.Yield.wait(100)
    Keystroke.PressAndRelease(Key.Enter.value)

def Draw():
    global vars

    height = 28*len(vars.characters)
    PyImGui.set_next_window_pos(233, 947-height)

    if PyBox._Utils.BeginWindow('Reroll', vars.is_showing):
        PyImGui.push_style_var2(ImGui.ImGuiStyleVar.ButtonTextAlign, 0, 0.5)

        for character in vars.characters:
            if PyImGui.button(f'      {character.name} ({character.level})', width = 200):
                vars.is_showing = False
                GLOBAL_CACHE.Coroutines.append(Reroll(character.name))

            PyImGui.same_line(6,-1)
            ImGui.DrawTexture(character.icon, 22, 22)

        PyImGui.pop_style_var(1)
        PyImGui.end()

    PyBox._Utils.EndWindow()

def Update():
    global vars

    if PyBox._Utils.CanDraw():
        if vars.is_showing:
            if not vars.characters:
                GetCharacters()
            Draw()

        if not vars.is_showing and vars.characters:
            vars.characters = []