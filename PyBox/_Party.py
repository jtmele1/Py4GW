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
    fsm_started = False
    invite_fsm = FSM('Invite')

    skills = [[782,780,775,440,2108,2233,3427,436],
              [782,780,775,440,2108,447,1195,2235],
              [1519,1523,1764,1514,1544,2235,2108,436],
              [1240,982,911,1249,1232,1480,1230,791]]

vars = Variables()

def DrawControlPanel():
    names = ['Character 1', 'Character 2', 'Character 3', 'Character 4']

    if PyBox._Utils.BeginWindow('HeroAI Control Panel'):
    
        # players = GLOBAL_CACHE.ShMem.GetAllActivePlayers()
        # for player in players:
        #     if not player.IsAccount:
        #         continue
        #     PyImGui.text(player.CharacterName)
        #     print(player.Skills)

        for i, name in enumerate(names):
            PyImGui.text(name)

            PyImGui.begin_group()
            PyImGui.push_style_var2(ImGui.ImGuiStyleVar.ItemSpacing, 4, 2)
            PyImGui.push_style_var2(ImGui.ImGuiStyleVar.FramePadding, 3, 1)
            PyImGui.push_style_var2(ImGui.ImGuiStyleVar.ButtonTextAlign, 0.5,0.5)
            ImGui.colored_button('480',Color(204,0,0,255),Color(204,0,0,255),Color(204,0,0,255), 150, 13)
            ImGui.colored_button('24',Color(30,94,153,255),Color(30,94,153,255),Color(30,94,153,255), 150, 13)
            PyImGui.pop_style_var(3)
            PyImGui.end_group()

            PyImGui.push_style_var2(ImGui.ImGuiStyleVar.FramePadding, 0, 0)
            PyImGui.same_line(0,-1)
            ImGui.ImageButton(f'##{i}fight','behavior/fight.png',22,22, 3)
            PyImGui.same_line(0,-1)
            ImGui.ImageButton(f'##{i}guard','behavior/guard.png',22,22, 3)
            PyImGui.same_line(0,-1)
            ImGui.ImageButton(f'##{i}run','behavior/run.png',22,22, 3)

            PyImGui.push_style_var2(ImGui.ImGuiStyleVar.ItemSpacing, 0, 4)

            for j in range(8):
                ImGui.ImageButtonExtended(f'##{i},{j}',f'../{GLOBAL_CACHE.Skill.ExtraData.GetTexturePath(vars.skills[i][j])}',(36,36), uv0 = (0.0625,0.0625), uv1 = (0.9375, 0.9375), frame_padding=0)
                if j < 7:
                    PyImGui.same_line(0,-1)

            if i < 3:
                PyImGui.separator()

            PyImGui.pop_style_var(2)

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

        if vars.fsm_started and not vars.invite_fsm.is_finished():
            vars.invite_fsm.update()