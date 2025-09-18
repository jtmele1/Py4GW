# region imports
from Py4GWCoreLib import *
import PyBox._Utils
import ctypes

user32 = ctypes.WinDLL("user32", use_last_error=True)
# endregion

class SkillBarPlus:
    ini = IniHandler(os.path.join(os.path.normpath(os.path.dirname(os.path.abspath(__file__))), 'Skillbar +.ini'))
    
    class SkillsPlus:
        overlay         = PyOverlay.Overlay()
        skill_ids       = []
        coords          = []
        font_size       = 40
        draw_bg         = True
        bg_default      = Utils.RGBToColor(0, 255, 0, 50)
        bg_near         = Utils.RGBToColor(255, 0, 0, 150)
        near_threshold  = 3
        draw_duration   = False
        duration_font   = 16
        duration_bg     = Utils.RGBToColor(0, 0, 0, 255)
        duration_bar    = Utils.RGBToColor(100, 100, 100, 255)
        duration_offset = 0
        duration_bar_height = 20
        skill_height = 100

        def Clear(self):
            self.coords = []

        def GetSkillFrames(self):
            for i in range(8):
                frame_id = UIManager.GetChildFrameID(641635682, [i])
                if not UIManager.FrameExists(frame_id): 
                    continue
                coords = UIManager.GetFrameCoords(frame_id)
                self.coords.append(coords)

            if len(self.coords) < 8:
                self.coords = []

        def DrawText(self, caption, text, x, y, w, h):
            PyImGui.set_next_window_pos(x, y)
            PyImGui.set_next_window_size(w, h)
            
            flags=(PyImGui.WindowFlags.NoCollapse        | 
                   PyImGui.WindowFlags.NoTitleBar        |
                   PyImGui.WindowFlags.NoScrollbar       |
                   PyImGui.WindowFlags.NoScrollWithMouse |
                   PyImGui.WindowFlags.NoBackground      |
                   PyImGui.WindowFlags.NoMouseInputs     |
                   PyImGui.WindowFlags.AlwaysAutoResize) 
            
            PyImGui.push_style_var(ImGui.ImGuiStyleVar.WindowRounding, 0)
            PyImGui.push_style_var(ImGui.ImGuiStyleVar.WindowBorderSize, 0)
            PyImGui.push_style_var2(ImGui.ImGuiStyleVar.WindowPadding, 0, 0)
            PyImGui.push_style_color(PyImGui.ImGuiCol.Text, (1,1,1,1))
            
            if PyImGui.begin(caption, flags):
                PyImGui.text(text)
            PyImGui.end()

            PyImGui.pop_style_var(3)
            PyImGui.pop_style_color(1)

        def DrawBackground(self, coords, color):
            left, top, right, bottom = coords
            self.overlay.DrawQuadFilled(PyOverlay.Point2D(left,top),
                                        PyOverlay.Point2D(right,top),
                                        PyOverlay.Point2D(right,bottom),
                                        PyOverlay.Point2D(left,bottom),
                                        color)
            
        def DrawDurationBar(self, id, coords, duration, remaining):
            ImGui.push_font("Regular", self.duration_font)

            percentage = remaining/duration
            remaining = math.floor(remaining) if remaining > 1 else round(remaining,1)
                
            text_width, text_height = PyImGui.calc_text_size(str(remaining))

            left, top, right, bottom = coords
            self.skill_height = bottom - top
            top += self.duration_offset
            bottom = top + int(text_height*.75 + 4)
            self.duration_bar_height = bottom - top
            self.overlay.DrawQuadFilled(PyOverlay.Point2D(left,top),
                                        PyOverlay.Point2D(right,top),
                                        PyOverlay.Point2D(right,bottom + 2),
                                        PyOverlay.Point2D(left,bottom + 2),
                                        self.duration_bg)
            
            bar_length = int(((right - 1) - (left + 1))*percentage)
            self.overlay.DrawQuadFilled(PyOverlay.Point2D(left + 1,top + 1),
                                        PyOverlay.Point2D(left + bar_length,top + 1),
                                        PyOverlay.Point2D(left + bar_length,bottom + 1),
                                        PyOverlay.Point2D(left + 1,bottom + 1),
                                        self.duration_bar)
            
            width = right - left
            height = bottom - top
            text_width = text_width + 4
            text_height = text_height*.75 + 4

            self.DrawText(id, str(remaining), left + (width - text_width)/2, 3 + top + (height - text_height)/2, text_width, text_height)

            ImGui.pop_font()

        def Draw(self):
            self.overlay.BeginDraw()

            if not self.coords: return

            for i in range(8):
                if self.draw_bg or self.draw_duration:
                    skill_id = GLOBAL_CACHE.SkillBar.GetSkillIDBySlot(i+1)
                    duration = 0
                    remaining = 0
                    for effect in GLOBAL_CACHE.Effects.GetEffects(GLOBAL_CACHE.Player.GetAgentID()):
                        if effect.skill_id == skill_id:
                            duration = effect.duration
                            remaining = effect.time_remaining/1000
                            break

                    if remaining and remaining < 50000:
                        if self.draw_bg:
                            color = self.bg_near
                            if remaining > self.near_threshold + 1:
                                color = self.bg_default
                            elif remaining > self.near_threshold:
                                bg_color = tuple(int(c * 255) for c in Utils.ColorToTuple(self.bg_default))
                                near_color = tuple(int(c * 255) for c in Utils.ColorToTuple(self.bg_near))
                                amount = 1 - (remaining - self.near_threshold)
                                color = Color(*bg_color).shift(Color(*near_color), amount).to_color()


                            self.DrawBackground(self.coords[i], color)

                        if self.draw_duration:
                            self.DrawDurationBar(f'duration{i}', self.coords[i], duration, remaining)

                recharge = GLOBAL_CACHE.SkillBar.GetSkillData(i+1).get_recharge/1000
                recharge = math.floor(recharge) if recharge > 1 else round(recharge,1)
                if 1000 > recharge > 0:
                    left, top, right, bottom = self.coords[i]

                    width = right - left
                    height = bottom - top

                    ImGui.push_font("Regular", self.font_size)
                    
                    text_width, text_height = PyImGui.calc_text_size(str(recharge))
                    text_width = text_width
                    text_height = text_height*.75

                    self.DrawText(f'skill{i}', str(recharge), left + (width - text_width)/2, top + (height - text_height)/2, text_width, text_height)

                    ImGui.pop_font()

            self.overlay.EndDraw()

        def Config(self):
            if PyImGui.tree_node(f'Skillbar##node'):
                self.font_size = PyImGui.slider_int('Font Size##Skillbar',  self.font_size,  10, 100)
                self.draw_bg = PyImGui.checkbox('Draw Background Colors', self.draw_bg)
                if self.draw_bg:
                    self.bg_default = Utils.TupleToColor(PyImGui.color_edit4('Under Skill Effect', Utils.ColorToTuple(self.bg_default)))
                    self.bg_near = Utils.TupleToColor(PyImGui.color_edit4('Skill Effect Nearly Expired', Utils.ColorToTuple(self.bg_near)))
                    self.near_threshold = PyImGui.input_int('Nearly Expired Threshold (s)', self.near_threshold)

                self.draw_duration = PyImGui.checkbox('Draw Effect Durations on Skillbar', self.draw_duration)
                if self.draw_duration:
                    self.duration_font   = PyImGui.slider_int('Font Size##EffectDuration',  self.duration_font,  4, 30)
                    self.duration_bg     = Utils.TupleToColor(PyImGui.color_edit4('Duration Bar Background', Utils.ColorToTuple(self.duration_bg)))
                    self.duration_bar    = Utils.TupleToColor(PyImGui.color_edit4('Duration Bar Foreground', Utils.ColorToTuple(self.duration_bar)))
                    self.duration_offset = PyImGui.slider_int('Duration Bar Y Offset',  self.duration_offset,  -self.duration_bar_height - 1, self.skill_height)
                PyImGui.tree_pop()

    class EffectsPlus:
        font_size = 20
        bg_color  = Utils.RGBToColor(0, 0, 0, 150)

        def DrawText(self, caption, text, x, y, w, h):
            PyImGui.set_next_window_pos(x, y)
            PyImGui.set_next_window_size(w, h)
            
            flags=(PyImGui.WindowFlags.NoCollapse        | 
                   PyImGui.WindowFlags.NoTitleBar        |
                   PyImGui.WindowFlags.NoScrollbar       |
                   PyImGui.WindowFlags.NoScrollWithMouse |
                   PyImGui.WindowFlags.AlwaysAutoResize) 
            
            PyImGui.push_style_color(PyImGui.ImGuiCol.WindowBg, Utils.ColorToTuple(self.bg_color))
            PyImGui.push_style_var(ImGui.ImGuiStyleVar.WindowRounding, 0)
            PyImGui.push_style_var(ImGui.ImGuiStyleVar.WindowBorderSize, 0)
            PyImGui.push_style_var2(ImGui.ImGuiStyleVar.WindowPadding, 2, 2)
            
            if PyImGui.begin(caption, flags):
                PyImGui.text(text)
            PyImGui.end()

            PyImGui.pop_style_color(1)
            PyImGui.pop_style_var(3)

        def Draw(self):
            active = []

            for effect in GLOBAL_CACHE.Effects.GetEffects(GLOBAL_CACHE.Player.GetAgentID()):
                frame_id = UIManager.GetChildFrameID(1726357791, [effect.skill_id + 4])
                if not UIManager.FrameExists(frame_id): 
                    continue

                time_remaining = effect.time_remaining/1000
                if time_remaining > 30*60:
                    continue
                time_remaining = math.floor(time_remaining) if time_remaining > 1 else round(time_remaining,1)

                active.append((effect.skill_id, frame_id, time_remaining))

            unique_ids = set([act[0] for act in active])

            for skill_id in unique_ids:
                filtered = [act for act in active if act[0] == skill_id]
                newest = max(filtered, key=lambda act: act[2])
                effect, frame_id, time_remaining = newest

                _, _, right, bottom = UIManager.GetFrameCoords(frame_id)

                ImGui.push_font("Regular", self.font_size)
                time_remaining = str(time_remaining)
                text_width, text_height = PyImGui.calc_text_size(time_remaining)
                text_width = text_width + 4
                text_height = text_height*.75 + 4

                self.DrawText(f'effect{skill_id}', time_remaining, right - text_width, bottom - text_height, text_width, text_height)

                ImGui.pop_font()

        def Config(self):
            if PyImGui.tree_node(f'Effects'):
                self.font_size = PyImGui.slider_int('Font Size##Effects',  self.font_size,  5, 50)
                self.bg_color = Utils.TupleToColor(PyImGui.color_edit4('Background', Utils.ColorToTuple(self.bg_color)))
                PyImGui.tree_pop()

    class AutoCast:
        action_queue = ActionQueueManager()
        enable_click = True
        slots = [False]*8
        cast_timer = Timer()
        cast_timer.Start()
        click_timer = Timer()
        click_timer.Start()

        def CanQueue(self, slot):
            return self.cast_timer.HasElapsed(150) and Routines.Checks.Skills.IsSkillSlotReady(slot) and Routines.Checks.Skills.CanCast()

        def Cast(self):
            for i in range(8):
                if self.slots[i] and self.CanQueue(i + 1):
                    player_id = GLOBAL_CACHE.Player.GetAgentID()
                    skill_id = GLOBAL_CACHE.SkillBar.GetSkillIDBySlot(i + 1)
                    if (Routines.Checks.Skills.HasEnoughEnergy(player_id, skill_id)     and 
                        Routines.Checks.Skills.HasEnoughAdrenaline(player_id, skill_id) and 
                        Routines.Checks.Skills.HasEnoughLife(player_id, skill_id)):
                        self.cast_timer.Reset()
                        self.action_queue.AddAction('ACTION',SkillBar.UseSkill, i + 1)

        def Config(self):
            if PyImGui.tree_node(f'Auto Cast'):
                self.enable_click = PyImGui.checkbox('Enable alt + right click on a skillbar skill to toggle autocasting.', self.enable_click)

                icon_size = 42
                offset = icon_size + 34

                for i in range(8):
                    if not Map.IsMapReady(): return
                    if self.slots[i]:
                        PyImGui.push_style_color(PyImGui.ImGuiCol.Button,        (0, 0.70, 0, 1))
                        PyImGui.push_style_color(PyImGui.ImGuiCol.ButtonHovered, (0, 0.85, 0, 1))
                        PyImGui.push_style_color(PyImGui.ImGuiCol.ButtonActive,  (0, 0.90, 0, 1))
                    else:
                        PyImGui.push_style_color(PyImGui.ImGuiCol.Button,        (.5, .5, .5, 0.3))
                        PyImGui.push_style_color(PyImGui.ImGuiCol.ButtonHovered, (.5, .5, .5, 0.4))
                        PyImGui.push_style_color(PyImGui.ImGuiCol.ButtonActive,  (.5, .5, .5, 0.5))

                    texture_path = f'..\\{GLOBAL_CACHE.Skill.ExtraData.GetTexturePath(SkillBar.GetSkillIDBySlot(i + 1))}'
                    if texture_path:
                        if ImGui.ImageButton(f'##slot_{i}', texture_path, icon_size, icon_size, frame_padding = 3):
                            self.slots[i] = not self.slots[i]
                        PyImGui.same_line(offset,-1)
                        offset += icon_size + 10

                    PyImGui.pop_style_color(3)
                PyImGui.tree_pop()

    skills = SkillsPlus()
    effects = EffectsPlus()
    auto = AutoCast()

    def LoadConfig(self):
        self.skills.font_size       = self.ini.read_int('skills', 'font', 40)
        self.skills.draw_bg         = self.ini.read_bool('skills', 'draw_bg', True)
        self.skills.bg_default      = self.ini.read_int('skills', 'color_default', Utils.RGBToColor(0, 255, 0, 50))
        self.skills.bg_near         = self.ini.read_int('skills', 'color_near', Utils.RGBToColor(255, 0, 0, 150))
        self.skills.near_threshold  = self.ini.read_int('skills', 'threshold',3)
        self.skills.draw_duration   = self.ini.read_bool('skills', 'draw_duration', False)
        self.skills.duration_font   = self.ini.read_int('skills', 'duration_font', 16)
        self.skills.duration_bg     = self.ini.read_int('skills', 'duration_bg', Utils.RGBToColor(0, 0, 0, 255))
        self.skills.duration_bar    = self.ini.read_int('skills', 'duration_bar', Utils.RGBToColor(100, 100, 100, 255))
        self.skills.duration_offset = self.ini.read_int('skills', 'duration_offset', 0)

        self.effects.font_size      = self.ini.read_int('effects', 'font', 20)
        self.effects.bg_color       = self.ini.read_int('effects', 'color', Utils.RGBToColor(0, 0, 0, 150))

        self.auto.enable_click      = self.ini.read_bool('auto', 'enable_click', False)

    def SaveConfig(self):
        self.ini.write_key('skills', 'font', str(self.skills.font_size))
        self.ini.write_key('skills', 'draw_bg', str(self.skills.draw_bg))
        self.ini.write_key('skills', 'color_default', str(self.skills.bg_default))
        self.ini.write_key('skills', 'color_near', str(self.skills.bg_near))
        self.ini.write_key('skills', 'threshold', str(self.skills.near_threshold))
        self.ini.write_key('skills', 'draw_duration', str(self.skills.draw_duration))
        self.ini.write_key('skills', 'duration_font', str(self.skills.duration_font))
        self.ini.write_key('skills', 'duration_bg', str(self.skills.duration_bg))
        self.ini.write_key('skills', 'duration_bar', str(self.skills.duration_bar))
        self.ini.write_key('skills', 'duration_offset', str(self.skills.duration_offset))

        self.ini.write_key('effects', 'font', str(self.effects.font_size))
        self.ini.write_key('effects', 'color', str(self.effects.bg_color))

        self.ini.write_key('auto', 'enable_click', str(self.auto.enable_click))

    def DrawConfig(self):
        if PyImGui.collapsing_header('Skillbar'):
            self.skills.Config()
            self.effects.Config()
            self.auto.Config()

#sbp = SkillBarPlus()

skills = SkillBarPlus.SkillsPlus()
effects = SkillBarPlus.EffectsPlus()
auto = SkillBarPlus.AutoCast()
#sbp.LoadConfig()

def IsKeyPressed(vk_code):
    value = user32.GetAsyncKeyState(vk_code) & 0x8000
    is_value_not_zero = value != 0
    if is_value_not_zero:
        return True
    return False

def DrawConfig():
    if PyImGui.collapsing_header(f'Skillbar'):
        skills.Config()
        effects.Config()
        auto.Config()

class Variables:
    icon              = IconsFontAwesome5.ICON_LIST
    can_show_button   = False
    is_showing_button = False
    is_showing        = False
    is_snappable      = False
    offset_x          = 0
    offset_y          = 0
    pos_x             = 500
    pos_y             = 500

vars = Variables()

# class SkillData:
#     recharge = 0
#     max_recharge = 0

# skill_data = [SkillData() for i in range(1,9)]

# def DrawSkillBar():
#     global skill_data

#     def GetPointOnSquare(angle, size):
#         l = math.fabs(math.tan(math.radians(angle))*size/2)

#         return l

#         if angle > 315 or angle <= 45:
#             y = size/2
#             x = y / math.tan(math.radians(angle))
#         elif 135 >= angle > 45:
#             x = -size/2
#             y = x * math.tan(math.radians(angle))
#         elif 225 >= angle > 135:
#             x = -size/2
#             y = x * math.tan(math.radians(angle))
#         else:
#             x = size/2
#             y = x * math.tan(math.radians(angle))

#         return x, y

#     def DrawRecharge(slot, x, y, size):
#         global skill_data

#         recharge = GLOBAL_CACHE.SkillBar.GetSkillData(slot).get_recharge/1000

#         if recharge > 0:
#             x += size*(slot-1)
#             y += 5

#             skill_data[slot-1].recharge = recharge
#             if not skill_data[slot-1].max_recharge:
#                 skill_data[slot-1].max_recharge = recharge

#             recharge_fraction = 1 - skill_data[slot-1].recharge/skill_data[slot-1].max_recharge
            
#             if recharge_fraction < 0.75:
#                 # draw top left half
#                 x1 = x
#                 x2 = x1 + size/2
#                 y1 = y
#                 y2 = y1 + size/2

#                 PyImGui.draw_list_add_quad_filled(x1, y1, x2, y1, x2 ,y2, x1, y2, Utils.RGBToColor(0,0,0,200)) 

#                 if recharge_fraction > 0.5:
#                     ...
                
#             if recharge_fraction < 0.5:
#                 # draw top left half
#                 x1 = x
#                 x2 = x1 + size/2
#                 y1 = y + size/2
#                 y2 = y1 + size/2

#                 PyImGui.draw_list_add_quad_filled(x1, y1, x2, y1, x2 ,y2, x1, y2, Utils.RGBToColor(0,0,0,200))

#                 if recharge_fraction > 0.25:
#                     ...
            
#             if recharge_fraction < 0.25:
#                 # draw top left half
#                 x1 = x + size/2
#                 x2 = x1 + size/2
#                 y1 = y + size/2
#                 y2 = y1 + size/2
                
#                 PyImGui.draw_list_add_quad_filled(x1, y1, x2, y1, x2 ,y2, x1, y2, Utils.RGBToColor(0,0,0,200))

#                 if recharge_fraction < 0.125:
#                     l = GetPointOnSquare(360*recharge_fraction, size)

#                     xa = x + size/2
#                     ya = y + size/2

#                     xb = x + size
#                     yb = y + size/2

#                     xc = x + size
#                     yc = y

#                     xd = x + size/2 + l
#                     yd = y

#                     PyImGui.draw_list_add_quad_filled(xa, ya, xb, yb, xc, yc, xd, yd, Utils.RGBToColor(0,0,0,200))

#             # x1 = x + size*(slot-1)
#             # x2 = x1 + size
#             # y1 = y + 5
#             # y2 = y1 + size
#             # y1 += recharge_fraction*size
#             # PyImGui.draw_list_add_quad_filled(x1, y1, 
#             #                                     x2, y1, 
#             #                                     x2 ,y2,
#             #                                     x1, y2, Utils.RGBToColor(0,0,0,200))

#         else:
#             skill_data[slot-1].recharge = 0
#             skill_data[slot-1].max_recharge = 0

#     def GetTypeOverlay(skill_id):
#         match GLOBAL_CACHE.Skill.GetType(skill_id)[0]:
#             case 6:
#                 return 'enchantment'
#             case 4:
#                 return 'hex'
#             case 25:
#                 return 'wpn_spell'
#             case 14:
#                 match GLOBAL_CACHE.Skill.Data.GetCombo(skill_id):
#                     case 1:
#                         return 'lead_atk'
#                     case 2:
#                         return 'offhand_atk'
#                     case 3:
#                         return 'dual_atk'
#         return None

#     x = 650
#     y = 1100
#     skill_size = 74
#     PyImGui.set_next_window_pos(x,y)

#     if PyBox._Utils.BeginHiddenWindow('SkillbarSkills'):
#         PyImGui.push_style_var2(ImGui.ImGuiStyleVar.ItemSpacing, 0, 0)
#         for i in range(1,9):
#             skill_id = SkillBar.GetSkillIDBySlot(i)
#             path = f'../{GLOBAL_CACHE.Skill.ExtraData.GetTexturePath(skill_id)}'

#             size = skill_size - 2
#             padding = 1
#             color = (0,0,0,1)

#             if GLOBAL_CACHE.Skill.Flags.IsElite(skill_id):
#                 size -= 6
#                 padding = 4
#                 color = (1,1,0,1)

#             PyImGui.push_style_color(PyImGui.ImGuiCol.Button,        color)
#             PyImGui.push_style_color(PyImGui.ImGuiCol.ButtonHovered, color)
#             PyImGui.push_style_color(PyImGui.ImGuiCol.ButtonActive,  color)

#             if ImGui.ImageButtonExtended(f'##skillbarskill{i}',path,(size,size), 
#                                          uv0 = (0.0625,0.0625), uv1 = (0.9375, 0.9375), 
#                                          #int_color = (255, 75, 75, 255),
#                                          frame_padding = padding):
#                 GLOBAL_CACHE.SkillBar.UseSkill(i)

#             overlay = GetTypeOverlay(skill_id)
#             if overlay:
#                 PyImGui.same_line(0,-1)
#                 PyImGui.set_cursor_pos_x((i-1)*skill_size)
#                 ImGui.DrawTexture(f'skill_overlays/{overlay}.png', skill_size, skill_size)

#             DrawRecharge(i, x, y, skill_size)

#             PyImGui.pop_style_color(3)
#             PyImGui.same_line(0,-1)
  
#         PyImGui.pop_style_var(1)
#         PyImGui.end()
#     PyBox._Utils.EndHiddenWindow()


def Update():
    global vars, skills, effects, auto

    try:
        if Map.IsMapLoading():
            skills.Clear()
            auto.slots = [False]*8

        if PyBox._Utils.CanDraw() and Map.IsExplorable():
            # DrawSkillBar()

            if not skills.coords:
                skills.GetSkillFrames()
            skills.Draw()
            effects.Draw()
            auto.Cast()

            if PyImGui.get_io().key_alt and IsKeyPressed(2) and auto.enable_click and auto.click_timer.HasElapsed(200):
                skill_id = SkillBar.GetHoveredSkillID()
                if skill_id:
                    slot = SkillBar.GetSlotBySkillID(skill_id)
                    auto.slots[slot - 1] = not auto.slots[slot - 1]
                    auto.click_timer.Reset()

            for i, coords in enumerate(skills.coords):
                if auto.slots[i]:
                    left, top, right, bottom = coords
                    skills.overlay.BeginDraw()
                    skills.overlay.DrawQuad(PyOverlay.Point2D(left + 1, top + 2),
                                            PyOverlay.Point2D(right - 1, top + 2),
                                            PyOverlay.Point2D(right - 1, bottom),
                                            PyOverlay.Point2D(left + 1, bottom),
                                            Utils.RGBToColor(50,50,255,255),
                                            2)
                    skills.overlay.EndDraw()

    except ImportError as e:
        Py4GW.Console.Log('Compass+', f'ImportError encountered: {str(e)}', Py4GW.Console.MessageType.Error)
        Py4GW.Console.Log('Compass+', f'Stack trace: {traceback.format_exc()}', Py4GW.Console.MessageType.Error)
    except ValueError as e:
        Py4GW.Console.Log('Compass+', f'ValueError encountered: {str(e)}', Py4GW.Console.MessageType.Error)
        Py4GW.Console.Log('Compass+', f'Stack trace: {traceback.format_exc()}', Py4GW.Console.MessageType.Error)
    except TypeError as e:
        Py4GW.Console.Log('Compass+', f'TypeError encountered: {str(e)}', Py4GW.Console.MessageType.Error)
        Py4GW.Console.Log('Compass+', f'Stack trace: {traceback.format_exc()}', Py4GW.Console.MessageType.Error)
    except Exception as e:
        Py4GW.Console.Log('Compass+', f'Unexpected error encountered: {str(e)}', Py4GW.Console.MessageType.Error)
        Py4GW.Console.Log('Compass+', f'Stack trace: {traceback.format_exc()}', Py4GW.Console.MessageType.Error)
    finally:
        pass