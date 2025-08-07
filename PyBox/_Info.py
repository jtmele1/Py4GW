# region imports
from Py4GWCoreLib import *
import PyBox._Utils
# endregion

class Variables:
    icon              = IconsFontAwesome5.ICON_INFO_CIRCLE
    is_showing        = False
    lookup_skill      = 0
    first_run         = True

vars = Variables()

def DrawCameraInfo():
    if PyImGui.collapsing_header('Camera##info'):
        PyImGui.indent(11)
        pos    = GLOBAL_CACHE.Camera.GetPosition()
        target = GLOBAL_CACHE.Camera.GetLookAtTarget()
        yaw    = GLOBAL_CACHE.Camera.GetYaw()
        pitch  = GLOBAL_CACHE.Camera.GetPitch()


        PyImGui.input_text('Position##camera', f'{pos[0]:.0f}, {pos[1]:.0f}, {pos[2]:.0f}', PyImGui.InputTextFlags.ReadOnly)
        PyImGui.input_text('Target##camera', f'{target[0]:.0f}, {target[1]:.0f}, {target[2]:.0f}', PyImGui.InputTextFlags.ReadOnly)
        PyImGui.input_text('Yaw, Pitch##camera', f'{yaw:.2f}, {pitch:.2f}', PyImGui.InputTextFlags.ReadOnly)
        PyImGui.unindent(11)

def DrawPlayer():
    if PyImGui.collapsing_header('Player##info'):
        PyImGui.indent(11)
        cache = GLOBAL_CACHE.Player
        agent = cache.GetAgent().living_agent

        agent_id = cache.GetAgentID()
        pos = cache.GetXY()
        speed = cache.GetAgent().velocity_x, cache.GetAgent().velocity_y
        player_id = agent.player_number
        profession = agent.profession, agent.secondary_profession
        title = cache.GetActiveTitleID()
        effects = GLOBAL_CACHE.Effects.GetEffects(agent_id)
        

        PyImGui.input_text('Agent ID##player', f'{agent_id}', PyImGui.InputTextFlags.ReadOnly)
        PyImGui.input_text('Position##player', f'{pos[0]:.0f}, {pos[1]:.0f}', PyImGui.InputTextFlags.ReadOnly)
        PyImGui.input_text('Speed##player', f'{speed[0]:.0f}, {speed[1]:.0f}', PyImGui.InputTextFlags.ReadOnly)
        PyImGui.input_text('Player ID##player', f'{player_id}', PyImGui.InputTextFlags.ReadOnly)
        PyImGui.input_text('Profession##player', f'{profession[0].GetName()} ({profession[0].ToInt()}), {profession[1].GetName()} ({profession[1].ToInt()})', PyImGui.InputTextFlags.ReadOnly)
        PyImGui.input_text('Title##player', f'{TITLE_NAME[TitleID(title)]} ({title})', PyImGui.InputTextFlags.ReadOnly)

        if effects:
            PyImGui.text('Effects:')
            for effect in effects:
                PyImGui.text(f'id: {effect.skill_id} | attriute lvl: {effect.attribute_level} | remaining: {round(effect.time_remaining/1000)}')
        PyImGui.unindent(11)

def DrawTarget():
    if PyImGui.collapsing_header('Target##info'):
        PyImGui.indent(11)
        target_id = GLOBAL_CACHE.Player.GetTargetID()

        pos = GLOBAL_CACHE.Agent.GetXY(target_id)
        speed = GLOBAL_CACHE.Agent.GetVelocityXY(target_id)
        profession = GLOBAL_CACHE.Agent.GetProfessions(target_id)
        effects = GLOBAL_CACHE.Effects.GetEffects(target_id)
        
        PyImGui.input_text('Agent ID##target', f'{target_id}', PyImGui.InputTextFlags.ReadOnly)
        PyImGui.input_text('Position##target', f'{pos[0]:.0f}, {pos[1]:.0f}', PyImGui.InputTextFlags.ReadOnly)
        PyImGui.input_text('Speed##target', f'{speed[0]:.0f}, {speed[1]:.0f}', PyImGui.InputTextFlags.ReadOnly)
        PyImGui.input_text('Profession##target', f'{profession[0].GetName()} ({profession[0].ToInt()}), {profession[1].GetName()} ({profession[1].ToInt()})', PyImGui.InputTextFlags.ReadOnly)

        if effects:
            PyImGui.text('Effects:')
            for effect in effects:
                PyImGui.text(f'id: {effect.skill_id} | attriute lvl: {effect.attribute_level} | remaining: {round(effect.time_remaining/1000)}')
        PyImGui.unindent(11)

def DrawMap():
    if PyImGui.collapsing_header('Map##info'):
        PyImGui.indent(11)
        name = GLOBAL_CACHE.Map.GetMapName()
        id = GLOBAL_CACHE.Map.GetMapID()
        district = GLOBAL_CACHE.Map.GetDistrict()
        region = GLOBAL_CACHE.Map.GetRegion()
        type = GLOBAL_CACHE.Map.GetRegionType()

        PyImGui.input_text('Name##map', f'{name}', PyImGui.InputTextFlags.ReadOnly)
        PyImGui.input_text('ID##map', f'{id}', PyImGui.InputTextFlags.ReadOnly)
        PyImGui.input_text('District##map', f'{district}', PyImGui.InputTextFlags.ReadOnly)
        PyImGui.input_text('Region##map', f'{region[1]} ({region[0]})', PyImGui.InputTextFlags.ReadOnly)
        PyImGui.input_text('Type##map', f'{type[1]} ({type[0]})', PyImGui.InputTextFlags.ReadOnly)
        PyImGui.unindent(11)

def DrawHoveredItem():
    if PyImGui.collapsing_header('Hovered Item##info'):
        PyImGui.indent(11)
        item_id = GLOBAL_CACHE.Inventory.GetHoveredItemID()

        if item_id:
            slot = GLOBAL_CACHE.Inventory.FindItemBagAndSlot(item_id)
            model_id = GLOBAL_CACHE.Item.GetModelID(item_id)
            name = GLOBAL_CACHE.Item.GetName(item_id)
            type = GLOBAL_CACHE.Item.GetItemType(item_id)
            mods = GLOBAL_CACHE.Item.Customization.Modifiers.GetModifiers(item_id)

            PyImGui.input_text('Bag, Slot##item', f'{slot[0]}, {slot[1]}', PyImGui.InputTextFlags.ReadOnly)
            PyImGui.input_text('Item ID##item', f'{item_id}', PyImGui.InputTextFlags.ReadOnly)
            PyImGui.input_text('Model ID##item', f'{model_id}', PyImGui.InputTextFlags.ReadOnly)
            PyImGui.input_text('Name##item', f'{name}', PyImGui.InputTextFlags.ReadOnly)
            PyImGui.input_text('Type##item', f'{type[1]} ({type[0]})', PyImGui.InputTextFlags.ReadOnly)

            if mods:
                PyImGui.text('Mod Structs (identifier, arg1, arg2)')
                for i, mod in enumerate(mods):
                    struct = hex(int(mod.GetModBits(),2))
                    id   = mod.GetIdentifier()
                    arg1 = mod.GetArg1()
                    arg2 = mod.GetArg2()

                    PyImGui.input_text(f'##{i}itemmods', f'{struct} ({id}, {arg1}, {arg2})', PyImGui.InputTextFlags.ReadOnly)
        PyImGui.unindent(11)

def DrawHoveredSkill():
    if PyImGui.collapsing_header('Hovered Skill##info'):
        PyImGui.indent(11)
        id = GLOBAL_CACHE.SkillBar.GetHoveredSkillID()

        if id:
            name = Skill.GetName(id)
            prof = Skill.GetProfession(id)
            attr = Skill.Attribute.GetAttribute(id)
            type = Skill.GetType(id)

            PyImGui.input_text('ID##hskill', f'{id}', PyImGui.InputTextFlags.ReadOnly)
            PyImGui.input_text('Name##hskill', f'{name}', PyImGui.InputTextFlags.ReadOnly)
            PyImGui.input_text('Profession##hskill', f'{prof[1]} ({prof[0]})', PyImGui.InputTextFlags.ReadOnly)
            PyImGui.input_text('Attribute##hskill', f'{attr.GetName()} ({int(attr.attribute_id)})', PyImGui.InputTextFlags.ReadOnly)
            PyImGui.input_text('Type##hskill', f'{type[1]} ({type[0]})', PyImGui.InputTextFlags.ReadOnly)
        PyImGui.unindent(11)

def DrawLookupSkill():
    global vars

    if PyImGui.collapsing_header('Lookup Skill##info'):
        PyImGui.indent(11)
        vars.lookup_skill = PyImGui.input_int('ID##lskill', vars.lookup_skill)

        name = Skill.GetName(vars.lookup_skill)
        prof = Skill.GetProfession(vars.lookup_skill)
        attr = Skill.Attribute.GetAttribute(vars.lookup_skill)
        type = Skill.GetType(vars.lookup_skill)

        PyImGui.input_text('Name##lskill', f'{name}', PyImGui.InputTextFlags.ReadOnly)
        PyImGui.input_text('Profession##lskill', f'{prof[1]} ({prof[0]})', PyImGui.InputTextFlags.ReadOnly)
        PyImGui.input_text('Attribute##hskill', f'{attr.GetName()} ({int(attr.attribute_id)})', PyImGui.InputTextFlags.ReadOnly)
        PyImGui.input_text('Type##lskill', f'{type[1]} ({type[0]})', PyImGui.InputTextFlags.ReadOnly)
        PyImGui.unindent(11)

def Draw():
    global vars

    if vars.first_run:
        vars.first_run = False
        PyImGui.set_next_window_pos(900, 500)

    PyImGui.set_next_window_size(315, -1)
    if PyBox._Utils.BeginWindow('Info'):
        PyImGui.indent(1)

        DrawCameraInfo()
        DrawPlayer()
        DrawTarget()
        DrawMap()
        DrawHoveredItem()
        DrawHoveredSkill()
        DrawLookupSkill()

        PyImGui.unindent(1)

        PyImGui.end()

    PyBox._Utils.EndWindow()

def Update():
    global vars

    if vars.is_showing and PyBox._Utils.CanDraw():
        Draw()