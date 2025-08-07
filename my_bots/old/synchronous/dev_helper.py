import csv
import inspect
from Py4GWCoreLib import *

class windows:
    main_module = ImGui.WindowModule('Developer Tools', window_name='Developer Tools', window_size=(150, 208),
                                       window_pos=(900,600), window_flags=PyImGui.WindowFlags.AlwaysAutoResize)

def filter_list(array, idx_to_keep):
    return [val for id, val in enumerate(array) if id in idx_to_keep]

def custom_table(title, headers, data):
        """
        Purpose: Display a table using PyImGui.
        Args:
            title (str): The title of the table.
            headers (list of str): The header names for the table columns.
            data (list of values or tuples): The data to display in the table. 
                - If it's a list of single values, display them in one column.
                - If it's a list of tuples, display them across multiple columns.
        Returns: None
        """
        if len(data) == 0:
            return  # No data to display

        first_row = data[0]
        if isinstance(first_row, tuple):
            num_columns = len(first_row)
        else:
            num_columns = 1  # Single values will be displayed in one column

        # Start the table with dynamic number of columns
        if PyImGui.begin_table(title, num_columns, PyImGui.TableFlags.Borders |
                                                   PyImGui.TableFlags.RowBg |
                                                   PyImGui.TableFlags.NoHostExtendX):
            for i, header in enumerate(headers):
                PyImGui.table_setup_column(header)
            PyImGui.table_headers_row()

            for row in data:
                PyImGui.table_next_row()
                if isinstance(row, tuple):
                    for i, cell in enumerate(row):
                        PyImGui.table_set_column_index(i)
                        PyImGui.text(str(cell))
                else:
                    PyImGui.table_set_column_index(0)
                    PyImGui.text(str(row))
            PyImGui.end_table()

def SaveInventory():
    items = dir(Item)
    for item in items:
        if item.startswith('__'): continue

        Py4GW.Console.Log('csv', f'{item} {inspect.isfunction(item)}', Py4GW.Console.MessageType.Info)
    Py4GW.Console.Log('csv', f'{dir(Py4GW.Console.MessageType)}', Py4GW.Console.MessageType.Debug)
    Py4GW.Console.Log('csv', f'{dir(Py4GW.Console.MessageType)}', Py4GW.Console.MessageType.Error)
    Py4GW.Console.Log('csv', f'{dir(Py4GW.Console.MessageType)}', Py4GW.Console.MessageType.Info)
    Py4GW.Console.Log('csv', f'{dir(Py4GW.Console.MessageType)}', Py4GW.Console.MessageType.Notice)
    Py4GW.Console.Log('csv', f'{dir(Py4GW.Console.MessageType)}', Py4GW.Console.MessageType.Performance)
    Py4GW.Console.Log('csv', f'{dir(Py4GW.Console.MessageType)}', Py4GW.Console.MessageType.Success)
    Py4GW.Console.Log('csv', f'{dir(Py4GW.Console.MessageType)}', Py4GW.Console.MessageType.Warning)

def DrawPlayer():
    def DrawGeneral():
        headers = ['Level','Primary [ID]', 'Secondary [ID]',
                   'Health [%]','Energy [%]',
                   'Rotation','Position','Velocity']
        agent = Player.GetAgentID()
        player_data = [Agent.GetLevel(agent),
                       f'{Agent.GetProfessionNames(agent)[0]} [{Agent.GetProfessionIDs(agent)[0]}]',
                       f'{Agent.GetProfessionNames(agent)[1]} [{Agent.GetProfessionIDs(agent)[1]}]',
                       f'{round(Agent.GetMaxHealth(agent)*Agent.GetHealth(agent))} [{round(100*Agent.GetHealth(agent))}]',
                       f'{round(Agent.GetMaxEnergy(agent)*Agent.GetEnergy(agent))} [{round(100*Agent.GetEnergy(agent))}]',
                       round(Agent.GetRotationAngle(agent),3),
                       (round(Agent.GetXY(agent)[0]),round(Agent.GetXY(agent)[1])),
                       (round(Agent.GetVelocityXY(agent)[0]),round(Agent.GetVelocityXY(agent)[1]))]

        data = []
        for i in range(len(headers)):
            data.append(tuple([headers[i],player_data[i]]))

        custom_table('Location', ['Data','Value'], data)

    def DrawAttributes():
        headers = ['Attribute','Base', 'Level']
        data = []
        for attribute in Agent.GetAttributes(Player.GetAgentID()):
            data.append((attribute.GetName(),
                         attribute.level_base,
                         attribute.level))
        custom_table('Skills', headers, data)

    def DrawSkillBar():
        headers = ['Slot','Name','ID','Type',
                   'Profession','Attribute',
                   'Energy','Adrenaline','Activation',
                   'Aftercast','Recharge','Cast']
        data = []
        for i in range(1,9):
            skill_instance = PySkill.Skill(SkillBar.GetSkillIDBySlot(i))
            skill_data = [i,
                        str(skill_instance.id.GetName()).replace('_',' '),
                        skill_instance.id.id,
                        skill_instance.type.GetName(),
                        skill_instance.profession.GetName(),
                        skill_instance.attribute.GetName(),
                        skill_instance.energy_cost,
                        skill_instance.adrenaline,
                        skill_instance.activation,
                        skill_instance.aftercast,
                        skill_instance.recharge]
            data.append(tuple(skill_data))
        custom_table('Skills', headers, data)

    def DrawEffects():
        headers = ['Name','Skill ID','Effect ID','Profession','Attribute [Level]','Duration','Time Remaining','Time Elapsed']
        data = []

        for effect in Effects.GetEffects(Player.GetAgentID()):
            data.append((Skill.GetName(effect.skill_id).replace('_',' '),
                         effect.skill_id,
                         effect.effect_id,
                         Skill.GetProfession(effect.skill_id)[1],
                         f'{Skill.Attribute.GetAttribute(effect.skill_id).GetName()} [{effect.attribute_level}]',
                         effect.duration,
                         FormatTime(effect.time_remaining,mask='mm:ss'),
                         FormatTime(effect.time_elapsed,mask='mm:ss')))
        custom_table('Effects', headers, data)

    tabs = {'General'    : lambda:DrawGeneral(),
            'Attributes' : lambda:DrawAttributes(),
            'SkillBar'   : lambda:DrawSkillBar(),
            'Effects'    : lambda:DrawEffects()}
    for tab, display in tabs.items():
        if PyImGui.collapsing_header(tab):
            display()

def DrawAgents():
    global agent_names, agent_ids

    agent_arrays = {'Allies'               : AgentArray.GetAllyArray(),
                    'Neutrals'             : AgentArray.GetNeutralArray(),
                    'Enemies'              : AgentArray.GetEnemyArray(),
                    'Spirits/Minions/Pets' : AgentArray.GetSpiritPetArray().extend(AgentArray.GetMinionArray()),
                    'Items'                : AgentArray.GetItemArray(),
                    'Gadgets'              : AgentArray.GetGadgetArray()}

    misc = AgentArray.GetAgentArray()
    if agent_arrays['Allies']:
        misc = AgentArray.Manipulation.Subtract(misc,agent_arrays['Allies'])
    if agent_arrays['Neutrals']:
        misc = AgentArray.Manipulation.Subtract(misc,agent_arrays['Neutrals'])
    if agent_arrays['Enemies']:
        misc = AgentArray.Manipulation.Subtract(misc,agent_arrays['Enemies'])
    if agent_arrays['Spirits/Minions/Pets']:
        misc = AgentArray.Manipulation.Subtract(misc,agent_arrays['Spirits/Minions/Pets'])
    if agent_arrays['Items']:
        misc = AgentArray.Manipulation.Subtract(misc,agent_arrays['Items'])
    if agent_arrays['Gadgets']:
        misc = AgentArray.Manipulation.Subtract(misc,agent_arrays['Gadgets'])
    agent_arrays['Misc'] = misc


    headers = ['Agent ID','Name','Gadget ID','Player #','Owner ID','Level','Primary [ID]','Secondary [ID]',
               'Is NPC', 'Has Quest', 'Viewable In Party',
               'HP (%)','Rotation','Position','Velocity','Distance','Model ID', 'Type [ID]','Quantity','Salvageable','PlayerNumber','Rel Angle']
    living_idx = [0,1,3,4,5,6,7,8,10,11,12,13,14,15,21]
    item_idx   = [0,1,13,15,16,17,18,19]
    gadget_idx = [0,1,2,12,13,15]
    misc_idx   = [0,1,3,4,5,6,7,9,10,11,12,13,14,15]

    p_x, p_y = Player.GetXY()

    def get_agent_propeties(agent):
        e_x, e_y = Agent.GetXY(agent)
        properties = [agent,
                      Agent.GetName(agent) if Agent.IsNameReady(agent) else '',
                      Agent.GetGadgetID(agent),
                      Agent.GetPlayerNumber(agent),
                      Agent.GetOwnerID(agent),
                      Agent.GetLevel(agent),
                      f'{Agent.GetProfessionNames(agent)[0]} [{Agent.GetProfessionIDs(agent)[0]}]',
                      f'{Agent.GetProfessionNames(agent)[1]} [{Agent.GetProfessionIDs(agent)[1]}]',
                      Agent.IsNPC(agent),
                      Agent.HasQuest(agent),
                      Agent.CanBeViewedInPartyWindow(agent),
                      round(100*Agent.GetHealth(agent)),
                      round(Agent.GetRotationAngle(agent),3),
                      (round(Agent.GetXY(agent)[0]),round(Agent.GetXY(agent)[1])),
                      (round(Agent.GetVelocityXY(agent)[0]),round(Agent.GetVelocityXY(agent)[1])), 
                      round(Utils.Distance(Agent.GetXY(agent),Player.GetXY())),
                      Item.GetModelID(Agent.GetItemAgent(agent).item_id),
                      f'{Item.GetItemType(Agent.GetItemAgent(agent).item_id)[1]} [{Item.GetItemType(Agent.GetItemAgent(agent).item_id)[0]}]',
                      Item.Properties.GetQuantity(Agent.GetItemAgent(agent).item_id),
                      Item.Usage.IsSalvageable(Agent.GetItemAgent(agent).item_id),
                      Agent.GetPlayerNumber(agent),
                      math.fabs(math.pi - (math.atan2(e_y - p_y, e_x - p_x) - Agent.GetRotationAngle(Player.GetAgentID())))]
        
        for i, row in enumerate(properties):
            if isinstance(row, bool):
                if row:
                    properties[i] = IconsFontAwesome5.ICON_CHECK
                else:
                    properties[i] = IconsFontAwesome5.ICON_TIMES
        return properties

    for type, agent_array in agent_arrays.items():
        if not agent_array: continue

        if PyImGui.collapsing_header(f'{type} ({len(agent_array)})'):
            if type == 'Items':
                filter_idx = item_idx.copy()
            elif type == 'Gadgets':
                filter_idx = gadget_idx.copy()
            elif type == 'Misc':
                filter_idx = misc_idx.copy()
            else:
                filter_idx = living_idx.copy()

            data = []
            for agent in agent_array:
                agent_data= filter_list(get_agent_propeties(agent),filter_idx)
                data.append(tuple(agent_data))
            custom_table(f'Agents{type}', filter_list(headers,filter_idx), data)

    if PyImGui.button("Request Agent Names", PyImGui.get_window_size()[0]-20):
        for agent_id in AgentArray.GetAgentArray():
            Agent.RequestName(agent_id)

def DrawInventory():
    global item_names, item_ids

    headers = ['Slot','Name','Item ID','Model ID','Type [ID]',
               'Rarity [ID]','Quantity','Value',
               'Usable','Undentified','Salvageable',
               'Weapon','Armor','Material','Rare Material']
    general_idx   = [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14]
    equipment_idx = [0,1,2,3,4,5,7,9,10,11,12]
    material_idx  = [0,1,2,3,6,7,14]

    bags = {'Inventory' : [1,2,3,4,5,22],
            'Storage'   : [8,9,10,11,12,13,14,15,16,17,18,19,20,21,6]}

    def get_item_propeties(item):
        properties = [Item.GetSlot(item) + 1,
                      Item.GetName(item) if Item.IsNameReady(item) else '',
                      item,
                      Item.GetModelID(item),
                      f'{Item.GetItemType(item)[1]} [{Item.GetItemType(item)[0]}]',
                      f'{Item.Rarity.GetRarity(item)[1]} [{Item.Rarity.GetRarity(item)[0]}]',
                      Item.Properties.GetQuantity(item),
                      Item.Properties.GetValue(item),
                      Item.Usage.IsUsable(item),
                      not Item.Usage.IsIdentified(item),
                      Item.Usage.IsSalvageable(item),
                      Item.Type.IsWeapon(item),
                      Item.Type.IsArmor(item),
                      Item.Type.IsMaterial(item),
                      Item.Type.IsRareMaterial(item)]
        
        for i, row in enumerate(properties):
            if isinstance(row, bool):
                if row:
                    properties[i] = IconsFontAwesome5.ICON_CHECK
                else:
                    properties[i] = IconsFontAwesome5.ICON_TIMES
        return properties
    
    for name, bag_nums in bags.items():
        if PyImGui.collapsing_header(name):
            for bag_num in bag_nums:
                bags_to_check = ItemArray.CreateBagList(bag_num)
                item_array = ItemArray.GetItemArray(bags_to_check)
                if len(item_array) <= 0: continue

                if PyImGui.tree_node(f'{Bag(bag_num).name.replace('_',' ')} [{len(item_array)}]'):
                    if bag_num not in [5,6,22]:
                        filter_idx = general_idx.copy()
                    elif bag_num in [5,22]:
                        filter_idx = equipment_idx.copy()
                    elif bag_num in [6]:
                        filter_idx = material_idx.copy()

                    data = []
                    for item in item_array:
                        item_data = filter_list(get_item_propeties(item),filter_idx)
                        data.append(tuple(item_data))
                    custom_table(f'Inv{bag_num}', filter_list(headers,filter_idx), data)
                    PyImGui.tree_pop()

    if PyImGui.button('Request Item Names', PyImGui.get_window_size()[0]-20):
        bags_to_check = ItemArray.CreateBagList(*range(1,23))
        for item in ItemArray.GetItemArray(bags_to_check):
            Item.RequestName(item)

    if PyImGui.button('Open Storage', PyImGui.get_window_size()[0]-20):
        Inventory.OpenXunlaiWindow()

    if PyImGui.button('Save to CSV', PyImGui.get_window_size()[0]-20):
        SaveInventory()

def DrawTrader():
    Trading.merchant_instance().update()
    item_arrays = {'Merchant'  : Trading.Merchant.GetOfferedItems(),
                   'Trader'    : Trading.Trader.GetOfferedItems(),
                   'Crafter'   : Trading.Crafter.GetOfferedItems(),
                   'Collector' : Trading.Collector.GetOfferedItems(),}

    headers = ['Item ID','Name','Model ID','Type [ID]',
               'Rarity [ID]','Value',
               'Usable','Undentified','Salvageable',
               'Weapon','Armor','Material','Rare Material']
    # general_idx   = [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14]
    # equipment_idx = [0,1,2,3,4,5,7,9,10,11,12]
    # material_idx  = [0,1,2,3,6,7,14]

    def get_item_propeties(item):
        properties = [item,
                      '?',
                      Item.GetModelID(item),
                      f'{Item.GetItemType(item)[1]} [{Item.GetItemType(item)[0]}]',
                      f'{Item.Rarity.GetRarity(item)[1]} [{Item.Rarity.GetRarity(item)[0]}]',
                      Item.Properties.GetValue(item),
                      Item.Usage.IsUsable(item),
                      not Item.Usage.IsIdentified(item),
                      Item.Usage.IsSalvageable(item),
                      Item.Type.IsWeapon(item),
                      Item.Type.IsArmor(item),
                      Item.Type.IsMaterial(item),
                      Item.Type.IsRareMaterial(item)]
        
        for i, row in enumerate(properties):
            if isinstance(row, bool):
                if row:
                    properties[i] = IconsFontAwesome5.ICON_CHECK
                else:
                    properties[i] = IconsFontAwesome5.ICON_TIMES
        return properties

    for type, item_array in item_arrays.items():
        if not item_array: continue

        if PyImGui.collapsing_header(f'{type} ({len(item_array)})'):
            data = []
            for item in item_array:
                item_data = get_item_propeties(item)
                data.append(tuple(item_data))
            custom_table(f'Trader', headers, data)

def DrawMap():
    headers = ['Name','ID','Instance Type',
               'Uptime','Campaign [ID]','Continent [ID]',
               'Players','Party Size','Mission','Hard Mode']
    vanq_headers = ['Foes Killed', 'Foes to Kill']
    
    map_data = [Map.GetMapName(),
                Map.GetMapID(),
                Map.map_instance().instance_type.GetName(),
                FormatTime(Map.GetInstanceUptime(), mask='hh:mm:ss'),
                f'{Map.GetCampaign()[1]} [{Map.GetCampaign()[0]}]',
                f'{Map.GetContinent()[1]} [{Map.GetContinent()[0]}]',
                Map.GetAmountOfPlayersInInstance(),
                Map.GetMaxPartySize(),
                Map.HasEnterChallengeButton(),
                Party.IsHardMode()]
    

    if Map.IsVanquishable() and Party.IsHardMode():
        headers.extend(vanq_headers)
        map_data.extend([Map.GetFoesKilled(),
                         Map.GetFoesToKill()])
        
    for i, row in enumerate(map_data):
        if isinstance(row, bool):
            if row:
                map_data[i] = IconsFontAwesome5.ICON_CHECK
            else:
                map_data[i] = IconsFontAwesome5.ICON_TIMES
    
    data = []
    for i in range(len(headers)):
        data.append(tuple([headers[i],map_data[i]]))

    custom_table('Map', ['Data','Value'], data)

def DrawCamera():
    headers = ['GetLookAtAgentID','GetMaxDistance','GetYaw','GetPitch','GetCameraZoom','GetYawRightClick','GetYawRightClick2','GetPitchRightClick',
               'GetDistance2','GetAccelerationConstant','GetTimeSinceLastKeyboardRotation','GetTimeSinceLastMouseRotation','GetTimeSinceLastMouseMove','GetTimeSinceLastAgentSelection',
               'GetTimeInTheMap','GetTimeInTheDistrict','GetYawToGo','GetPitchToGo','GetDistanceToGo','GetMaxDistance2','GetPosition','GetCameraPositionToGo',
               'GetCameraPositionInverted','GetCameraPositionInvertedToGo','GetLookAtTarget','GetAtTargetToGo','GetFieldOfView','GetFielsOfView2']
    
    cam_data = [Camera.GetLookAtAgentID(),
                Camera.GetMaxDistance(),
                Camera.GetYaw(),
                Camera.GetPitch(),
                Camera.GetCameraZoom(),
                Camera.GetYawRightClick(),
                Camera.GetYawRightClick2(),
                Camera.GetPitchRightClick(),
                Camera.GetDistance2(),
                Camera.GetAccelerationConstant(),
                Camera.GetTimeSinceLastKeyboardRotation(),
                Camera.GetTimeSinceLastMouseRotation(),
                Camera.GetTimeSinceLastMouseMove(),
                Camera.GetTimeSinceLastAgentSelection(),
                Camera.GetTimeInTheMap(),
                Camera.GetTimeInTheDistrict(),
                Camera.GetYawToGo(),
                Camera.GetPitchToGo(),
                Camera.GetDistanceToGo(),
                Camera.GetMaxDistance2(),
                Camera.GetPosition(),
                Camera.GetCameraPositionToGo(),
                Camera.GetCameraPositionInverted(),
                Camera.GetCameraPositionInvertedToGo(),
                Camera.GetLookAtTarget(),
                Camera.GetAtTargetToGo(),
                Camera.GetFieldOfView(),
                Camera.GetFielsOfView2()]

    data = []
    for i in range(len(headers)):
        data.append(tuple([headers[i],cam_data[i]]))

    custom_table('Camera', ['Data','Value'], data)

def Debug(message, title = 'DEBUG', msg_type = 'Debug'):
    py4gw_msg_type = Py4GW.Console.MessageType.Debug
    if   msg_type == 'Debug':       py4gw_msg_type = Py4GW.Console.MessageType.Debug
    elif msg_type == 'Error':       py4gw_msg_type = Py4GW.Console.MessageType.Error
    elif msg_type == 'Info':        py4gw_msg_type = Py4GW.Console.MessageType.Info
    elif msg_type == 'Notice':      py4gw_msg_type = Py4GW.Console.MessageType.Notice
    elif msg_type == 'Performance': py4gw_msg_type = Py4GW.Console.MessageType.Performance
    elif msg_type == 'Success':     py4gw_msg_type = Py4GW.Console.MessageType.Success
    elif msg_type == 'Warning':     py4gw_msg_type = Py4GW.Console.MessageType.Warning
    Py4GW.Console.Log(title, str(message), py4gw_msg_type)

def DrawWindow():
    global windows

    try:
        if windows.main_module.first_run:    
            PyImGui.set_next_window_pos(windows.main_module.window_pos[0], windows.main_module.window_pos[1])
            windows.main_module.first_run = False

        if PyImGui.begin(windows.main_module.window_name, windows.main_module.window_flags):
            # style
            PyImGui.push_style_color(PyImGui.ImGuiCol.Button,        (.2,.2,.2,1))
            PyImGui.push_style_color(PyImGui.ImGuiCol.ButtonHovered, (.3,.3,.3,1))
            PyImGui.push_style_color(PyImGui.ImGuiCol.ButtonActive,  (.4,.4,.4,1))
            PyImGui.push_style_color(PyImGui.ImGuiCol.Header,        (.2,.2,.2,1))
            PyImGui.push_style_color(PyImGui.ImGuiCol.HeaderActive,  (.2,.2,.2,1))
            PyImGui.push_style_color(PyImGui.ImGuiCol.HeaderHovered, (.3,.3,.3,1))
            PyImGui.push_style_color(PyImGui.ImGuiCol.TabActive,     (.2,.2,.2,1))
            PyImGui.push_style_color(PyImGui.ImGuiCol.TabHovered,    (.3,.3,.3,1))
            if PyImGui.begin_tab_bar(''):

                tabs = {'Player'    : lambda:DrawPlayer(),
                        'Agents'    : lambda:DrawAgents(),
                        'Inventory' : lambda:DrawInventory(),
                        'Trader'    : lambda:DrawTrader(),
                        'Map'       : lambda:DrawMap(),
                        'Camera'    : lambda:DrawCamera()}

                for tab, func in tabs.items():
                    if PyImGui.begin_tab_item(tab):
                        func()
                        PyImGui.end_tab_item()
                PyImGui.end_tab_bar()
            PyImGui.pop_style_color(8)
            PyImGui.end()

    except Exception as e:
        current_function = inspect.currentframe().f_code.co_name
        Py4GW.Console.Log(windows.main_module.module_name, f'Error in {current_function}: {str(e)}', Py4GW.Console.MessageType.Error)
        raise

def main():
    global windows

    try:
        if Party.IsPartyLoaded():
            DrawWindow()
            #Py4GW.Console.Log('DEBUG', dir(Effects.GetEffects(Player.GetAgentID())[0]), Py4GW.Console.MessageType.Error)

    except ImportError as e:
        Py4GW.Console.Log(windows.main_module.module_name, f'ImportError encountered: {str(e)}', Py4GW.Console.MessageType.Error)
        Py4GW.Console.Log(windows.main_module.module_name, f'Stack trace: {traceback.format_exc()}', Py4GW.Console.MessageType.Error)
    except ValueError as e:
        Py4GW.Console.Log(windows.main_module.module_name, f'ValueError encountered: {str(e)}', Py4GW.Console.MessageType.Error)
        Py4GW.Console.Log(windows.main_module.module_name, f'Stack trace: {traceback.format_exc()}', Py4GW.Console.MessageType.Error)
    except TypeError as e:
        Py4GW.Console.Log(windows.main_module.module_name, f'TypeError encountered: {str(e)}', Py4GW.Console.MessageType.Error)
        Py4GW.Console.Log(windows.main_module.module_name, f'Stack trace: {traceback.format_exc()}', Py4GW.Console.MessageType.Error)
    except Exception as e:
        Py4GW.Console.Log(windows.main_module.module_name, f'Unexpected error encountered: {str(e)}', Py4GW.Console.MessageType.Error)
        Py4GW.Console.Log(windows.main_module.module_name, f'Stack trace: {traceback.format_exc()}', Py4GW.Console.MessageType.Error)
    finally:
        pass

if __name__ == '__main__':
    main()