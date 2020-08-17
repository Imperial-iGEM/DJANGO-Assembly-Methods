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


def run(protocol: protocol_api.ProtocolContext):
    def bbassemble(source_to_digest, digest_to_storage, digest_to_construct,
                   reagent_to_digest, reagent_to_construct):
        # Define constants
        CANDIDATE_TIPRACK_SLOT = '3'
        TIPRACK_TYPE = 'opentrons_96_tiprack_10ul'
        PIPETTE_TYPE = 'p10_single'
        PIPETTE_MOUNT = 'right'
        SOURCE_PLATE_TYPE = 'biorad_96_wellplate_200ul_pcr'
        SOURCE_PLATE_POSITION = '2'
        DESTINATION_PLATE_TYPE = 'biorad_96_wellplate_200ul_pcr'
        TUBE_RACK_TYPE = 'opentrons_24_tuberack_nest_1.5ml_snapcap'
        TUBE_RACK_POSITION = '4'

        # load labware
        source_plate = protocol.load_labware(SOURCE_PLATE_TYPE,
                                             SOURCE_PLATE_POSITION)
        tube_rack = protocol.load_labware(TUBE_RACK_TYPE, TUBE_RACK_POSITION)
        tip_rack = protocol.load_labware(TIPRACK_TYPE, CANDIDATE_TIPRACK_SLOT)
        pipette = protocol.load_instrument(PIPETTE_TYPE, PIPETTE_MOUNT,
                                           tip_racks=[tip_rack])
        tc_mod = protocol.load_module('Thermocycler Module')
        dest_plate = tc_mod.load_labware(DESTINATION_PLATE_TYPE)
        tc_mod.open_lid()

        '''
            Digestion procedure:
        '''
        # Part transfers to digest tubes
        for source_well in source_to_digest.keys():
            source_plate_well = source_plate.wells_by_name()[source_well]
            val = source_to_digest[source_well]
            digest_wells = []
            # vols = []
            for i in range(len(val)):
                digest_wells.append(dest_plate.wells_by_name()[val[i][0]])
                # vols.append(val[i][1])
            vol = val[0][1]
            pipette.transfer(vol, source_plate_well, digest_wells, 
                             blow_out=True)

        # transferring reagents
        for reagent_well in reagent_to_digest.keys():
            reagent_plate_well = tube_rack.wells_by_name()[reagent_well]
            val = reagent_to_digest[reagent_well]
            pipette.pick_up_tip()
            for i in range(len(val)):
                dest_well = dest_plate.wells_by_name()[val[i][0]]
                vol = val[i][1]
                pipette.transfer(vol, reagent_plate_well, dest_well,
                                 new_tip='never')
            pipette.drop_tip()

        digest_wells = []
        digest_wells = [dest_plate.wells_by_name()[key] for key in
                        digest_to_construct.keys()]
        for digest_well in digest_wells:
            pipette.pick_up_tip()
            pipette.mix(5, 10, digest_well)
            pipette.drop_tip()

        tc_mod.close_lid()
        profile1 = [{'temperature': 37, 'hold_time_seconds': 600},
                    {'temperature': 80, 'hold_time_seconds': 1200}]
        tc_mod.execute_profile(steps=profile1, repetitions=1)

        '''
            Ligation procedure:
        '''
        tc_mod.open_lid()

        for digest_well in digest_to_construct.keys():
            digest_plate_well = dest_plate.wells_by_name()[digest_well]
            val = digest_to_construct[digest_well]
            construct_wells = []
            # vols = []
            for i in range(len(val)):
                construct_wells.append(dest_plate.wells_by_name()[val[i][0]])
                # vols.append(val[i][1])
            vol = val[0][1]
            pipette.transfer(vol, digest_plate_well, construct_wells,
                             blow_out=True)
            
        for digest_well in digest_to_storage.keys():
            digest_plate_well = dest_plate.wells_by_name()[digest_well]
            val = digest_to_storage[digest_well]
            storage_wells = []
            # vols = []
            for i in range(len(val)):
                storage_wells.append(tube_rack.wells_by_name()[val[i][0]])
                # vols.append(val[i][1])
            vol = val[0][1]
            pipette.transfer(vol, digest_plate_well, storage_wells,
                             blow_out=True)
        
        for reagent_well in reagent_to_construct.keys():
            reagent_plate_well = tube_rack.wells_by_name()[reagent_well]
            val = reagent_to_construct[reagent_well]
            construct_wells = []
            # vols = []
            for i in range(len(val)):
                construct_wells.append(dest_plate.wells_by_name()[val[i][0]])
                # vols.append(val[i][1])
            vol = val[0][1]
            pipette.transfer(vol, reagent_plate_well, construct_wells)
        
        for construct_well in construct_wells:
            pipette.pick_up_tip()
            pipette.mix(5, 10, construct_well)
            pipette.drop_tip()

        tc_mod.close_lid()
        profile2 = [{'temperature': 25, 'hold_time_seconds': 600},
                    {'temperature': 80, 'hold_time_seconds': 1200}]
        tc_mod.execute_profile(steps=profile2, repetitions=1)
        tc_mod.open_lid()

    bbassemble(source_to_digest, digest_to_storage, digest_to_construct,
               reagent_to_digest, reagent_to_construct)
