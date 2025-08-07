# region imports
from Py4GWCoreLib import *
import PyBox._Utils
# endregion

class Variables:
    icon              = IconsFontAwesome5.ICON_FEATHER_ALT
    is_showing        = False

    selected_common_mat = 0
    selected_rare_mat = 0
    common_mat_count = 0
    rare_mat_count = 0

    materials = {
        ModelID.Bone                    : ['10 Bones',                    0],
        ModelID.Iron_Ingot              : ['10 Iron Ingots',              0],
        ModelID.Tanned_Hide_Square      : ['10 Tanned Hide Squares',      0],
        ModelID.Scale                   : ['10 Scales',                   0],
        ModelID.Chitin_Fragment         : ['10 Chitin Fragments',         0],
        ModelID.Bolt_Of_Cloth           : ['10 Bolts of Cloth',           0],
        ModelID.Wood_Plank              : ['10 Wood Planks',              0],
        ModelID.Granite_Slab            : ['10 Granite Slabs',            0],
        ModelID.Pile_Of_Glittering_Dust : ['10 Piles of Glittering Dust', 0],
        ModelID.Plant_Fiber             : ['10 Plant Fibers',             0],
        ModelID.Feather                 : ['10 Feathers',                 0],
        ModelID.Fur_Square              : ['Fur Square',                  0],
        ModelID.Bolt_Of_Linen           : ['Bolt of Linen',               0],
        ModelID.Bolt_Of_Damask          : ['Bolt of Damask',              0],
        ModelID.Bolt_Of_Silk            : ['Bolt of Silk',                0],
        ModelID.Glob_Of_Ectoplasm       : ['Glob of Ectoplasm',           0],
        ModelID.Steel_Ingot             : ['Steel Ingot',                 0],
        ModelID.Deldrimor_Steel_Ingot   : ['Deldrimor Steel Ingot',       0],
        ModelID.Monstrous_Claw          : ['Monstrous Claw',              0],
        ModelID.Monstrous_Eye           : ['Monstrous Eye',               0],
        ModelID.Monstrous_Fang          : ['Monstrous Fang',              0],
        ModelID.Ruby                    : ['Ruby',                        0],
        ModelID.Sapphire                : ['Sapphire',                    0],
        ModelID.Diamond                 : ['Diamond',                     0],
        ModelID.Onyx_Gemstone           : ['Onyx Gemstone',               0],
        ModelID.Bone                    : ['Lump of Charcoal',            0],
        ModelID.Lump_Of_Charcoal        : ['Obsidian Shard',              0],
        ModelID.Tempered_Glass_Vial     : ['Tempered Glass Vial',         0],
        ModelID.Leather_Square          : ['Leather Square',              0],
        ModelID.Elonian_Leather_Square  : ['Elonian Leather Square',      0],
        ModelID.Vial_Of_Ink             : ['Vial of Ink',                 0],
        ModelID.Roll_Of_Parchment       : ['Roll of Parchment',           0],
        ModelID.Roll_Of_Vellum          : ['Roll of Vellum',              0],
        ModelID.Spiritwood_Plank        : ['Spiritwood Plank',            0],
        ModelID.Amber_Chunk             : ['Amber Chunk',                 0],
        ModelID.Jadeite_Shard           : ['Jadeite Shard',               0],
    }

    common_mats = {
        '10 Bones'                    : [ModelID.Bone,                    0],
        '10 Iron Ingots'              : [ModelID.Iron_Ingot,              0],
        '10 Tanned Hide Squares'      : [ModelID.Tanned_Hide_Square,      0],
        '10 Scales'                   : [ModelID.Scale,                   0],
        '10 Chitin Fragments'         : [ModelID.Chitin_Fragment,         0],
        '10 Bolts of Cloth'           : [ModelID.Bolt_Of_Cloth,           0],
        '10 Wood Planks'              : [ModelID.Wood_Plank,              0],
        '10 Granite Slabs'            : [ModelID.Granite_Slab,            0],
        '10 Piles of Glittering Dust' : [ModelID.Pile_Of_Glittering_Dust, 0],
        '10 Plant Fibers'             : [ModelID.Plant_Fiber,             0],
        '10 Feathers'                 : [ModelID.Feather,                 0],
    }

    rare_mats = {
        'Fur Square'             : [ModelID.Fur_Square,             0],
        'Bolt of Linen'          : [ModelID.Bolt_Of_Linen,          0],
        'Bolt of Damask'         : [ModelID.Bolt_Of_Damask,         0],
        'Bolt of Silk'           : [ModelID.Bolt_Of_Silk,           0],
        'Glob of Ectoplasm'      : [ModelID.Glob_Of_Ectoplasm,      0],
        'Steel Ingot'            : [ModelID.Steel_Ingot,            0],
        'Deldrimor Steel Ingot'  : [ModelID.Deldrimor_Steel_Ingot,  0],
        'Monstrous Claw'         : [ModelID.Monstrous_Claw,         0],
        'Monstrous Eye'          : [ModelID.Monstrous_Eye,          0],
        'Monstrous Fang'         : [ModelID.Monstrous_Fang,         0],
        'Ruby'                   : [ModelID.Ruby,                   0],
        'Sapphire'               : [ModelID.Sapphire,               0],
        'Diamond'                : [ModelID.Diamond,                0],
        'Onyx Gemstone'          : [ModelID.Onyx_Gemstone,          0],
        'Lump of Charcoal'       : [ModelID.Bone,                   0],
        'Obsidian Shard'         : [ModelID.Lump_Of_Charcoal,       0],
        'Tempered Glass Vial'    : [ModelID.Tempered_Glass_Vial,    0],
        'Leather Square'         : [ModelID.Leather_Square,         0],
        'Elonian Leather Square' : [ModelID.Elonian_Leather_Square, 0],
        'Vial of Ink'            : [ModelID.Vial_Of_Ink,            0],
        'Roll of Parchment'      : [ModelID.Roll_Of_Parchment,      0],
        'Roll of Vellum'         : [ModelID.Roll_Of_Vellum,         0],
        'Spiritwood Plank'       : [ModelID.Spiritwood_Plank,       0],
        'Amber Chunk'            : [ModelID.Amber_Chunk,            0],
        'Jadeite Shard'          : [ModelID.Jadeite_Shard,          0],
    }

vars = Variables()

def BuyMats(items):
    PyBox._Utils.SendInfoChat('Buying materials...')

    item_list = Trading.Trader.GetOfferedItems()

    for model_id, count in items:
        if not count:
            continue

        item_id = 0
        for item in item_list:
            if Item.GetModelID(item) == model_id:
                item_id = item
                break

        if not item_id:
            PyBox._Utils.SendInfoChat(f'Model ID [{model_id}] not found.', color = 'FF0000')
            continue
        
        for i in range(count):
            GLOBAL_CACHE.Trading.Trader.RequestQuote(item_id)

            timer = Timer()
            timer.Start()
            while True:
                yield from Routines.Yield.wait(50)
                cost = Trading.Trader.GetQuotedValue()
                if cost >= 0:
                    break
                
                if timer.HasElapsed(2000):
                    PyBox._Utils.SendInfoChat('Error quoting item, cancelling.', color = 'FF0000')
                    return

            GLOBAL_CACHE.Trading.Trader.BuyItem(item_id, cost)

            timer = Timer()
            timer.Start()
            while True:
                yield from Routines.Yield.wait(50)
                if Trading.IsTransactionComplete():
                    break
                
                if timer.HasElapsed(2000):
                    PyBox._Utils.SendInfoChat('Error buying item, cancelling.', color = 'FF0000')
                    return

def SellMats(items):
    PyBox._Utils.SendInfoChat('Selling materials...')

    bag_list = ItemArray.CreateBagList(Bags.Backpack, Bags.BeltPouch, Bags.Bag1, Bags.Bag2)
    item_list = ItemArray.GetItemArray(bag_list)

    for model_id, count in items:
        if not count:
            continue

        item_id = 0
        for item in item_list:
            if Item.GetModelID(item) == model_id:
                item_id = item
                break

        if not item_id:
            PyBox._Utils.SendInfoChat(f'None of Model ID [{model_id}] found in inventory.', color = 'FF0000')
            continue
        
        for _ in range(count):
            item_list = ItemArray.GetItemArray(bag_list)
            if not item_id in item_list:
                PyBox._Utils.SendInfoChat(f'Not enough of Model ID [{model_id}] to sell.', color = 'FF0000')
                continue
            
            GLOBAL_CACHE.Trading.Trader.RequestSellQuote(item_id)
            
            timer = Timer()
            timer.Start()
            while True:
                yield from Routines.Yield.wait(50)
                cost = Trading.Trader.GetQuotedValue()
                
                if cost >= 0:
                    break

                if timer.HasElapsed(2000):
                    PyBox._Utils.SendInfoChat('Error quoting item, cancelling.', color = 'FF0000')
                    return

            GLOBAL_CACHE.Trading.Trader.SellItem(item_id, cost)

            timer = Timer()
            timer.Start()
            while True:
                yield from Routines.Yield.wait(50)
                if Trading.IsTransactionComplete():
                    break

                if timer.HasElapsed(2000):
                    PyBox._Utils.SendInfoChat('Error selling item, cancelling.', color = 'FF0000')
                    return

def Draw():
    global vars
    
    # common
    PyImGui.push_item_width(190)
    items = list(vars.common_mats.keys())
    if PyBox._Utils.BeginWindow('Materials'):
        PyImGui.push_item_width(190)
        if PyImGui.begin_combo('##common_mats_combo', items[vars.selected_common_mat], PyImGui.ImGuiComboFlags.NoFlag):
            for i, item in enumerate(items):
                is_selected = (i == vars.selected_common_mat)
                if PyImGui.selectable(item, is_selected, PyImGui.SelectableFlags.NoFlag, (0,0)):
                    vars.selected_common_mat = i
            PyImGui.end_combo()
        PyImGui.pop_item_width()

        PyImGui.same_line(0, -1)

        PyImGui.push_item_width(100)
        vars.common_mat_count = max(PyImGui.input_int('##common_mats_input', vars.common_mat_count), 0)
        PyImGui.pop_item_width()

        PyImGui.same_line(0, -1)
        if PyImGui.button('Buy##common', 35):
            GLOBAL_CACHE.Coroutines.append(BuyMats(vars.common_mats[items[vars.selected_common_mat]], vars.common_mat_count))

        PyImGui.same_line(0, -1)
        if PyImGui.button('Sell##common', 35):
            GLOBAL_CACHE.Coroutines.append(SellMats(vars.common_mats[items[vars.selected_common_mat]], vars.common_mat_count))

        # rare
        PyImGui.push_item_width(190)
        items = list(vars.rare_mats.keys())
        if PyImGui.begin_combo('##rare_mats_combo', items[vars.selected_rare_mat], PyImGui.ImGuiComboFlags.NoFlag):
            for i, item in enumerate(items):
                is_selected = (i == vars.selected_rare_mat)
                if PyImGui.selectable(item, is_selected, PyImGui.SelectableFlags.NoFlag, (0,0)):
                    vars.selected_rare_mat = i
            PyImGui.end_combo()
        PyImGui.pop_item_width()

        PyImGui.same_line(0, -1)

        PyImGui.push_item_width(100)
        vars.rare_mat_count = max(PyImGui.input_int('##rare_mats_input', vars.rare_mat_count), 0)
        PyImGui.pop_item_width()

        PyImGui.same_line(0, -1)
        if PyImGui.button('Buy##rare', 35):
            GLOBAL_CACHE.Coroutines.append(BuyMats(vars.rare_mats[items[vars.selected_rare_mat]], vars.rare_mat_count))

        PyImGui.same_line(0, -1)
        if PyImGui.button('Sell##rare', 35):
            GLOBAL_CACHE.Coroutines.append(SellMats(vars.rare_mats[items[vars.selected_rare_mat]], vars.rare_mat_count))

        PyImGui.end()
    PyBox._Utils.EndWindow()

def Draw1():
    global vars

    item_list = Trading.Trader.GetOfferedItems()
    item_models = [Item.GetModelID(item_id) for item_id in item_list]

    trader_type = 0
    if ModelID.Bone in item_models:
        trader_type = 1
    elif ModelID.Fur_Square in item_models:
        trader_type = 2

    if trader_type == 0:
        PyImGui.set_next_window_pos(233, 929) # 370
        PyImGui.set_next_window_size(274, 46)
        if PyBox._Utils.BeginWindow('Materials'):
            PyImGui.text('Interact with a material trader.')

            PyImGui.end()
        PyBox._Utils.EndWindow()
    elif trader_type == 1:
        PyImGui.set_next_window_pos(233, 611) # 370
        if PyBox._Utils.BeginWindow('Common Materials'):
            for item in vars.common_mats:
                PyImGui.push_item_width(168)
                PyImGui.input_text(f'##{item}materials', item, PyImGui.InputTextFlags.ReadOnly)
                PyImGui.pop_item_width()

                PyImGui.same_line(0, -1)

                PyImGui.push_item_width(94)
                vars.common_mats[item][1] = max(PyImGui.input_int(f'##{item}materalsinput', vars.common_mats[item][1]), 0)
                PyImGui.pop_item_width()

            if PyImGui.button(IconsFontAwesome5.ICON_SHOPPING_CART, 86):
                GLOBAL_CACHE.Coroutines.append(BuyMats(vars.common_mats.values()))
            
            PyImGui.same_line(0, -1)
            if PyImGui.button(IconsFontAwesome5.ICON_SACK_DOLLAR, 86):
                GLOBAL_CACHE.Coroutines.append(SellMats(vars.common_mats.values()))

            PyImGui.same_line(0, -1)
            if PyImGui.button(IconsFontAwesome5.ICON_ERASER, 86):
                for item in vars.common_mats:
                    vars.common_mats[item][1] = 0

            PyImGui.end()
        PyBox._Utils.EndWindow()
    elif trader_type == 2:
        PyImGui.set_next_window_pos(233, 219) # 370
        if PyBox._Utils.BeginWindow('Rare Materials'):
            for item in vars.rare_mats:
                PyImGui.push_item_width(168)
                PyImGui.input_text(f'##{item}materials', item, PyImGui.InputTextFlags.ReadOnly)
                PyImGui.pop_item_width()

                PyImGui.same_line(0, -1)

                PyImGui.push_item_width(94)
                vars.rare_mats[item][1] = max(PyImGui.input_int(f'##{item}materalsinput', vars.rare_mats[item][1]), 0)
                PyImGui.pop_item_width()

            if PyImGui.button(IconsFontAwesome5.ICON_SHOPPING_CART, 86):
                GLOBAL_CACHE.Coroutines.append(BuyMats(vars.rare_mats.values()))
            
            PyImGui.same_line(0, -1)
            if PyImGui.button(IconsFontAwesome5.ICON_SACK_DOLLAR, 86):
                GLOBAL_CACHE.Coroutines.append(SellMats(vars.rare_mats.values()))

            PyImGui.same_line(0, -1)
            if PyImGui.button(IconsFontAwesome5.ICON_ERASER, 86):
                for item in vars.rare_mats:
                    vars.rare_mats[item][1] = 0

            PyImGui.end()
        PyBox._Utils.EndWindow()

def Update():
    global vars
    
    if PyBox._Utils.CanDraw():
        if vars.is_showing:
            Draw1()