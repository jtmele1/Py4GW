# region imports
from Py4GWCoreLib import *
import PyBox._Utils
import random
# endregion

class Variables:
    cache = CacheData()
    heroAI_status = True
    heroAI_icon = IconsFontAwesome5.ICON_USERS
    show_control_panel = False
    expand_chars = [True] * 8

vars = Variables()

def DrawControlPanel():
    global vars

    def DrawBarEffects(player):
        offset = 297
        hex  = False
        cond = False
        ench = False
        wep  = False

        if GLOBAL_CACHE.Agent.IsHexed(player.PlayerID):
            hex  = True
            offset -= 18
        if GLOBAL_CACHE.Agent.IsConditioned(player.PlayerID):
            cond = True
            offset -= 18
        if GLOBAL_CACHE.Agent.IsEnchanted(player.PlayerID):
            ench = True
            offset -= 18
        if GLOBAL_CACHE.Agent.IsWeaponSpelled(player.PlayerID):
            wep  = True
            offset -= 18
        
        if hex:
            PyImGui.same_line(0, -1)
            PyImGui.set_cursor_pos_x(offset)
            offset += 18
            ImGui.DrawTexture(r'PyBox\hp_bar\hex.png', 18, 18)
        if cond:
            PyImGui.same_line(0, -1)
            PyImGui.set_cursor_pos_x(offset)
            offset += 18
            ImGui.DrawTexture(r'PyBox\hp_bar\condition.png', 18, 18)
        if ench:
            PyImGui.same_line(0, -1)
            PyImGui.set_cursor_pos_x(offset)
            offset += 18
            ImGui.DrawTexture(r'PyBox\hp_bar\enchantment.png', 18, 18)
        if wep:
            PyImGui.same_line(0, -1)
            PyImGui.set_cursor_pos_x(offset)
            offset += 18
            ImGui.DrawTexture(r'PyBox\hp_bar\weapon.png', 18, 18)

    def DrawCondensedPlayer(player, i):
        width    = 295
        height   = 18
        fill_c   = Color(50,50,50,255)

        health_p = max(0, player.PlayerHP)
        health_w = math.floor(width*health_p)
        health_c = Color(204,0,0,255)

        # hp
        if health_w == 0:
            if ImGui.colored_button(f'##{player.CharacterName}', fill_c, fill_c, fill_c, width, height):
                vars.expand_chars[i] = not vars.expand_chars[i]
            PyImGui.same_line(4, -1)
        else:
            if ImGui.colored_button(f'##{player.CharacterName}', health_c, health_c, health_c, health_w, height):
                vars.expand_chars[i] = not vars.expand_chars[i]
            PyImGui.same_line(0, -1)
            if health_w < width:
                ImGui.colored_button(f'##{player.CharacterName}', Color(255, 255, 255, 255), Color(255, 255, 255, 255), Color(255, 255, 255, 255), 1, height)
                PyImGui.same_line(0, -1)
                if ImGui.colored_button(f'##{player.CharacterName}', fill_c, fill_c, fill_c, width - health_w - 1, height):
                    vars.expand_chars[i] = not vars.expand_chars[i]
                PyImGui.same_line(0, -1)

        PyImGui.set_cursor_pos_x(4)
        if ImGui.colored_button(f'          {player.CharacterName}', Color(0,0,0,0), Color(0,0,0,0), Color(0,0,0,0), 295, 18):
            vars.expand_chars[i] = not vars.expand_chars[i]

        PyImGui.same_line(4, -1)
        primary, secondary = GLOBAL_CACHE.Agent.GetProfessionsTexturePaths(player.PlayerID)
        ImGui.DrawTexture(rf'..\{primary}', 18, 18)
        PyImGui.same_line(0, -1)
        ImGui.DrawTexture(rf'..\{secondary}', 18, 18)
        DrawBarEffects(player)
        PyImGui.dummy(0,4)

    def DrawPlayer(player, i):
        if PyImGui.button(f'          {player.CharacterName}', 295, 18):
            vars.expand_chars[i] = not vars.expand_chars[i]

        PyImGui.same_line(4, -1)
        primary, secondary = GLOBAL_CACHE.Agent.GetProfessionsTexturePaths(player.PlayerID)
        ImGui.DrawTexture(rf'D:\Games\Guild Wars\Py4GW\{primary}', 18, 18)
        PyImGui.same_line(0, -1)
        ImGui.DrawTexture(rf'D:\Games\Guild Wars\Py4GW\{secondary}', 18, 18)
        # PyImGui.same_line(0, -1)
        # PyImGui.set_cursor_pos_x(6)
        #PyImGui.text('R/Me')
        DrawBarEffects(player)
        PyImGui.dummy(0,4)

    def DrawHPEnergy(player):
        width    = 147
        height   = 13
        fill_c   = Color(50,50,50,255)

        health_p = max(0, player.PlayerHP)
        health_w = math.floor(width*health_p)
        health_r = round(player.PlayerMaxHP*player.PlayerHealthRegen/1.98)
        health_s = str(math.floor(health_p*player.PlayerMaxHP))
        health_c = Color(204,0,0,255)

        energy_p = max(0, player.PlayerEnergy)
        energy_w = math.floor(width*energy_p)
        energy_r = round(player.PlayerMaxEnergy*player.PlayerEnergyRegen/0.33)
        energy_s = str(math.floor(energy_p*player.PlayerMaxEnergy))
        energy_c = Color(30,94,153,255)

        # hp
        if health_w == 0:
            ImGui.colored_button('', fill_c, fill_c, fill_c, width, height)
            PyImGui.same_line(0, -1)
        else:
            ImGui.colored_button('', health_c, health_c, health_c, health_w, height)
            PyImGui.same_line(0, -1)
            if health_w < width:
                ImGui.colored_button('', Color(255, 255, 255, 255), Color(255, 255, 255, 255), Color(255, 255, 255, 255), 1, height)
                PyImGui.same_line(0, -1)
                ImGui.colored_button('', fill_c, fill_c, fill_c, width - health_w - 1, height)
                PyImGui.same_line(0, -1)

        PyImGui.dummy(1, 0)
        PyImGui.same_line(0, -1)

        # energy
        if energy_w == 0:
            ImGui.colored_button('', fill_c, fill_c, fill_c, width, height)
            PyImGui.same_line(0, -1)
        else:
            ImGui.colored_button('', energy_c, energy_c, energy_c, energy_w, height)
            PyImGui.same_line(0, -1)
            if energy_w < width:
                ImGui.colored_button('', Color(255, 255, 255, 255), Color(255, 255, 255, 255), Color(255, 255, 255, 255), 1, height)
                PyImGui.same_line(0, -1)
                ImGui.colored_button('', fill_c, fill_c, fill_c, width - energy_w - 1, height)
                PyImGui.same_line(0, -1)

        PyImGui.push_style_var2(ImGui.ImGuiStyleVar.FramePadding, 3, 0)

        y_cursor = PyImGui.get_cursor_pos_y()

        health_center = 77.5
        x , _ = PyImGui.calc_text_size(health_s)
        PyImGui.set_cursor_pos_x(int(health_center - x/2))
        PyImGui.set_cursor_pos_y(y_cursor - 2)
        PyImGui.text(health_s)

        if health_r > 0:
            PyImGui.same_line(0, -1)
            health_r *= IconsFontAwesome5.ICON_CARET_RIGHT
            ImGui.push_font('Regular', 8)
            PyImGui.set_cursor_pos_x(int(health_center + x/2 + 3))
            PyImGui.set_cursor_pos_y(y_cursor - 1)
            PyImGui.text(f'{health_r}')
            ImGui.pop_font()
            #PyImGui.set_cursor_pos_y(y_cursor)
        elif health_r < 0:
            PyImGui.same_line(0, -1)
            health_r = round(math.fabs(health_r)) * IconsFontAwesome5.ICON_CARET_LEFT
            ImGui.push_font('Regular', 8)
            x1, _ = PyImGui.calc_text_size(health_r)
            PyImGui.set_cursor_pos_x(int(health_center - x/2 - x1 - 2))
            PyImGui.set_cursor_pos_y(y_cursor - 1)
            PyImGui.text(f'{health_r}')
            ImGui.pop_font()
            #PyImGui.set_cursor_pos_y(y_cursor)

        PyImGui.same_line(0, -1)

        energy_center = 225.5
        x , _ = PyImGui.calc_text_size(energy_s)
        PyImGui.set_cursor_pos_x(int(energy_center - x/2))
        PyImGui.set_cursor_pos_y(y_cursor - 2)
        PyImGui.text(energy_s)

        if energy_r > 0:
            PyImGui.same_line(0, -1)
            energy_r *= IconsFontAwesome5.ICON_CARET_RIGHT
            ImGui.push_font('Regular', 8)
            PyImGui.set_cursor_pos_x(int(energy_center + x/2 + 3))
            PyImGui.set_cursor_pos_y(y_cursor - 1)
            PyImGui.text(f'{energy_r}')
            ImGui.pop_font()
            #PyImGui.set_cursor_pos_y(y_cursor)
        elif energy_r < 0:
            PyImGui.same_line(0, -1)
            energy_r = round(math.fabs(energy_r)) * IconsFontAwesome5.ICON_CARET_LEFT
            ImGui.push_font('Regular', 8)
            x1, _ = PyImGui.calc_text_size(energy_r)
            PyImGui.set_cursor_pos_x(int(energy_center - x/2 - x1 - 2))
            PyImGui.set_cursor_pos_y(y_cursor - 1)
            PyImGui.text(f'{energy_r}')
            ImGui.pop_font()
            #PyImGui.set_cursor_pos_y(y_cursor)

        PyImGui.set_cursor_pos_y(y_cursor + 17)
        PyImGui.pop_style_var(1)

    def DrawSkills(player):
        skills = player.Skillbar

        for j, skill_id in enumerate(skills):
            uv0 = 0.0625
            uv1 = 0.9375
            size = 36

            if Skill.Flags.IsElite(skill_id):
                uv0 = 0
                uv1 = 1

            if ImGui.ImageButtonExtended(f'##{i}{skill_id}',f'{GLOBAL_CACHE.Skill.ExtraData.GetTexturePath(skill_id)}',(size, size), uv0 = (uv0, uv0), uv1 = (uv1, uv1), frame_padding = 0):
                GLOBAL_CACHE.ShMem.SendMessage(vars.cache.account_email, player.AccountEmail, SharedCommandType.UseSkill, (j + 1, 0, 0, 0))

            if j < 7:
                PyImGui.same_line(0,-1)
                PyImGui.dummy(1,0)
                PyImGui.same_line(0,-1)

    def DrawEffects(player):
        # max 11
        effects = player.PlayerBuffs

        cols = 0
        effect_spacing = False
        for j, skill_id in enumerate(effects):
            if not skill_id:
                continue
            cols += 1

            if not effect_spacing:
                PyImGui.dummy(0,4)
            effect_spacing = True

            uv0 = 0.0625
            uv1 = 0.9375
            size = 24

            if Skill.Flags.IsElite(skill_id):
                uv0 = 0
                uv1 = 1

            ImGui.ImageButtonExtended(f'##{i}{skill_id}',f'{GLOBAL_CACHE.Skill.ExtraData.GetTexturePath(skill_id)}',(size, size), uv0 = (uv0, uv0), uv1 = (uv1, uv1), frame_padding = 0)

            PyImGui.same_line(0,-1)
            PyImGui.dummy(1,0)
            if j < 11:
                PyImGui.same_line(0,-1)

        if effect_spacing:
            return True
        
        PyImGui.dummy(0,4)
        return False

    if PyBox._Utils.BeginWindow('Party'):
        # if PyImGui.button(IconsFontAwesome5.ICON_USERS):
        #     ToggleHeroAI()

        # if GLOBAL_CACHE.Map.IsExplorable():
        #     if PyImGui.button(IconsFontAwesome5.ICON_TIMES):
        #         ResignAll()

        PyImGui.push_style_var2(ImGui.ImGuiStyleVar.ItemSpacing, 0, 0)
        PyImGui.push_style_var2(ImGui.ImGuiStyleVar.ButtonTextAlign, 0, 0)
        PyImGui.push_style_var2(ImGui.ImGuiStyleVar.FramePadding, 0, 3)
        PyImGui.push_style_color(PyImGui.ImGuiCol.Text, (.9,.9,.9,1))

        player_count = GLOBAL_CACHE.Party.GetPlayerCount()
        for i in range(player_count):
            player = GLOBAL_CACHE.ShMem.GetAccountDataFromPartyNumber(i)
            if not player: continue
            if not player.IsAccount: continue

            if vars.expand_chars[i]:
                DrawPlayer(player, i)
                DrawHPEnergy(player)
                DrawSkills(player)
                if DrawEffects(player) and i < player_count - 1:
                    PyImGui.dummy(0, 0)
                    PyImGui.dummy(0, 4)

                #if i < player_count - 1:
                    # PyImGui.dummy(0,4)
                    # ImGui.colored_button('', Color(255, 255, 255, 128), Color(255, 255, 255, 128), Color(255, 255, 255, 128), 295, 3)
                    #PyImGui.dummy(0,4)
            else:
                DrawCondensedPlayer(player, i)

        PyImGui.pop_style_var(3)
        PyImGui.pop_style_color(1)
        PyImGui.end()

    PyBox._Utils.EndWindow()

def DrawControlPanel1():
    global vars

    def DrawBarEffects(player):
        offset = 297
        hex  = False
        cond = False
        ench = False
        wep  = False

        if GLOBAL_CACHE.Agent.IsHexed(player.PlayerID):
            hex  = True
            offset -= 18
        if GLOBAL_CACHE.Agent.IsConditioned(player.PlayerID):
            cond = True
            offset -= 18
        if GLOBAL_CACHE.Agent.IsEnchanted(player.PlayerID):
            ench = True
            offset -= 18
        if GLOBAL_CACHE.Agent.IsWeaponSpelled(player.PlayerID):
            wep  = True
            offset -= 18
        
        y = 0
        PyImGui.same_line(0, -1)
        if hex or cond or ench or wep:
            y = PyImGui.get_cursor_pos_y() - 3

        if hex:
            PyImGui.set_cursor_pos(offset, y)
            offset += 18
            ImGui.DrawTexture(r'PyBox\hp_bar\hex.png', 18, 18)
        if cond:
            PyImGui.set_cursor_pos(offset, y)
            offset += 18
            ImGui.DrawTexture(r'PyBox\hp_bar\condition.png', 18, 18)
        if ench:
            PyImGui.set_cursor_pos(offset, y)
            offset += 18
            ImGui.DrawTexture(r'PyBox\hp_bar\enchantment.png', 18, 18)
        if wep:
            PyImGui.set_cursor_pos(offset, y)
            offset += 18
            ImGui.DrawTexture(r'PyBox\hp_bar\weapon.png', 18, 18)

    def DrawCondensedPlayer(player, i):
        width    = 295
        height   = 18
        fill_c   = Color(50,50,50,255)

        health_p = max(0, player.PlayerHP)
        health_w = math.floor(width*health_p)
        health_c = Color(204,0,0,255)

        primary, secondary = GLOBAL_CACHE.Agent.GetProfessionShortNames(player.PlayerID)
        lvl = GLOBAL_CACHE.Agent.GetLevel(player.PlayerID)

        y = PyImGui.get_cursor_pos_y()
        # hp
        if health_w == 0:
            if ImGui.colored_button(f'##h{player.CharacterName}', fill_c, fill_c, fill_c, width, height):
                vars.expand_chars[i] = not vars.expand_chars[i]
            PyImGui.same_line(4, -1)
        else:
            if ImGui.colored_button(f'##l{player.CharacterName}', health_c, health_c, health_c, health_w, height):
                vars.expand_chars[i] = not vars.expand_chars[i]
            PyImGui.same_line(0, -1)
            if health_w < width:
                ImGui.colored_button(f'##e{player.CharacterName}', Color(255, 255, 255, 255), Color(255, 255, 255, 255), Color(255, 255, 255, 255), 1, height)
                PyImGui.same_line(0, -1)
                if ImGui.colored_button(f'##{player.CharacterName}', fill_c, fill_c, fill_c, width - health_w - 1, height):
                    vars.expand_chars[i] = not vars.expand_chars[i]
                PyImGui.same_line(0, -1)

        PyImGui.set_cursor_pos(51, y + 1)
        PyImGui.text_colored(player.CharacterName, (0,0,0,1))
        PyImGui.set_cursor_pos(50, y + 3)
        PyImGui.text(player.CharacterName)

        PyImGui.set_cursor_pos(8, y + 4)
        PyImGui.text_colored(f'{primary}/{secondary}{lvl}', (0,0,0,1))
        PyImGui.set_cursor_pos(7, y + 3)
        PyImGui.text(f'{primary}/{secondary}{lvl}')

        DrawBarEffects(player)

        PyImGui.dummy(0, 4)

    def DrawPlayer(player, i):
        if PyImGui.button(f'          {player.CharacterName}', 295, 18):
            vars.expand_chars[i] = not vars.expand_chars[i]

        # PyImGui.same_line(4, -1)
        # primary, secondary = GLOBAL_CACHE.Agent.GetProfessionsTexturePaths(player.PlayerID)
        # ImGui.DrawTexture(primary, 18, 18)
        # PyImGui.same_line(0, -1)
        # ImGui.DrawTexture(secondary, 18, 18)
        PyImGui.same_line(0, -1)
        PyImGui.set_cursor_pos_x(6)
        PyImGui.text('R/Me')
        DrawBarEffects(player)
        PyImGui.dummy(0,4)

    def DrawHPEnergy(player):
        width    = 147
        height   = 13
        fill_c   = Color(50,50,50,255)

        health_p = max(0, player.PlayerHP)
        health_w = math.floor(width*health_p)
        health_r = round(player.PlayerMaxHP*player.PlayerHealthRegen/1.98)
        health_s = str(math.floor(health_p*player.PlayerMaxHP))
        health_c = Color(204,0,0,255)

        energy_p = max(0, player.PlayerEnergy)
        energy_w = math.floor(width*energy_p)
        energy_r = round(player.PlayerMaxEnergy*player.PlayerEnergyRegen/0.33)
        energy_s = str(math.floor(energy_p*player.PlayerMaxEnergy))
        energy_c = Color(30,94,153,255)

        # hp
        if health_w == 0:
            ImGui.colored_button('', fill_c, fill_c, fill_c, width, height)
            PyImGui.same_line(0, -1)
        else:
            ImGui.colored_button('', health_c, health_c, health_c, health_w, height)
            PyImGui.same_line(0, -1)
            if health_w < width:
                ImGui.colored_button('', Color(255, 255, 255, 255), Color(255, 255, 255, 255), Color(255, 255, 255, 255), 1, height)
                PyImGui.same_line(0, -1)
                ImGui.colored_button('', fill_c, fill_c, fill_c, width - health_w - 1, height)
                PyImGui.same_line(0, -1)

        PyImGui.dummy(1, 0)
        PyImGui.same_line(0, -1)

        # energy
        if energy_w == 0:
            ImGui.colored_button('', fill_c, fill_c, fill_c, width, height)
            PyImGui.same_line(0, -1)
        else:
            ImGui.colored_button('', energy_c, energy_c, energy_c, energy_w, height)
            PyImGui.same_line(0, -1)
            if energy_w < width:
                ImGui.colored_button('', Color(255, 255, 255, 255), Color(255, 255, 255, 255), Color(255, 255, 255, 255), 1, height)
                PyImGui.same_line(0, -1)
                ImGui.colored_button('', fill_c, fill_c, fill_c, width - energy_w - 1, height)
                PyImGui.same_line(0, -1)

        PyImGui.push_style_var2(ImGui.ImGuiStyleVar.FramePadding, 3, 0)

        y_cursor = PyImGui.get_cursor_pos_y()

        health_center = 77.5
        x , _ = PyImGui.calc_text_size(health_s)
        PyImGui.set_cursor_pos_x(int(health_center - x/2))
        PyImGui.set_cursor_pos_y(y_cursor - 2)
        PyImGui.text(health_s)

        if health_r > 0:
            PyImGui.same_line(0, -1)
            health_r *= IconsFontAwesome5.ICON_CARET_RIGHT
            ImGui.push_font('Regular', 8)
            PyImGui.set_cursor_pos_x(int(health_center + x/2 + 3))
            PyImGui.set_cursor_pos_y(y_cursor - 1)
            PyImGui.text(f'{health_r}')
            ImGui.pop_font()
            #PyImGui.set_cursor_pos_y(y_cursor)
        elif health_r < 0:
            PyImGui.same_line(0, -1)
            health_r = round(math.fabs(health_r)) * IconsFontAwesome5.ICON_CARET_LEFT
            ImGui.push_font('Regular', 8)
            x1, _ = PyImGui.calc_text_size(health_r)
            PyImGui.set_cursor_pos_x(int(health_center - x/2 - x1 - 2))
            PyImGui.set_cursor_pos_y(y_cursor - 1)
            PyImGui.text(f'{health_r}')
            ImGui.pop_font()
            #PyImGui.set_cursor_pos_y(y_cursor)

        PyImGui.same_line(0, -1)

        energy_center = 225.5
        x , _ = PyImGui.calc_text_size(energy_s)
        PyImGui.set_cursor_pos_x(int(energy_center - x/2))
        PyImGui.set_cursor_pos_y(y_cursor - 2)
        PyImGui.text(energy_s)

        if energy_r > 0:
            PyImGui.same_line(0, -1)
            energy_r *= IconsFontAwesome5.ICON_CARET_RIGHT
            ImGui.push_font('Regular', 8)
            PyImGui.set_cursor_pos_x(int(energy_center + x/2 + 3))
            PyImGui.set_cursor_pos_y(y_cursor - 1)
            PyImGui.text(f'{energy_r}')
            ImGui.pop_font()
            #PyImGui.set_cursor_pos_y(y_cursor)
        elif energy_r < 0:
            PyImGui.same_line(0, -1)
            energy_r = round(math.fabs(energy_r)) * IconsFontAwesome5.ICON_CARET_LEFT
            ImGui.push_font('Regular', 8)
            x1, _ = PyImGui.calc_text_size(energy_r)
            PyImGui.set_cursor_pos_x(int(energy_center - x/2 - x1 - 2))
            PyImGui.set_cursor_pos_y(y_cursor - 1)
            PyImGui.text(f'{energy_r}')
            ImGui.pop_font()
            #PyImGui.set_cursor_pos_y(y_cursor)

        PyImGui.set_cursor_pos_y(y_cursor + 17)
        PyImGui.pop_style_var(1)

    def DrawSkills(player):
        skills = player.Skillbar

        for j, skill_id in enumerate(skills):
            uv0 = 0.0625
            uv1 = 0.9375
            size = 36

            if Skill.Flags.IsElite(skill_id):
                uv0 = 0
                uv1 = 1

            if ImGui.ImageButtonExtended(f'##{i}{skill_id}',f'{GLOBAL_CACHE.Skill.ExtraData.GetTexturePath(skill_id)}',(size, size), uv0 = (uv0, uv0), uv1 = (uv1, uv1), frame_padding = 0):
                GLOBAL_CACHE.ShMem.SendMessage(vars.cache.account_email, player.AccountEmail, SharedCommandType.UseSkill, (j + 1, 0, 0, 0))

            if j < 7:
                PyImGui.same_line(0,-1)
                PyImGui.dummy(1,0)
                PyImGui.same_line(0,-1)

    def DrawEffects(player):
        # max 11
        effects = player.PlayerBuffs

        cols = 0
        effect_spacing = False
        for j, skill_id in enumerate(effects):
            if not skill_id:
                continue
            cols += 1

            if not effect_spacing:
                PyImGui.dummy(0,4)
            effect_spacing = True

            uv0 = 0.0625
            uv1 = 0.9375
            size = 24

            if Skill.Flags.IsElite(skill_id):
                uv0 = 0
                uv1 = 1

            ImGui.ImageButtonExtended(f'##{i}{skill_id}',f'{GLOBAL_CACHE.Skill.ExtraData.GetTexturePath(skill_id)}',(size, size), uv0 = (uv0, uv0), uv1 = (uv1, uv1), frame_padding = 0)

            PyImGui.same_line(0,-1)
            PyImGui.dummy(1,0)
            if j < 11:
                PyImGui.same_line(0,-1)

        if effect_spacing:
            return True
        
        PyImGui.dummy(0,4)
        return False

    if PyBox._Utils.BeginWindow('Party'):
        # if PyImGui.button(IconsFontAwesome5.ICON_USERS):
        #     ToggleHeroAI()

        # if GLOBAL_CACHE.Map.IsExplorable():
        #     if PyImGui.button(IconsFontAwesome5.ICON_TIMES):
        #         ResignAll()

        PyImGui.push_style_var2(ImGui.ImGuiStyleVar.ItemSpacing, 0, 0)
        PyImGui.push_style_var2(ImGui.ImGuiStyleVar.ButtonTextAlign, 0, 0)
        PyImGui.push_style_var2(ImGui.ImGuiStyleVar.FramePadding, 0, 3)
        PyImGui.push_style_color(PyImGui.ImGuiCol.Text, (.9,.9,.9,1))

        player_count = GLOBAL_CACHE.Party.GetPlayerCount()
        for i in range(player_count):
            player = GLOBAL_CACHE.ShMem.GetAccountDataFromPartyNumber(i)
            if not player: continue
            if not player.IsAccount: continue

            # if vars.expand_chars[i]:
            #     DrawPlayer(player, i)
            #     DrawHPEnergy(player)
            #     DrawSkills(player)
            #     if DrawEffects(player) and i < player_count - 1:
            #         PyImGui.dummy(0, 0)
            #         PyImGui.dummy(0, 4)

            #     #if i < player_count - 1:
            #         # PyImGui.dummy(0,4)
            #         # ImGui.colored_button('', Color(255, 255, 255, 128), Color(255, 255, 255, 128), Color(255, 255, 255, 128), 295, 3)
            #         #PyImGui.dummy(0,4)
            # else:
            DrawCondensedPlayer(player, i)

        PyImGui.pop_style_var(3)
        PyImGui.pop_style_color(1)
        PyImGui.end()

    PyBox._Utils.EndWindow()

def MapCheck(self_account, candidate):
    if (candidate.MapID == self_account.MapID and
        candidate.MapRegion == self_account.MapRegion and
        candidate.MapDistrict == self_account.MapDistrict):
        return True
    return False
    
def PartyCheck(self_account, candidate):
    if self_account.PartyID == candidate.PartyID:
        return True
    return False

def ToggleControlPanel():
    global vars

    vars.show_control_panel = not vars.show_control_panel

def ToggleHeroAI():
    global vars

    accounts = GLOBAL_CACHE.ShMem.GetAllAccountData()
    sender_email = vars.cache.account_email
    if vars.heroAI_status:
        vars.heroAI_icon = IconsFontAwesome5.ICON_USERS_SLASH
        PyBox._Utils.SendInfoChat('Disabling HeroAI.')
        for account in accounts:
            GLOBAL_CACHE.ShMem.SendMessage(sender_email, account.AccountEmail, SharedCommandType.DisableHeroAI, (0,0,0,0))
    else:
        vars.heroAI_icon = IconsFontAwesome5.ICON_USERS
        PyBox._Utils.SendInfoChat('Enabling HeroAI.')
        for account in accounts:
            GLOBAL_CACHE.ShMem.SendMessage(sender_email, account.AccountEmail, SharedCommandType.EnableHeroAI, (0,0,0,0))
    vars.heroAI_status = not vars.heroAI_status

def SummonTeam():
    global vars
    account_email = GLOBAL_CACHE.Player.GetAccountEmail()
    self_account = GLOBAL_CACHE.ShMem.GetAccountDataFromEmail(account_email)
    accounts = GLOBAL_CACHE.ShMem.GetAllAccountData()
        
    for account in accounts:
        if account.AccountEmail == account_email or MapCheck(self_account, account):
            continue

        GLOBAL_CACHE.ShMem.SendMessage(account_email, account.AccountEmail, SharedCommandType.LeaveParty, (0,0,0,0))
        yield from Routines.Yield.wait(100)
        GLOBAL_CACHE.ShMem.SendMessage(account_email, account.AccountEmail, SharedCommandType.TravelToMap, 
                                       (self_account.MapID,self_account.MapRegion,self_account.MapDistrict,0))

    arrived = False
    timer = Timer()
    timer.Start()
    while not arrived:
        arrived = True
        yield from Routines.Yield.wait(500)
        if timer.HasElapsed(10000):
            break

        for account in accounts:
            if account.AccountEmail == account_email:
                continue

            if not MapCheck(self_account, account):
                arrived = False

    for account in accounts:
        if account.AccountEmail == account_email or PartyCheck(self_account, account):
            continue

        GLOBAL_CACHE.Party.Players.InvitePlayer(account.CharacterName)
        yield from Routines.Yield.wait(500)
        GLOBAL_CACHE.ShMem.SendMessage(account_email, account.AccountEmail,SharedCommandType.InviteToParty, (self_account.PlayerID,0,0,0))

def GatherTeam():
    PyBox._Utils.SendInfoChat('Summoning team.')
    GLOBAL_CACHE.Coroutines.append(SummonTeam())

def ResignAll():
    global vars

    accounts = GLOBAL_CACHE.ShMem.GetAllAccountData()
    sender_email = vars.cache.account_email
    PyBox._Utils.SendInfoChat('Resigning...')
    for account in accounts:
        GLOBAL_CACHE.ShMem.SendMessage(sender_email, account.AccountEmail, SharedCommandType.Resign, (0,0,0,0))

def DrawPartyWindow():
    global vars

    frame_id = UIManager.GetFrameIDByHash(3332025202)
    
    if not UIManager.FrameExists(frame_id):
        return
    
    left, top, _, _ = UIManager.GetFrameCoords(frame_id)
    PyImGui.set_next_window_pos(left + 160, top - 3)

    if PyBox._Utils.BeginHiddenWindow('PartyControls'):
        if GLOBAL_CACHE.Map.IsExplorable():
            widgets = [(IconsFontAwesome5.ICON_LIST , 'Control Panel', ToggleControlPanel), 
                       (vars.heroAI_icon            , 'Follow'       , ToggleHeroAI),
                       (IconsFontAwesome5.ICON_TIMES, 'Resign'       , ResignAll)]
        else:
            widgets = [(IconsFontAwesome5.ICON_LIST , 'Control Panel', ToggleControlPanel), 
                       (vars.heroAI_icon            , 'Follow'       , ToggleHeroAI),
                       (IconsFontAwesome5.ICON_ARROWS_DOWN_TO_PEOPLE, 'Gather Team', GatherTeam)]

        for icon, name, func in widgets:
            if PyImGui.button(f'{icon}##visible'):
                func()
            PyImGui.same_line(0.0, 0)

    PyImGui.end()

    PyBox._Utils.EndHiddenWindow()

def Update():
    global vars

    if PyBox._Utils.CanDraw():
        DrawPartyWindow()
        if vars.show_control_panel:
            DrawControlPanel()