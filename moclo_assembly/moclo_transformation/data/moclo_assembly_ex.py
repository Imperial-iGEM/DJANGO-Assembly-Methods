dna_plate_map_dict = {"input-dna-map": [["I13453_AB-1", "I13453_AB-2", "I13453_AB-4", "B0034m_BC-1", "C0012m_CD-1", "C0012m_CD-2", "C0012m_CD-4", "E0040m_C1N-1", "E0040m_C1N-2", "E0040m_C1N-4"], ["J23100_AB-1", "J23100_AB-2", "J23100_AB-4", "B0034m_BC-2", "C0040_CD-1", "C0040_CD-2", "C0040_CD-4", "3xFLAG_CC1-1", "3xFLAG_CC1-2", "3xFLAG_CC1-4"], ["J23102_AB-1", "J23102_AB-2", "J23102_AB-4", "B0034m_BC-4", "C0062_CD-1", "C0062_CD-2", "C0062_CD-4", "12 aa GS Linker_NO-1", "12 aa GS Linker_NO-2", "12 aa GS Linker_NO-4"], ["J23103_AB-1", "J23103_AB-2", "J23103_AB-4", "B0015_DE-1", "C0080_CD-1", "C0080_CD-2", "C0080_CD-4", "6xHIS_OD-1", "6xHIS_OD-2", "6xHIS_OD-4"], ["J23106_AB-1", "J23106_AB-2", "J23106_AB-4", "B0015_DE-2", "E0030_CD-1", "E0030_CD-2", "E0030_CD-4", "DVK_AE-1", "DVK_AE-2", "DVK_AE-4"], ["J23107_AB-1", "J23107_AB-2", "J23107_AB-4", "B0015_DE-4", "E0040m_CD-1", "E0040m_CD-2", "E0040m_CD-4", "DVK_CD-1", "DVK_CD-2", "DVK_CD-4"], ["J23116_AB-1", "J23116_AB-2", "J23116_AB-4", "", "E1010m_CD-1", "E1010m_CD-2", "E1010m_CD-4", "", "", ""], ["R0040_AB-1", "R0040_AB-2", "R0040_AB-4", "", "deGFP_CD-1", "deGFP_CD-2", "deGFP_CD-4", "", "", ""]]}

combinations_to_make = [{"name": "2-E0040m-1", "parts": ["E0040m_CD-1", "DVK_CD-1"]}, {"name": "2-C0012m-1", "parts": ["C0012m_CD-1", "DVK_CD-1"]}, {"name": "2-C0040-1", "parts": ["C0040_CD-1", "DVK_CD-1"]}, {"name": "2-C0062-1", "parts": ["C0062_CD-1", "DVK_CD-1"]}, {"name": "2-C0080-1", "parts": ["C0080_CD-1", "DVK_CD-1"]}, {"name": "2-E0030-1", "parts": ["E0030_CD-1", "DVK_CD-1"]}, {"name": "2-E1010m-1", "parts": ["E1010m_CD-1", "DVK_CD-1"]}, {"name": "2-deGFP-1", "parts": ["deGFP_CD-1", "DVK_CD-1"]}, {"name": "2-E0040m-2", "parts": ["E0040m_CD-2", "DVK_CD-2"]}, {"name": "2-C0012m-2", "parts": ["C0012m_CD-2", "DVK_CD-2"]}, {"name": "2-C0040-2", "parts": ["C0040_CD-2", "DVK_CD-2"]}, {"name": "2-C0062-2", "parts": ["C0062_CD-2", "DVK_CD-2"]}, {"name": "2-C0080-2", "parts": ["C0080_CD-2", "DVK_CD-2"]}, {"name": "2-E0030-2", "parts": ["E0030_CD-2", "DVK_CD-2"]}, {"name": "2-E1010m-2", "parts": ["E1010m_CD-2", "DVK_CD-2"]}, {"name": "2-deGFP-2", "parts": ["deGFP_CD-2", "DVK_CD-2"]}, {"name": "2-E0040m-4", "parts": ["E0040m_CD-4", "DVK_CD-4"]}, {"name": "2-C0012m-4", "parts": ["C0012m_CD-4", "DVK_CD-4"]}, {"name": "2-C0040-4", "parts": ["C0040_CD-4", "DVK_CD-4"]}, {"name": "2-C0062-4", "parts": ["C0062_CD-4", "DVK_CD-4"]}, {"name": "2-C0080-4", "parts": ["C0080_CD-4", "DVK_CD-4"]}, {"name": "2-E0030-4", "parts": ["E0030_CD-4", "DVK_CD-4"]}, {"name": "2-E1010m-4", "parts": ["E1010m_CD-4", "DVK_CD-4"]}, {"name": "2-deGFP-4", "parts": ["deGFP_CD-4", "DVK_CD-4"]}, {"name": "5-J23106-1", "parts": ["J23106_AB-1", "B0034m_BC-1", "E0040m_CD-1", "B0015_DE-1", "DVK_AE-1"]}, {"name": "5-I13453-1", "parts": ["I13453_AB-1", "B0034m_BC-1", "E0040m_CD-1", "B0015_DE-1", "DVK_AE-1"]}, {"name": "5-J23100-1", "parts": ["J23100_AB-1", "B0034m_BC-1", "E0040m_CD-1", "B0015_DE-1", "DVK_AE-1"]}, {"name": "5-J23102-1", "parts": ["J23102_AB-1", "B0034m_BC-1", "E0040m_CD-1", "B0015_DE-1", "DVK_AE-1"]}, {"name": "5-J23103-1", "parts": ["J23103_AB-1", "B0034m_BC-1", "E0040m_CD-1", "B0015_DE-1", "DVK_AE-1"]}, {"name": "5-J23107-1", "parts": ["J23107_AB-1", "B0034m_BC-1", "E0040m_CD-1", "B0015_DE-1", "DVK_AE-1"]}, {"name": "5-J23116-1", "parts": ["J23116_AB-1", "B0034m_BC-1", "E0040m_CD-1", "B0015_DE-1", "DVK_AE-1"]}, {"name": "5-R0040-1", "parts": ["R0040_AB-1", "B0034m_BC-1", "E0040m_CD-1", "B0015_DE-1", "DVK_AE-1"]}, {"name": "5-J23106-2", "parts": ["J23106_AB-2", "B0034m_BC-2", "E0040m_CD-2", "B0015_DE-2", "DVK_AE-2"]}, {"name": "5-I13453-2", "parts": ["I13453_AB-2", "B0034m_BC-2", "E0040m_CD-2", "B0015_DE-2", "DVK_AE-2"]}, {"name": "5-J23100-2", "parts": ["J23100_AB-2", "B0034m_BC-2", "E0040m_CD-2", "B0015_DE-2", "DVK_AE-2"]}, {"name": "5-J23102-2", "parts": ["J23102_AB-2", "B0034m_BC-2", "E0040m_CD-2", "B0015_DE-2", "DVK_AE-2"]}, {"name": "5-J23103-2", "parts": ["J23103_AB-2", "B0034m_BC-2", "E0040m_CD-2", "B0015_DE-2", "DVK_AE-2"]}, {"name": "5-J23107-2", "parts": ["J23107_AB-2", "B0034m_BC-2", "E0040m_CD-2", "B0015_DE-2", "DVK_AE-2"]}, {"name": "5-J23116-2", "parts": ["J23116_AB-2", "B0034m_BC-2", "E0040m_CD-2", "B0015_DE-2", "DVK_AE-2"]}, {"name": "5-R0040-2", "parts": ["R0040_AB-2", "B0034m_BC-2", "E0040m_CD-2", "B0015_DE-2", "DVK_AE-2"]}, {"name": "5-J23106-4", "parts": ["J23106_AB-4", "B0034m_BC-4", "E0040m_CD-4", "B0015_DE-4", "DVK_AE-4"]}, {"name": "5-I13453-4", "parts": ["I13453_AB-4", "B0034m_BC-4", "E0040m_CD-4", "B0015_DE-4", "DVK_AE-4"]}, {"name": "5-J23100-4", "parts": ["J23100_AB-4", "B0034m_BC-4", "E0040m_CD-4", "B0015_DE-4", "DVK_AE-4"]}, {"name": "5-J23102-4", "parts": ["J23102_AB-4", "B0034m_BC-4", "E0040m_CD-4", "B0015_DE-4", "DVK_AE-4"]}, {"name": "5-J23103-4", "parts": ["J23103_AB-4", "B0034m_BC-4", "E0040m_CD-4", "B0015_DE-4", "DVK_AE-4"]}, {"name": "5-J23107-4", "parts": ["J23107_AB-4", "B0034m_BC-4", "E0040m_CD-4", "B0015_DE-4", "DVK_AE-4"]}, {"name": "5-J23116-4", "parts": ["J23116_AB-4", "B0034m_BC-4", "E0040m_CD-4", "B0015_DE-4", "DVK_AE-4"]}, {"name": "5-R0040-4", "parts": ["R0040_AB-4", "B0034m_BC-4", "E0040m_CD-4", "B0015_DE-4", "DVK_AE-4"]}, {"name": "8--J23106-1", "parts": ["J23106_AB-1", "B0034m_BC-1", "3xFLAG_CC1-1", "E0040m_C1N-1", "12 aa GS Linker_NO-1", "6xHIS_OD-1", "B0015_DE-1", "DVK_AE-1"]}, {"name": "8-I13453-1", "parts": ["I13453_AB-1", "B0034m_BC-1", "3xFLAG_CC1-1", "E0040m_C1N-1", "12 aa GS Linker_NO-1", "6xHIS_OD-1", "B0015_DE-1", "DVK_AE-1"]}, {"name": "8-J23100-1", "parts": ["J23100_AB-1", "B0034m_BC-1", "3xFLAG_CC1-1", "E0040m_C1N-1", "12 aa GS Linker_NO-1", "6xHIS_OD-1", "B0015_DE-1", "DVK_AE-1"]}, {"name": "8-J23102-1", "parts": ["J23102_AB-1", "B0034m_BC-1", "3xFLAG_CC1-1", "E0040m_C1N-1", "12 aa GS Linker_NO-1", "6xHIS_OD-1", "B0015_DE-1", "DVK_AE-1"]}, {"name": "8-J23103-1", "parts": ["J23103_AB-1", "B0034m_BC-1", "3xFLAG_CC1-1", "E0040m_C1N-1", "12 aa GS Linker_NO-1", "6xHIS_OD-1", "B0015_DE-1", "DVK_AE-1"]}, {"name": "8-J23107-1", "parts": ["J23107_AB-1", "B0034m_BC-1", "3xFLAG_CC1-1", "E0040m_C1N-1", "12 aa GS Linker_NO-1", "6xHIS_OD-1", "B0015_DE-1", "DVK_AE-1"]}, {"name": "8-J23116-1", "parts": ["J23116_AB-1", "B0034m_BC-1", "3xFLAG_CC1-1", "E0040m_C1N-1", "12 aa GS Linker_NO-1", "6xHIS_OD-1", "B0015_DE-1", "DVK_AE-1"]}, {"name": "8-R0040-1", "parts": ["R0040_AB-1", "B0034m_BC-1", "3xFLAG_CC1-1", "E0040m_C1N-1", "12 aa GS Linker_NO-1", "6xHIS_OD-1", "B0015_DE-1", "DVK_AE-1"]}, {"name": "8--J23106-2", "parts": ["J23106_AB-2", "B0034m_BC-2", "3xFLAG_CC1-2", "E0040m_C1N-2", "12 aa GS Linker_NO-2", "6xHIS_OD-2", "B0015_DE-2", "DVK_AE-2"]}, {"name": "8-I13453-2", "parts": ["I13453_AB-2", "B0034m_BC-2", "3xFLAG_CC1-2", "E0040m_C1N-2", "12 aa GS Linker_NO-2", "6xHIS_OD-2", "B0015_DE-2", "DVK_AE-2"]}, {"name": "8-J23100-2", "parts": ["J23100_AB-2", "B0034m_BC-2", "3xFLAG_CC1-2", "E0040m_C1N-2", "12 aa GS Linker_NO-2", "6xHIS_OD-2", "B0015_DE-2", "DVK_AE-2"]}, {"name": "8-J23102-2", "parts": ["J23102_AB-2", "B0034m_BC-2", "3xFLAG_CC1-2", "E0040m_C1N-2", "12 aa GS Linker_NO-2", "6xHIS_OD-2", "B0015_DE-2", "DVK_AE-2"]}, {"name": "8-J23103-2", "parts": ["J23103_AB-2", "B0034m_BC-2", "3xFLAG_CC1-2", "E0040m_C1N-2", "12 aa GS Linker_NO-2", "6xHIS_OD-2", "B0015_DE-2", "DVK_AE-2"]}, {"name": "8-J23107-2", "parts": ["J23107_AB-2", "B0034m_BC-2", "3xFLAG_CC1-2", "E0040m_C1N-2", "12 aa GS Linker_NO-2", "6xHIS_OD-2", "B0015_DE-2", "DVK_AE-2"]}, {"name": "8-J23116-2", "parts": ["J23116_AB-2", "B0034m_BC-2", "3xFLAG_CC1-2", "E0040m_C1N-2", "12 aa GS Linker_NO-2", "6xHIS_OD-2", "B0015_DE-2", "DVK_AE-2"]}, {"name": "8-R0040-2", "parts": ["R0040_AB-2", "B0034m_BC-2", "3xFLAG_CC1-2", "E0040m_C1N-2", "12 aa GS Linker_NO-2", "6xHIS_OD-2", "B0015_DE-2", "DVK_AE-2"]}, {"name": "8--J23106-4", "parts": ["J23106_AB-4", "B0034m_BC-4", "3xFLAG_CC1-4", "E0040m_C1N-4", "12 aa GS Linker_NO-4", "6xHIS_OD-4", "B0015_DE-4", "DVK_AE-4"]}, {"name": "8-I13453-4", "parts": ["I13453_AB-4", "B0034m_BC-4", "3xFLAG_CC1-4", "E0040m_C1N-4", "12 aa GS Linker_NO-4", "6xHIS_OD-4", "B0015_DE-4", "DVK_AE-4"]}, {"name": "8-J23100-4", "parts": ["J23100_AB-4", "B0034m_BC-4", "3xFLAG_CC1-4", "E0040m_C1N-4", "12 aa GS Linker_NO-4", "6xHIS_OD-4", "B0015_DE-4", "DVK_AE-4"]}, {"name": "8-J23102-4", "parts": ["J23102_AB-4", "B0034m_BC-4", "3xFLAG_CC1-4", "E0040m_C1N-4", "12 aa GS Linker_NO-4", "6xHIS_OD-4", "B0015_DE-4", "DVK_AE-4"]}, {"name": "8-J23103-4", "parts": ["J23103_AB-4", "B0034m_BC-4", "3xFLAG_CC1-4", "E0040m_C1N-4", "12 aa GS Linker_NO-4", "6xHIS_OD-4", "B0015_DE-4", "DVK_AE-4"]}, {"name": "8-J23107-4", "parts": ["J23107_AB-4", "B0034m_BC-4", "3xFLAG_CC1-4", "E0040m_C1N-4", "12 aa GS Linker_NO-4", "6xHIS_OD-4", "B0015_DE-4", "DVK_AE-4"]}, {"name": "8-J23116-4", "parts": ["J23116_AB-4", "B0034m_BC-4", "3xFLAG_CC1-4", "E0040m_C1N-4", "12 aa GS Linker_NO-4", "6xHIS_OD-4", "B0015_DE-4", "DVK_AE-4"]}, {"name": "8-R0040-4", "parts": ["R0040_AB-4", "B0034m_BC-4", "3xFLAG_CC1-4", "E0040m_C1N-4", "12 aa GS Linker_NO-4", "6xHIS_OD-4", "B0015_DE-4", "DVK_AE-4"]}]

reagent_to_mm = {"H12": [["reagents_plate", "H12", "5.0"], ["reagents_plate", "G12", "5.0"], ["reagents_plate", "F12", "5.0"], ["reagents_plate", "E12", "9.0"], ["reagents_plate", "D12", "5.0"], ["reagents_plate", "C12", "13.0"]], "G12": [["reagents_plate", "H12", "10"], ["reagents_plate", "G12", "10"], ["reagents_plate", "F12", "10"], ["reagents_plate", "E12", "18"], ["reagents_plate", "D12", "10"], ["reagents_plate", "C12", "26"]], "F12": [["reagents_plate", "H12", "20"], ["reagents_plate", "G12", "20"], ["reagents_plate", "F12", "20"], ["reagents_plate", "E12", "36"], ["reagents_plate", "D12", "20"]], "E12": [["reagents_plate", "C12", "52"]], "A1": [["trough", "H12", "125.0"], ["trough", "G12", "125.0"], ["trough", "F12", "125.0"], ["trough", "E12", "117.0"], ["trough", "D12", "65.0"], ["trough", "C12", "13.0"]]}

master_mix_dicts = [{"well": "H12", "no_parts": 2, "vol_per_assembly": 16, "combinations": ["2-E0040m-1", "2-C0012m-1", "2-C0040-1", "2-C0062-1", "2-C0080-1", "2-E0030-1", "2-E1010m-1", "2-deGFP-1"], "no_assemblies": 8, "buffer_vol": 20, "ligase_vol": 5.0, "enzyme_vol": 10, "water_vol": 125.0, "plate": "reaction_plate"}, {"well": "G12", "no_parts": 2, "vol_per_assembly": 16, "combinations": ["2-E0040m-2", "2-C0012m-2", "2-C0040-2", "2-C0062-2", "2-C0080-2", "2-E0030-2", "2-E1010m-2", "2-deGFP-2"], "no_assemblies": 8, "buffer_vol": 20, "ligase_vol": 5.0, "enzyme_vol": 10, "water_vol": 125.0, "plate": "reaction_plate"}, {"well": "F12", "no_parts": 2, "vol_per_assembly": 16, "combinations": ["2-E0040m-4", "2-C0012m-4", "2-C0040-4", "2-C0062-4", "2-C0080-4", "2-E0030-4", "2-E1010m-4", "2-deGFP-4"], "no_assemblies": 8, "buffer_vol": 20, "ligase_vol": 5.0, "enzyme_vol": 10, "water_vol": 125.0, "plate": "reaction_plate"}, {"well": "E12", "no_parts": 5, "vol_per_assembly": 10, "combinations": ["5-J23106-1", "5-I13453-1", "5-J23100-1", "5-J23102-1", "5-J23103-1", "5-J23107-1", "5-J23116-1", "5-R0040-1", "5-J23106-2", "5-I13453-2", "5-J23100-2", "5-J23102-2", "5-J23103-2", "5-J23107-2", "5-J23116-2", "5-R0040-2"], "no_assemblies": 16, "buffer_vol": 36, "ligase_vol": 9.0, "enzyme_vol": 18, "water_vol": 117.0, "plate": "reaction_plate"}, {"well": "D12", "no_parts": 5, "vol_per_assembly": 10, "combinations": ["5-J23106-4", "5-I13453-4", "5-J23100-4", "5-J23102-4", "5-J23103-4", "5-J23107-4", "5-J23116-4", "5-R0040-4"], "no_assemblies": 8, "buffer_vol": 20, "ligase_vol": 5.0, "enzyme_vol": 10, "water_vol": 65.0, "plate": "reaction_plate"}, {"well": "C12", "no_parts": 8, "vol_per_assembly": 4, "combinations": ["8--J23106-1", "8-I13453-1", "8-J23100-1", "8-J23102-1", "8-J23103-1", "8-J23107-1", "8-J23116-1", "8-R0040-1", "8--J23106-2", "8-I13453-2", "8-J23100-2", "8-J23102-2", "8-J23103-2", "8-J23107-2", "8-J23116-2", "8-R0040-2", "8--J23106-4", "8-I13453-4", "8-J23100-4", "8-J23102-4", "8-J23103-4", "8-J23107-4", "8-J23116-4", "8-R0040-4"], "no_assemblies": 24, "buffer_vol": 52, "ligase_vol": 13.0, "enzyme_vol": 26, "water_vol": 13.0, "plate": "reaction_plate"}]

thermocycle = True

pipetteMount10 = "right"

reaction_plate_type = "biorad_96_wellplate_200ul_pcr"

reagent_plate_type = "biorad_96_wellplate_200ul_pcr"

trough_type = "usascientific_12_reservoir_22ml"

from opentrons import protocol_api

metadata = {'apiLevel': '2.2',
            'protocolName': 'Generalised MoClo Protocol for OT-2 v2',
            'author': 'Gabrielle Johnston',
            'description': 'Generalised DAMP Lab MoClo protocol for OT-2 v2'}


def run(protocol: protocol_api.ProtocolContext):

    def create_master_mix(reagent_to_mm_dict, master_mix_dicts, pipette,
                          reaction_plate, reagents_plate, trough):

        for key, value in reagent_to_mm_dict.items():
            pipette.pick_up_tip()
            for index, mm_dest in enumerate(value):
                if index == 0:
                    # only need to find source once
                    if mm_dest[0] == 'reagents_plate':
                        source = reagents_plate.wells_by_name()[key]
                    else:
                        if key == 'A1':
                            source = trough.wells()[0]
                        else:
                            source = trough.wells_by_name()[key]
                dest = reaction_plate.wells_by_name()[mm_dest[1]]
                vol = float(mm_dest[2])
                pipette.transfer(vol, source, dest, new_tip='never')
            pipette.blow_out()
            pipette.drop_tip()

        for mm_dict in master_mix_dicts:
            mm_well = reaction_plate.wells_by_name()[mm_dict['well']]
            pipette.pick_up_tip()
            pipette.mix(2, 10, mm_well)
            pipette.blow_out()
            pipette.drop_tip()

    def get_combination_well_no_parts(combinations_to_make):
        combination_well_dict = {}
        for i, combination in enumerate(combinations_to_make):
            key = str(len(combination['parts']))
            if key not in combination_well_dict.keys():
                combination_well_dict[key] = [i]
            else:
                combination_well_dict[key].append(i)
        return combination_well_dict

    def find_dna(name, dna_plate_map_dict, dna_plate_dict):
        """Return a well containing the named DNA."""
        for plate_name, plate_map in dna_plate_map_dict.items():
            for i, row in enumerate(plate_map):
                for j, dna_name in enumerate(row):
                    if dna_name == name:
                        well_num = 8 * j + i
                        return(dna_plate_dict[plate_name].wells()[well_num])
        raise ValueError("Could not find dna piece named \"{0}\"".format(name))

    # This function checks if the DNA parts exist in the DNA plates and
    # returns for well locaion of output DNA combinations

    def find_combination(name, combinations_to_make, reaction_plate):
        """Return a well containing the named combination."""
        for i, combination in enumerate(combinations_to_make):
            if combination["name"] == name:
                return reaction_plate.wells()[i]
        raise ValueError("Could not find combination \"{0}\".".format(name))

    def moclo_protocol(dna_plate_map_dict, combinations_to_make,
                       thermocycle=False,
                       reaction_plate_type='biorad_96_wellplate_200ul_pcr',
                       reagent_plate_type='biorad_96_wellplate_200ul_pcr',
                       trough_type='usascientific_12_reservoir_22ml'):

        # Load in Bio-Rad 96 Well Plate on temp deck for moclos,
        # transformation, and outgrowth.
        if thermocycle:
            tc_mod = protocol.load_module('thermocycler')
            tc_mod.open_lid()
            reaction_plate = tc_mod.load_labware(reaction_plate_type)
            tc_mod.set_block_temperature(10)
        else:
            temp_deck = protocol.load_module('tempdeck', 10)
            reaction_plate = temp_deck.load_labware(reaction_plate_type)
            temp_deck.set_temperature(10)

        # Load in 2 10ul tipracks and 2 300ul tipracks
        tr_10 = [protocol.load_labware('opentrons_96_tiprack_10ul', '3'),
                 protocol.load_labware('opentrons_96_tiprack_10ul', '6')]

        # Load in pipettes
        p10_single = protocol.load_instrument('p10_single',
                                              mount=pipetteMount10,
                                              tip_racks=tr_10)

        ''' Need to provide the instructions for loading reagent'''
        reagents_plate = protocol.load_labware(reagent_plate_type,
                                               '4', 'Reagents Plate')
        '''
            This deck slot location is dedicated for the reaction plate after
            MoClo protocol is completed, so at the beginning of the protocol
            there isn't an actual plate existing in this slot location.
        '''
        #post_moclo_reaction_plate = protocol.load_labware(
            #'biorad_96_wellplate_200ul_pcr', '9', 'Post-MoClo Reaction Plate')

        # Load in water, SOC, and wash trough (USA Scientific 12 Well Reservoir
        # 22ml)
        trough = protocol.load_labware(trough_type, '5',
                                       'Reagents trough')
        wash_0 = trough.wells()[1]  # Well 2
        wash_1 = trough.wells()[2]  # Well 3
        # soc = trough.wells()[3]  # Well 4
        # liquid_waste = trough.wells()[4]  # Well 5

        # Load in up to 2 DNA plates (Bio-Rad 96 Well Plate 200ul PCR)
        # plate_name = dna_plate_map_dict.keys() # because there should be only
        # 1 input plate
        # input_dna_plate = labware.load('biorad_96_wellplate_200ul_pcr', '1',
        # 'Input DNA Plate')
        dna_plate_dict = {}
        for plate_name in dna_plate_map_dict.keys():
            dna_plate_dict[plate_name] = protocol.load_labware(
                reaction_plate_type, '1', 'Input DNA Plate')

        no_assemblies_dict = {}
        for combinations in combinations_to_make:
            no_parts = len(combinations['parts'])
            if str(no_parts) in no_assemblies_dict.keys():
                no_assemblies_dict[str(no_parts)] += 1
            else:
                no_assemblies_dict[str(no_parts)] = 1

        wells_assembly = get_combination_well_no_parts(combinations_to_make)
        protocol.comment("--------------------------------------------")
        protocol.comment("Creating master mix")
        protocol.comment("--------------------------------------------")
        create_master_mix(reagent_to_mm, master_mix_dicts, p10_single,
                          reaction_plate, reagents_plate, trough)

        for no_parts, no_assemblies in no_assemblies_dict.items():
            n_part_mm_dicts = [mm_dict for mm_dict in master_mix_dicts
                               if mm_dict['no_parts'] == no_parts]
            wells_open_assembly = wells_assembly[no_parts]
            protocol.comment("--------------------------------------------")
            protocol.comment(
                "Transferring mm for {0}-part assembly.".format(no_parts))
            protocol.comment("--------------------------------------------")
            for i, entries in enumerate(n_part_mm_dicts):
                mm_vol_per_assembly = entries['vol_per_assembly']
                p10_single.pick_up_tip()
                mm_well = reagents_plate.wells()[entries['well']]
                no_assemblies_mm = entries['no_assemblies']
                if i == len(entries) - 1:
                    dest_wells = wells_open_assembly
                else:
                    dest_wells = wells_open_assembly[0:no_assemblies_mm-1]
                wells_new = [well for well in wells_open_assembly
                             if (well not in dest_wells)]
                wells_open_assembly = wells_new
                dest_wells_plate = [reaction_plate.wells()[well].bottom(0.3)
                                    for well in dest_wells]

                p10_single.transfer(mm_vol_per_assembly, mm_well,
                                    dest_wells_plate, blow_out=True,
                                    new_tip='never')
                p10_single.drop_tip()

        # gives dictionary with keys = parts,
        # values = names of combinations that parts are in
        combinations_by_part = {}
        for i in combinations_to_make:
            name = i["name"]
            for j in i["parts"]:
                if j in combinations_by_part.keys():
                    combinations_by_part[j].append(name)
                else:
                    combinations_by_part[j] = [name]

        # This section of the code combines and mix the DNA parts according to
        # the combination list
        protocol.comment("--------------------------------------------")
        protocol.comment("Transferring parts to reaction plates.")
        protocol.comment("--------------------------------------------")
        for part, combinations in combinations_by_part.items():
            # find dna -> returns source well where part is
            part_well = find_dna(part, dna_plate_map_dict, dna_plate_dict)
            combination_wells = [find_combination(x, combinations_to_make,
                                                  reaction_plate)
                                 for x in combinations]
            p10_single.pick_up_tip()
            while combination_wells:
                if len(combination_wells) > 5:
                    current_wells = combination_wells[0:5]
                    combination_wells = combination_wells[5:]
                else:
                    current_wells = combination_wells
                    combination_wells = []
                p10_single.aspirate(2 * len(current_wells),
                                    part_well.bottom(0.5))
                for i in current_wells:
                    p10_single.dispense(2, i.bottom(0.5))
                if combination_wells:
                    p10_single.mix(2, 10, wash_0.bottom(0.5))
                    p10_single.blow_out()
                    p10_single.mix(2, 10, wash_1.bottom(0.5))
                    p10_single.blow_out()
            # Two washing steps are added to allow recycling of the tips
            p10_single.drop_tip()

        if thermocycle:
            protocol.comment("--------------------------------------------")
            protocol.comment("Running thermocycler")
            protocol.comment("--------------------------------------------")
            tc_mod.close_lid()
            profile1 = [
                {'temperature': 37, 'hold_time_seconds': 90},
                {'temperature': 16, 'hold_time_seconds': 180}]
            profile2 = [
                {'temperature': 50, 'hold_time_seconds': 300},
                {'temperature': 80, 'hold_time_seconds': 600}]

            tc_mod.execute_profile(steps=profile1, repetitions=35)
            tc_mod.execute_profile(steps=profile2, repetitions=1)
            tc_mod.open_lid()
            tc_mod.deactivate()
            protocol.comment(
                'Remove the reaction plate and thermocycler module.')
            protocol.comment(
                'Insert the temperature module in position 10.')
        else:
            temp_deck.deactivate()
            protocol.comment(
                'Seal the reaction plate with adhesive film and remove.')
            protocol.comment(
                'Thermocycle the reaction plate on a benchtop thermocycler.')
            protocol.comment('Use the following thermocycler settings:')
            protocol.comment(
                '35 cycles of 37°C for 1.5 minutes and 16°C for 3 minutes')
            protocol.comment(
                '1 cycle of 50°C for 5 minutes and 80°C for 10 minutes')

        protocol.comment('Remove the Input_DNA_Plate from the Deck Space.')
        protocol.comment(
            'Remaining DNA may be saved by sealing the Input_DNA_Plate with adhesive film and storing at -20°C')
        protocol.comment(
            'Insert the reaction plate into deck positon 7')

    moclo_protocol(dna_plate_map_dict, combinations_to_make, thermocycle,
                   reaction_plate_type, reagent_plate_type, trough_type)
