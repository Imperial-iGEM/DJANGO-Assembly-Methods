from opentrons import protocol_api
# from opentrons import legacy_api
# import numpy as np

metadata = {'apiLevel': '2.2',
            'protocolName': 'Assembly Template v2',
            'author': 'Gabrielle Johnston',
            'description': 'DNABot updated assembly template'}
    

def run(protocol: protocol_api.ProtocolContext):
    def final_assembly(final_assembly_dict, tiprack_num,
                       tiprack_type='opentrons_96_tiprack_10ul',
                       p10_mount='right',
                       mag_plate_type='biorad_96_wellplate_200ul_pcr',
                       tube_rack_type='opentrons_24_tuberack_nest_1.5ml_snapcap',
                       aluminum_block_type='opentrons_96_aluminumblock_biorad_wellplate_200ul'):
        """Implements final assembly reactions using an opentrons OT-2.

        Args:
        final_assembly_dict (dict): Dictionary with keys and values corresponding to destination and associated linker-ligated part wells, respectively.
        tiprack_num (int): Number of tipracks required during run.

        """
        # Constants
        CANDIDATE_TIPRACK_SLOTS = ['3', '6', '9', '2', '5', '8', '11']
        # PIPETTE_MOUNT = 'right'
        PIPETTE_MOUNT = p10_mount
        # MAG_PLATE_TYPE = 'biorad_96_wellplate_200ul_pcr'
        MAG_PLATE_TYPE = mag_plate_type
        MAG_PLATE_POSITION = '1'
        # TUBE_RACK_TYPE = 'opentrons_24_tuberack_nest_1.5ml_snapcap'
        TUBE_RACK_TYPE = tube_rack_type
        TUBE_RACK_POSITION = '7'
        # DESTINATION_PLATE_TYPE = 'opentrons_96_aluminumblock_biorad_wellplate_200ul'
        DESTINATION_PLATE_TYPE = aluminum_block_type
        TEMPDECK_SLOT = '4'
        TEMP = 20
        TOTAL_VOL = 15
        PART_VOL = 1.5
        MIX_SETTINGS = (1, 3)

        # Errors
        sample_number = len(final_assembly_dict.keys())
        if sample_number > 96:
            raise ValueError('Final assembly nummber cannot exceed 96.')

        slots = CANDIDATE_TIPRACK_SLOTS[:tiprack_num]
        tipracks = [protocol.load_labware(tiprack_type, slot)
                for slot in slots]
        pipette = protocol.load_instrument('p10_single', PIPETTE_MOUNT, tip_racks=tipracks)

        # Define Labware and set temperature
        #mag_mod = protocol.load_module('magnetic module', MAG_PLATE_POSITION)
        temp_mod = protocol.load_module('temperature module', TEMPDECK_SLOT)
        tube_rack = protocol.load_labware(TUBE_RACK_TYPE, TUBE_RACK_POSITION)
        #magbead_plate = mag_mod.load_labware(MAG_PLATE_TYPE)
        magbead_plate = protocol.load_labware(MAG_PLATE_TYPE, MAG_PLATE_POSITION)
        #destination_plate = protocol.load_labware(DESTINATION_PLATE_TYPE, TEMPDECK_SLOT, share=True)
        destination_plate = temp_mod.load_labware(DESTINATION_PLATE_TYPE)
        temp_mod.set_temperature(TEMP)

        # Master mix transfers
        final_assembly_lens = []
        for values in final_assembly_dict.values():
            final_assembly_lens.append(len(values))
        unique_assemblies_lens = list(set(final_assembly_lens))
        master_mix_well_letters = ['A', 'B', 'C', 'D']
        for x in unique_assemblies_lens:
            master_mix_well = master_mix_well_letters[(x - 1) // 6] + str(x - 1)
            destination_plate_wells = [destination_plate.wells_by_name()[key] 
                for key, value in list(final_assembly_dict.items())]
            pipette.pick_up_tip()
            pipette.transfer(TOTAL_VOL - x * PART_VOL, tube_rack.wells_by_name()[master_mix_well],
                            destination_plate_wells,
                            new_tip='never')
            pipette.drop_tip()

        # Part transfers
        for key, values in final_assembly_dict.items():
            mag_bead_wells = [magbead_plate.wells_by_name()[value] for value in values]
            pipette.transfer(PART_VOL, mag_bead_wells,
                             destination_plate.wells_by_name()[key], mix_after=MIX_SETTINGS,
                             new_tip='always')

        temp_mod.deactivate()


    final_assembly(final_assembly_dict=final_assembly_dict,
                   tiprack_num=tiprack_num, p10_mount=p10_mount,
                   mag_plate_type=mag_plate_type, tube_rack_type=tube_rack_type,
                   aluminum_block_type=aluminum_block_type)