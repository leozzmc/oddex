PetalburgCity_PokemonCenter_1F_MapScripts::
	map_script MAP_SCRIPT_ON_TRANSITION, PetalburgCity_PokemonCenter_1F_OnTransition
	map_script MAP_SCRIPT_ON_RESUME, CableClub_OnResume
	.byte 0

PetalburgCity_PokemonCenter_1F_OnTransition:
	setrespawn HEAL_LOCATION_PETALBURG_CITY
	call Common_EventScript_UpdateBrineyLocation
	end

PetalburgCity_PokemonCenter_1F_EventScript_Nurse::
	setvar VAR_0x800B, LOCALID_PETALBURG_NURSE
	call Common_EventScript_PkmnCenterNurse
	waitmessage
	waitbuttonpress
	release
	end

PetalburgCity_PokemonCenter_1F_EventScript_FatMan::
	msgbox PetalburgCity_PokemonCenter_1F_Text_PCStorageSystem, MSGBOX_NPC
	end

PetalburgCity_PokemonCenter_1F_EventScript_Youngster::
	msgbox PetalburgCity_PokemonCenter_1F_Text_OranBerryRegainedHP, MSGBOX_NPC
	end

PetalburgCity_PokemonCenter_1F_EventScript_Woman::
	lock
	faceplayer
	msgbox PetalburgCity_PokemonCenter_1F_Text_ManyTypesOfPokemon, MSGBOX_DEFAULT
	specialvar VAR_RESULT, IsStarterInParty
	goto_if_eq VAR_RESULT, TRUE, PetalburgCity_PokemonCenter_1F_EventScript_SayStarterTypeInfo
	release
	end

@ The type texts below are written for the current STARTER_* roles (Grinpack grass/dark,
@ Trekkeye fire/steel, Ridgecap water/flying). If content/roles.toml points the starters at other
@ species, rewrite these texts to match and rerecord the to_petalburg baselines.
PetalburgCity_PokemonCenter_1F_EventScript_SayStarterTypeInfo::
	call_if_eq VAR_STARTER_MON, 0, PetalburgCity_PokemonCenter_1F_EventScript_SayStarterGrassType
	call_if_eq VAR_STARTER_MON, 1, PetalburgCity_PokemonCenter_1F_EventScript_SayStarterFireType
	call_if_eq VAR_STARTER_MON, 2, PetalburgCity_PokemonCenter_1F_EventScript_SayStarterWaterType
	release
	end

PetalburgCity_PokemonCenter_1F_EventScript_SayStarterGrassType::
	bufferspeciesname STR_VAR_1, SPECIES_ODDEX_STARTER_GRASS
	msgbox PetalburgCity_PokemonCenter_1F_Text_StarterGrassTypeInfo, MSGBOX_DEFAULT
	return

PetalburgCity_PokemonCenter_1F_EventScript_SayStarterFireType::
	bufferspeciesname STR_VAR_1, SPECIES_ODDEX_STARTER_FIRE
	msgbox PetalburgCity_PokemonCenter_1F_Text_StarterFireTypeInfo, MSGBOX_DEFAULT
	return

PetalburgCity_PokemonCenter_1F_EventScript_SayStarterWaterType::
	bufferspeciesname STR_VAR_1, SPECIES_ODDEX_STARTER_WATER
	msgbox PetalburgCity_PokemonCenter_1F_Text_StarterWaterTypeInfo, MSGBOX_DEFAULT
	return

PetalburgCity_PokemonCenter_1F_Text_PCStorageSystem:
	.string "That PC-based POKéMON Storage\n"
	.string "System…\p"
	.string "Whoever made it must be some kind\n"
	.string "of a scientific wizard!$"

PetalburgCity_PokemonCenter_1F_Text_OranBerryRegainedHP:
	.string "When my POKéMON ate an\n"
	.string "ORAN BERRY, it regained HP!$"

PetalburgCity_PokemonCenter_1F_Text_ManyTypesOfPokemon:
	.string "There are many types of POKéMON.\p"
	.string "All types have their strengths and\n"
	.string "weaknesses against other types.\p"
	.string "Depending on the types of POKéMON,\n"
	.string "a battle could be easy or hard.$"

PetalburgCity_PokemonCenter_1F_Text_StarterGrassTypeInfo:
	.string "For example, your {STR_VAR_1}\n"
	.string "is a GRASS and DARK type.\p"
	.string "It's strong against WATER, ROCK,\n"
	.string "GROUND, PSYCHIC and GHOST types.\p"
	.string "PSYCHIC moves don't even touch it!\p"
	.string "But, BUG moves hit it very hard,\n"
	.string "and FIRE, ICE, FLYING, POISON,\l"
	.string "FIGHTING and FAIRY moves hurt, too.$"

PetalburgCity_PokemonCenter_1F_Text_StarterFireTypeInfo:
	.string "For example, your {STR_VAR_1}\n"
	.string "is a FIRE and STEEL type.\p"
	.string "It's strong against GRASS, ICE,\n"
	.string "BUG, STEEL, ROCK and FAIRY types.\p"
	.string "POISON moves don't even touch it!\p"
	.string "But, GROUND moves hit it very hard,\n"
	.string "and WATER and FIGHTING moves hurt.$"

PetalburgCity_PokemonCenter_1F_Text_StarterWaterTypeInfo:
	.string "For example, your {STR_VAR_1}\n"
	.string "is a WATER and FLYING type.\p"
	.string "It's strong against FIRE, ROCK,\n"
	.string "GROUND, BUG, GRASS and FIGHTING.\p"
	.string "GROUND moves don't even touch it!\p"
	.string "But, it's very weak to ELECTRIC,\n"
	.string "and ROCK moves hurt it, too.$"
