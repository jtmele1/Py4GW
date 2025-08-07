from Py4GWCoreLib import *
from enum import StrEnum
import re
class Mods:
    class Weapon:
        class Prefix(StrEnum):
            Barbed = '0x246801de'
            Crippling = '0x246801e1'
            Cruel = '0x246801e2'
            Heavy = '0x246801e6'
            Poisonous = '0x246801e4'
            Silencing = '0x246801e5'
            Ebon = '0x24b80b00'
            Fiery = '0x24b80500'
            Icy = '0x24b80300'
            Shocking = '0x24b80400'
            Furious = '0x23b8000a'
            Sundering = '0x23f81414'
            Vampiric3 = '0x25280300'
            Vampiric5 = '0x25280500'
            Zealous = '0x25180001'
            Adept = '0x28081400'
            Defensive = '0x'
            Hale = '0x'
            Insightful = '0x22d80005'
            Swift = '0x'

        class Suffix(StrEnum):
            Defensive = '0x21080005'
            Shelter = '0x21580007'
            Warding = '0x21280007'
            Enchanting = '0x22b80014'
            Swiftness = '0x22080a00'
            Aptitude = '0x'
            Fortitude = '0x23481e00'
            Devotion = '0x23682d00'
            Endurance = '0x'
            Valor = '0x23783c00'
            Mastery = '0x'
            Quickening = '0x'
            Memory = '0x28381400'
        
        class Inscription(StrEnum):
            ...

    class Armor:
        class Insignia(StrEnum):
            # warrior
            Knights = '0x240801f9'
            Lieutenants = '0x24080208'
            Stonefist = '0x24080209'
            Dreadnought = '0x240801fa'
            Sentinels = '0x240801fb'
            # ranger
            Frostbound = '0x240801fc'
            Pyrebound = '0x240801fe'
            Stormbound = '0x240801ff'
            Scouts = '0x24080201'
            Earthbound = '0x240801fd'
            Beastmaster = '0x24080200'
            # monk
            Wanderers = '0x240801f6'
            Disciples = '0x240801f7'
            Anchorites = '0x240801f8'
            # necromancer
            Bloodstained = '0x2408020a'
            Tormentor = '0x240801ec'
            Bonelace = '0x240801ee'
            MinionMaster = '0x240801ef'
            Blighters = '0x240801f0'
            Undertakers = '0x240801ed'
            # mesmer
            Virtuosos = '0x240801e4'
            Artificers = '0x240801e2'
            Prodigys = '0x240801e3'
            # elementalist
            Prismatic = '0x240801f1'
            Hydromancer = '0x240801f2'
            Geomancer = '0x240801f3'
            Pyromancer = '0x240801f4'
            Aeromancer = '0x240801f5'
            # assassin
            Vanguards = '0x240801de'
            Infiltrators = '0x240801df'
            Saboteurs = '0x240801e0'
            Nightstalkers = '0x240801e1'
            # ritualist
            Shamans = '0x24080204'
            GhostForge = '0x24080205'
            Mystics = '0x24080206'
            # dervish
            Windwalker = '0x24080202'
            Forsaken = '0x24080203'
            # paragon
            Centurions = '0x24080207'
            # common
            Survivor = '0x240801e6'
            Radiant = '0x240801e5'
            Stalwart = '0x240801e7'
            Brawlers = '0x240801e8'
            Blessed = '0x240801e9'
            Heralds = '0x240801ea'
            Sentrys = '0x240801eb'

        class Rune(StrEnum):
            # warrior
            MinorAbsorption = '0x240800fc'
            MinorTactics = '0x21e81501'
            MinorStrength = '0x21e81101'
            MinorAxeMastery = '0x21e81201'
            MinorHammerMastery = '0x21e81301'
            MinorSwordsmanship = '0x21e81401'
            MajorAbsorption = '0x240800fd'
            MajorTactics = '0x21e81502'
            MajorStrength = '0x21e81102'
            MajorAxeMastery = '0x21e81202'
            MajorHammerMastery = '0x21e81302'
            MajorSwordsmanship = '0x21e81402'
            SuperiorAbsorption = '0x240800fe'
            SuperiorTactics = '0x21e81503'
            SuperiorStrength = '0x21e81103'
            SuperiorAxeMastery = '0x21e81203'
            SuperiorHammerMastery = '0x21e81303'
            SuperiorSwordsmanship = '0x21e81403'
            # ranger
            MinorWildernessSurvival = "0x21e81801"
            MinorExpertise = "0x21e81701"
            MinorBeastMastery = "0x21e81601"
            MinorMarksmanship = "0x21e81901"
            MajorWildernessSurvival = "0x21e81802"
            MajorExpertise = "0x21e81702"
            MajorBeastMastery = "0x21e81602"
            MajorMarksmanship = "0x21e81902"
            SuperiorWildernessSurvival = "0x21e81803"
            SuperiorExpertise = "0x21e81703"
            SuperiorBeastMastery = "0x21e81603"
            SuperiorMarksmanship = "0x21e81903"
            # monk
            MinorHealingPrayers = "0x21e80d01"
            MinorSmitingPrayers = "0x21e80e01"
            MinorProtectionPrayers = "0x21e80f01"
            MinorDivineFavor = "0x21e81001"
            MajorHealingPrayers = "0x21e80d02"
            MajorSmitingPrayers = "0x21e80e02"
            MajorProtectionPrayers = "0x21e80f02"
            MajorDivineFavor = "0x21e81002"
            SuperiorHealingPrayers = "0x21e80d03"
            SuperiorSmitingPrayers = "0x21e80e03"
            SuperiorProtectionPrayers = "0x21e80f03"
            SuperiorDivineFavor = "0x21e81003"
            # necromancer
            MinorBloodMagic = "0x21e80401"
            MinorDeathMagic = "0x21e80501"
            MinorSoulReaping = "0x21e80601"
            MinorCurses = "0x21e80701"
            MajorBloodMagic = "0x21e80402"
            MajorDeathMagic = "0x21e80502"
            MajorSoulReaping = "0x21e80602"
            MajorCurses = "0x21e80702"
            SuperiorBloodMagic = "0x21e80403"
            SuperiorDeathMagic = "0x21e80503"
            SuperiorSoulReaping = "0x21e80603"
            SuperiorCurses = "0x21e80703"
            # mesmer
            MinorFastCasting = "0x21e80001"
            MinorDominationMagic = "0x21e80201"
            MinorIllusionMagic = "0x21e80101"
            MinorInspirationMagic = "0x21e80301"
            MajorFastCasting = "0x21e80002"
            MajorDominationMagic = "0x21e80202"
            MajorIllusionMagic = "0x21e80102"
            MajorInspirationMagic = "0x21e80302"
            SuperiorFastCasting = "0x21e80003"
            SuperiorDominationMagic = "0x21e80203"
            SuperiorIllusionMagic = "0x21e80103"
            SuperiorInspirationMagic = "0x21e80303"
            # elementalist
            MinorEnergyStorage = "0x21e80c01"
            MinorFireMagic = "0x21e80a01"
            MinorAirMagic = "0x21e80801"
            MinorEarthMagic = "0x21e80901"
            MinorWaterMagic = "0x21e80b01"
            MajorEnergyStorage = "0x21e80c02"
            MajorFireMagic = "0x21e80a02"
            MajorAirMagic = "0x21e80802"
            MajorEarthMagic = "0x21e80902"
            MajorWaterMagic = "0x21e80b02"
            SuperiorEnergyStorage = "0x21e80c03"
            SuperiorFireMagic = "0x21e80a03"
            SuperiorAirMagic = "0x21e80803"
            SuperiorEarthMagic = "0x21e80903"
            SuperiorWaterMagic = "0x21e80b03"
            # assassin
            MinorCriticalStrikes = "0x21e82301"
            MinorDaggerMastery = "0x21e81d01"
            MinorDeadlyArts = "0x21e81e01"
            MinorShadowArts = "0x21e81f01"
            MajorCriticalStrikes = "0x21e82302"
            MajorDaggerMastery = "0x21e81d02"
            MajorDeadlyArts = "0x21e81e02"
            MajorShadowArts = "0x21e81f02"
            SuperiorCriticalStrikes = "0x21e82303"
            SuperiorDaggerMastery = "0x21e81d03"
            SuperiorDeadlyArts = "0x21e81e03"
            SuperiorShadowArts = "0x21e81f03"
            # ritualist
            MinorChannelingMagic = "0x21e82201"
            MinorRestorationMagic = "0x21e82101"
            MinorCommuning = "0x21e82001"
            MinorSpawningPower = "0x21e82401"
            MajorChannelingMagic = "0x21e82202"
            MajorRestorationMagic = "0x21e82102"
            MajorCommuning = "0x21e82002"
            MajorSpawningPower = "0x21e82402"
            SuperiorChannelingMagic = "0x21e82203"
            SuperiorRestorationMagic = "0x21e82103"
            SuperiorCommuning = "0x21e82003"
            SuperiorSpawningPower = "0x21e82403"
            # dervish
            MinorMysticism = "0x21e82c01"
            MinorEarthPrayers = "0x21e82b01"
            MinorScytheMastery = "0x21e82901"
            MinorWindPrayers = "0x21e82a01"
            MajorMysticism = "0x21e82c02"
            MajorEarthPrayers = "0x21e82b02"
            MajorScytheMastery = "0x21e82902"
            MajorWindPrayers = "0x21e82a02"
            SuperiorMysticism = "0x21e82c03"
            SuperiorEarthPrayers = "0x21e82b03"
            SuperiorScytheMastery = "0x21e82903"
            SuperiorWindPrayers = "0x21e82a03"
            # paragon
            MinorLeadership = "0x21e82801"
            MinorMotivation = "0x21e82701"
            MinorCommand = "0x21e82601"
            MinorSpearMastery = "0x21e82501"
            MajorLeadership = "0x21e82802"
            MajorMotivation = "0x21e82702"
            MajorCommand = "0x21e82602"
            MajorSpearMastery = "0x21e82502"
            SuperiorLeadership = "0x21e82803"
            SuperiorMotivation = "0x21e82703"
            SuperiorCommand = "0x21e82603"
            SuperiorSpearMastery = "0x21e82503"
            # common
            Attunement = "0x24080211"
            Recovery = "0x24080213"
            Restoration = "0x24080214"
            Clarity = "0x24080215"
            Purity = "0x24080216"
            MinorVigor = "0x240800ff"
            MinorVigor1 = "0x240800c2"
            SuperiorVigor = "0x24080101"
            MajorVigor = "0x24080100"
            Vitae = "0x24080212"


armor_mods = {
    # region warrior
    '0x240801f9' : "Knight's Insignia",
    '0x24080208' : "Lieutenant's Insignia",
    '0x24080209' : "Stonefist Insignia",
    '0x240801fa' : "Dreadnought Insignia",
    '0x240801fb' : "Sentinel's Insignia",
    '0x240800fc' : "Rune of Minor Absorption",
    '0x21e81501' : "Rune of Minor Tactics",
    '0x21e81101' : "Rune of Minor Strength",
    '0x21e81201' : "Rune of Minor Axe Mastery",
    '0x21e81301' : "Rune of Minor Hammer Mastery",
    '0x21e81401' : "Rune of Minor Swordsmanship",
    '0x240800fd' : "Rune of Major Absorption",
    '0x21e81502' : "Rune of Major Tactics",
    '0x21e81102' : "Rune of Major Strength",
    '0x21e81202' : "Rune of Major Axe Mastery",
    '0x21e81302' : "Rune of Major Hammer Mastery",
    '0x21e81402' : "Rune of Major Swordsmanship",
    '0x240800fe' : "Rune of Superior Absorption",
    '0x21e81503' : "Rune of Superior Tactics",
    '0x21e81103' : "Rune of Superior Strength",
    '0x21e81203' : "Rune of Superior Axe Mastery",
    '0x21e81303' : "Rune of Superior Hammer Mastery",
    '0x21e81403' : "Rune of Superior Swordsmanship",
    # endregion
    # region ranger
    '0x240801fc' : "Frostbound Insignia",
    '0x240801fe' : "Pyrebound Insignia",
    '0x240801ff' : "Stormbound Insignia",
    '0x24080201' : "Scout's Insignia",
    '0x240801fd' : "Earthbound Insignia",
    '0x24080200' : "Beastmaster's Insignia",
    '0x21e81801' : "Rune of Minor Wilderness Survival",
    '0x21e81701' : "Rune of Minor Expertise",
    '0x21e81601' : "Rune of Minor Beast Mastery",
    '0x21e81901' : "Rune of Minor Marksmanship",
    '0x21e81802' : "Rune of Major Wilderness Survival",
    '0x21e81702' : "Rune of Major Expertise",
    '0x21e81602' : "Rune of Major Beast Mastery",
    '0x21e81902' : "Rune of Major Marksmanship",
    '0x21e81803' : "Rune of Superior Wilderness Survival",
    '0x21e81703' : "Rune of Superior Expertise",
    '0x21e81603' : "Rune of Superior Beast Mastery",
    '0x21e81903' : "Rune of Superior Marksmanship",
    # endregion
    # region monk
    '0x240801f6' : "Wanderer's Insignia",
    '0x240801f7' : "Disciple's Insignia",
    '0x240801f8' : "Anchorite's Insignia",
    '0x21e80d01' : "Rune of Minor Healing Prayers",
    '0x21e80e01' : "Rune of Minor Smiting Prayers",
    '0x21e80f01' : "Rune of Minor Protection Prayers",
    '0x21e81001' : "Rune of Minor Divine Favor",
    '0x21e80d02' : "Rune of Major Healing Prayers",
    '0x21e80e02' : "Rune of Major Smiting Prayers",
    '0x21e80f02' : "Rune of Major Protection Prayers",
    '0x21e81002' : "Rune of Major Divine Favor",
    '0x21e80d03' : "Rune of Superior Healing Prayers",
    '0x21e80e03' : "Rune of Superior Smiting Prayers",
    '0x21e80f03' : "Rune of Superior Protection Prayers",
    '0x21e81003' : "Rune of Superior Divine Favor",
    # endregion
    # region necromancer
    '0x2408020a' : "Bloodstained Insignia",
    '0x240801ec' : "Tormentor's Insignia",
    '0x240801ee' : "Bonelace Insignia",
    '0x240801ef' : "Minion Master's Insignia",
    '0x240801f0' : "Blighter's Insignia",
    '0x240801ed' : "Undertaker's Insignia",
    '0x21e80401' : "Rune of Minor Blood Magic",
    '0x21e80501' : "Rune of Minor Death Magic",
    '0x21e80701' : "Rune of Minor Curses",
    '0x21e80601' : "Rune of Minor Soul Reaping",
    '0x21e80402' : "Rune of Major Blood Magic",
    '0x21e80502' : "Rune of Major Death Magic",
    '0x21e80702' : "Rune of Major Curses",
    '0x21e80602' : "Rune of Major Soul Reaping",
    '0x21e80403' : "Rune of Superior Blood Magic",
    '0x21e80503' : "Rune of Superior Death Magic",
    '0x21e80703' : "Rune of Superior Curses",
    '0x21e80603' : "Rune of Superior Soul Reaping",
    # endregion
    # region mesmer
    '0x240801e4' : "Virtuoso's Insignia",
    '0x240801e2' : "Artificer's Insignia",
    '0x240801e3' : "Prodigy's Insignia",
    '0x21e80001' : "Rune of Minor Fast Casting",
    '0x21e80201' : "Rune of Minor Domination Magic",
    '0x21e80101' : "Rune of Minor Illusion Magic",
    '0x21e80301' : "Rune of Minor Inspiration Magic",
    '0x21e80002' : "Rune of Major Fast Casting",
    '0x21e80202' : "Rune of Major Domination Magic",
    '0x21e80102' : "Rune of Major Illusion Magic",
    '0x21e80302' : "Rune of Major Inspiration Magic",
    '0x21e80003' : "Rune of Superior Fast Casting",
    '0x21e80203' : "Rune of Superior Domination Magic",
    '0x21e80103' : "Rune of Superior Illusion Magic",
    '0x21e80303' : "Rune of Superior Inspiration Magic",
    # endregion
    # region elementalist
    '0x240801f2' : "Hydromancer Insignia",
    '0x240801f3' : "Geomancer Insignia",
    '0x240801f4' : "Pyromancer Insignia",
    '0x240801f5' : "Aeromancer Insignia",
    '0x240801f1' : "Prismatic Insignia",
    '0x21e80c01' : "Rune of Minor Energy Storage",
    '0x21e80a01' : "Rune of Minor Fire Magic",
    '0x21e80801' : "Rune of Minor Air Magic",
    '0x21e80901' : "Rune of Minor Earth Magic",
    '0x21e80b01' : "Rune of Minor Water Magic",
    '0x21e80c02' : "Rune of Major Energy Storage",
    '0x21e80a02' : "Rune of Major Fire Magic",
    '0x21e80802' : "Rune of Major Air Magic",
    '0x21e80902' : "Rune of Major Earth Magic",
    '0x21e80b02' : "Rune of Major Water Magic",
    '0x21e80c03' : "Rune of Superior Energy Storage",
    '0x21e80a03' : "Rune of Superior Fire Magic",
    '0x21e80803' : "Rune of Superior Air Magic",
    '0x21e80903' : "Rune of Superior Earth Magic",
    '0x21e80b03' : "Rune of Superior Water Magic",
    # endregion
    # region assassin
    '0x240801de' : "Vanguard's Insignia",
    '0x240801df' : "Infiltrator's Insignia",
    '0x240801e0' : "Saboteur's Insignia",
    '0x240801e1' : "Nightstalker's Insignia",
    '0x21e82301' : "Rune of Minor Critical Strikes",
    '0x21e81d01' : "Rune of Minor Dagger Mastery",
    '0x21e81e01' : "Rune of Minor Deadly Arts",
    '0x21e81f01' : "Rune of Minor Shadow Arts",
    '0x21e82302' : "Rune of Major Critical Strikes",
    '0x21e81d02' : "Rune of Major Dagger Mastery",
    '0x21e81e02' : "Rune of Major Deadly Arts",
    '0x21e81f02' : "Rune of Major Shadow Arts",
    '0x21e82303' : "Rune of Superior Critical Strikes",
    '0x21e81d03' : "Rune of Superior Dagger Mastery",
    '0x21e81e03' : "Rune of Superior Deadly Arts",
    '0x21e81f03' : "Rune of Superior Shadow Arts",
    # endregion
    # region ritualist
    '0x24080204' : "Shaman's Insignia",
    '0x24080205' : "Ghost Forge Insignia",
    '0x24080206' : "Mystic's Insignia",
    '0x21e82201' : "Rune of Minor Channeling Magic",
    '0x21e82101' : "Rune of Minor Restoration Magic",
    '0x21e82001' : "Rune of Minor Communing",
    '0x21e82401' : "Rune of Minor Spawning Power",
    '0x21e82202' : "Rune of Major Channeling Magic",
    '0x21e82102' : "Rune of Major Restoration Magic",
    '0x21e82002' : "Rune of Major Communing",
    '0x21e82402' : "Rune of Major Spawning Power",
    '0x21e82203' : "Rune of Superior Channeling Magic",
    '0x21e82103' : "Rune of Superior Restoration Magic",
    '0x21e82003' : "Rune of Superior Communing",
    '0x21e82403' : "Rune of Superior Spawning Power",
    # endregion
    # region dervish
    '0x24080202' : "Windwalker Insignia",
    '0x24080203' : "Forsaken Insignia",
    '0x21e82c01' : "Rune of Minor Mysticism",
    '0x21e82b01' : "Rune of Minor Earth Prayers",
    '0x21e82901' : "Rune of Minor Scythe Mastery",
    '0x21e82a01' : "Rune of Minor Wind Prayers",
    '0x21e82c02' : "Rune of Major Mysticism",
    '0x21e82b02' : "Rune of Major Earth Prayers",
    '0x21e82902' : "Rune of Major Scythe Mastery",
    '0x21e82a02' : "Rune of Major Wind Prayers",
    '0x21e82c03' : "Rune of Superior Mysticism",
    '0x21e82b03' : "Rune of Superior Earth Prayers",
    '0x21e82903' : "Rune of Superior Scythe Mastery",
    '0x21e82a03' : "Rune of Superior Wind Prayers",
    # endregion
    # region paragon
    '0x24080207' : "Centurion's Insignia",
    '0x21e82801' : "Rune of Minor Leadership",
    '0x21e82701' : "Rune of Minor Motivation",
    '0x21e82601' : "Rune of Minor Command",
    '0x21e82501' : "Rune of Minor Spear Mastery",
    '0x21e82802' : "Rune of Major Leadership",
    '0x21e82702' : "Rune of Major Motivation",
    '0x21e82602' : "Rune of Major Command",
    '0x21e82502' : "Rune of Major Spear Mastery",
    '0x21e82803' : "Rune of Superior Leadership",
    '0x21e82703' : "Rune of Superior Motivation",
    '0x21e82603' : "Rune of Superior Command",
    '0x21e82503' : "Rune of Superior Spear Mastery",
    # endregion
    # region common
    '0x240801e6' : "Survivor Insignia",
    '0x240801e5' : "Radiant Insignia",
    '0x240801e7' : "Stalwart Insignia",
    '0x240801e8' : "Brawler's Insignia",
    '0x240801e9' : "Blessed Insignia",
    '0x240801ea' : "Herald's Insignia",
    '0x240801eb' : "Sentry's Insignia",
    '0x24080211' : "Rune of Attunement",
    '0x24080213' : "Rune of Recovery",
    '0x24080214' : "Rune of Restoration",
    '0x24080215' : "Rune of Clarity",
    '0x24080216' : "Rune of Purity",
    '0x240800ff' : "Rune of Minor Vigor",
    '0x240800c2' : "Rune of Minor Vigor",
    '0x24080101' : "Rune of Superior Vigor",
    '0x24080100' : "Rune of Major Vigor",
    '0x24080212' : "Rune of Vitae",
    # endregion
}

def GetMods(item_id):
    mods = []
    for mod in Item.Customization.Modifiers.GetModifiers(item_id):
        mod_hex = hex(int(mod.GetModBits(),2)) # type: ignore

        if mod_hex in Mods.Armor.Insignia:
            mods.append(Mods.Armor.Insignia(mod_hex).name)
        elif mod_hex in Mods.Armor.Rune:
            mods.append(Mods.Armor.Rune(mod_hex).name)
        elif mod_hex in Mods.Weapon.Prefix:
            mods.append(Mods.Weapon.Prefix(mod_hex).name)
        elif mod_hex in Mods.Weapon.Suffix:
            mods.append(Mods.Weapon.Suffix(mod_hex).name)


        # mod_string = f'{mod_hex}, {mod.GetIdentifier()}|{mod.GetArg1()}|{mod.GetArg2()}'
        # if mod_hex in mod_list:
        #     mod_string += f', {mod_list[mod_hex]}'
        
        # mods.append(mod_string)

    return mods
            
def CheckMods(item_id):
    mod_list = {
        '24080202', "Windwalker Insignia",
        '240801EC', "Tormentor's Insignia",
        '240801E3', "Prodigy's Insignia",
        '21E80001', "Rune of Minor Fast Casting",
        '21E80301', "Rune of Minor Inspiration Magic",
        '21E80203', "Rune of Superior Domination Magic",
        '24080204', "Shaman's Insignia",
        '21E82401', "Rune of Minor Spawning Power",
        '240800FF', "Rune of Minor Vigor",
        '240800C2', "Rune of Minor Vigor",
        '24080101', "Rune of Superior Vigor",
        '24080100', "Rune of Major Vigor",
    }

first = True
def main():
    global first, armor_mods

    try:
        item_id = Inventory.GetHoveredItemID()
        if item_id:
            pos = Overlay().GetMouseCoords()
        
            PyImGui.set_next_window_pos(pos[0] + 20, pos[1])
            PyImGui.begin_tooltip()

            PyImGui.text(f'Item ID: {item_id}')
            PyImGui.text(f'Type: {Item.GetItemType(item_id)[0]}, {Item.GetItemType(item_id)[1]}')
            PyImGui.text(f'Model ID: {Item.GetModelID(item_id)}')
            PyImGui.separator()
            PyImGui.text(f'Mods:')
            for mod in GetMods(item_id):
                PyImGui.text(mod)

            for mod in Item.Customization.Modifiers.GetModifiers(item_id):
                PyImGui.text(f'{mod.ToString()}')

            PyImGui.end_tooltip()

    except ImportError as e:
        Py4GW.Console.Log('BOT', f'ImportError encountered: {str(e)}', Py4GW.Console.MessageType.Error)
        Py4GW.Console.Log('BOT', f'Stack trace: {traceback.format_exc()}', Py4GW.Console.MessageType.Error)
    except ValueError as e:
        Py4GW.Console.Log('BOT', f'ValueError encountered: {str(e)}', Py4GW.Console.MessageType.Error)
        Py4GW.Console.Log('BOT', f'Stack trace: {traceback.format_exc()}', Py4GW.Console.MessageType.Error)
    except TypeError as e:
        Py4GW.Console.Log('BOT', f'TypeError encountered: {str(e)}', Py4GW.Console.MessageType.Error)
        Py4GW.Console.Log('BOT', f'Stack trace: {traceback.format_exc()}', Py4GW.Console.MessageType.Error)
    except Exception as e:
        Py4GW.Console.Log('BOT', f'Unexpected error encountered: {str(e)}', Py4GW.Console.MessageType.Error)
        Py4GW.Console.Log('BOT', f'Stack trace: {traceback.format_exc()}', Py4GW.Console.MessageType.Error)
    finally:
        pass

if __name__ == '__main__':
    main()