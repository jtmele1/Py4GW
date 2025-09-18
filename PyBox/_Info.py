# region imports
from Py4GWCoreLib import *
import PyBox._Utils
import re
# endregion

class Variables:
    icon              = IconsFontAwesome5.ICON_INFO_CIRCLE
    is_showing        = False
    queues = [
        'ACTION',
        'LOOT',
        'MERCHANT',
        'SALVAGE',
        'IDENTIFY',  
    ]
    GLOBAL_CACHE._ActionQueueManager
    hovered_item      = 0
    hovered_skill     = 0
    lookup_skill      = 0
    first_run         = True

vars = Variables()

def DrawActionQueue():
    global vars

    if PyImGui.collapsing_header('Action Queue##info'):
        PyImGui.indent(11)
        if PyImGui.begin_tab_bar("InfoTabBar"):
            for queue_name in vars.queues:
                if PyImGui.begin_tab_item(queue_name.capitalize()):
                    action_queue = GLOBAL_CACHE._ActionQueueManager.GetAllActionNames(queue_name)
                    action_history = GLOBAL_CACHE._ActionQueueManager.GetHistoryNames(queue_name)

                    if PyImGui.begin_child("InfoCurrentActions", size=(295, 76), border=True, flags=PyImGui.WindowFlags.HorizontalScrollbar):
                        for action in action_queue:
                            PyImGui.text(f"{action}")
                        PyImGui.end_child()
                        
                    if PyImGui.button("Clear Queue", 96):
                        GLOBAL_CACHE._ActionQueueManager.ResetQueue(queue_name)
                        
                    PyImGui.same_line(0, -1)
                    if PyImGui.button("Clear History", 95):
                        GLOBAL_CACHE._ActionQueueManager.ClearHistory(queue_name)
                     
                    PyImGui.same_line(0, -1)  
                    if PyImGui.button("Copy", 96):
                        PyImGui.set_clipboard_text("\n".join(action_history))
                        
                    if PyImGui.begin_child("InfoHistoryActions", size=(295, 152),border=True, flags=PyImGui.WindowFlags.HorizontalScrollbar):
                        for action in reversed(action_history):
                            PyImGui.text(f"{action}")
                        PyImGui.end_child()
                    PyImGui.end_tab_item() 
            PyImGui.end_tab_bar()
        PyImGui.unindent(11)

def DrawCoroutines():
    if PyImGui.collapsing_header('Coroutines##info'):
        PyImGui.indent(11)
        if PyImGui.button('Clear All##coroutines', 295):
            GLOBAL_CACHE.Coroutines.clear()
        for routine in GLOBAL_CACHE.Coroutines:
            name = routine.__qualname__
            #if PyImGui.button(f'Remove##{name}',height = 12):
            #    ...
            #PyImGui.same_line(0, -1)  
            PyImGui.text(name)
        PyImGui.unindent(11)

def DrawCamera():
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
                PyImGui.text(f'ID: {effect.skill_id} | Attribute Lvl: {effect.attribute_level} | Remaining: {math.floor(effect.time_remaining/1000)}')
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
                PyImGui.text(f'ID: {effect.skill_id} | Attribute Lvl: {effect.attribute_level} | Remaining: {math.floor(effect.time_remaining/1000)}')
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
    global vars

    if PyImGui.collapsing_header('Hovered Item##info'):
        PyImGui.indent(11)
        item_id = GLOBAL_CACHE.Inventory.GetHoveredItemID()

        if item_id:
            vars.hovered_item = item_id

        if vars.hovered_item:
            bag, slot = GLOBAL_CACHE.Inventory.FindItemBagAndSlot(vars.hovered_item)
            bag_name = Bags(bag).name if bag else 'None'
            model_id = GLOBAL_CACHE.Item.GetModelID(vars.hovered_item)
            name = GLOBAL_CACHE.Item.GetName(vars.hovered_item)
            type = GLOBAL_CACHE.Item.GetItemType(vars.hovered_item)
            mods = GLOBAL_CACHE.Item.Customization.Modifiers.GetModifiers(vars.hovered_item)

            PyImGui.input_text('Bag, Slot##item', f'{bag_name} ({bag}), {slot}', PyImGui.InputTextFlags.ReadOnly)
            PyImGui.input_text('Item ID##item', f'{vars.hovered_item}', PyImGui.InputTextFlags.ReadOnly)
            PyImGui.input_text('Model ID##item', f'{model_id}', PyImGui.InputTextFlags.ReadOnly)
            PyImGui.input_text('Name##item', f'{name}', PyImGui.InputTextFlags.ReadOnly)
            PyImGui.input_text('Type##item', f'{type[1]} ({type[0]})', PyImGui.InputTextFlags.ReadOnly)

            if mods:
                PyImGui.text('Mod Structs (identifier, arg1, arg2)')
                for i, mod in enumerate(mods):
                    struct = hex(int(mod.GetModBits(),2))
                    struct = struct[:2] + struct[2:].upper()
                    id   = mod.GetIdentifier()
                    arg1 = mod.GetArg1()
                    arg2 = mod.GetArg2()

                    PyImGui.input_text(f'##{i}itemmods', f'{struct} ({id}, {arg1}, {arg2})', PyImGui.InputTextFlags.ReadOnly)
        PyImGui.unindent(11)

def DrawHoveredSkill():
    global vars

    if PyImGui.collapsing_header('Hovered Skill##info'):
        PyImGui.indent(11)
        id = GLOBAL_CACHE.SkillBar.GetHoveredSkillID()
        
        if id in SkillTextureMap:
            vars.hovered_skill = id
        
        if vars.hovered_skill:
            name = SkillTextureMap[vars.hovered_skill]
            name = re.sub(r'^\[\d+\]\s*-\s*(.*?)\.[^.]+$', r'\1', name, flags=re.IGNORECASE)
            prof = Skill.GetProfession(vars.hovered_skill)
            attr = Skill.Attribute.GetAttribute(vars.hovered_skill)
            type = Skill.GetType(vars.hovered_skill)

            PyImGui.input_text('ID##hskill', f'{vars.hovered_skill}', PyImGui.InputTextFlags.ReadOnly)
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

        id = 0
        if vars.lookup_skill in SkillTextureMap:
            id = vars.lookup_skill

        if id:
            name = SkillTextureMap[id]
            name = re.sub(r'^\[\d+\]\s*-\s*(.*?)\.[^.]+$', r'\1', name, flags=re.IGNORECASE)
        else:
            name = 'No Skill'
        prof = Skill.GetProfession(id)
        attr = Skill.Attribute.GetAttribute(id)
        type = Skill.GetType(id)

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
    if PyBox._Utils.BeginWindow('Info', vars.is_showing):
        PyImGui.indent(1)

        DrawActionQueue()
        DrawCoroutines()
        DrawCamera()
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