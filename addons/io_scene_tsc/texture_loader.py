"""Find and load textures for imported meshes."""

import bpy
import pathlib


from . import utils


def create_material(obj: bpy.types.Object, texture_name: str, texture_file_path: pathlib.Path) -> None:
    """Load the texture file, create a Blender material using it and add it to a material slot in the object."""
    material_list = [material.name.casefold() for material in bpy.data.materials]
    try:
        material_index = material_list.index(texture_name.casefold())
        material = bpy.data.materials[material_index]
    except ValueError as _:
        material = None

    if material is None:
        material = bpy.data.materials.new(name=texture_name)

        image = bpy.data.images.get(texture_file_path.as_posix())
        if image is None:
            image = bpy.data.images.load(texture_file_path.as_posix())
        material.use_nodes = True

        image_node = material.node_tree.nodes.new('ShaderNodeTexImage')
        image_node.image = image

        principled_bsdf = material.node_tree.nodes.get('Principled BSDF')
        material.node_tree.links.new(image_node.outputs[0], principled_bsdf.inputs[0])
        principled_bsdf.inputs[2].default_value = 0.5
        principled_bsdf.inputs[12].default_value = 0.0

        if image.depth == 32:  # noqa: PLR2004
            material.node_tree.links.new(image_node.outputs[1], principled_bsdf.inputs[4])
            material.blend_method = 'HASHED'

        specular_file_path = pathlib.Path(
            texture_file_path.parent,
            texture_file_path.stem + " specular" + texture_file_path.suffix,
        )
        if specular_file_path.is_file():
            specular_image = bpy.data.images.get(specular_file_path.as_posix())
            if specular_image is None:
                specular_image = bpy.data.images.load(specular_file_path.as_posix())

            specular_image_node = material.node_tree.nodes.new('ShaderNodeTexImage')
            specular_image_node.image = specular_image

            material.node_tree.links.new(specular_image_node.outputs[0], principled_bsdf.inputs[12])

    if material.name not in obj.data.materials:
        obj.data.materials.append(material)


THE_SIMS_SHADER_ID_TEXTURE_ID_LOOKUP = {
    0x10004FD7: 0x6C8CAD96,
    0x10FE3D7A: 0x4ADE6AE6,
    0x15BB3E8A: 0x1A18CA65,
    0x17D1AD3B: 0x40B79A7B,
    0x183E34C6: 0x7FB2FC6F,
    0x1A6A4508: 0xB5ACF38A,
    0x1ACBBDC: 0xF116BF68,
    0x1AED28DF: 0xDC7EF963,
    0x1AF0C1EB: 0xA2189743,
    0x1BD20E3A: 0xF72F4B32,
    0x23EEE8: 0x4FCAC910,
    0x2541CA3A: 0x42BFE986,
    0x26D66694: 0xA4D3DAEC,
    0x27286B20: 0xD642A386,
    0x2993CBEB: 0x6CBA5F95,
    0x29B27C53: 0x62F643AD,
    0x2B614ECB: 0x6CBA5F95,
    0x2C1AFF1: 0xECA92364,
    0x2C2B14B2: 0x2561181F,
    0x2C79DDCE: 0x3CC4348F,
    0x2F0A9B2: 0x572722B2,
    0x3B45B5E5: 0x2A738260,
    0x3CE99816: 0x6D7EAB00,
    0x42F94BA: 0x72A4B31D,
    0x4373B37D: 0xB5F77901,
    0x43D7C14C: 0x65C702CD,
    0x44333F82: 0x6ABB20F2,
    0x466EBC9: 0x7DD84C1A,
    0x4746F8E6: 0x419B5794,
    0x47E5D9CD: 0xEFC9E781,
    0x4AFE9729: 0x583A48CF,
    0x4C721C4E: 0x6CBA5F95,
    0x4CCAC608: 0x27CD4201,
    0x4E2681E6: 0xF5F5F8E8,
    0x4E9DC9: 0x637472D7,
    0x50FCBAB7: 0x3CC4348F,
    0x51D15602: 0xA4D3DAEC,
    0x51DB7D2A: 0x2E458ED1,
    0x52D907CB: 0x65F53FE3,
    0x5ABAC3A9: 0xCCE49970,
    0x5B7A34F4: 0x3A5B477C,
    0x64DC35D1: 0x985715E4,
    0x654D8292: 0x188459ED,
    0x6A789176: 0xFA89FD15,
    0x6BCC5DC2: 0x70CF5F85,
    0x6E0D4262: 0x1AD0206F,
    0x71ED3226: 0x1840B68A,
    0x770E33E: 0x1559D4BC,
    0x79AA6203: 0xCCCB664,
    0x7A99DCDC: 0xC40F4E32,
    0x7DC81D03: 0x4917ACD9,
    0x7F8AD867: 0xD60FC949,
    0x89091E6D: 0x6C8CAD96,
    0x90D7B5FE: 0x8B28FCF6,
    0x912242BB: 0x5E23D5B8,
    0x9211830F: 0xF0F62A15,
    0x9444F651: 0x5B656B5E,
    0x967AB73F: 0xE0F19098,
    0x977F60F3: 0x2BD8DAA2,
    0x9980C819: 0xFF5C01AC,
    0x9A1FBCDE: 0x52E2B2A3,
    0xA2A0EA04: 0xB154D360,
    0xA3552905: 0x41966197,
    0xA5637B0B: 0xE48CAC57,
    0xAE93BE1B: 0x223C5A4B,
    0xB4781545: 0x65E386DF,
    0xBC13FC51: 0x2C23E58C,
    0xBC5DFE21: 0x54B10280,
    0xBD2ACF79: 0x985715E4,
    0xBDCC0DDC: 0x5F100A0F,
    0xBE35D0C4: 0xA2B792A8,
    0xBED0FFC9: 0x625AD2F,
    0xBF286AF3: 0x37AC1C6F,
    0xC0715375: 0x62F643AD,
    0xC0E532FA: 0x985715E4,
    0xC52DC139: 0xC62C2B64,
    0xC84F8C57: 0xC72A8402,
    0xC8D807B8: 0xA4D3DAEC,
    0xCB98196F: 0xFDA60B13,
    0xCE2D3036: 0xC0AF5542,
    0xCE4E7ADE: 0x99284D9E,
    0xCEEED9CB: 0x14FD025B,
    0xCF65E336: 0xB9EEC491,
    0xD0C82B7E: 0xE6B98A30,
    0xD760B9F: 0xF5695284,
    0xD9DA57D2: 0xD5C2BA2E,
    0xDA83A2BC: 0x3D90456F,
    0xDB6A33BD: 0xBF632156,
    0xDC222275: 0xD889C7AE,
    0xE0A8E648: 0xA52025E4,
    0xE0EAD657: 0x4C4F9B19,
    0xE523691A: 0xC556E676,
    0xE8136BD8: 0xD476C00D,
    0xEE2EED81: 0xF5695284,
    0xEF318CE4: 0xCACD5421,
    0xEFACC883: 0x5B9A18FA,
    0xF09E4203: 0x3FB58587,
    0xF5B622C8: 0x985715E4,
    0xFE727B39: 0xAE682D86,
    0xFEDD7F11: 0xE0EAD657,
}


THE_SIMS_BUSTIN_OUT_SHADER_ID_TEXTURE_ID_LOOKUP = {
    0x10004FD7: 0x6C8CAD96,
    0x10FE3D7A: 0x4ADE6AE6,
    0x117EEE29: 0xD1FE04B5,
    0x11AF39B5: 0x11AF39B5,
    0x13AA754D: 0x8D21206C,
    0x149AE75D: 0xF80C6C4F,
    0x15BB3E8A: 0x1A18CA65,
    0x162FDD02: 0x162FDD02,
    0x163691FF: 0xB5139D50,
    0x17D1AD3B: 0x40B79A7B,
    0x182173C7: 0x182173C7,
    0x183E34C6: 0x7FB2FC6F,
    0x1A4A7A57: 0x1A4A7A57,
    0x1A6A4508: 0xB5ACF38A,
    0x1A802F0B: 0x77F360DD,
    0x1ACBBDC: 0xF116BF68,
    0x1ADE21D1: 0x49EFE325,
    0x1AED28DF: 0xDC7EF963,
    0x1B9297AA: 0x1B9297AA,
    0x1BF9CCD4: 0x556D289A,
    0x1D27BE4E: 0x1D27BE4E,
    0x1EC79B52: 0x19267D20,
    0x1F5FEB86: 0x1F5FEB86,
    0x1F6FA20F: 0x1F6FA20F,
    0x215DD80B: 0x556D289A,
    0x23EEE8: 0x4FCAC910,
    0x23F742E7: 0x5FFBE46C,
    0x24D30B0: 0xFD39A53C,
    0x2541CA3A: 0x42BFE986,
    0x26D66694: 0xA4D3DAEC,
    0x27286B20: 0xD642A386,
    0x278649EF: 0x67179764,
    0x287C18D5: 0x287C18D5,
    0x28C0FDA6: 0xCD2F482C,
    0x28E7B63: 0x28E7B63,
    0x2A17345A: 0xC67279F9,
    0x2B037439: 0x2B037439,
    0x2BFC556D: 0x117EEE29,
    0x2C16900B: 0x2C16900B,
    0x2C18F76B: 0xCCEABD9C,
    0x2C79DDCE: 0x3CC4348F,
    0x2CC5D52F: 0xB4EEF5BB,
    0x2D6374C8: 0xC8BBC6C4,
    0x2F11DCCC: 0x2F11DCCC,
    0x2F94A0A5: 0x5FFBE46C,
    0x2FA00B7F: 0x2FA00B7F,
    0x2FB7016: 0x88BED91C,
    0x2FC012E8: 0x117EEE29,
    0x31488F35: 0x31488F35,
    0x31AAA40B: 0xA2B792A8,
    0x323EE053: 0xE5E73DAE,
    0x32420593: 0xFF248F1B,
    0x32660BE6: 0x32660BE6,
    0x329C458B: 0x329C458B,
    0x34AD7C26: 0x34AD7C26,
    0x35C1DF28: 0x35C1DF28,
    0x37162033: 0x35D473A3,
    0x3799831: 0xDCA16A16,
    0x3A4282BD: 0x3A4282BD,
    0x3B45B5E5: 0x2A738260,
    0x3C8315BD: 0x117EEE29,
    0x3CE99816: 0x6D7EAB00,
    0x3D2CADEF: 0xB2C8F2F0,
    0x3D8A014E: 0xCB43CFDF,
    0x3E1146AF: 0x705B04F3,
    0x410DDD1B: 0x410DDD1B,
    0x41BE5307: 0x79BDE166,
    0x42F94BA: 0x72A4B31D,
    0x43D7C14C: 0x65C702CD,
    0x43E6CB9B: 0x43E6CB9B,
    0x44333F82: 0x6ABB20F2,
    0x4494333E: 0x4494333E,
    0x44B30BDD: 0xE53EDE99,
    0x45453505: 0x32420593,
    0x462B67BC: 0x6A0D4B71,
    0x46601902: 0x46601902,
    0x46FF0443: 0xBFB9EE2A,
    0x47E5D9CD: 0xEFC9E781,
    0x47F555E0: 0x6A0D4B71,
    0x496F75C8: 0x496F75C8,
    0x49DA8081: 0xFF248F1B,
    0x4A08AA3: 0x35861C6F,
    0x4AFE9729: 0x583A48CF,
    0x4BFB9BA0: 0x35D473A3,
    0x4E2681E6: 0xF5F5F8E8,
    0x4E9916BA: 0x4E9916BA,
    0x4E9DC9: 0x637472D7,
    0x4FBC4B34: 0x4FBC4B34,
    0x50FCBAB7: 0x3CC4348F,
    0x5155E7D7: 0x8C8CFCD6,
    0x5166C26: 0xE2DFD385,
    0x51D15602: 0xA4D3DAEC,
    0x52F9FDE9: 0x5E9076EB,
    0x5358461A: 0x70C10F1D,
    0x541452DA: 0x9089FDCE,
    0x5445446: 0x49EFE325,
    0x54EBF8E8: 0x54EBF8E8,
    0x54F87898: 0x54F87898,
    0x550BEC90: 0x550BEC90,
    0x550CD4A1: 0x375142E8,
    0x557A78BE: 0x2A1B62EE,
    0x56114E13: 0x56114E13,
    0x572722B2: 0x572722B2,
    0x5815031C: 0x5815031C,
    0x5854E29B: 0xE61E7D20,
    0x59059753: 0xB9C03468,
    0x5A64445E: 0xCD2F482C,
    0x5ABAC3A9: 0xCCE49970,
    0x5B7A34F4: 0x3A5B477C,
    0x5D1810C3: 0x105D321B,
    0x5E3B86BC: 0xE96A4E8,
    0x5E6782A1: 0xCD2395BD,
    0x5FA8B0C7: 0x9743835,
    0x602ABDD8: 0x7B469A0C,
    0x61B5D7D6: 0x61B5D7D6,
    0x61EA1771: 0x61EA1771,
    0x624092FE: 0x92E55148,
    0x6240FE3C: 0x59C888DC,
    0x627E8034: 0x735AEEF4,
    0x63216BF: 0x63216BF,
    0x6338440A: 0x91E7088E,
    0x63D8DCE1: 0x63D8DCE1,
    0x6413C7C8: 0x117EEE29,
    0x64DC35D1: 0x985715E4,
    0x65FA142A: 0x65FA142A,
    0x661280E9: 0x661280E9,
    0x69F32DBB: 0x7ED1BDAC,
    0x6A208ED8: 0x6A208ED8,
    0x6A789176: 0xFA89FD15,
    0x6ADDAB40: 0x6ADDAB40,
    0x6BCC5DC2: 0x70CF5F85,
    0x6C7BB4CC: 0x6C7BB4CC,
    0x6CA23589: 0xEDEBF7E9,
    0x6D7627A9: 0x98338F79,
    0x6E0D4262: 0x1AD0206F,
    0x6E81AACA: 0x6E81AACA,
    0x6E88C3F: 0x8D469B4B,
    0x6FAAB275: 0xFD39A53C,
    0x707E01C9: 0x707E01C9,
    0x70DBCAA4: 0x9FB6938F,
    0x71BA2E9A: 0x14FC1A0F,
    0x71ED3226: 0x1840B68A,
    0x733B6098: 0x733B6098,
    0x755AF34E: 0x755AF34E,
    0x76126037: 0x117EEE29,
    0x771F9603: 0x771F9603,
    0x773C79E2: 0x773C79E2,
    0x774FDE0A: 0x774FDE0A,
    0x7822957E: 0x7822957E,
    0x79AA6203: 0xCCCB664,
    0x7A99DCDC: 0xC40F4E32,
    0x7B375282: 0x3FC90814,
    0x7B61ADDF: 0x7B61ADDF,
    0x7B739CC0: 0xCDDD1EDE,
    0x7C8D12D1: 0x718F5663,
    0x7D7834C6: 0x9CC7775E,
    0x7DCFA32: 0xB2C8F2F0,
    0x7DF09B53: 0x7DF09B53,
    0x7E996DB2: 0x7E996DB2,
    0x7ED1BDAC: 0x7ED1BDAC,
    0x7FB062FC: 0x7FB062FC,
    0x805E897E: 0xE323B8A6,
    0x811D7865: 0x811D7865,
    0x8166E481: 0x105D321B,
    0x83947811: 0xCB43CFDF,
    0x85AFAB17: 0x85AFAB17,
    0x86875C74: 0xAE175C51,
    0x86D4964A: 0xDF9F0A58,
    0x871A9884: 0x6C7BB4CC,
    0x87345411: 0xC29A13D7,
    0x87BE9516: 0x98338F79,
    0x8856F449: 0x2EC4092E,
    0x89091E6D: 0x6C8CAD96,
    0x8AC791FF: 0x70C10F1D,
    0x8B9F7D9D: 0xA786BD26,
    0x8DF69FD2: 0x45A83BAC,
    0x8E4E8777: 0x8E4E8777,
    0x906522F: 0xC9191F0B,
    0x90D7B5FE: 0x8B28FCF6,
    0x919F339C: 0x919F339C,
    0x9211830F: 0xF0F62A15,
    0x921B38C1: 0x921B38C1,
    0x9250C8BA: 0x572722B2,
    0x92A63D27: 0x92A63D27,
    0x92B379D6: 0x92B379D6,
    0x92E55148: 0x92E55148,
    0x940356EC: 0x940356EC,
    0x9444F651: 0x5B656B5E,
    0x9463B6EC: 0x9463B6EC,
    0x950CB3A7: 0x64661E84,
    0x967AB73F: 0xE0F19098,
    0x96D3C7C9: 0x96D3C7C9,
    0x9743835: 0x9743835,
    0x977F60F3: 0x2BD8DAA2,
    0x97E8BDD2: 0x61EA1771,
    0x99220653: 0xE6990DF6,
    0x99D3A837: 0x8BC399CB,
    0x9A1FBCDE: 0x52E2B2A3,
    0x9B794B37: 0xCA17808F,
    0x9C521B0E: 0x59C888DC,
    0x9C9D9825: 0x9C9D9825,
    0x9F01F3E8: 0x9F01F3E8,
    0xA0223301: 0xA0223301,
    0xA14A5E80: 0xA14A5E80,
    0xA14B735D: 0xC9191F0B,
    0xA1DB71E4: 0x88BED91C,
    0xA2A0EA04: 0xB154D360,
    0xA57378E4: 0xA57378E4,
    0xA5B2718: 0xA5B2718,
    0xA652F65B: 0x6F6DDF7,
    0xA6B5F01C: 0xA6B5F01C,
    0xA85E3F8F: 0xA85E3F8F,
    0xA85E54C3: 0xA85E54C3,
    0xA8D88C65: 0xC5C69E99,
    0xA9F8638D: 0x7CE69F62,
    0xAAAD9661: 0xAAAD9661,
    0xAAB50608: 0xE2C6385A,
    0xAAB66CD2: 0xAAB66CD2,
    0xAB6F5A5C: 0xAB6F5A5C,
    0xAE93BE1B: 0x223C5A4B,
    0xAEEA7AA: 0x70C10F1D,
    0xAF21720A: 0x83733B2C,
    0xB020277A: 0xE2C6385A,
    0xB175496F: 0xB175496F,
    0xB41AF196: 0xA3BCA99F,
    0xB443171C: 0x557A78BE,
    0xB4781545: 0x65E386DF,
    0xB66B2061: 0x64661E84,
    0xB7B2364B: 0x435DE23C,
    0xB829B5C1: 0xAE65D4A9,
    0xB873BC96: 0xCD2395BD,
    0xB97E0E50: 0x8FD5188,
    0xB9B6B09C: 0xB9B6B09C,
    0xBAA25DF0: 0xBAA25DF0,
    0xBAF6C9D: 0xBAF6C9D,
    0xBC13FC51: 0x2C23E58C,
    0xBC5DFE21: 0x54B10280,
    0xBCAD15E2: 0x6F656E76,
    0xBD2ACF79: 0x985715E4,
    0xBDD17741: 0xBDD17741,
    0xBDDE2CEA: 0xCAD91C7C,
    0xBED0FFC9: 0x625AD2F,
    0xBF286AF3: 0x37AC1C6F,
    0xBFAEC15D: 0xBFAEC15D,
    0xC08FE639: 0xFE305E68,
    0xC0E532FA: 0x985715E4,
    0xC29A13D7: 0xFD39A53C,
    0xC3424435: 0xCB43CFDF,
    0xC36D15E4: 0x869E39E,
    0xC4174E9: 0x35D473A3,
    0xC49CCB14: 0x7CE69F62,
    0xC5206DB6: 0x1275A9C3,
    0xC6E557FA: 0xC6E557FA,
    0xC6E56767: 0xC6E56767,
    0xC8A9F1CB: 0xC8A9F1CB,
    0xC8CD28E5: 0x64661E84,
    0xC8D807B8: 0xA4D3DAEC,
    0xCB98196F: 0xFDA60B13,
    0xCC02BD2A: 0xCC02BD2A,
    0xCC2BF8B2: 0x2BCA7663,
    0xCD2395BD: 0xCD2395BD,
    0xCDBBB43F: 0x63D8DCE1,
    0xCE2D3036: 0xC0AF5542,
    0xCE3E134D: 0x64E0E172,
    0xCE4E7ADE: 0x99284D9E,
    0xCF65E336: 0xB9EEC491,
    0xCF8F1FF9: 0x9089FDCE,
    0xCFD287D0: 0xCFD287D0,
    0xD0890CA1: 0xE67026F1,
    0xD0C82B7E: 0xE6B98A30,
    0xD28AB359: 0xAE175C51,
    0xD43A1415: 0x8E4E8777,
    0xD47F142B: 0xD47F142B,
    0xD641CC07: 0xE1AFB0B1,
    0xD684486D: 0x2561181F,
    0xD6D82BE2: 0x8166E481,
    0xD9DA57D2: 0xD5C2BA2E,
    0xDA19E0C9: 0x43114132,
    0xDB6A33BD: 0xBF632156,
    0xDC222275: 0xD889C7AE,
    0xDC628C32: 0xDC628C32,
    0xDCACF35E: 0xDCACF35E,
    0xDFCFCA0F: 0x9089FDCE,
    0xE09D0EA5: 0xE09D0EA5,
    0xE0A8E648: 0xA52025E4,
    0xE0EAD657: 0x4C4F9B19,
    0xE431F730: 0x1275A9C3,
    0xE47FA72E: 0xDB208841,
    0xE523691A: 0xC556E676,
    0xE5A10DB1: 0xE5A10DB1,
    0xE8136BD8: 0xD476C00D,
    0xE8404627: 0x6D0ED0CC,
    0xE8F565D7: 0xE8F565D7,
    0xE94F18D6: 0x40A4847C,
    0xE9D29B1E: 0xAE5E8912,
    0xEB97E938: 0xEB97E938,
    0xEBEAC370: 0x45A83BAC,
    0xECEF2B2: 0xA14A5E80,
    0xEFACC883: 0x5B9A18FA,
    0xF095A049: 0xE34DD49,
    0xF0A43A75: 0xF0A43A75,
    0xF1DA5BFA: 0xF1DA5BFA,
    0xF242686D: 0x7B09D36E,
    0xF3291734: 0x3CA945D1,
    0xF5022F4A: 0x9089FDCE,
    0xF584D6BF: 0x21E250E3,
    0xF5B622C8: 0x985715E4,
    0xF5F5F8E8: 0xF5F5F8E8,
    0xF6CABD05: 0x5E63299A,
    0xF7EE78F: 0xF0214C18,
    0xF7F86450: 0x82322F4E,
    0xF88D90E: 0x3E88D019,
    0xF8D79C3A: 0xF8D79C3A,
    0xF9B39D1: 0x4E112B74,
    0xF9FBA9C6: 0x4ACEBF72,
    0xFA3286E0: 0xFA3286E0,
    0xFB1936B1: 0xC8E14DAF,
    0xFC562840: 0xE0CA4C4F,
    0xFCFA0204: 0xFCFA0204,
    0xFDA9673: 0xFDA9673,
    0xFE727B39: 0xAE682D86,
    0xFE9814C9: 0x1275A9C3,
    0xFEDD7F11: 0xE0EAD657,
    0xFF368B: 0x117EEE29,
    0xFF5D3231: 0xFF5D3231,
    0xFFEE5095: 0x3B281D8,
}


THE_URBZ_SHADER_ID_TEXTURE_ID_LOOKUP = {
    0x10004FD7: 0x6C8CAD96,
    0x105A8FD1: 0xE02BBA87,
    0x110D74C: 0x6292ED88,
    0x1134CE39: 0x6FD3BE2D,
    0x113F9350: 0xE6B98A30,
    0x115DF1B5: 0x73299646,
    0x117EEE29: 0xD1FE04B5,
    0x11D5C4CF: 0x4E0B10A2,
    0x1273CCE0: 0x2609535A,
    0x133926DB: 0x44CE8422,
    0x1381352E: 0xE8860FBE,
    0x139EAFF: 0x7538C9FE,
    0x13AA754D: 0x8D21206C,
    0x142F5690: 0x65AFE72B,
    0x143CA1C9: 0xEEB5400C,
    0x14CA6416: 0x200222BE,
    0x14FB0EEC: 0xE3A2E817,
    0x153D36ED: 0xD14AD1EA,
    0x1572EFD8: 0x706B3366,
    0x1577A09: 0x16605CCF,
    0x15790BE1: 0x13F28B5C,
    0x15BB3E8A: 0x1A18CA65,
    0x16B12E95: 0xC38927D7,
    0x16D042F8: 0x78E9652D,
    0x17467B29: 0x60DD42D5,
    0x17B4B65: 0x1D6C70CD,
    0x181650E1: 0xF8C758CE,
    0x18B15FED: 0x488CD75A,
    0x1991049B: 0xCF717C1D,
    0x19C4380B: 0x821295BF,
    0x19DE6F84: 0x40FC3B4,
    0x1A42955: 0x361F4B94,
    0x1AC8260: 0x543C9E94,
    0x1B006D70: 0x9940141D,
    0x1B08020F: 0x88B06ED6,
    0x1BC977BB: 0xCD1DB7E6,
    0x1C15E7F4: 0x7F97DD30,
    0x1C1690A5: 0xA36FF65E,
    0x1C1B6B57: 0xF578CE62,
    0x1C7DC111: 0xE25DBAB,
    0x1CC137D9: 0x543C9E94,
    0x1CEC401C: 0xA9CE3E2D,
    0x1D11BD2: 0xC226D233,
    0x1D18C2D3: 0xFAF3E82F,
    0x1DB67895: 0xE1C74FCE,
    0x1E0C5A60: 0x7D0FED21,
    0x1E970A4: 0xB4CB0E95,
    0x1ED318CE: 0x187BF702,
    0x1F04EA99: 0xD327A3DB,
    0x1F922CF4: 0xDBF1D3C2,
    0x1FC19DC4: 0x67541E65,
    0x1FEDE00E: 0x2B6458D9,
    0x2082476B: 0xCF954823,
    0x211DE8A1: 0x7922EB3D,
    0x21F3AE56: 0x42719492,
    0x22A1B474: 0x10532EF3,
    0x22B317F: 0x1F10857B,
    0x232B38CE: 0x5829FDDC,
    0x23FA7805: 0xFB4353C8,
    0x2455C976: 0xA474EF35,
    0x257EE807: 0x2774CE7E,
    0x25AC1AF0: 0xB7BCA6F1,
    0x25D1765D: 0x3F8BE7CC,
    0x25DDF1DB: 0x30DE01DE,
    0x262736EB: 0x23FD55F3,
    0x266AC55D: 0x6292ED88,
    0x267CD082: 0x26059920,
    0x2689445A: 0xB42BFB68,
    0x26D593A: 0xE1C74FCE,
    0x26D9E0F: 0xF578CE62,
    0x2951992B: 0x5347B916,
    0x29D11ABF: 0x7BCE6719,
    0x29F8E3CB: 0x7492FF3F,
    0x2A339472: 0x91913DB8,
    0x2ACD49B6: 0xF41A6E6,
    0x2B599795: 0x9E5A7C0,
    0x2B904B3: 0x8401CBB2,
    0x2B969D51: 0xDCA27B81,
    0x2C79DDCE: 0x3CC4348F,
    0x2CA020F2: 0x40287B93,
    0x2D0CF64E: 0x706B3366,
    0x2D14A235: 0x7C7CDC3F,
    0x2D1D2672: 0xFB964EAB,
    0x2D22AC70: 0xBABF337,
    0x2D3AA661: 0x972C8A11,
    0x2DAED9A9: 0x82338AF1,
    0x2E677C8C: 0xD560461C,
    0x2E865060: 0x28B82885,
    0x2E86FAB4: 0xFE5D4FDF,
    0x2E9EDB64: 0x339A501,
    0x2FE4FEBD: 0x13842217,
    0x309F6FB1: 0x8DC9DE2E,
    0x30E313F: 0xD59C7BB5,
    0x3152FE76: 0x86ACB063,
    0x32D8723E: 0x36FD14EC,
    0x33624C34: 0xC86576A4,
    0x339BEBDC: 0x1E3C95B9,
    0x3415C2F0: 0xD3017A8,
    0x35C24056: 0x82338AF1,
    0x364C5B0: 0xD59C7BB5,
    0x36CE5870: 0x91913DB8,
    0x377E094C: 0xA87E4573,
    0x3799831: 0xDCA16A16,
    0x379AC3D: 0xFA0BD0C7,
    0x379CF73B: 0x99FA946C,
    0x38747420: 0xC584A3D2,
    0x38FD832C: 0x3FAC9CFB,
    0x39CAAF9D: 0xA87E4573,
    0x3A208304: 0xC0C68FB4,
    0x3BCD2DC9: 0x5622D01A,
    0x3BDB4FE: 0xE063E670,
    0x3C0F3906: 0x892D4737,
    0x3C3753B9: 0x61676C59,
    0x3C4C7E4E: 0xEEB5400C,
    0x3C8315BD: 0x117EEE29,
    0x3CAE43D3: 0x5A94379F,
    0x3CE38808: 0x4B7A27E9,
    0x3CF04FC5: 0xB65FEDE4,
    0x3D4A6DE0: 0x3D635A62,
    0x3ED5BA70: 0xD6766DC8,
    0x3EDD9D4E: 0x9764D6E6,
    0x3EF40E53: 0x71839329,
    0x3F8CE0B9: 0xC86576A4,
    0x4015650F: 0x781467,
    0x4035104A: 0xB42BFB68,
    0x40901A9: 0xD59C7BB5,
    0x40F1A6E9: 0x6DF5F3C0,
    0x419914EC: 0xA87E4573,
    0x41F1A1B6: 0x4E83792E,
    0x41FDE76F: 0x1F10857B,
    0x423D0F53: 0xA3BCA99F,
    0x426D701F: 0xEAE9154B,
    0x43B50375: 0x6E127D10,
    0x43E794C2: 0x2570F3E7,
    0x4443F18: 0xF0EAD394,
    0x44592BA7: 0x69FE55C2,
    0x44A724B: 0xD79D1101,
    0x45671C70: 0x322AF47E,
    0x45D90B11: 0xF42AC16E,
    0x463F526: 0xD59C7BB5,
    0x4674A590: 0xDB010002,
    0x485C2366: 0xA28044A2,
    0x485C44F4: 0x37BE8D01,
    0x4892E335: 0xA8B22F78,
    0x4919F43B: 0xA60C9ACA,
    0x4949AE89: 0x6BB7020E,
    0x49C5F67D: 0x2349AEA4,
    0x49D34521: 0x30244AB6,
    0x4A2C0E2E: 0x5867532E,
    0x4A76FD72: 0xCF80584F,
    0x4AA862D: 0xDF7975E5,
    0x4AC3DD05: 0xD025F331,
    0x4B566618: 0x5742FCF2,
    0x4C21D1AF: 0xF903AF9E,
    0x4C9B3D8: 0x274853F2,
    0x4CD623AE: 0x60B98F91,
    0x4E1A9E8C: 0x3FAC9CFB,
    0x4E7CBE92: 0xFF282D36,
    0x4E9146BA: 0x651C5DB5,
    0x4F2DB23D: 0xA87E4573,
    0x4FC27EC5: 0xBAE55CC4,
    0x503504D7: 0x1AB07C2A,
    0x50F6FA97: 0x7FA6F01,
    0x5124E117: 0xE4069F26,
    0x513661E1: 0xF86E3DE3,
    0x5155E7D7: 0x8C8CFCD6,
    0x51880520: 0xE4DFE11E,
    0x51A851DB: 0xF5F2036F,
    0x51DD46FF: 0x325F7C3B,
    0x5358461A: 0x70C10F1D,
    0x53AD64E0: 0xF9803C02,
    0x540CDF68: 0xCBE67563,
    0x5446A9D4: 0x10532EF3,
    0x55017EA8: 0x1EBEDB04,
    0x551AF6A9: 0xB869EEDC,
    0x56A55968: 0xDCB6CCFE,
    0x56A752CA: 0x7CFD9514,
    0x57FAF501: 0x7922EB3D,
    0x5861E714: 0xFE5D4FDF,
    0x588297D2: 0xF12A81B6,
    0x59A5BCF7: 0xA2A28667,
    0x59B170D4: 0x78EEE164,
    0x59DAA9C: 0x48ABAC6D,
    0x5B13152: 0x53EBC000,
    0x5BADBA8E: 0x3B7D4D71,
    0x5BDDBBC1: 0x972C8A11,
    0x5BEF05E0: 0x78A965CA,
    0x5C1D8FB1: 0x27614F9,
    0x5C93EFEA: 0x6D91597B,
    0x5CCDED1: 0x8CAC9459,
    0x5DD519C9: 0xAB54489F,
    0x5EA3978D: 0x2B5FB197,
    0x60097E63: 0x6B31F792,
    0x607ED2: 0x6D9F2B9C,
    0x609F9494: 0xED8DAEB6,
    0x617829A1: 0x35D473A3,
    0x617987DF: 0x54D09C5F,
    0x61A77F5D: 0x66F48339,
    0x623B4C2: 0xE0469206,
    0x624092FE: 0x92E55148,
    0x6254B079: 0xFD5895E6,
    0x62710C8D: 0xA682B676,
    0x6289A0CA: 0x9D148563,
    0x62C5D603: 0xE74B90F9,
    0x62E0A585: 0xF41A6E6,
    0x63567A6F: 0x4EF1040A,
    0x6396E3C: 0x317714C9,
    0x63AFDD87: 0x98A8E717,
    0x650FFF5D: 0x7515A70D,
    0x65B2D98A: 0xE5235601,
    0x66BD9271: 0xE02BBA87,
    0x66C753A2: 0xFFB6AAC5,
    0x67BE2FBD: 0x4733DA5,
    0x68241422: 0xB559DE44,
    0x689B4255: 0x9D148563,
    0x68EA48A0: 0xABFABB36,
    0x69268064: 0x67541E65,
    0x698A6878: 0x2041FCF2,
    0x6A9ADCB1: 0xE25DBAB,
    0x6AB353EA: 0xC7AF9728,
    0x6AD7DF8E: 0x706B3366,
    0x6B1C5BC1: 0xF578CE62,
    0x6B99F23E: 0x96B88ED6,
    0x6BCC5DC2: 0x70CF5F85,
    0x6BD7278F: 0x8551D4B,
    0x6D940A: 0xD59C7BB5,
    0x6E2B329: 0x1C079CB0,
    0x6E851672: 0x70C10F1D,
    0x6E88C3F: 0x2A4303A2,
    0x6E9D2070: 0xA6ECCD12,
    0x6EF135EA: 0x529D80D6,
    0x6FB8D6E2: 0x4EF1040A,
    0x70DBCAA4: 0x2A4303A2,
    0x70DE739C: 0x317714C9,
    0x710F5584: 0x781467,
    0x719A0BEC: 0x3737E274,
    0x71A285C: 0x349E3208,
    0x71BA2E9A: 0x14FC1A0F,
    0x71C7980D: 0xC4E5E63C,
    0x724D9B8D: 0xDF7975E5,
    0x72BA68CC: 0xBFFFBCAC,
    0x72DA48B1: 0x16F93F97,
    0x72F0A060: 0xADC261F5,
    0x737AB73C: 0x48ABAC6D,
    0x743B27BC: 0x4E6B75B2,
    0x7471EF5C: 0x91B8AADA,
    0x747B126F: 0x5DAC038,
    0x74F9FF74: 0xCFD0C359,
    0x756AAE99: 0xF578CE62,
    0x7570E902: 0x93D91195,
    0x75921511: 0x77879680,
    0x75A9E9C5: 0xE80CF6B0,
    0x762BB0DF: 0xC309CEEE,
    0x765EF306: 0xE4069F26,
    0x77142397: 0xDD4A4DD0,
    0x772F655: 0x6B92906,
    0x77BF445A: 0xD9B186DF,
    0x7804660A: 0x955B73F2,
    0x780F81EC: 0x40287B93,
    0x784D4625: 0x448193B3,
    0x787F70B3: 0xE1AC0207,
    0x790631D6: 0x650A3BB2,
    0x7935D530: 0x5742FCF2,
    0x797DE79E: 0xE6D875C,
    0x79EFE6F3: 0xCBE10A74,
    0x7B0E1D97: 0xD08ACEE2,
    0x7B6FD2A1: 0x707EDF35,
    0x7C28E9C5: 0x96857607,
    0x7CE3DDC2: 0x3FC77608,
    0x7D433C9B: 0x9ED4EF77,
    0x7DCFA32: 0x2A4303A2,
    0x7E534AD7: 0x53F434B2,
    0x7E6AD54D: 0x317714C9,
    0x7EB1E38F: 0x67BD038B,
    0x7EF67F16: 0x7538C9FE,
    0x802C9186: 0xD2143E7F,
    0x81310D86: 0x25184DB,
    0x8139E380: 0x120FA09C,
    0x82DF933A: 0xCCACC707,
    0x84057207: 0x6D327685,
    0x84716198: 0xB1657432,
    0x85123AED: 0xF578CE62,
    0x854A20A7: 0x27342AED,
    0x858374F2: 0x10718CF8,
    0x85C0B39A: 0x8791F244,
    0x85E342A1: 0xD61EEACE,
    0x862D62DD: 0x2591CE38,
    0x86543228: 0x60D2BED,
    0x86B5CB49: 0xB59BA459,
    0x86F54CDF: 0xB89278B5,
    0x877D020A: 0x325F7C3B,
    0x8784A5E2: 0xE4069F26,
    0x87C1EEBC: 0x8C2EA3A6,
    0x87C27BD2: 0xE2357B11,
    0x87CD3D4D: 0xD814B1FC,
    0x88562F58: 0x5F6B151E,
    0x88DC8ED: 0x317714C9,
    0x88E91E91: 0xEE6DC42D,
    0x89091E6D: 0x6C8CAD96,
    0x8973732D: 0x4F6F3D20,
    0x8A0DC4ED: 0xAA8F3246,
    0x8A2ED5E6: 0x3C1B7051,
    0x8A460EE2: 0xB5B42310,
    0x8A68D8AD: 0xF1A3034,
    0x8AC791FF: 0x70C10F1D,
    0x8AD5F494: 0x7FA6F01,
    0x8BA02E04: 0xB466DDB5,
    0x8BEA738D: 0x361AD0D0,
    0x8BFEFD02: 0x1D6C70CD,
    0x8C22FE69: 0x87D9F072,
    0x8C2AFBAA: 0x7E4F2F24,
    0x8CA476C6: 0xF578CE62,
    0x8D34B69D: 0x6F90514A,
    0x8DEA1312: 0xD6C259F6,
    0x8DF69FD2: 0x45A83BAC,
    0x8E673818: 0x2591CE38,
    0x8E7516AE: 0x5742FCF2,
    0x8EFE5F8C: 0x91B8AADA,
    0x8F05F802: 0xA2A28667,
    0x8F7E9604: 0x6D327685,
    0x8FF872CF: 0x3FEDDC57,
    0x906522F: 0xE1C74FCE,
    0x91B24852: 0x43500F44,
    0x920A1800: 0x7094A716,
    0x9287A760: 0x8791F244,
    0x92A015D0: 0x497B7AEF,
    0x92ADD4F2: 0xD5A5766,
    0x92F96F52: 0x69FE55C2,
    0x93006C44: 0xE29900B7,
    0x931188FD: 0x7A959947,
    0x932CD6A1: 0x261C0A8F,
    0x933D34B1: 0xE7467E9E,
    0x93758D30: 0x67E33C4F,
    0x9449D048: 0x40592928,
    0x9475780C: 0x28573761,
    0x94DDAECE: 0x7B6EA833,
    0x94E382E3: 0x36B8EBF4,
    0x95154780: 0x6E127D10,
    0x979A1B31: 0x236A5668,
    0x97F1AA4D: 0xA1EF726F,
    0x98DFC664: 0x4CE32B09,
    0x99220653: 0x2A4303A2,
    0x9A1FBCDE: 0x52E2B2A3,
    0x9A61E4C7: 0x959509A,
    0x9A81955A: 0xF903AF9E,
    0x9A8EF157: 0xB783DAFD,
    0x9B64CFB5: 0xF578CE62,
    0x9BCD9731: 0x96714CFA,
    0x9C090BAC: 0xF578CE62,
    0x9CBEAC3A: 0x7163EA06,
    0x9D793B52: 0xB30B2C8,
    0x9E0DBF19: 0x9D148563,
    0x9E21F54B: 0x5918AADB,
    0x9E94507B: 0x6B60FA13,
    0x9F061E7: 0x5F746C65,
    0x9F1BADA7: 0x341E44DE,
    0x9F6243F2: 0x495C92F6,
    0xA08BF42A: 0xC309CEEE,
    0xA0942E75: 0xADA0941B,
    0xA0FEB7F3: 0xE4069F26,
    0xA14B735D: 0xE1C74FCE,
    0xA1DD5451: 0xDCA27B81,
    0xA22A98E2: 0x25CEF95E,
    0xA2452239: 0x7791BFD5,
    0xA27A53C1: 0x7E4F2F24,
    0xA2F69079: 0xD79D1101,
    0xA3E2B25E: 0xA74CF9E0,
    0xA48D7C25: 0x25CEF95E,
    0xA68EC203: 0xC9DA2C36,
    0xA6C9E328: 0xF12A81B6,
    0xA6FBBF9: 0xE11AB573,
    0xA7007E98: 0x63C7BF02,
    0xA767DCF8: 0xC4E5E63C,
    0xA8F30E22: 0x53F434B2,
    0xA9608350: 0x2E78D6A9,
    0xA99F5951: 0xDB89C566,
    0xA9B8CA5F: 0xA71294AF,
    0xACEA7F09: 0x4695A560,
    0xAE465CE0: 0x9606744D,
    0xAE5D1D01: 0x90414E08,
    0xAEA80B24: 0xF4CF5D92,
    0xAEF5EC07: 0xF95AF948,
    0xAF03D044: 0x70726168,
    0xAF1E9817: 0x33AF3B8B,
    0xAF646D1D: 0xB58247C8,
    0xAF6A31B0: 0x7939780,
    0xAFE5B9B2: 0xEEE87DC4,
    0xB1A7865A: 0x705B04F3,
    0xB2CB9D9C: 0xDDB2B939,
    0xB3632ECA: 0x5F9254D7,
    0xB41017C3: 0x65D21268,
    0xB41AF196: 0xA3BCA99F,
    0xB4F4CF2F: 0x9F108D2C,
    0xB50F9972: 0x98A8E717,
    0xB53606E8: 0x286C2588,
    0xB5F63E9A: 0x4EF1040A,
    0xB68A5A3D: 0x411DE046,
    0xB6E8E571: 0xCC8BA28E,
    0xB7B74386: 0x955B73F2,
    0xB7FFBC06: 0x6927937,
    0xB873BC96: 0xCD2395BD,
    0xB8A933E6: 0x7CFD9514,
    0xB8C8EA7E: 0x1F10857B,
    0xB9078D61: 0x28573761,
    0xB9189217: 0x4EF1040A,
    0xB9C53453: 0xD9B186DF,
    0xBAAD14FD: 0xAF13816A,
    0xBB98F48F: 0x9C10C9A0,
    0xBC23BAD5: 0xA9274252,
    0xBCDCF473: 0x74CF6960,
    0xBD264061: 0xC39788F5,
    0xBD472C30: 0xBE337A25,
    0xBD6D9CDA: 0xE7467E9E,
    0xBD77637A: 0x8551D4B,
    0xBE635759: 0x6B92906,
    0xBF3B9523: 0xB9256F09,
    0xC022D3A0: 0x16281275,
    0xC06D479D: 0x411DE046,
    0xC1BB8FF: 0x706B3366,
    0xC1BFEC5: 0x840A3145,
    0xC23B9F18: 0x1E273F4,
    0xC2C7A639: 0x85FEAE29,
    0xC3D11B48: 0x286C2588,
    0xC472022: 0x37363679,
    0xC50F850F: 0x71A65B69,
    0xC52171DB: 0xE8860FBE,
    0xC683B1B4: 0xEEB5400C,
    0xC68503DD: 0xCA2A0B91,
    0xC68AB7E9: 0x4C8D45AB,
    0xC850366B: 0x81CD4661,
    0xC902750: 0x4581D8F5,
    0xCA4C04E9: 0xA9CE3E2D,
    0xCA63F4A1: 0x7ED17898,
    0xCAB5A301: 0x7F97DD30,
    0xCB6E179D: 0x7D0FED21,
    0xCB88874C: 0x63D10348,
    0xCB8A817A: 0xE7467E9E,
    0xCB98196F: 0xFDA60B13,
    0xCBB79FED: 0x474F0D3C,
    0xCC4A095D: 0xAF13816A,
    0xCD7A8B0E: 0xBABF337,
    0xCE751B51: 0xC39788F5,
    0xCE85955: 0x2F3E2247,
    0xCE92FBF5: 0x31CB8D26,
    0xCFB8A05D: 0x1D6C70CD,
    0xD0890CA1: 0xE67026F1,
    0xD0C82B7E: 0xE6B98A30,
    0xD17A5638: 0xFBFDC866,
    0xD3AB67B7: 0xA805712F,
    0xD3EEEFEB: 0xA805712F,
    0xD43A1415: 0x8E4E8777,
    0xD49D4E61: 0x7E4F2F24,
    0xD4CD6378: 0xC8F88C3A,
    0xD5920766: 0xEE633AFD,
    0xD64F9E7: 0xE29900B7,
    0xD6AA49C: 0xD59C7BB5,
    0xD717F730: 0x9F20B6F8,
    0xD73138AF: 0xA750FDF8,
    0xD7493451: 0xB4CB0E95,
    0xD7B093B9: 0x6292ED88,
    0xD81AEBA8: 0x70EB5098,
    0xD8BA00A1: 0x90414E08,
    0xD8DDE68B: 0x23DADC1B,
    0xD92EF047: 0x57BF6F0B,
    0xD98AFB94: 0x8539920A,
    0xD98D2C10: 0x7939780,
    0xD9D38C1F: 0xCA3C95EB,
    0xDA4FFB81: 0x989AA6D4,
    0xDAF319E2: 0xB0AA3C1A,
    0xDB6A33BD: 0xBF632156,
    0xDC3434B6: 0xAF6E8132,
    0xDDC05D68: 0x4F8728D8,
    0xDEA3EC29: 0x9D052F7E,
    0xDF7CD98B: 0xF64C3C7C,
    0xDF8203FC: 0x5610DDE3,
    0xDFD80F81: 0xD327A3DB,
    0xE007D93: 0x1F10857B,
    0xE0A41FD4: 0x105ADDD8,
    0xE0EAD657: 0x4C4F9B19,
    0xE0ED51AB: 0xA94762B9,
    0xE1B55A07: 0x88FC1334,
    0xE20D85C6: 0xA2D6E004,
    0xE3B80C5D: 0x3641E6C8,
    0xE3F610C6: 0x2FCF7D61,
    0xE4075CD2: 0xE29900B7,
    0xE4ED05A0: 0x7094A716,
    0xE4F1AEE9: 0xD5A5766,
    0xE506FC12: 0x56E53F1E,
    0xE52A356E: 0x4D9521C4,
    0xE53BAF29: 0x1E3C95B9,
    0xE54AA861: 0x915C56AB,
    0xE5AC9774: 0x9E7D7FA5,
    0xE5C208C1: 0xC86576A4,
    0xE5DA2911: 0xE7467E9E,
    0xE62604D6: 0x74E21FD5,
    0xE62F6DAD: 0x88BED91C,
    0xE6418E97: 0xB30B2C8,
    0xE658CAD: 0xBA40FF1E,
    0xE712C375: 0xBA849303,
    0xE7DA27E: 0x23DADC1B,
    0xE8136BD8: 0xD476C00D,
    0xE8493B3D: 0x855876F4,
    0xE89A17D8: 0xCB90CE06,
    0xE92B81EF: 0x88B06ED6,
    0xE92CA44C: 0xC86576A4,
    0xE96D8670: 0xAEE2D86B,
    0xE998498B: 0x4A481FED,
    0xE9D29B1E: 0x2A4303A2,
    0xE9E55BC0: 0x6C171670,
    0xEA6CFF51: 0x685F6873,
    0xEA88D8AA: 0x3A78E446,
    0xEAA73980: 0xC226D233,
    0xEAAF7DF3: 0x892D4737,
    0xEB0E3B3A: 0xF578CE62,
    0xEBA9B6E1: 0x68702128,
    0xEBEAC370: 0x45A83BAC,
    0xEC63FF23: 0xF578CE62,
    0xED8620A3: 0x7FC2E2D4,
    0xEDBC636B: 0x23FD55F3,
    0xEE6D8776: 0x6F90514A,
    0xEEBE02DC: 0xD68B0B40,
    0xEF5340AF: 0x92CE80D1,
    0xEF9DA8C1: 0x706B3366,
    0xF03C1F43: 0xBF072E8E,
    0xF0B82A3C: 0xBC99BF1B,
    0xF0CA81A8: 0x6292ED88,
    0xF0E559DD: 0xCF548F44,
    0xF12A20ED: 0xD814B1FC,
    0xF2150A7B: 0xF578CE62,
    0xF2967C38: 0xB1657432,
    0xF3291734: 0x2A4303A2,
    0xF46AEDCB: 0xAB074136,
    0xF48207C9: 0x7208DA53,
    0xF4F46095: 0x65EEC9F4,
    0xF538513F: 0x13AD4B8D,
    0xF608E930: 0x6CEFB9C9,
    0xF6148123: 0x1E967A6,
    0xF63A3A0A: 0xD2109855,
    0xF6F835E: 0x33E2D926,
    0xF753EAA3: 0x42719492,
    0xF79889C1: 0x2B17E300,
    0xF83E9F91: 0x339A501,
    0xF8C73879: 0xD560461C,
    0xF8DF809: 0x1D7E9112,
    0xF952DCEC: 0xFA48196A,
    0xF9BF5857: 0x5039F54A,
    0xFA919FFD: 0x37E96AC6,
    0xFACDE60A: 0x7E4F2F24,
    0xFB8A4EF9: 0x455493A,
    0xFBA34650: 0xF578CE62,
    0xFBE52A6D: 0xBD2D3B07,
    0xFCB1B0C4: 0xB9D3557,
    0xFD0D6E2D: 0x361AD0D0,
    0xFD5DD805: 0x9E7D7FA5,
    0xFE0DBEAF: 0x697AC6FB,
    0xFE6E2539: 0x58000000,
    0xFE8197D1: 0xCA2DE671,
    0xFEB132F8: 0x5F6B151E,
    0xFF005B4D: 0x70EB5098,
    0xFF0AA526: 0x6A817C77,
}


THE_SIMS_2_SHADER_ID_TEXTURE_ID_LOOKUP = {
    0x10004FD7: 0x6C8CAD96,
    0x102311E3: 0x3ABB8B92,
    0x1134CE39: 0x6FD3BE2D,
    0x117EEE29: 0xD1FE04B5,
    0x11D5C4CF: 0x4E0B10A2,
    0x12502C71: 0x4975B20F,
    0x128521C9: 0x567841F4,
    0x12896ACD: 0xEE846AE9,
    0x12923CF7: 0xE489C6E5,
    0x129D709A: 0xA87381FF,
    0x12EAF880: 0x4DDD3537,
    0x1320A05B: 0x7303CA3F,
    0x143CA1C9: 0xEEB5400C,
    0x15315786: 0xC146CF08,
    0x15BB3E8A: 0x1A18CA65,
    0x15C64320: 0xFB517438,
    0x15E8E5D0: 0x567841F4,
    0x17B4B65: 0x1D6C70CD,
    0x1852745E: 0x278D1DA8,
    0x19B39D10: 0x3F000000,
    0x1A57F5D3: 0x9F11E81C,
    0x1A998430: 0x931CC426,
    0x1B08020F: 0x88B06ED6,
    0x1B649EC4: 0xFFB6AAC5,
    0x1BF6870B: 0xA4E31BCB,
    0x1DB67895: 0xE1C74FCE,
    0x1E6C062E: 0x38369108,
    0x1E9DE59A: 0xF4A3FFCF,
    0x1EAE280D: 0x9E12E763,
    0x1F04EA99: 0xD327A3DB,
    0x1FD6DDC7: 0x1EDD394C,
    0x2088C2B5: 0x9BB8C18,
    0x20C03BDE: 0xD59C7BB5,
    0x215D20E: 0x9E12E763,
    0x21D6425D: 0xFFB6AAC5,
    0x22B317F: 0x1F10857B,
    0x22BE4EA4: 0xAC44FCC6,
    0x234F244: 0xD96DDDCF,
    0x236A877: 0xE3107C90,
    0x25A4B7D: 0x99C934BC,
    0x276F0951: 0xFC307EE9,
    0x27ADFFC7: 0xD59C7BB5,
    0x281F7282: 0x733AECFC,
    0x2858350: 0x6D3CC1C4,
    0x295345DE: 0x6A4C6603,
    0x29F8E3CB: 0x7492FF3F,
    0x2B28320B: 0xA87381FF,
    0x2B969D51: 0xDCA27B81,
    0x2C472022: 0x37363679,
    0x2D1D2672: 0xFB964EAB,
    0x2D31F06C: 0xCCE49970,
    0x2D79BDAE: 0x9F11E81C,
    0x2E1805C9: 0x4B82EF9D,
    0x3198765E: 0x18706891,
    0x31F609DF: 0xCFCBA79F,
    0x3242DBA0: 0x537C6406,
    0x325EE732: 0x8BF86EF1,
    0x33279867: 0x4A0DEBD3,
    0x35F01709: 0x3F258626,
    0x3714372C: 0xF7E12221,
    0x374F35FA: 0xFCA6911F,
    0x37921423: 0xC663F21A,
    0x3837FA89: 0x8A52385F,
    0x38724639: 0x33E5F08B,
    0x39DB0A9F: 0xD59C7BB5,
    0x3A271A78: 0xE473B56C,
    0x3A6930: 0x35034063,
    0x3B623BE7: 0xA1F7FA2B,
    0x3C4C7E4E: 0xEEB5400C,
    0x3CAE43D3: 0x5A94379F,
    0x3EDD9D4E: 0x9764D6E6,
    0x3EF954DA: 0x1AD9B009,
    0x4015650F: 0x781467,
    0x41FDE76F: 0x1F10857B,
    0x423D0F53: 0xA3BCA99F,
    0x424597E5: 0xEFDC690A,
    0x42E73DF: 0x4E01ED2B,
    0x43866824: 0x51866457,
    0x457EC109: 0xA2A9FBCD,
    0x46E10EAB: 0x76BC1C5C,
    0x47CF141B: 0x722BE697,
    0x49926958: 0xC1F242CA,
    0x49BE788D: 0x4971D3D,
    0x4A2C0E2E: 0x5867532E,
    0x4A7D912F: 0x4971D3D,
    0x4AE6D946: 0x9F11E81C,
    0x4B4359FD: 0xB45322E6,
    0x4B6966D1: 0x8B1C8CB0,
    0x4CD0EF02: 0xDD992522,
    0x4EDC3A09: 0xD59C7BB5,
    0x4F30CA1F: 0x389BC30E,
    0x4F646488: 0x4575A045,
    0x50AACF51: 0xD59C7BB5,
    0x50C06D66: 0xCFE5A532,
    0x5155E7D7: 0x8C8CFCD6,
    0x51880520: 0xE4DFE11E,
    0x523195F: 0x392B3D5E,
    0x5358461A: 0x70C10F1D,
    0x5422D29F: 0xB428EA82,
    0x556E3C19: 0x3F000000,
    0x57BEEDE1: 0x8E9C042B,
    0x57C70B48: 0xD59C7BB5,
    0x57EC02F9: 0x73E9C778,
    0x59B156F5: 0x22CCE3BD,
    0x5A738641: 0xD674A9CF,
    0x5BEF05E0: 0x78A965CA,
    0x5D5156FE: 0x9D052F7E,
    0x5DD8A35F: 0xFD4EFC15,
    0x5E007D93: 0x1F10857B,
    0x618B9A6: 0x9F11E81C,
    0x624092FE: 0x92E55148,
    0x6289A0CA: 0x9D148563,
    0x62E0A585: 0xF41A6E6,
    0x62EFD546: 0x567841F4,
    0x6376967F: 0x1C886A42,
    0x6582115F: 0x567841F4,
    0x66D495B8: 0x1A99CF2F,
    0x689B4255: 0x9D148563,
    0x698A6878: 0x2041FCF2,
    0x6A3940CD: 0xB8483304,
    0x6A6866BD: 0x8EEAA95D,
    0x6A8C2B49: 0x4EEF7EE,
    0x6BD89351: 0x40960DCA,
    0x6E2B329: 0x1C079CB0,
    0x6E36B220: 0x9E12E763,
    0x6E851672: 0x70C10F1D,
    0x6EF135EA: 0x529D80D6,
    0x6F0AD0BD: 0x31038B20,
    0x710F5584: 0x781467,
    0x719A0BEC: 0x3737E274,
    0x71BA2E9A: 0x14FC1A0F,
    0x723575C0: 0xCFD2354F,
    0x72DA48B1: 0x16F93F97,
    0x72FD84C2: 0x60545FDB,
    0x736CC54D: 0xB314C5C8,
    0x73FE1688: 0xB399D563,
    0x775ABEDB: 0xCBD8ECEA,
    0x7774E6C4: 0x79E3BC0C,
    0x77BF445A: 0xD9B186DF,
    0x7816C38: 0xF201CAF8,
    0x797DE79E: 0xE6D875C,
    0x7C00EA9F: 0xED6CE6B2,
    0x7D6AA49C: 0xD59C7BB5,
    0x7DCFA32: 0x2A4303A2,
    0x7E03228F: 0x7EACD3C,
    0x7FF3507C: 0xC3E0E58,
    0x81F8C781: 0xFFB6AAC5,
    0x8346148A: 0xDFB80A3A,
    0x844B7E81: 0xB8483304,
    0x85D7F6BF: 0xBDAC1740,
    0x85E342A1: 0xD61EEACE,
    0x862D62DD: 0x2591CE38,
    0x86543228: 0x60D2BED,
    0x869B650A: 0xB45322E6,
    0x89091E6D: 0x6C8CAD96,
    0x89CAC6DC: 0xD97C5F58,
    0x8AE86A39: 0xCE3BBD2F,
    0x8B8C7073: 0x567841F4,
    0x8BFEFD02: 0x1D6C70CD,
    0x8CCAD414: 0x8D77FEBA,
    0x8D591B61: 0x2FAF7A56,
    0x8D69E0C1: 0x27F988BA,
    0x8DF69FD2: 0x45A83BAC,
    0x8E673818: 0x2591CE38,
    0x8EB9B609: 0x471C2A0B,
    0x8F23CA0D: 0x75C8B84B,
    0x906522F: 0xC9191F0B,
    0x92964A4C: 0x29F28D35,
    0x92CF6A4D: 0x70083700,
    0x9364C5B0: 0xD59C7BB5,
    0x93A157A5: 0xD3262D90,
    0x940901A9: 0xD59C7BB5,
    0x94DDAECE: 0x7B6EA833,
    0x95634FAA: 0xAF103C46,
    0x95881571: 0xDE65BD,
    0x958DA7D4: 0x188B2C26,
    0x96BFF2B9: 0xFCA6911F,
    0x97EC06F6: 0xDC97CB55,
    0x98000A76: 0xB783DAFD,
    0x98460A3B: 0x70FC30F3,
    0x99220653: 0x2A4303A2,
    0x9924AE28: 0xC146CF08,
    0x9A1FBCDE: 0x52E2B2A3,
    0x9A8EF157: 0xB783DAFD,
    0x9B917CE8: 0x71104D8C,
    0x9C07AF5B: 0xAF83314D,
    0x9D091A8: 0x807E6040,
    0x9E0DBF19: 0x821295BF,
    0x9E21F54B: 0x5918AADB,
    0x9E6897CA: 0x251E6ADD,
    0x9E942125: 0x2EFE9850,
    0x9EA86F8B: 0x567841F4,
    0x9F797DE1: 0xE91EAE3F,
    0xA0D25B25: 0xD59C7BB5,
    0xA14B735D: 0xC9191F0B,
    0xA1DD5451: 0xDCA27B81,
    0xA2BD4B82: 0xA781E0A2,
    0xA2E7BA6A: 0xD9F37BFC,
    0xA689170D: 0x6DF29D37,
    0xA6D940A: 0xD59C7BB5,
    0xA70971C6: 0xA1BC0FE1,
    0xA7BF9F3C: 0xD59C7BB5,
    0xA99C8CD0: 0xB783DAFD,
    0xAA428A38: 0x5AAADC9,
    0xABD45EF: 0x8A03EFFB,
    0xAC8125BC: 0x3F000000,
    0xAD962808: 0x83F62F9B,
    0xAEA80B24: 0xF4CF5D92,
    0xAEF5EC07: 0xF95AF948,
    0xB0557083: 0x27F988BA,
    0xB418BB0C: 0xD0747E08,
    0xB41AF196: 0xA3BCA99F,
    0xB4F4CF2F: 0x9F108D2C,
    0xB6B8C2F4: 0x70C10F1D,
    0xB7115473: 0xECC60A66,
    0xB712E256: 0xD59C7BB5,
    0xB873BC96: 0xCD2395BD,
    0xB8C8EA7E: 0x1F10857B,
    0xB9C53453: 0xD9B186DF,
    0xB9C96A64: 0xD59C7BB5,
    0xB9F00B98: 0x4AC9CE02,
    0xBB01F1B7: 0x42D7D10C,
    0xBB704470: 0x4AC9CE02,
    0xBEA4AE7D: 0xD59C7BB5,
    0xC015D2C0: 0xD59C7BB5,
    0xC1C7D48D: 0xB02B5132,
    0xC26D593A: 0xE1C74FCE,
    0xC29A13D7: 0xFD39A53C,
    0xC568E6EA: 0xD9F37BFC,
    0xC57905C0: 0xB428EA82,
    0xC62D613B: 0xCC2F0172,
    0xC63D7534: 0xA7EB869E,
    0xC683B1B4: 0xEEB5400C,
    0xC6A1E10: 0xAF103C46,
    0xC728BC14: 0xE91EAE3F,
    0xC797F20E: 0x389BC30E,
    0xC799508C: 0x300A78B0,
    0xC84F66E: 0xF0ABDCA0,
    0xC8653AB2: 0x9E12E763,
    0xC9A39EEB: 0xD59C7BB5,
    0xCA3C382C: 0xB15C7BA8,
    0xCADEAC22: 0x51EDCF93,
    0xCB6F0E5C: 0x46B08DBA,
    0xCB98196F: 0xFDA60B13,
    0xCBB79FED: 0x474F0D3C,
    0xCD2389B7: 0x693622ED,
    0xCD4BD055: 0x567841F4,
    0xCDBBB43F: 0x63D8DCE1,
    0xCE27FBA9: 0xABF42D34,
    0xCECB2F6A: 0x29D71A8D,
    0xCECE5AF2: 0xD59C7BB5,
    0xCF0635BF: 0xF515EA1B,
    0xCF9DC91D: 0x5D4A4597,
    0xCFB8A05D: 0x1D6C70CD,
    0xD003FC97: 0xB02B5132,
    0xD0890CA1: 0xE67026F1,
    0xD0B8AFAA: 0xD59C7BB5,
    0xD20F20A1: 0x44E2D513,
    0xD2286FA1: 0x99D73407,
    0xD26BB748: 0xD95F31C8,
    0xD2F7C699: 0x5AAADC9,
    0xD3F5E58: 0x2F071229,
    0xD40C4CEA: 0xD1F69DEA,
    0xD43A1415: 0x8E4E8777,
    0xD53F3594: 0xA003D4F0,
    0xD7A8EBBB: 0x7E699E0F,
    0xD7CE8534: 0x693622ED,
    0xD7D56BB3: 0xD59C7BB5,
    0xD7E93C26: 0x8E9C042B,
    0xD8FC0030: 0xC2150E26,
    0xD9C56CD1: 0xFE9536CD,
    0xDB38C36A: 0xB35422C8,
    0xDB6A33BD: 0xBF632156,
    0xDD851A43: 0x11B73834,
    0xDEA3EC29: 0x9D052F7E,
    0xDF8203FC: 0x5610DDE3,
    0xDFD80F81: 0xD327A3DB,
    0xE2647F3C: 0xAF103C46,
    0xE30E313F: 0xD59C7BB5,
    0xE463F526: 0xD59C7BB5,
    0xE76BD9A9: 0xC4490949,
    0xE7C720FC: 0xC19A1FAF,
    0xE7EA4D68: 0xE9E109C8,
    0xE8136BD8: 0xD476C00D,
    0xE92B81EF: 0x88B06ED6,
    0xE9BB3409: 0xEFDC690A,
    0xEAFA0E7E: 0xBEAC0611,
    0xEB6BC7FB: 0x34858354,
    0xEBEAC370: 0x45A83BAC,
    0xEC9F8919: 0xA754EE6B,
    0xED71910C: 0xB8FAF548,
    0xED960382: 0x4AC9CE02,
    0xEFF2CECE: 0xE3107C90,
    0xF1057E55: 0x2EFE9850,
    0xF10E4869: 0x755C77D0,
    0xF434C8D1: 0x3F000000,
    0xF46AEDCB: 0xAB074136,
    0xF4F46095: 0x65EEC9F4,
    0xF8586222: 0x8697E2F8,
    0xF8A4A3E6: 0x37BAEDDD,
    0xF8F78B1A: 0x99C934BC,
    0xFAC3975E: 0xDA2A98EE,
    0xFC3D20: 0x70C10F1D,
    0xFC8B40E5: 0x567841F4,
    0xFD936E2F: 0x33A9F6A7,
    0xFE867B83: 0xD84FBC49,
}


def lookup_shader_id_texture_id(texture_id: int, game_type: utils.GameType) -> int:
    """Get the texture id used by a shader."""
    match game_type:
        case utils.GameType.THESIMS:
            return THE_SIMS_SHADER_ID_TEXTURE_ID_LOOKUP.get(texture_id, texture_id)
        case utils.GameType.THESIMSBUSTINOUT:
            return THE_SIMS_BUSTIN_OUT_SHADER_ID_TEXTURE_ID_LOOKUP.get(texture_id, texture_id)
        case utils.GameType.THEURBZ:
            return THE_URBZ_SHADER_ID_TEXTURE_ID_LOOKUP.get(texture_id, texture_id)
        case utils.GameType.THESIMS2:
            return THE_SIMS_2_SHADER_ID_TEXTURE_ID_LOOKUP.get(texture_id, texture_id)

    return texture_id
