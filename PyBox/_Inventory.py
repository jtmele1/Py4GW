# region imports
from Py4GWCoreLib import *
import PyBox._Utils
import ctypes

user32 = ctypes.WinDLL("user32", use_last_error=True)
# endregion

def IsKeyPressed(vk_code):
    value = user32.GetAsyncKeyState(vk_code) & 0x8000
    is_value_not_zero = value != 0
    if is_value_not_zero:
        return True
    return False

def GetFirstEmptySlot(type = 'storage'):
    from Py4GWCoreLib.enums import Bags
    bags_to_check = []
    if type == 'inventory':
        bags_to_check = ItemArray.CreateBagList(Bags.Backpack, Bags.BeltPouch, Bags.Bag1, Bags.Bag2)
    elif type == 'storage':
        bags_to_check = ItemArray.CreateBagList(Bags.Storage1, Bags.Storage2, Bags.Storage3, Bags.Storage4)

    for bag_enum in bags_to_check:
        bag = PyInventory.Bag(bag_enum.value, bag_enum.name)
        size = bag.GetSize()
        item_slots = [0] * size  # Pre-fill all slots with 0s

        for item in bag.GetItems():
            if 0 <= item.slot < size:
                item_slots[item.slot] = item.item_id

        for i, id in enumerate(item_slots):
            if id == 0:
                return bag_enum.value, i 
    
    return 0, 0

def CtrlClickItem():
    if GLOBAL_CACHE.Map.IsExplorable():
        hovered = GLOBAL_CACHE.Inventory.GetHoveredItemID()
        if PyImGui.get_io().key_ctrl and IsKeyPressed(1):
            if hovered and GLOBAL_CACHE.Item.Type.IsInventoryItem(hovered):
                Inventory.DropItem(hovered)
    elif GLOBAL_CACHE.Map.IsOutpost():
        hovered = GLOBAL_CACHE.Inventory.GetHoveredItemID()
        if not hovered: return
        if GLOBAL_CACHE.Item.Type.IsInventoryItem(hovered):
            if PyImGui.get_io().key_ctrl and IsKeyPressed(1):
                bag, slot = GetFirstEmptySlot('storage')
                if bag:
                    GLOBAL_CACHE.Inventory.MoveItem(hovered, bag, slot, quantity=GLOBAL_CACHE.Item.Properties.GetQuantity(hovered))
        elif GLOBAL_CACHE.Item.Type.IsStorageItem(hovered):
            if PyImGui.get_io().key_ctrl and IsKeyPressed(1):
                bag, slot = GetFirstEmptySlot('inventory')
                if bag:
                    GLOBAL_CACHE.Inventory.MoveItem(hovered, bag, slot, quantity=GLOBAL_CACHE.Item.Properties.GetQuantity(hovered))

def ProcessInventory():
    PyBox._Utils.SendInfoChat('Processing inventory...')

def Draw():
    global vars

    frame_id = UIManager.GetFrameIDByHash(291586130)
    if not UIManager.FrameExists(frame_id):
        return
    
    left, top, _, _ = UIManager.GetFrameCoords(frame_id)

    PyImGui.set_next_window_pos(left + 140, top - 3)

    if PyBox._Utils.BeginHiddenWindow('InventoryOverlay'):
        if PyImGui.button(f'{IconsFontAwesome5.ICON_ARROWS_SPIN}##inventory'):
            ProcessInventory()
        PyImGui.same_line(0, 0)

        if PyImGui.button(f'{IconsFontAwesome5.ICON_COG}##inventory'):
            ...
        PyImGui.same_line(0, 0)
        
        if PyImGui.button(f'{IconsFontAwesome5.ICON_BOX_OPEN}##inventory'):
            if not Inventory.IsStorageOpen():
                Inventory.OpenXunlaiWindow()

    PyImGui.end()

    PyBox._Utils.EndHiddenWindow()

def Update():
    if PyBox._Utils.CanDraw():
        Draw()
        CtrlClickItem()