from Py4GWCoreLib import *
import re
from typing import Any

class Variables:
    current_profession = 1
    current_attribute = 17
    current_skill_id = 317
    current_attr_value = -1

    skill_table = []

    drag_data = []
    drag_id = 0

    profession_map = {
        1  : 'Warrior',
        2  : 'Ranger',
        3  : 'Monk',
        4  : 'Necromancer',
        5  : 'Mesmer',
        6  : 'Elementalist',
        7  : 'Assassin',
        8  : 'Ritualist',
        9  : 'Paragon',
        10 : 'Dervish',
    }

    attributes_map = {
        0  : 'Fast Casting',
        1  : 'Illusion Magic',
        2  : 'Domination Magic',
        3  : 'Inspiration Magic',
        4  : 'Blood Magic',
        5  : 'Death Magic',
        6  : 'Soul Reaping',
        7  : 'Curses',
        8  : 'Air Magic',
        9  : 'Earth Magic',
        10 : 'Fire Magic',
        11 : 'Water Magic',
        12 : 'Energy Storage',
        13 : 'Healing Prayers',
        14 : 'Smiting Prayers',
        15 : 'Protection Prayers',
        16 : 'Divine Favor',
        17 : 'Strength',
        18 : 'Axe Mastery',
        19 : 'Hammer Mastery',
        20 : 'Swordsmanship',
        21 : 'Tactics',
        22 : 'Beast Mastery',
        23 : 'Expertise',
        24 : 'Wilderness Survival',
        25 : 'Marksmanship',
        29 : 'Dagger Mastery',
        30 : 'Deadly Arts',
        31 : 'Shadow Arts',
        32 : 'Communing',
        33 : 'Restoration Magic',
        34 : 'Channeling Magic',
        35 : 'Critical Strikes',
        36 : 'Spawning Power',
        37 : 'Spear Mastery',
        38 : 'Command',
        39 : 'Motivation',
        40 : 'Leadership',
        41 : 'Scythe Mastery',
        42 : 'Wind Prayers',
        43 : 'Earth Prayers',
        44 : 'Mysticism',
        45 : 'None',
        51 : 'No Attribute',
        -1 : 'Factions/Nightfall PvE',
        -2 : 'Eye of the North PvE'
    }

    profession_attribute_map = {
        1  : [17, 18, 19, 20, 21, 51, -1, -2],
        2  : [23, 22, 24, 25, 51, -1, -2],
        3  : [16, 13, 14, 15, 51, -1, -2],
        4  : [6, 4, 5, 7, 51, -1, -2],
        5  : [0, 1, 2, 3, 51, -1, -2],
        6  : [12, 8, 9, 10, 11, 51, -1, -2],
        7  : [35, 29, 30, 31, 51, -1, -2],
        8  : [36, 32, 33, 34, 51, -1, -2],
        9  : [40, 37,38, 39, 51, -1, -2],
        10 : [44, 41,42,43, 51, -1, -2],
    }
    
    skill_map = {}

    skill_by_id = {}

    profession_row_colors = {
        1  : Color(222, 185, 104, 100),
        2  : Color(147, 194, 74 , 100),
        3  : Color(171, 215, 229, 100),
        4  : Color(87 , 174, 112, 100),
        5  : Color(161, 84 , 146, 100),
        6  : Color(197, 75 , 75 , 100),
        7  : Color(234, 18 , 125, 100),
        8  : Color(39 , 234, 204, 100),
        9  : Color(208, 122, 14 , 100),
        10 : Color(97 , 115, 163, 100),
    }

vars = Variables()

class SkillData:
    def __init__(self, id, name):
        self.id            = id
        self.name          = name
        self.profession    = Skill.GetProfession(self.id)[1]
        self.attribute     = Skill.Attribute.GetAttribute(self.id).GetName()
        self.sacrifice     = Skill.Data.GetHealthCost(self.id)
        self.energy        = Skill.Data.GetEnergyCost(self.id)
        self.adrenaline    = math.ceil(Skill.Data.GetAdrenaline(self.id)/25)
        self.upkeep        = True if Skill.Attribute.GetDuration(self.id)[0] == 131072 else False
        self.overcast      = Skill.Data.GetOvercast(self.id)
        self.activation    = Skill.Data.GetActivation(self.id)
        self.recharge      = Skill.Data.GetRecharge(self.id)
        self.elite         = Skill.Flags.IsElite(self.id)
        self.campaign      = Skill.GetCampaign(self.id)[1]
        self.description   = Skill.GetConciseDescription(self.id)
        self.title         = Skill.ExtraData.GetTitle(self.id)
        self.skill_icon    = f'../{Skill.ExtraData.GetTexturePath(self.id)}'
        self.variable      = self.GetVariable()
        self.variable_icon = self.GetVariableIcon()
        self.cost          = self.GetCost()
        self.cost_icon     = self.GetCostIcon()

    def GetCost(self):
        if self.energy:
            return self.energy
        elif self.adrenaline:
            return self.adrenaline
        else:
            return None
        
    def GetCostIcon(self):
        if self.energy:
            return '../Textures/Game UI/Skill Description/energy.png'
        elif self.adrenaline:
            return '../Textures/Game UI/Skill Description/adrenaline.png'
        else:
            return None

    def GetVariable(self):
        if self.upkeep:
            return -1
        elif self.sacrifice > 0:
            return self.sacrifice
        elif self.overcast > 0:
            return self.overcast
        else:
            return None
        
    def GetVariableIcon(self):
        if self.upkeep:
            return '../Textures/Game UI/Skill Description/upkeep.png'
        elif self.sacrifice > 0:
            return '../Textures/Game UI/Skill Description/sacrifice.png'
        elif self.overcast > 0:
            return '../Textures/Game UI/Skill Description/overcast.png'
        else:
            return None

class SkillbarData:
    def __init__(self, template, primary, secondary, attributes, skills):
        self.template   = template
        self.primary    = primary
        self.secodary   = secondary
        self.attributes = attributes
        self.skills     = skills

def Log(message, title = 'Log', msg_type = 'Info'):
    py4gw_msg_type = Py4GW.Console.MessageType.Info
    if   msg_type == 'Debug':       py4gw_msg_type = Py4GW.Console.MessageType.Debug
    elif msg_type == 'Error':       py4gw_msg_type = Py4GW.Console.MessageType.Error
    elif msg_type == 'Info':        py4gw_msg_type = Py4GW.Console.MessageType.Info
    elif msg_type == 'Notice':      py4gw_msg_type = Py4GW.Console.MessageType.Notice
    elif msg_type == 'Performance': py4gw_msg_type = Py4GW.Console.MessageType.Performance
    elif msg_type == 'Success':     py4gw_msg_type = Py4GW.Console.MessageType.Success
    elif msg_type == 'Warning':     py4gw_msg_type = Py4GW.Console.MessageType.Warning
    Py4GW.Console.Log(title, str(message), py4gw_msg_type)

def BeginWindow(name):
    flags = (PyImGui.WindowFlags.AlwaysAutoResize  |
             PyImGui.WindowFlags.NoScrollWithMouse | 
             PyImGui.WindowFlags.NoSavedSettings)

    PyImGui.push_style_var( ImGui.ImGuiStyleVar.WindowBorderSize, 0)
    PyImGui.push_style_var2(ImGui.ImGuiStyleVar.WindowPadding,    4, 4)
    PyImGui.push_style_var( ImGui.ImGuiStyleVar.WindowRounding,   0)
    PyImGui.push_style_var( ImGui.ImGuiStyleVar.FrameRounding,    0)
    PyImGui.push_style_var2(ImGui.ImGuiStyleVar.ItemSpacing,      4, 4)

    PyImGui.push_style_color(PyImGui.ImGuiCol.SliderGrab,       (.9, .9, .9, 1))
    PyImGui.push_style_color(PyImGui.ImGuiCol.SliderGrabActive, (.9, .9, .9, 1))

    PyImGui.push_style_color(PyImGui.ImGuiCol.Button,        (.5, .5, .5, 0.3))
    PyImGui.push_style_color(PyImGui.ImGuiCol.ButtonHovered, (.5, .5, .5, 0.4))
    PyImGui.push_style_color(PyImGui.ImGuiCol.ButtonActive,  (.5, .5, .5, 0.5))

    PyImGui.push_style_color(PyImGui.ImGuiCol.Header,         (.5, .5, .5, 0.3))
    PyImGui.push_style_color(PyImGui.ImGuiCol.HeaderHovered,  (.5, .5, .5, 0.4))
    PyImGui.push_style_color(PyImGui.ImGuiCol.HeaderActive,   (.5, .5, .5, 0.5))

    PyImGui.push_style_color(PyImGui.ImGuiCol.FrameBg,        (.5, .5, .5, 0.3))
    PyImGui.push_style_color(PyImGui.ImGuiCol.FrameBgHovered, (.5, .5, .5, 0.4))
    PyImGui.push_style_color(PyImGui.ImGuiCol.FrameBgActive,  (.5, .5, .5, 0.5))

    PyImGui.push_style_color(PyImGui.ImGuiCol.WindowBg,         (0, 0, 0, 0.7))
    PyImGui.push_style_color(PyImGui.ImGuiCol.TitleBg,          (0, 0, 0, 0.7))
    PyImGui.push_style_color(PyImGui.ImGuiCol.TitleBgActive,    (0, 0, 0, 0.7))
    PyImGui.push_style_color(PyImGui.ImGuiCol.TitleBgCollapsed, (0, 0, 0, 0.7))

    return PyImGui.begin(name, flags)

def EndWindow():
    PyImGui.pop_style_var(5)
    PyImGui.pop_style_color(15)

def BuildSkillMap():
    global vars

    for profession, attributes in vars.profession_attribute_map.items():
        vars.skill_map[profession] = {}
        for attribute in attributes:
            vars.skill_map[profession][attribute] = []

    for skill_id, name in SkillTextureMap.items():
        if not Skill.Flags.IsPlayable(skill_id):
            continue

        skill = SkillData(skill_id, name.split(' - ', 1)[1].split('.')[0])
        vars.skill_by_id[skill_id] = skill

        prof = Skill.GetProfession(skill_id)[0]
        attr = Skill.Attribute.GetAttribute(skill_id).attribute_id.value

        if Skill.Flags.IsPvP(skill_id):
            continue

        if attr == 51:
            if prof == 0:
                if skill.title in [38, 39, 40, 41]:
                    for professon in vars.profession_attribute_map:
                        vars.skill_map[professon][-2].append(skill)
                elif skill.title in [20]:
                    for professon in vars.profession_attribute_map:
                        vars.skill_map[professon][-1].append(skill)
                else:
                    for professon in vars.profession_attribute_map:
                        vars.skill_map[professon][51].append(skill)
            else:
                if skill.title in [5, 6, 17]:
                    vars.skill_map[prof][-1].append(skill)
                else:
                    vars.skill_map[prof][51].append(skill)
        else:
            vars.skill_map[prof][attr].append(skill)

    for profession, attributes in vars.profession_attribute_map.items():
        for attribute in attributes:
            vars.skill_map[profession][attribute] = sorted(vars.skill_map[profession][attribute], key=lambda skill: skill.name)

def BeginGroup(width):
    PyImGui.push_item_width(width)
    PyImGui.push_style_var2(ImGui.ImGuiStyleVar.ButtonTextAlign, 0, 0.5)
    PyImGui.push_style_var2(ImGui.ImGuiStyleVar.ItemSpacing, 4, 0)

    start_x, start_y = PyImGui.get_cursor_screen_pos()
    PyImGui.begin_group()

    return start_x, start_y

def EndGroup(start_x, start_y, end_x, end_y):
    PyImGui.pop_item_width()
    PyImGui.pop_style_var(2)
    PyImGui.end_group()

    PyImGui.draw_list_add_rect(start_x, start_y, end_x, end_y,
                               Utils.RGBToColor(150,150,150,255),0 ,0 ,1)

def Base64ToBin64(char):
	match char:
		case 'A': return '000000'
		case 'B': return '100000'
		case 'C': return '010000'
		case 'D': return '110000'
		case 'E': return '001000'
		case 'F': return '101000'
		case 'G': return '011000'
		case 'H': return '111000'
		case 'I': return '000100'
		case 'J': return '100100'
		case 'K': return '010100'
		case 'L': return '110100'
		case 'M': return '001100'
		case 'N': return '101100'
		case 'O': return '011100'
		case 'P': return '111100'
		case 'Q': return '000010'
		case 'R': return '100010'
		case 'S': return '010010'
		case 'T': return '110010'
		case 'U': return '001010'
		case 'V': return '101010'
		case 'W': return '011010'
		case 'X': return '111010'
		case 'Y': return '000110'
		case 'Z': return '100110'
		case 'a': return '010110'
		case 'b': return '110110'
		case 'c': return '001110'
		case 'd': return '101110'
		case 'e': return '011110'
		case 'f': return '111110'
		case 'g': return '000001'
		case 'h': return '100001'
		case 'i': return '010001'
		case 'j': return '110001'
		case 'k': return '001001'
		case 'l': return '101001'
		case 'm': return '011001'
		case 'n': return '111001'
		case 'o': return '000101'
		case 'p': return '100101'
		case 'q': return '010101'
		case 'r': return '110101'
		case 's': return '001101'
		case 't': return '101101'
		case 'u': return '011101'
		case 'v': return '111101'
		case 'w': return '000011'
		case 'x': return '100011'
		case 'y': return '010011'
		case 'z': return '110011'
		case '0': return '001011'
		case '1': return '101011'
		case '2': return '011011'
		case '3': return '111011'
		case '4': return '000111'
		case '5': return '100111'
		case '6': return '010111'
		case '7': return '110111'
		case '8': return '001111'
		case '9': return '101111'
		case '+': return '011111'
		case '/': return '111111'

def Bin64ToDec(binary):
    decimal = 0

    for i in range(0, len(binary)):
        if binary[i] == '1':
            decimal += 2**(i)

    return decimal

def DecodeSkillTemplate(template):
    enc_template = ''

    for char in template:
        enc_template = f'{enc_template}{Base64ToBin64(char)}'
 
    template_type = Bin64ToDec(enc_template[:4])
    # if template_type != 14:
    #     return (None, None, None, None)
    enc_template = enc_template[4:]

    version_number = Bin64ToDec(enc_template[:4])
    enc_template = enc_template[4:]

    prof_bits = Bin64ToDec(enc_template[:2]) * 2 + 4
    enc_template = enc_template[2:]

    prof_primary = Bin64ToDec(enc_template[:prof_bits])
    enc_template = enc_template[prof_bits:]

    prof_secondary = Bin64ToDec(enc_template[:prof_bits])
    enc_template = enc_template[prof_bits:]

    attributes_count = Bin64ToDec(enc_template[:4])
    enc_template = enc_template[4:]

    attributes_bits = Bin64ToDec(enc_template[:4]) + 4
    enc_template = enc_template[4:]
    
    attributes = {}
    for i in range(attributes_count):
        attr = Bin64ToDec(enc_template[:attributes_bits])
        enc_template = enc_template[attributes_bits:]
        value = Bin64ToDec(enc_template[:4])
        enc_template = enc_template[4:]
        attributes[attr] = value
    
    skill_bits = Bin64ToDec(enc_template[:4]) + 8
    enc_template = enc_template[4:]

    skills = []
    for i in range(8):
        skill = Bin64ToDec(enc_template[:skill_bits])
        enc_template = enc_template[skill_bits:]
        skills.append(skill)

    # Log(f'Decoding template: {template}')
    # Log(f'   Primary Profession - {vars.profession_map[prof_primary]}')
    # Log(f'   Secondary Profession - {vars.profession_map[prof_secondary]}')
    # Log(f'   Attributes:')
    # for attr, value in attributes.items():
    #     Log(f'      {vars.attributes_map[attr]} - {value}')
    # Log(f'   Skills:')
    # for skill in skills:
    #     Log(f'      {Skill.GetName(skill)} ({skill})')

    return (prof_primary, prof_secondary, attributes, skills)

def SkillbarFromTemplate(template):
    primary, secondary, attributes, skills = DecodeSkillTemplate(template)
    return SkillbarData(template, primary, secondary, attributes, skills)

def DrawToopTip():
    ...

def DrawSkillbars():
    global vars

    templates = ['OgcTYt72Zyhhh5gB3gHMXcsm2A',
                 'OgcTY5L2Vyhhh5gB3gH83YVaXE',
                 'OgcTY5L2Vyhhh5gB3gH83YVaXE',
                 'OgKiYxsM9eNfRupehgtLyDSbA',
                 'OgKiYxsM9eNfRupehgtLyDSbA',
                 'OgKiYxsM9eNfRupehgtLyDSbA',
                 'OAOjQyh8zQl1AAAAYgaiSTTOXM',
                 'OACiAyk8gNtePuwJ0E56MvY']
    
    if not vars.skill_table:
        for template in templates:
            bar = SkillbarFromTemplate(template)

            skills = []
            for skill in bar.skills:
                skills.append(skill)
            
            vars.skill_table.append(skills)

    PyImGui.begin_group()
    PyImGui.push_style_var2(ImGui.ImGuiStyleVar.ItemSpacing, 0, 8)

    start_x, start_y = BeginGroup(530)
    end_y = 0

    PyImGui.dummy(0,5)
    for i, bar in enumerate(vars.skill_table):
        PyImGui.dummy(1,4)
        PyImGui.same_line(0, -1)
        for j, skill in enumerate(bar):
            icon = 'no_skill.png'
            if skill:
                icon = vars.skill_by_id[skill].skill_icon

                if vars.skill_by_id[skill].elite:
                    PyImGui.push_style_color(PyImGui.ImGuiCol.Button,        (1, 1, 0, 1))
                    PyImGui.push_style_color(PyImGui.ImGuiCol.ButtonHovered, (1, 1, 0, 1))
                    PyImGui.push_style_color(PyImGui.ImGuiCol.ButtonActive,  (1, 1, 0, 1))
                    ImGui.ImageButtonExtended(f'##skill{i}{j}', icon, (58, 58), uv0 = (0.0625,0.0625), uv1 = (0.9375, 0.9375), frame_padding=3)
                    PyImGui.pop_style_color(3)
                else:
                    ImGui.ImageButtonExtended(f'##skill{i}{j}', icon, (64, 64), uv0 = (0.0625,0.0625), uv1 = (0.9375, 0.9375), frame_padding=0)
            else:
                ImGui.ImageButtonExtended(f'##skill{i}{j}', icon, (64, 64), uv0 = (0.0625,0.0625), uv1 = (0.9375, 0.9375), frame_padding=0)

            if PyImGui.is_item_hovered(): 
                # starting drag
                if PyImGui.is_mouse_dragging(0, 1):
                    if not vars.drag_data:
                        vars.drag_data.append([i, j])
                        vars.drag_id = vars.skill_table[i][j]

                # ending drag from skill bar
                if vars.drag_data and not PyImGui.is_mouse_down(0):
                    vars.drag_data.append([i, j])

                    if len(vars.drag_data) == 2:
                        drag_start = vars.drag_data[0]
                        drag_end = vars.drag_data[1]

                        start_a = vars.skill_table[drag_start[0]][drag_start[1]]
                        start_b = vars.skill_table[drag_end[0]][drag_end[1]]

                        if start_a:
                            vars.skill_table[drag_end[0]][drag_end[1]] = start_a
    
                            if start_b:
                                vars.skill_table[drag_start[0]][drag_start[1]] = start_b
                            else:
                                vars.skill_table[drag_start[0]][drag_start[1]] = 0
                    else:
                        drag_end = vars.drag_data[0]
                        vars.skill_table[drag_end[0]][drag_end[1]] = vars.drag_id

                    vars.drag_data = []
                    vars.drag_id = 0

                # ending drag from skill list
                if vars.drag_id and not PyImGui.is_mouse_down(0):
                    vars.skill_table[i][j] = vars.drag_id
                    vars.drag_id = 0

            PyImGui.same_line(0, -1)
        PyImGui.dummy(0,0)
        
        if i < len(templates) - 1:
            PyImGui.dummy(1,4)

    _, end_y = PyImGui.get_cursor_screen_pos()
    EndGroup(start_x, start_y, start_x + 550, end_y + 5)

    PyImGui.same_line(0, -1)
    PyImGui.dummy(1,4)

    PyImGui.pop_style_var(1)
    PyImGui.end_group()

def DrawProfessionSelect():
    start_x, start_y = BeginGroup(200)
    end_y = 0

    selected_prof = vars.current_profession
    
    for profession in vars.profession_attribute_map:
        color = vars.profession_row_colors[profession].to_tuple_normalized()
        if profession == selected_prof:
            PyImGui.push_style_color(PyImGui.ImGuiCol.Button,        (color[0], color[1], color[2], 100/255))
        else:
            PyImGui.push_style_color(PyImGui.ImGuiCol.Button,        (0, 0, 0, 0))
        
        PyImGui.push_style_color(PyImGui.ImGuiCol.ButtonHovered, (color[0], color[1], color[2], 125/255))
        PyImGui.push_style_color(PyImGui.ImGuiCol.ButtonActive,  (color[0], color[1], color[2], 150/255))

        if PyImGui.button(f'     {vars.profession_map[profession]}', 200, 21):
            vars.current_profession = profession

        PyImGui.same_line(2,-1)
        ImGui.DrawTexture(f'professions/{vars.profession_map[profession]}.png', 20, 20)

        PyImGui.pop_style_color(4)

    _, end_y = PyImGui.get_cursor_screen_pos()
    EndGroup(start_x, start_y, start_x + 200, end_y)

    if selected_prof != vars.current_profession:
        vars.current_attribute = vars.profession_attribute_map[vars.current_profession][0]

def DrawAttributeSelect():
    start_x, start_y = BeginGroup(200)
    end_y = 0

    atts = vars.profession_attribute_map[vars.current_profession]

    for attribute in atts:
        color = vars.profession_row_colors[vars.current_profession].to_tuple_normalized()
        if attribute == vars.current_attribute:
            PyImGui.push_style_color(PyImGui.ImGuiCol.Button,        (color[0], color[1], color[2], 100/255))
        else:
            PyImGui.push_style_color(PyImGui.ImGuiCol.Button,        (0, 0, 0, 0))

        PyImGui.push_style_color(PyImGui.ImGuiCol.ButtonHovered, (color[0], color[1], color[2], 125/255))
        PyImGui.push_style_color(PyImGui.ImGuiCol.ButtonActive,  (color[0], color[1], color[2], 150/255))

        if PyImGui.button(vars.attributes_map[attribute], 200, 21):
            vars.current_attribute = attribute

        PyImGui.pop_style_color(3)

    if vars.current_profession not in [1, 6]:
            PyImGui.dummy(200, 21)

    _, end_y = PyImGui.get_cursor_screen_pos()
    EndGroup(start_x, start_y, start_x + 200, end_y)

    # start_x, start_y = BeginGroup(140)
    # end_y = 0

    # vars.current_attr_value = PyImGui.input_int('', vars.current_attr_value)

    # vars.current_attr_value = max(min(vars.current_attr_value, 21), -1)

    # _, end_y = PyImGui.get_cursor_screen_pos()
    # EndGroup(start_x, start_y, start_x + 140, end_y)

def resolve_skill_description(raw_desc: str, skill_id: int, attribute_level: int = 0) -> str:
    """
    Replace all [! ... !] progression tags in a skill description using the correct progression values.
    If attribute_level is given, resolve using that rank.
    If not, resolve as a min–max range from level 0 to 15.
    """

    # Get all progression fields (now supports multiple)
    progressions = Skill.GetProgressionData(skill_id)
    if not progressions:
        return raw_desc

    # Wrap all progressions into known_fields format
    known_fields: list[dict[str, Any]] = [{
        "attribute": attr,
        "field": field_name,
        "values": values_dict
    } for attr, field_name, values_dict in progressions]

    def format_value(v: float) -> str:
        """Format numbers like 20.0 → 20, 17.50 → 17.5"""
        return f"{v:.2f}".rstrip('0').rstrip('.') if '.' in f"{v:.2f}" else str(int(v))

    def match_score(tag_values: list[float], values: dict[int, float]) -> float:
        """Compare tag values to progression data at levels 0, 12, 15"""
        v0 = values.get(0, 0.0)
        v12 = values.get(12, v0)
        v15 = values.get(15, v0)
        if len(tag_values) == 1:
            return abs(tag_values[0] - v15)
        elif len(tag_values) == 2:
            return abs(tag_values[0] - v0) + abs(tag_values[1] - v15)
        elif len(tag_values) == 3:
            return abs(tag_values[0] - v0) + abs(tag_values[1] - v12) + abs(tag_values[2] - v15)
        return float('inf')

    def find_best_field(tag_values: list[float]) -> dict[str, Any]:
        """Find the best matching field based on tag values"""
        best_field = known_fields[0]
        best_score = match_score(tag_values, best_field["values"])

        for field in known_fields[1:]:
            score = match_score(tag_values, field["values"])
            if score < best_score:
                best_score = score
                best_field = field

        return best_field

    def replace_tag(match: re.Match) -> str:
        tag_values = [float(g) for g in match.groups() if g is not None]

        best_field = find_best_field(tag_values)
        values = best_field["values"]

        if attribute_level >= 0:
            level = max(0, min(attribute_level, max(values.keys())))
            resolved_value = values.get(level)
            if resolved_value is None:
                available_levels = sorted(k for k in values if k <= level)
                resolved_value = values[available_levels[-1]] if available_levels else 0.0
            return format_value(resolved_value)
        else:
            # If attribute_level is not set, preserve the tag range
            if len(tag_values) == 1:
                return format_value(tag_values[0])
            elif len(tag_values) == 2:
                return f"{format_value(tag_values[0])}...{format_value(tag_values[1])}"
            else:
                return f"{format_value(tag_values[0])}...{format_value(tag_values[1])}...{format_value(tag_values[2])}"


    # Regex pattern for [!x!], [!x...y!], [!x...y...z!]
    pattern = r'\[\!(\d+(?:\.\d+)?)(?:\.\.\.(\d+(?:\.\d+)?))?(?:\.\.\.(\d+(?:\.\d+)?))?\!\]'
    desc = re.sub(pattern, replace_tag, raw_desc)

    if desc[0] == ' ':
        desc = desc[1:]

    desc = desc.replace('( ', '(')
    return desc

def DrawSkillInfo():
    start_x, start_y = BeginGroup(548)
    end_y = 0

    skill = vars.skill_by_id[vars.current_skill_id]

    PyImGui.dummy(4,4)
    PyImGui.dummy(0,0)
    PyImGui.same_line(0, -1)
    ImGui.DrawTexture(skill.skill_icon, 90, 90)
    PyImGui.same_line(0, -1)

    PyImGui.begin_group()

    PyImGui.dummy(2,1)
    ImGui.push_font('Bold', 16)
    PyImGui.text(skill.name)
    ImGui.pop_font()

    if skill.variable_icon != None:
        PyImGui.same_line(0, -1)
        ImGui.DrawTexture(skill.variable_icon, 16, 16)
    if skill.variable != None:
        PyImGui.same_line(0, -1)
        PyImGui.text(f'{skill.variable}')

    if skill.cost_icon:
        PyImGui.same_line(0, -1)
        ImGui.DrawTexture(skill.cost_icon, 16, 16)
    if skill.cost:
        PyImGui.same_line(0, -1)
        PyImGui.text(f'{skill.cost}')

    if skill.activation:
        PyImGui.same_line(0, -1)
        ImGui.DrawTexture('../Textures/Game UI/Skill Description/activation.png', 16, 16)
    if skill.activation:
        PyImGui.same_line(0, -1)
        PyImGui.text(f'{skill.activation}')

    if skill.recharge:
        PyImGui.same_line(0, -1)
        ImGui.DrawTexture('../Textures/Game UI/Skill Description/recharge.png', 16, 16)
    if skill.recharge:
        PyImGui.same_line(0, -1)
        PyImGui.text(f'{skill.recharge}')


    ImGui.push_font('Bold', 14)
    PyImGui.text(f'{skill.description.split('.', 1)[0]} ({skill.campaign})')
    ImGui.pop_font()
    PyImGui.dummy(0,4)

    PyImGui.text_wrapped(f'{resolve_skill_description(skill.description.split('.', 1)[1], skill.id, vars.current_attr_value)}')

    PyImGui.end_group()

    _, end_y = PyImGui.get_cursor_screen_pos()
    EndGroup(start_x, start_y, start_x + 548, end_y + 4)

    PyImGui.dummy(1,0)

def DrawSkillSelect():
    start_x, start_y = BeginGroup(404)
    end_y = 0
    PyImGui.dummy(0,3)
    PyImGui.begin_child('skill_child', (404, 329),False,PyImGui.WindowFlags.AlwaysVerticalScrollbar)

    if PyImGui.begin_table('skill_table', 10, PyImGui.TableFlags.RowBg, 404, 329):
        PyImGui.table_setup_column('0',  PyImGui.TableColumnFlags.WidthFixed, 29)
        PyImGui.table_setup_column('1',  PyImGui.TableColumnFlags.WidthFixed, 135)
        PyImGui.table_setup_column('2',  PyImGui.TableColumnFlags.WidthFixed, 16)
        PyImGui.table_setup_column('3',  PyImGui.TableColumnFlags.WidthFixed, 16)
        PyImGui.table_setup_column('4',  PyImGui.TableColumnFlags.WidthFixed, 16)
        PyImGui.table_setup_column('5',  PyImGui.TableColumnFlags.WidthFixed, 16)
        PyImGui.table_setup_column('6',  PyImGui.TableColumnFlags.WidthFixed, 16)
        PyImGui.table_setup_column('7',  PyImGui.TableColumnFlags.WidthFixed, 28)
        PyImGui.table_setup_column('8',  PyImGui.TableColumnFlags.WidthFixed, 16)
        PyImGui.table_setup_column('9', PyImGui.TableColumnFlags.WidthFixed, 16)

        for i, skill in enumerate(vars.skill_map[vars.current_profession][vars.current_attribute]):
            PyImGui.table_next_row()

            PyImGui.table_next_column()
            PyImGui.dummy(1,0)
            PyImGui.same_line(0,-1)
            # if ImGui.ImageButtonExtended(f'##{i}', skill.skill_icon, (24, 24), uv0 = (0.0625,0.0625), uv1 = (0.9375, 0.9375), frame_padding = 0):
            #     vars.current_skill_id = skill.id


            if skill.elite:
                PyImGui.push_style_color(PyImGui.ImGuiCol.Button,        (1, 1, 0, 1))
                PyImGui.push_style_color(PyImGui.ImGuiCol.ButtonHovered, (1, 1, 0, 1))
                PyImGui.push_style_color(PyImGui.ImGuiCol.ButtonActive,  (1, 1, 0, 1))
                if ImGui.ImageButtonExtended(f'##{i}', skill.skill_icon, (22, 22), uv0 = (0.0625,0.0625), uv1 = (0.9375, 0.9375), frame_padding = 1):
                    vars.current_skill_id = skill.id
                PyImGui.pop_style_color(3)
            else:
                if ImGui.ImageButtonExtended(f'##{i}', skill.skill_icon, (24, 24), uv0 = (0.0625,0.0625), uv1 = (0.9375, 0.9375), frame_padding = 0):
                    vars.current_skill_id = skill.id


            
            if PyImGui.is_item_hovered() and PyImGui.is_mouse_dragging(0, 1):
                if not vars.drag_data:
                    vars.drag_id = skill.id

            PyImGui.table_next_column()
            PyImGui.dummy(0,7)
            PyImGui.text(f'{skill.name}')

            PyImGui.table_next_column()
            PyImGui.dummy(0,5)
            if skill.variable_icon != None:
                ImGui.DrawTexture(skill.variable_icon, 16, 16)
            PyImGui.table_next_column()
            PyImGui.dummy(0,7)
            if skill.variable != None:
                PyImGui.text(f'{skill.variable}')

            PyImGui.table_next_column()
            PyImGui.dummy(0,5)
            if skill.cost_icon:
                ImGui.DrawTexture(skill.cost_icon, 16, 16)
            PyImGui.table_next_column()
            PyImGui.dummy(0,7)
            if skill.cost:
                PyImGui.text(f'{skill.cost}')

            PyImGui.table_next_column()
            PyImGui.dummy(0,5)
            if skill.activation:
                ImGui.DrawTexture('../Textures/Game UI/Skill Description/activation.png', 16, 16)
            PyImGui.table_next_column()
            PyImGui.dummy(0,7)
            if skill.activation:
                PyImGui.text(f'{skill.activation}')

            PyImGui.table_next_column()
            PyImGui.dummy(0,5)
            if skill.recharge:
                ImGui.DrawTexture('../Textures/Game UI/Skill Description/recharge.png', 16, 16)
            PyImGui.table_next_column()
            PyImGui.dummy(0,7)
            if skill.recharge:
                PyImGui.text(f'{skill.recharge}')

        PyImGui.end_table()

    PyImGui.end_child()
    _, end_y = PyImGui.get_cursor_screen_pos()

    EndGroup(start_x, start_y, start_x + 404, end_y + 4)

    PyImGui.dummy(0,0)

def DrawDragTooltip():
    if vars.drag_id:
        PyImGui.push_style_var2(ImGui.ImGuiStyleVar.WindowPadding, 0,0)
        PyImGui.push_style_var(ImGui.ImGuiStyleVar.WindowBorderSize, 0)

        mouse_pos = PyImGui.get_io().mouse_pos_x, PyImGui.get_io().mouse_pos_y - 30

        PyImGui.set_next_window_pos(*mouse_pos)

        PyImGui.begin_tooltip()
        ImGui.ImageButtonExtended(f'##skilltooltip', vars.skill_by_id[vars.drag_id].skill_icon, (42, 42), 
                                  uv0 = (0.0625,0.0625), uv1 = (0.9375, 0.9375), frame_padding = 0)
        PyImGui.end_tooltip()
        PyImGui.pop_style_var(2)

def Draw():
    global vars

    if not vars.skill_map:
        BuildSkillMap()

    if BeginWindow('Py-ned'):
        # PyImGui.text(str(vars.drag_id))
        # PyImGui.text(str(vars.drag_data))
        # PyImGui.text(str(PyImGui.is_mouse_down(0)))
        DrawSkillbars()
        PyImGui.same_line(0, -1)
        PyImGui.begin_group()
        DrawProfessionSelect()
        PyImGui.same_line(0, -1)
        DrawAttributeSelect()

        DrawSkillSelect()
        PyImGui.end_group()
        #DrawSkillInfo()

        DrawDragTooltip()

        PyImGui.end()
    EndWindow()

    # # drag cleanup
    # if (vars.drag_id or vars.drag_data) and not PyImGui.is_mouse_down(0) and not PyImGui.is_window_hovered():
    #     drag_start = vars.drag_data[0]
    #     vars.skill_table[drag_start[0]][drag_start[1]] = 0
    #     vars.drag_data = []
    #     vars.drag_id = 0

# region main
def main():
    global modules, decoded
    try:
        if Map.IsMapReady() and Party.IsPartyLoaded() and not Map.IsInCinematic() and not UIManager.IsWorldMapShowing():
            Draw()

    except ImportError as e:
        Py4GW.Console.Log('PyBox', f'ImportError encountered: {str(e)}', Py4GW.Console.MessageType.Error)
        Py4GW.Console.Log('PyBox', f'Stack trace: {traceback.format_exc()}', Py4GW.Console.MessageType.Error)
    except ValueError as e:
        Py4GW.Console.Log('PyBox', f'ValueError encountered: {str(e)}', Py4GW.Console.MessageType.Error)
        Py4GW.Console.Log('PyBox', f'Stack trace: {traceback.format_exc()}', Py4GW.Console.MessageType.Error)
    except TypeError as e:
        Py4GW.Console.Log('PyBox', f'TypeError encountered: {str(e)}', Py4GW.Console.MessageType.Error)
        Py4GW.Console.Log('PyBox', f'Stack trace: {traceback.format_exc()}', Py4GW.Console.MessageType.Error)
    except Exception as e:
        Py4GW.Console.Log('PyBox', f'Unexpected error encountered: {str(e)}', Py4GW.Console.MessageType.Error)
        Py4GW.Console.Log('PyBox', f'Stack trace: {traceback.format_exc()}', Py4GW.Console.MessageType.Error)
    finally:
        pass

if __name__ == '__main__':
    main()
# endregion