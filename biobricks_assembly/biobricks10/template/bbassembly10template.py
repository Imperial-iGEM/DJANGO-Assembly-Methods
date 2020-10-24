from opentrons import protocol_api


metadata = {'apiLevel': '2.2',
            'protocolName': 'BioBricks assembly template',
            'author': 'Gabrielle Johnston',
            'description': 'Opentrons BioBricks RFC 10 assembly template'}

'''
    Input to bbassemble:
        source_to_digest = dictionary of keys as source wells, values = list
        of tuples of destination wells and volumes to be transferred
        digest_to_storage = dictionary of keys as digest destination wells,
        values = list of tuples of reagent wells and volumes
        digest_to_construct: keys = digest destination wells, values =
        tuples of construct destination wells and volumes
        etc...
'''

'''
    Parameters for extra customisation:
    use_p300: if selected, uses a p300 single pipette in the mount that the p10
    pipette is not using
    transfer_t4_manually: transfer the t4 ligase and t4 ligase buffer manually
    so that you don't any on dead volume
    water_trough: True or False -> makes water in trough and other reagents in
    extra well_plate (other reagents includes digest storage)
'''


def run(protocol: protocol_api.ProtocolContext):
    def bbassemble(source_to_digest, digest_to_construct, reagent_to_digest,
                   reagent_to_construct, reagents_dict, p10_mount='left',
                   p10_type='p10_single',
                   well_plate_type='biorad_96_wellplate_200ul_pcr',
                   tube_rack_type='opentrons_24_tuberack_nest_1.5ml_snapcap',
                   thermocycle=False, use_p300=False,
                   transfer_t4_manually=False, water_trough=False):
        # Define constants
        CANDIDATE_TIPRACK_SLOT = '3'
        TIPRACK_TYPE = 'opentrons_96_tiprack_10ul'
        PIPETTE_TYPE = p10_type
        PIPETTE_MOUNT = p10_mount
        SOURCE_PLATE_TYPE = well_plate_type
        SOURCE_PLATE_POSITION = '2'
        DESTINATION_PLATE_TYPE = well_plate_type
        TUBE_RACK_TYPE = tube_rack_type
        TUBE_RACK_POSITION = '4'

        # load labware
        source_plate = protocol.load_labware(SOURCE_PLATE_TYPE,
                                             SOURCE_PLATE_POSITION)
        if water_trough:
            reagents_plate = protocol.load_labware(SOURCE_PLATE_TYPE,
                                                   TUBE_RACK_POSITION)
            trough = protocol.load_labware('usascientific_12_reservoir_22ml',
                                           '6')
            water_well = trough.wells()[0]
        else:
            tube_rack = protocol.load_labware(
                TUBE_RACK_TYPE, TUBE_RACK_POSITION)
        tip_rack = protocol.load_labware(TIPRACK_TYPE, CANDIDATE_TIPRACK_SLOT)
        pipette = protocol.load_instrument(PIPETTE_TYPE, PIPETTE_MOUNT,
                                           tip_racks=[tip_rack])
        pipette.flow_rate.aspirate = 20
        if thermocycle:
            tc_mod = protocol.load_module('Thermocycler Module')
            # dest_plate = tc_mod.load_labware(DESTINATION_PLATE_TYPE)
            digest_plate = tc_mod.load_labware(DESTINATION_PLATE_TYPE)
            tc_mod.open_lid()
        else:
            digest_plate = protocol.load_labware(DESTINATION_PLATE_TYPE, '1')
            dest_plate = protocol.load_labware(DESTINATION_PLATE_TYPE, '7')

        '''
            Digestion procedure:
        '''
        if use_p300:
            if p10_mount == 'left':
                p300_mount = 'right'
            else:
                p300_mount = 'left'
            p300_tiprack = protocol.load_labware(
                'opentrons_96_tiprack_300ul', '9')
            p300_pipette = protocol.load_instrument(
                'p300_single', p300_mount, tip_racks=[p300_tiprack])
        # transferring reagents
        for reagent_well in reagent_to_digest.keys():
            if water_trough:
                if reagent_well == reagents_dict['water']:
                    reagent_plate_well = water_well
                else:
                    reagent_plate_well = reagents_plate.wells_by_name()[
                        reagent_well]
            else:
                reagent_plate_well = tube_rack.wells_by_name()[reagent_well]
            val = reagent_to_digest[reagent_well]
            vols = [entry[1] for entry in val]

            if use_p300 and all(vol >= 30 for vol in vols):
                p300_pipette.pick_up_tip()
                for i in range(len(val)):
                    dest_well = digest_plate.wells_by_name()[val[i][0]]
                    vol = val[i][1]
                    p300_pipette.transfer(vol, reagent_plate_well, dest_well,
                                          new_tip='never')
                p300_pipette.drop_tip()
            else:
                pipette.pick_up_tip()
                for i in range(len(val)):
                    dest_well = digest_plate.wells_by_name()[val[i][0]]
                    vol = val[i][1]
                    pipette.transfer(vol, reagent_plate_well, dest_well,
                                     new_tip='never')
                pipette.drop_tip()

        digest_wells = []
        digest_wells = [digest_plate.wells_by_name()[key] for key in
                        digest_to_construct.keys()]
        # Part transfers to digest tubes
        for source_well in source_to_digest.keys():
            source_plate_well = source_plate.wells_by_name()[source_well]
            val = source_to_digest[source_well]
            digest_wells = []
            # vols = []
            for i in range(len(val)):
                digest_wells.append(digest_plate.wells_by_name()[val[i][0]])
                # vols.append(val[i][1])
            vol = val[0][1]
            if vol < 10:
                pipette.pick_up_tip()
                for digest_well in digest_wells:
                    pipette.move_to(source_plate_well.bottom())
                    protocol.max_speeds['Z'] = 10
                    pipette.aspirate(vol, source_plate_well.bottom())
                    pipette.move_to(digest_well.top())
                    protocol.max_speeds['Z'] = None
                    pipette.dispense(vol, digest_well)
                    pipette.touch_tip(digest_well)
                    pipette.blow_out()
                pipette.drop_tip()
            else:
                pipette.transfer(vol, source_plate_well.bottom(), digest_wells,
                                 touch_tip=True, blow_out=True)

        if thermocycle:
            protocol.comment("--------------------------------------------")
            protocol.comment("Running thermocycler")
            protocol.comment("--------------------------------------------")
            tc_mod.close_lid()
            profile1 = [{'temperature': 37, 'hold_time_seconds': 600},
                        {'temperature': 80, 'hold_time_seconds': 1200}]
            tc_mod.execute_profile(steps=profile1, repetitions=1)
            tc_mod.open_lid()
            protocol.comment(
                'Remove the digest plate and move it into decks position 1')
            digest_plate1 = protocol.load_labware(DESTINATION_PLATE_TYPE, '1')
            protocol.comment(
                'Place a empty plate of the same type in the thermocycler.'
            )
        else:
            protocol.pause()
            protocol.comment(
                'If your digest plate does not fit in your benchtop thermocycler, please transfer your digests to a compatible plate'
            )
            protocol.comment(
                'Seal the digest/compatible plate with adhesive film and remove.')
            protocol.comment(
                'Thermocycle the plate on a benchtop thermocycler.')
            protocol.comment('Use the following thermocycler settings:')
            protocol.comment(
                '1 cycle of 37°C for 5 minutes and 80°C for 10 minutes')
            protocol.comment('If using a different plate for your thermocycler, please transfer digests back to their original wells.')
            protocol.comment('Return the digest plate to position 7.')
        protocol.pause()
        protocol.comment("You may insert your T4 Ligase into well {0}".format(
            reagents_dict['T4Ligase']))
        protocol.comment("You may insert your T4 Buffer into well {0}".format(
            reagents_dict['T4Ligase10X']))
        '''
            Ligation procedure:
        '''
        # Transfer water
        water_well_name = reagents_dict['water']
        val = reagent_to_construct[water_well_name]
        if water_trough:
            reagent_plate_well = water_well
        else:
            reagent_plate_well = tube_rack.wells_by_name()[water_well_name]
        if thermocycle:
            construct_wells = [digest_plate.wells_by_name()[val[i][0]] for i in
                               range(len(val))]
        else:
            construct_wells = [dest_plate.wells_by_name()[val[i][0]] for i in
                               range(len(val))]
        pipette.pick_up_tip()
        for i in range(len(val)):
            vol = val[i][1]
            pipette.transfer(vol, reagent_plate_well, construct_wells[i],
                             new_tip='never')
        pipette.drop_tip()
        if transfer_t4_manually:
            protocol.pause()
            protocol.comment(
                "Transfer 2 uL of the T4 Ligase Buffer into each of the construct wells."
            )
            protocol.comment(
                        "Transfer 1 uL of the T4 Ligase into each of the construct wells.")
        else:
            T4_list = ['T4Ligase10X', 'T4Ligase']
            for T4_entry in T4_list:
                well = reagents_dict[T4_entry]
                val = reagent_to_construct[well]
                if water_trough:
                    reagent_plate_well = reagents_plate.wells_by_name()[well]
                else:
                    reagent_plate_well = tube_rack.wells_by_name()[well]
                for i in range(len(val)):
                    if thermocycle:
                        construct_well = digest_plate.wells_by_name()[val[i][0]]
                    else:
                        construct_well = dest_plate.wells_by_name()[val[i][0]]
                    vol = val[i][1]
                    pipette.pick_up_tip()
                    pipette.move_to(reagent_plate_well.bottom())
                    protocol.max_speeds['Z'] = 10
                    pipette.aspirate(vol, reagent_plate_well.bottom())
                    pipette.move_to(construct_well.top())
                    protocol.max_speeds['Z'] = None
                    pipette.dispense(vol, construct_well)
                    pipette.touch_tip(construct_well)
                    pipette.blow_out()
                    pipette.drop_tip()

        for digest_well in digest_to_construct.keys():
            if thermocycle:
                digest_plate_well = digest_plate1.wells_by_name()[digest_well]
            else:
                digest_plate_well = digest_plate.wells_by_name()[digest_well]
            val = digest_to_construct[digest_well]
            construct_wells = []
            # vols = []
            for i in range(len(val)):
                if thermocycle:
                    construct_wells.append(digest_plate.wells_by_name()[val[i][0]])
                else:
                    construct_wells.append(dest_plate.wells_by_name()[val[i][0]])
                # vols.append(val[i][1])
            vol = val[0][1]

            # transfer from digest to construct
            pipette.pick_up_tip()
            for construct_well in construct_wells:
                pipette.move_to(digest_plate_well.bottom())
                protocol.max_speeds['Z'] = 10
                pipette.aspirate(vol, digest_plate_well.bottom())
                pipette.move_to(construct_well.top())
                protocol.max_speeds['Z'] = None
                pipette.dispense(vol, construct_well)
                pipette.touch_tip(construct_well)
                pipette.blow_out()
            pipette.drop_tip()

        '''for construct_well in construct_wells:
            pipette.pick_up_tip()
            pipette.mix(5, 10, construct_well)
            pipette.drop_tip()'''

        if thermocycle:
            protocol.comment("--------------------------------------------")
            protocol.comment("Running thermocycler")
            protocol.comment("--------------------------------------------")
            tc_mod.close_lid()
            profile2 = [{'temperature': 25, 'hold_time_seconds': 600},
                        {'temperature': 80, 'hold_time_seconds': 1200}]
            tc_mod.execute_profile(steps=profile2, repetitions=1)
            tc_mod.open_lid()

        else:
            protocol.pause()
            protocol.comment(
                'If your reaction plate does not fit in your benchtop thermocycler, please transfer your digests to a compatible plate'
            )
            protocol.comment(
                'Seal the reaction/compatible plate with adhesive film and remove.')
            protocol.comment(
                'Thermocycle the plate on a benchtop thermocycler.')
            protocol.comment('Use the following thermocycler settings:')
            protocol.comment(
                '1 cycle of 25°C for 5 minutes and 80°C for 10 minutes')

        protocol.comment('BioBricks assembly finished')

    bbassemble(source_to_digest, digest_to_construct, reagent_to_digest,
               reagent_to_construct, reagents_dict, p10_mount=p10_mount,
               p10_type=p10_type, well_plate_type=well_plate_type,
               tube_rack_type=tube_rack_type, thermocycle=thermocycle)