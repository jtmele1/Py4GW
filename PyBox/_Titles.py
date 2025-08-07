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

    titles = {
        'Hero' : 0,
        'Tyrian Cartographer' : 1,
        'Canthan Cartographer' : 2,
        'Gladiator' : 3,
        'Champion' : 4,
        'Kurzick' : 5,
        'Luxon' : 6,
        'Drunkard' : 7,
        'Survivor' : 9,
        'Kind of a Big Deal' : 10,
        'Tyrian Protector' : 13,
        'Canthan Protector' : 14,
        'Lucky' : 15,
        'Unlucky' : 16,
        'Sunspear' : 17,
        'Elonian Cartographer' : 18,
        'Elonian Protector' : 19,
        'Lightbringer' : 20,
        'Legendary Defender of Ascalon' : 21,
        'Commander' : 22,
        'Gamer' : 23,
        'Tyrian Skill Hunter' : 24,
        'Tyrian Vanquisher' : 25,
        'Canthan Skill Hunter' : 26,
        'Canthan Vanquisher' : 27,
        'Elonian Skill Hunter' : 28,
        'Elonian Vanquisher' : 29,
        'Legendary Cartographer' : 30,
        'Legendary Guardian' : 31,
        'Legendary Skill Hunter' : 32,
        'Legendary Vanquisher' : 33,
        'Sweet Tooth' : 34,
        'Tyrian Guardian' : 35,
        'Canthan Guardian' : 36,
        'Elonian Guardian' : 37,
        'Asuran' : 38,
        'Deldrimor' : 39,
        'Vanguard' : 40,
        'Norn' : 41,
        'Master of the North' : 42,
        'Party' : 43,
        'Zaishen' : 44,
        'Treasure Hunter' : 45,
        'Wisdom' : 46,
        'Codex' : 47,
    }

vars = Variables()

class TitleData:
    def __init__(self, title_id):
        self.title_id = title_id

        data = Player.GetTitle(self.title_id)

        self.percentage_based      = data.is_percentage_based
        self.current_points        = data.current_points/10 if self.percentage_based else data.current_points
        self.current_tier_index    = data.current_title_tier_index
        self.has_tiers             = data.has_tiers
        self.max_rank              = data.max_title_rank
        self.max_tier_index        = data.max_title_tier_index
        self.points_needed_current = data.points_needed_current_rank/10 if self.percentage_based else data.points_needed_current_rank
        self.points_needed_next    = data.points_needed_next_rank/10 if self.percentage_based else data.points_needed_next_rank
        self.props                 = data.props

        self.progress             = self.GetProgress()

    def GetProgress(self):
        if self.points_needed_next >= 4294967295:
            return 1

        if self.current_points >= 0:
            if self.points_needed_next - self.points_needed_current == 0:
                return 1
            
            return (self.current_points - self.points_needed_current)/(self.points_needed_next - self.points_needed_current)
        
        return 0

def Draw():
    global vars

    PyImGui.push_style_var2(ImGui.ImGuiStyleVar.ItemSpacing, 0, 0)
    PyImGui.set_next_window_size(300, -1)
    PyImGui.set_next_window_pos(233, 600)

    if PyBox._Utils.BeginWindow('Titles'):
        PyImGui.push_style_color(PyImGui.ImGuiCol.Button,        (.5, .5, .5, 0.6))
        PyImGui.push_style_color(PyImGui.ImGuiCol.ButtonHovered, (.5, .5, .5, 0.6))
        PyImGui.push_style_color(PyImGui.ImGuiCol.ButtonActive,  (.5, .5, .5, 0.6))

        for title, id in vars.titles.items():
            title_data = TitleData(id)

            if title_data.current_points <= 0:
                continue

            PyImGui.button(f'##{title}', title_data.progress * 292, 24)
            if title_data.progress < 1:
                PyImGui.same_line(0, 0)
                PyImGui.push_style_color(PyImGui.ImGuiCol.Button,        (.5, .5, .5, 0.3))
                PyImGui.push_style_color(PyImGui.ImGuiCol.ButtonHovered, (.5, .5, .5, 0.3))
                PyImGui.push_style_color(PyImGui.ImGuiCol.ButtonActive,  (.5, .5, .5, 0.3))
                PyImGui.button(f'##{title}1', (1-title_data.progress) * 292, 24)
                PyImGui.pop_style_color(3)

            PyImGui.same_line(6, 0)
            PyImGui.text(title)

            if title_data.progress < 1:
                x, _ = PyImGui.calc_text_size(f'{title_data.current_points}/{title_data.points_needed_next}')
                PyImGui.same_line(300 - 6 - x, 0)
                PyImGui.text(f'{title_data.current_points}/{title_data.points_needed_next}')

        PyImGui.pop_style_color(3)
        PyImGui.end()
        

    PyImGui.pop_style_var(1)

    PyBox._Utils.EndWindow()

def Update():
    global vars

    if PyBox._Utils.CanDraw():
        if vars.is_showing:
            Draw()