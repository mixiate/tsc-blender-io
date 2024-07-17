"""Get character IDs from model names and IDs."""

from . import utils


THE_SIMS_MODEL_ID_CHARACTER_ID_MAP = {
    0x8414147C: 0x64E0E172,  # blue_plate_sconce_a_00
    0x5BC8DEA: 0x9C9B1CAF,  # bottle_lamp_a_00
    0x5E13146F: 0x8DE4B3FD,  # carry_pizzabox_a_00
    0xCE23A4EF: 0x91E7088E,  # elite_reflections_chrome_lamp_a_00
    0x87AFD27C: 0xE63138FA,  # fight_3d_part
    0xF96953D1: 0x9CC7775E,  # halogen_heaven_lamp_by_contempto_a_00
    0x1274B029: 0x3A5EE732,  # hydrothera_bathtub_a_00
    0x9AEE727: 0xCD98A854,  # master_suite_tub_a_00
    0xCA88340B: 0xA2B792A8,  # oval_glass_sconce_a_00
    0x1DCC5C48: 0x85AFAB17,  # sani_queen_bathtub_a_00
    0x9CD3E29: 0x5E9076EB,  # top_brass_sconce_a_00
    0x24F1E2A2: 0x3E88D019,  # torchosterone_floor_lamp_a_00
    0xC890DFE1: 0x58A25BF4,  # torchosterone_table_lamp_a_00
    0xABCE6013: 0x419B5794,  # vanity_mirror_a_00
}


THE_SIMS_BUSTIN_OUT_MODEL_ID_CHARACTER_ID_MAP = {
    0x8414147C: 0x64E0E172,  # blue_plate_sconce_a_00
    0x5BC8DEA: 0x9C9B1CAF,  # bottle_lamp_a_00
    0xB29EE31A: 0x86D94398,  # cabinet_locker
    0x5E13146F: 0x8DE4B3FD,  # carry_pizzabox_a_00
    0xCE23A4EF: 0x91E7088E,  # elite_reflections_chrome_lamp_a_00
    0x87AFD27C: 0xE63138FA,  # fight_3d_part
    0xBF4F0A81: 0x868669BE,  # game_pooltable_club_x
    0xF96953D1: 0x9CC7775E,  # halogen_heaven_lamp_by_contempto_a_00
    0x1274B029: 0x3A5EE732,  # hydrothera_bathtub_a_00
    0x9D84F77C: 0x911367DE,  # lamp_garden_streetlamp_industrial_off
    0x7515D4F0: 0x9414BD62,  # lamp_table_x_gooseneck_widehead_off
    0x9AEE727: 0xCD98A854,  # master_suite_tub_a_00
    0xB1BE609A: 0x148FF674,  # o_lamp_wall_torch_arm_00
    0xCA88340B: 0xA2B792A8,  # oval_glass_sconce_a_00
    0x42D0B2AD: 0xB9665E3,  # pool_lshape
    0x1DCC5C48: 0x85AFAB17,  # sani_queen_bathtub_a_00
    0x9CD3E29: 0x5E9076EB,  # top_brass_sconce_a_00
    0x24F1E2A2: 0x3E88D019,  # torchosterone_floor_lamp_a_00
    0xC890DFE1: 0x58A25BF4,  # torchosterone_table_lamp_a_00
    0x2D24440B: 0xC5C69E99,  # zz_visit_tron
}


THE_URBZ_MODEL_ID_CHARACTER_ID_MAP = {
    0xFD7F6441: 0x24C58257,  # loading_dut
    0x89A7EA61: 0x24C58257,  # loading_english
    0x4D58E53C: 0x24C58257,  # loading_finn
    0xDC67C203: 0x24C58257,  # loading_fra
    0x5C986D7C: 0x24C58257,  # loading_ger
    0x816122B8: 0x24C58257,  # loading_ita
    0xBE91480: 0x24C58257,  # loading_japanese
    0xAF6D7C92: 0x24C58257,  # loading_kor
    0xE7D44FC: 0x24C58257,  # loading_norw
    0x45110D60: 0x24C58257,  # loading_pol
    0xF4BCC11A: 0x24C58257,  # loading_spa
    0x2AB2ED87: 0x24C58257,  # loading_tchinese
}


THE_SIMS_2_MODEL_ID_CHARACTER_ID_MAP = {
    0xFCDCC7AA: 0xDDA1A5D3,  # dm_bulldog
    0x6BF6C17F: 0xF2FF90C5,  # o_painting_eyetoy_2
    0x1CF1F1E9: 0xF2FF90C5,  # o_painting_eyetoy_3
    0x8295644A: 0xF2FF90C5,  # o_painting_eyetoy_4
    0xF59254DC: 0xF2FF90C5,  # o_painting_eyetoy_5
    0x6143FD5: 0x9F1D6E6F,  # o_painting_landscape_eyetoy_2
    0x71130F43: 0x9F1D6E6F,  # o_painting_landscape_eyetoy_3
    0xEF779AE0: 0x9F1D6E6F,  # o_painting_landscape_eyetoy_4
    0x9870AA76: 0x9F1D6E6F,  # o_painting_landscape_eyetoy_5
    0xA1DC2732: 0x38D57688,  # o_poster_eyetoy_2
    0xD6DB17A4: 0x38D57688,  # o_poster_eyetoy_3
    0x48BF8207: 0x38D57688,  # o_poster_eyetoy_4
    0x3FB8B291: 0x38D57688,  # o_poster_eyetoy_5
    0x82FAC10A: 0xFA1581E6,  # plumbing_bathtub_ornate_2x1
    0x14D1270F: 0xFA1581E6,  # plumbing_bathtub_ornate_2x1_empty_clean
    0x84ACF84F: 0xFA1581E6,  # plumbing_bathtub_ornate_new
    0x28261DF3: 0xFA1581E6,  # plumbing_bathtub_ornate_new_empty_clean
    0x1A8C4249: 0x94D1D6CA,  # plumbing_hottub_antigrav_doliphin
    0xEC5384BD: 0x94D1D6CA,  # plumbing_hottub_antigrav_waterblob
}


def get_character_id_from_model(model_name: str, model_id: int, game_type: utils.GameType) -> int:
    """Get the character ID from the model name or ID."""
    if model_name.startswith(("fa_", "af_")):
        return 0x1FB80AF4

    if model_name.startswith(("ma_", "am_")):
        return 0xFFA60350

    if game_type in (utils.GameType.THESIMS, utils.GameType.THESIMSBUSTINOUT) and model_name.startswith(
        ("fc_", "cf_", "mc_", "cm_"),
    ):
        return 0xD5E79699

    character_id = model_id

    match game_type:
        case utils.GameType.THESIMS:
            character_id = THE_SIMS_MODEL_ID_CHARACTER_ID_MAP.get(model_id, model_id)
        case utils.GameType.THESIMSBUSTINOUT:
            character_id = THE_SIMS_BUSTIN_OUT_MODEL_ID_CHARACTER_ID_MAP.get(model_id, model_id)
        case utils.GameType.THEURBZ:
            character_id = THE_URBZ_MODEL_ID_CHARACTER_ID_MAP.get(model_id, model_id)
        case utils.GameType.THESIMS2:
            character_id = THE_SIMS_2_MODEL_ID_CHARACTER_ID_MAP.get(model_id, model_id)

    return character_id
