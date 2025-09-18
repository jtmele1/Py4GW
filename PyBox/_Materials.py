# region imports
from Py4GWCoreLib import *
import PyBox._Utils
# endregion

class Variables:
    icon              = IconsFontAwesome5.ICON_FEATHER_ALT
    is_showing        = False
    
    common_mats = {
        '10 Bones'                    : [ModelID.Bone,                    0, '[921] - Bone.png'],
        '10 Wood Planks'              : [ModelID.Wood_Plank,              0, '[946] - Wood Plank.png'],
        '10 Iron Ingots'              : [ModelID.Iron_Ingot,              0, '[948] - Iron Ingot.png'],
        '10 Granite Slabs'            : [ModelID.Granite_Slab,            0, '[955] - Granite Slab.png'],
        '10 Tanned Hide Squares'      : [ModelID.Tanned_Hide_Square,      0, '[940] - Tanned Hide Square.png'],
        '10 Piles of Glittering Dust' : [ModelID.Pile_Of_Glittering_Dust, 0, '[929] - Pile_of_Glittering_Dust.png'],
        '10 Scales'                   : [ModelID.Scale,                   0, '[953] - Scale.png'],
        '10 Plant Fibers'             : [ModelID.Plant_Fiber,             0, '[934] - Plant Fiber.png'],
        '10 Chitin Fragments'         : [ModelID.Chitin_Fragment,         0, '[954] - Chitin Fragment.png'],
        '10 Feathers'                 : [ModelID.Feather,                 0, '[933] - Feather.png'],
        '10 Bolts of Cloth'           : [ModelID.Bolt_Of_Cloth,           0, '[925] - Bolt of Cloth.png'],
    }

    rare_mats = {
        'Fur Square'             : [ModelID.Fur_Square,             0, '[941] - Fur Square.png'],
        'Onyx Gemstone'          : [ModelID.Onyx_Gemstone,          0, '[936] - Onyx Gemstone.png'],
        'Bolt of Linen'          : [ModelID.Bolt_Of_Linen,          0, '[926] - Bolt of Linen.png'],
        'Lump of Charcoal'       : [ModelID.Lump_Of_Charcoal,       0, '[922] - Lump_of_Charcoal.png'],
        'Bolt of Damask'         : [ModelID.Bolt_Of_Damask,         0, '[927] - Bolt_of_Damask.png'],
        'Obsidian Shard'         : [ModelID.Obsidian_Shard,         0, '[945] - Obsidian Shard.png'],
        'Bolt of Silk'           : [ModelID.Bolt_Of_Silk,           0, '[928] - Bolt of Silk.png'],
        'Tempered Glass Vial'    : [ModelID.Tempered_Glass_Vial,    0, '[939] - Tempered Glass Vial.png'],
        'Glob of Ectoplasm'      : [ModelID.Glob_Of_Ectoplasm,      0, '[930] - Glob of Ectoplasm.png'],
        'Leather Square'         : [ModelID.Leather_Square,         0, '[942] - Leather Square.png'],
        'Steel Ingot'            : [ModelID.Steel_Ingot,            0, '[949] - Steel Ingot.png'],
        'Elonian Leather Square' : [ModelID.Elonian_Leather_Square, 0, '[943] - Elonian Leather Square.png'],
        'Deldrimor Steel Ingot'  : [ModelID.Deldrimor_Steel_Ingot,  0, '[950] - Deldrimor Steel Ingot.png'],
        'Vial of Ink'            : [ModelID.Vial_Of_Ink,            0, '[944] - Vial of Ink.png'],
        'Monstrous Claw'         : [ModelID.Monstrous_Claw,         0, '[923] - Monstrous Claw.png'],
        'Roll of Parchment'      : [ModelID.Roll_Of_Parchment,      0, '[951] - Roll_of_Parchment.png'],
        'Monstrous Eye'          : [ModelID.Monstrous_Eye,          0, '[931] - Monstrous Eye.png'],
        'Roll of Vellum'         : [ModelID.Roll_Of_Vellum,         0, '[952] - Roll_of_Vellum.png'],
        'Monstrous Fang'         : [ModelID.Monstrous_Fang,         0, '[932] - Monstrous Fang.png'],
        'Spiritwood Plank'       : [ModelID.Spiritwood_Plank,       0, '[956] - Spiritwood Plank.png'],
        'Ruby'                   : [ModelID.Ruby,                   0, '[937] - Ruby.png'],
        'Amber Chunk'            : [ModelID.Amber_Chunk,            0, '[6532] - Amber Chunk.png'],
        'Sapphire'               : [ModelID.Sapphire,               0, '[938] - Sapphire.png'],
        'Jadeite Shard'          : [ModelID.Jadeite_Shard,          0, '[6533] - Jadeite Shard.png'],
        'Diamond'                : [ModelID.Diamond,                0, '[935] - Diamond.png'],
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

    item_list = Trading.Trader.GetOfferedItems()
    item_models = [Item.GetModelID(item_id) for item_id in item_list]

    trader_type = 0
    if ModelID.Bone in item_models:
        trader_type = 1
    elif ModelID.Fur_Square in item_models:
        trader_type = 2

    if trader_type == 0:
        PyImGui.set_next_window_pos(233, 929)
        PyImGui.set_next_window_size(274, 46)
        if PyBox._Utils.BeginWindow('Materials', vars.is_showing):
            PyImGui.text('Interact with a material trader.')

            PyImGui.end()
        PyBox._Utils.EndWindow()
    elif trader_type == 1:
        PyImGui.set_next_window_pos(233, 779)
        if PyBox._Utils.BeginWindow('Common', vars.is_showing):
            new_line = False
            for item in vars.common_mats:
                ImGui.ImageButton(f'##{item}materials', f'Textures/Item Models/{vars.common_mats[item][2]}', 17.5, 22, frame_padding=1)
                if PyImGui.is_item_hovered():
                    PyImGui.set_tooltip(item)
                PyImGui.same_line(0, -1)

                PyImGui.push_item_width(93)
                vars.common_mats[item][1] = max(PyImGui.input_int(f'##{item}materalsinput', vars.common_mats[item][1]), 0)
                PyImGui.pop_item_width()

                if not new_line:
                    PyImGui.same_line(0, -1)
                    PyImGui.dummy(0, 0)
                    PyImGui.same_line(0, -1)
                new_line = not new_line

            if PyImGui.button(IconsFontAwesome5.ICON_SHOPPING_CART, 36):
                GLOBAL_CACHE.Coroutines.append(BuyMats(vars.common_mats.values()))
            
            PyImGui.same_line(0, -1)
            if PyImGui.button(IconsFontAwesome5.ICON_SACK_DOLLAR, 36):
                GLOBAL_CACHE.Coroutines.append(SellMats(vars.common_mats.values()))

            PyImGui.same_line(0, -1)
            if PyImGui.button(IconsFontAwesome5.ICON_ERASER, 36):
                for item in vars.common_mats:
                    vars.common_mats[item][1] = 0

            PyImGui.end()
        PyBox._Utils.EndWindow()
    elif trader_type == 2:
        PyImGui.set_next_window_pos(233, 583) # 370
        if PyBox._Utils.BeginWindow('Rare', vars.is_showing):
            new_line = False
            for item in vars.rare_mats:
                ImGui.ImageButton(f'##{item}materials', f'Textures/Item Models/{vars.rare_mats[item][2]}', 17.5, 22, frame_padding=1)
                if PyImGui.is_item_hovered():
                    PyImGui.set_tooltip(item)
                PyImGui.same_line(0, -1)

                PyImGui.same_line(0, -1)

                PyImGui.push_item_width(93)
                vars.rare_mats[item][1] = max(PyImGui.input_int(f'##{item}materalsinput', vars.rare_mats[item][1]), 0)
                PyImGui.pop_item_width()

                if not new_line:
                    PyImGui.same_line(0, -1)
                    PyImGui.dummy(0, 0)
                    PyImGui.same_line(0, -1)
                new_line = not new_line

            if PyImGui.button(IconsFontAwesome5.ICON_SHOPPING_CART, 36):
                GLOBAL_CACHE.Coroutines.append(BuyMats(vars.rare_mats.values()))
            
            PyImGui.same_line(0, -1)
            if PyImGui.button(IconsFontAwesome5.ICON_SACK_DOLLAR, 36):
                GLOBAL_CACHE.Coroutines.append(SellMats(vars.rare_mats.values()))

            PyImGui.same_line(0, -1)
            if PyImGui.button(IconsFontAwesome5.ICON_ERASER, 36):
                for item in vars.rare_mats:
                    vars.rare_mats[item][1] = 0

            PyImGui.end()
        PyBox._Utils.EndWindow()

def Update():
    global vars
    
    if PyBox._Utils.CanDraw():
        if vars.is_showing:
            Draw()