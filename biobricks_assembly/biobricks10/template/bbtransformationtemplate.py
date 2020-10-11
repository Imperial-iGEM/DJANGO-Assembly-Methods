from opentrons import protocol_api

metadata = {'apiLevel': '2.2',
            'protocolName': 'BioBricks transformation template',
            'author': 'iGEM',
            'description': 'Opentrons BioBricks transformation template'}


# Labware constants
PIPETTE_TYPE = p10_type
# PIPETTE_MOUNT = 'right'
PIPETTE_MOUNT = p10_mount
PIPETTE_TYPE2 = p300_type
PIPETTE_MOUNT2 = p300_mount
# PIPETTE_MOUNT2 = 'left'
# DESTINATION_PLATE_TYPE = 'corning_96_wellplate_360ul_flat'
DESTINATION_PLATE_TYPE = transformation_plate_type
# SOURCE_PLATE_TYPE = 'biorad_96_wellplate_200ul_pcr'
SOURCE_PLATE_TYPE = well_plate_type
TIPRACK_TYPE = 'opentrons_96_tiprack_10ul'
P300_TIPRACK_TYPE = 'opentrons_96_tiprack_300ul'
# TUBE_RACK_TYPE = 'opentrons_24_tuberack_nest_1.5ml_snapcap'
TUBE_RACK_TYPE = tube_rack_type
INCUBATION_TEMP = 4
# SOC_PLATE_TYPE = 'usascientific_96_wellplate_2.4ml_deep'
SOC_PLATE_TYPE = soc_plate_type
SOC_PLATE_SLOT = '7'
CANDIDATE_TIPRACK_SLOT = '3'
SOURCE_PLATE_POSITION = '2'
TUBE_RACK_POSITION = '4'

# load in through opentrons app
# AGAR_PLATE_TYPE = 'thermofisher_96_wellplate_180ul'
# AGAR_PLATE_SLOT = '1'
INCUBATION_TIME = 30
SOC_VOL = 200
SOC_MIX_SETTINGS = (4, 50)
TEMP_GROWTH = 37
OUTGROWTH_TIME = 60
SOC_ASPIRATION_RATE = 25
P300_DEFAULT_ASPIRATION_RATE = 150


def run(protocol: protocol_api.ProtocolContext):

    def transformation_rxns(competent_dict, control_dict, assembly_dict,
                            water_dict, source_plate, dest_plate, tube_rack,
                            pipette):
        for key in competent_dict.keys():
            competent_source_well = source_plate.wells_by_name()[key]
            val = competent_dict[key]
            competent_dest_wells = []
            for i in range(len(val)):
                competent_dest_wells.append(dest_plate.wells_by_name()[
                                                              val[i][0]])
            vol = val[0][1]
            pipette.transfer(vol, competent_source_well, competent_dest_wells)

        for key in control_dict.keys():
            control_source_well = source_plate.wells_by_name()[key]
            val = control_dict[key]
            control_dest_wells = []
            for i in range(len(val)):
                control_dest_wells.append(dest_plate.wells_by_name()[
                                                            val[i][0]])
            vol = val[0][1]
            pipette.transfer(vol, control_source_well, control_dest_wells)

        for key in assembly_dict.keys():
            dna_source_well = source_plate.wells_by_name()[key]
            val = assembly_dict[key]
            dna_dest_wells = []
            for i in range(len(val)):
                dna_dest_wells.append(dest_plate.wells_by_name()[
                                                        val[i][0]])
            vol = val[0][1]
            pipette.transfer(vol, dna_source_well, dna_dest_wells,
                             mix_after=(4, 5))

        for key in water_dict.keys():
            water_source_well = tube_rack.wells_by_name()[key]
            val = water_dict[key]
            water_dest_wells = []
            for i in range(len(val)):
                water_dest_wells.append(dest_plate.wells_by_name()[
                                                            val[i][0]])
            vol = val[0][1]
            pipette.transfer(vol, water_source_well, water_dest_wells,
                             mix_after=(4, 5))
        return competent_dest_wells, control_dest_wells

    def outgrowth(competent_wells, control_wells, soc_plate, pipette300,
                  temp_mod):
        soc = soc_plate.wells_by_name()['A1']

        # Add SOC to transformed cells
        pipette300.flow_rate.aspirate = SOC_ASPIRATION_RATE
        pipette300.transfer(SOC_VOL, soc, competent_wells,
                            new_tip='always', mix_after=SOC_MIX_SETTINGS)
        pipette300.flow_rate.aspirate = P300_DEFAULT_ASPIRATION_RATE

        pipette300.flow_rate.aspirate = SOC_ASPIRATION_RATE
        pipette300.transfer(SOC_VOL, soc, control_wells,
                            new_tip='always', mix_after=SOC_MIX_SETTINGS)
        pipette300.flow_rate.aspirate = P300_DEFAULT_ASPIRATION_RATE

        # Incubate for 1 hour at 37 °C
        temp_mod.set_temperature(TEMP_GROWTH)
        protocol.delay(minutes=OUTGROWTH_TIME)
        temp_mod.deactivate()

    def bb_transform(competent_dict, control_dict, assembly_dict, water_dict):
        # load labware
        temp_mod = protocol.load_module('temperature module', '10')
        source_plate = protocol.load_labware(SOURCE_PLATE_TYPE,
                                             SOURCE_PLATE_POSITION)
        dest_plate = temp_mod.load_labware(DESTINATION_PLATE_TYPE)
        # dest_plate = protocol.load_labware(DESTINATION_PLATE_TYPE, '1')
        tube_rack = protocol.load_labware(TUBE_RACK_TYPE, TUBE_RACK_POSITION)
        tip_rack = protocol.load_labware(TIPRACK_TYPE, CANDIDATE_TIPRACK_SLOT)
        tip_rack300 = protocol.load_labware(P300_TIPRACK_TYPE, '6')
        pipette = protocol.load_instrument(PIPETTE_TYPE, PIPETTE_MOUNT,
                                           tip_racks=[tip_rack])
        pipette300 = protocol.load_instrument(PIPETTE_TYPE2, PIPETTE_MOUNT2,
                                              tip_racks=[tip_rack300])
        soc_plate = protocol.load_labware(SOC_PLATE_TYPE, SOC_PLATE_SLOT)
        # agar_plate = protocol.load_labware(AGAR_PLATE_TYPE, AGAR_PLATE_SLOT)
        temp_mod.set_temperature(INCUBATION_TEMP)

        competent_wells, control_wells = transformation_rxns(
            competent_dict, control_dict, assembly_dict, water_dict,
            source_plate, dest_plate, tube_rack, pipette)

        protocol.delay(minutes=INCUBATION_TIME)
        protocol.pause()
        protocol.comment(
            'Remove transformation reactions and conduct heatshock.')
        protocol.comment(
            'After heatshock, return for 5 min incubation.')
        protocol.delay(minutes=5)
        protocol.pause()
        protocol.comment(
            'Introduce deep well plate containing SOC media. Resume run.')

        outgrowth(competent_wells, control_wells, soc_plate, pipette300,
                  temp_mod)

    bb_transform(competent_source_to_dest, control_source_to_dest,
                 assembly_source_to_dest, water_to_dest)
