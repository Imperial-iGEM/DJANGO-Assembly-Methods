from opentrons import protocol_api

metadata = {'apiLevel': '2.2',
            'protocolName': 'Clip Template v2',
            'author': 'Gabrielle Johnston',
            'description': 'DNABot updated clip template'}


def run(protocol: protocol_api.ProtocolContext):
    def clip(
        prefixes_wells,
        prefixes_plates,
        suffixes_wells,
        suffixes_plates,
        parts_wells,
        parts_plates,
        parts_vols,
        water_vols,
        tiprack_type='opentrons_96_tiprack_10ul',
        p10_mount='right',
        p10_type='p10_single',
        well_plate_type='biorad_96_wellplate_200ul_pcr',
        tube_rack_type='opentrons_24_tuberack_nest_1.5ml_snapcap'):
    
        """Implements linker ligation reactions using an opentrons OT-2."""

        # Constants
        INITIAL_TIP = 'A1'
        CANDIDATE_TIPRACK_SLOTS = ['3', '6', '9']
        PIPETTE_TYPE = p10_type
        # PIPETTE_MOUNT = 'right'
        PIPETTE_MOUNT = p10_mount
        # SOURCE_PLATE_TYPE = 'biorad_96_wellplate_200ul_pcr'
        SOURCE_PLATE_TYPE = well_plate_type
        # DESTINATION_PLATE_TYPE = 'biorad_96_wellplate_200ul_pcr'
        DESTINATION_PLATE_TYPE = well_plate_type
        DESTINATION_PLATE_POSITION = '1'
        # TUBE_RACK_TYPE = 'opentrons_24_tuberack_nest_1.5ml_snapcap'
        TUBE_RACK_TYPE = tube_rack_type
        TUBE_RACK_POSITION = '4'
        MASTER_MIX_WELL = 'A1'
        WATER_WELL = 'A2'
        INITIAL_DESTINATION_WELL = 'A1'
        MASTER_MIX_VOLUME = 20
        LINKER_MIX_SETTINGS = (4, 10)
        PART_MIX_SETTINGS = (4, 10)

        # Tiprack slots
        total_tips = 4 * len(parts_wells)
        letter_dict = {'A': 0, 'B': 1, 'C': 2,
                       'D': 3, 'E': 4, 'F': 5, 'G': 6, 'H': 7}

        initial_destination_well_index = letter_dict[INITIAL_DESTINATION_WELL[0]]*12 \
            + int(INITIAL_DESTINATION_WELL[1]) - 1

        tiprack_1_tips = (
            13 - int(INITIAL_TIP[1:])) * 8 - letter_dict[INITIAL_TIP[0]]
        if total_tips > tiprack_1_tips:
            tiprack_num = 1 + (total_tips - tiprack_1_tips) // 96 + \
                (1 if (total_tips - tiprack_1_tips) % 96 > 0 else 0)
        else:
            tiprack_num = 1
        slots = CANDIDATE_TIPRACK_SLOTS[:tiprack_num]

        source_plates = {}
        source_plates_keys = list(set((
            prefixes_plates + suffixes_plates + parts_plates)))
        for key in source_plates_keys:
            source_plates[key] = protocol.load_labware(SOURCE_PLATE_TYPE, key)

        tipracks = [protocol.load_labware(tiprack_type, slot)
                    for slot in slots]
        if PIPETTE_TYPE != 'p10_single':
            print('Define labware must be changed to use', PIPETTE_TYPE)
            exit()
        pipette = protocol.load_instrument('p10_single', PIPETTE_MOUNT,
                                           tip_racks=tipracks)
        pipette.flow_rate.aspirate = 20
        #pipette.pick_up_tip(tipracks[0].well(INITIAL_TIP))
        destination_plate = protocol.load_labware(
            DESTINATION_PLATE_TYPE, DESTINATION_PLATE_POSITION)
        tube_rack = protocol.load_labware(TUBE_RACK_TYPE, TUBE_RACK_POSITION)
        master_mix = tube_rack.wells_by_name()[MASTER_MIX_WELL]
        water = tube_rack.wells_by_name()[WATER_WELL]
        #destination_wells = destination_plate.wells(
            #INITIAL_DESTINATION_WELL, length=int(len(parts_wells)))
        destination_wells = destination_plate.wells()[
            initial_destination_well_index:(
                initial_destination_well_index + int(len(parts_wells)))]

        # Transfers
        #pipette.pick_up_tip()
        pipette.pick_up_tip(tipracks[0].well(INITIAL_TIP))
        pipette.transfer(MASTER_MIX_VOLUME, master_mix,
                         destination_wells, new_tip='never', touch_tip=True,
                         blow_out=True)
        pipette.drop_tip()
        pipette.transfer(water_vols, water,
                         destination_wells, touch_tip=True,
                         new_tip='always')
        for clip_num in range(len(parts_wells)):
            prefix_wells = [prefix_well.bottom() for prefix_well in
                            source_plates[prefixes_plates[clip_num]].wells(
                prefixes_wells[clip_num])]
            for prefix_well in prefix_wells:
                pipette.pick_up_tip()
                pipette.move_to(prefix_well)
                protocol.max_speeds['Z'] = 10
                pipette.aspirate(1, prefix_well)
                pipette.move_to(destination_wells[clip_num].top())
                protocol.max_speeds['Z'] = None
                pipette.dispense(1, destination_wells[clip_num])
                pipette.touch_tip(destination_wells[clip_num])
                pipette.mix(LINKER_MIX_SETTINGS[0], LINKER_MIX_SETTINGS[1],
                            destination_wells[clip_num])
                pipette.drop_tip()

            suffix_wells = [suffix_well.bottom() for suffix_well in
                            source_plates[suffixes_plates[clip_num]].wells(
                suffixes_wells[clip_num])]
            for suffix_well in suffix_wells:
                pipette.pick_up_tip()
                pipette.move_to(suffix_well)
                protocol.max_speeds['Z'] = 10
                pipette.aspirate(1, suffix_well)
                pipette.move_to(destination_wells[clip_num].top())
                protocol.max_speeds['Z'] = None
                pipette.dispense(1, destination_wells[clip_num])
                pipette.touch_tip(destination_wells[clip_num])
                pipette.mix(LINKER_MIX_SETTINGS[0], LINKER_MIX_SETTINGS[1],
                            destination_wells[clip_num])
                pipette.drop_tip()

            part_wells = [part_well.bottom() for part_well in
                          source_plates[parts_plates[clip_num]].wells(
                                 parts_wells[clip_num])]
            for part_well in part_wells:
                pipette.pick_up_tip()
                pipette.move_to(part_well)
                protocol.max_speeds['Z'] = 10
                pipette.aspirate(parts_vols[clip_num], part_well)
                pipette.move_to(destination_wells[clip_num].top())
                protocol.max_speeds['Z'] = None
                pipette.dispense(parts_vols[clip_num],
                                 destination_wells[clip_num])
                pipette.touch_tip(destination_wells[clip_num])
                pipette.mix(PART_MIX_SETTINGS[0], PART_MIX_SETTINGS[1],
                            destination_wells[clip_num])
                pipette.drop_tip()

    clip(**clips_dict, p10_mount=p10_mount, p10_type=p10_type, well_plate_type=well_plate_type, tube_rack_type=tube_rack_type)
