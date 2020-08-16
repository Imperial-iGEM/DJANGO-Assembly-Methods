from opentrons import protocol_api
import math

metadata = {'apiLevel': '2.2',
            'protocolName': 'BioBricks assembly template',
            'author': 'Gabrielle Johnston',
            'description': 'Opentrons BioBricks RFC 10 assembly template'}

'''
    Input to bbassemble:
        source plate dictionary with keys = role, values = [part def, well,
        concentration (ng/uL)]
        reagents dictionary with keys = reagent, values = well
        also use for storing leftover digest before second thermocycler starts
        destination plate dictionary with keys = digests and final product,
        values = pos
'''


def run(protocol: protocol_api.ProtocolContext):
    def bbassemble(source, reagents, dest):
        # Define constants
        CANDIDATE_TIPRACK_SLOT = '3'
        TIPRACK_TYPE = 'opentrons_96_tiprack_10ul'
        PART_AMOUNT = 500  # 500 ng
        PIPETTE_TYPE = 'p10_single'
        PIPETTE_MOUNT = 'right'
        SOURCE_PLATE_TYPE = 'biorad_96_wellplate_200ul_pcr'
        SOURCE_PLATE_POSITION = '2'
        DESTINATION_PLATE_TYPE = 'biorad_96_wellplate_200ul_pcr'
        TUBE_RACK_TYPE = 'opentrons_24_tuberack_nest_1.5ml_snapcap'
        TUBE_RACK_POSITION = '4'
        FILL_VOL = 50
        NEB_BUFFER_10X_VOL = 5
        ENZ_VOL = 1
        UP_ENZYMES = ['EcoRI-HF', 'SpeI']
        DOWN_ENZYMES = ['XbaI', 'PstI']
        PLASMID_ENZYMES = ['EcoRI-HF', 'PstI']
        DIGEST_COMB_VOL = 2
        T4_LIGASE_VOL = 1
        T4_LIGASE_VOL_10X = 2
        WATER_VOL_LIG = 11

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
        upstream_vol = math.ceil(PART_AMOUNT*(1/source['upstream'][2]))
        downstream_vol = math.ceil(PART_AMOUNT*(1/source['downstream'][2]))
        plasmid_vol = math.ceil(PART_AMOUNT*(1/source['plasmid'][2]))
        vols = [upstream_vol, downstream_vol, plasmid_vol]

        # Part transfers to digest tubes
        pipette.transfer(upstream_vol,
                         source_plate.wells_by_name()[source['upstream'][1]],
                         dest_plate.wells_by_name()[dest['upstream']],
                         blow_out=True)
        pipette.transfer(downstream_vol,
                         source_plate.wells_by_name()[source['downstream'][1]],
                         dest_plate.wells_by_name()[dest['downstream']],
                         blow_out=True)
        pipette.transfer(plasmid_vol,
                         source_plate.wells_by_name()[source['plasmid'][1]],
                         dest_plate.wells_by_name()[dest['plasmid']],
                         blow_out=True)

        # transferring water
        pipette.pick_up_tip()
        keys = [key for key in source.keys()]
        for i in range(3):
            water_vol = FILL_VOL - vols[i] - 2*ENZ_VOL - NEB_BUFFER_10X_VOL
            key = keys[i]
            pipette.transfer(water_vol,
                             tube_rack.wells_by_name()[reagents['water']],
                             dest_plate.wells_by_name()[dest[key]],
                             new_tip='never')
        pipette.drop_tip()

        dest_plate_digest_wells = [dest_plate.wells_by_name()[dest[key]]
                                   for key in source.keys()]
        pipette.pick_up_tip()
        pipette.transfer(NEB_BUFFER_10X_VOL,
                         tube_rack.wells_by_name()[reagents['NEBBuffer10X']],
                         dest_plate_digest_wells,
                         new_tip='never')
        pipette.drop_tip()

        # Upstream part enzymes
        for i in range(2):
            enz_well = tube_rack.wells_by_name()[reagents[UP_ENZYMES[i]]]
            if i == 0:
                pipette.transfer(ENZ_VOL, enz_well,
                                 dest_plate.wells_by_name()[dest['upstream']])
            else:
                pipette.transfer(ENZ_VOL, enz_well,
                                 dest_plate.wells_by_name()[dest['upstream']],
                                 mix_after=(5, 10))
        # Downstream part enzymes
        for i in range(2):
            enz_well = tube_rack.wells_by_name()[reagents[DOWN_ENZYMES[i]]]
            if i == 0:
                pipette.transfer(ENZ_VOL, enz_well,
                                 dest_plate.wells_by_name()[dest['downstream']]
                                 )
            else:
                pipette.transfer(ENZ_VOL, enz_well,
                                 dest_plate.wells_by_name()[dest['downstream']
                                                            ],
                                 mix_after=(5, 10))

        # Plasmid enzymes
        for i in range(2):
            enz_well = tube_rack.wells_by_name()[reagents[PLASMID_ENZYMES[i]]]
            if i == 0:
                pipette.transfer(ENZ_VOL, enz_well,
                                 dest_plate.wells_by_name()[dest['plasmid']])
            else:
                pipette.transfer(ENZ_VOL, enz_well,
                                 dest_plate.wells_by_name()[dest['plasmid']],
                                 mix_after=(5, 10))

        tc_mod.close_lid()
        profile1 = [{'temperature': 37, 'hold_time_seconds': 600},
                    {'temperature': 80, 'hold_time_seconds': 1200}]
        tc_mod.execute_profile(steps=profile1, repetitions=1)

        '''
            Ligation procedure:
        '''
        tc_mod.open_lid()

        construct_well = dest_plate.wells_by_name()[dest['construct']]
        pipette.transfer(WATER_VOL_LIG,
                         tube_rack.wells_by_name()[reagents['water']],
                         construct_well)

        for i in range(3):
            pipette.transfer(DIGEST_COMB_VOL, dest_plate_digest_wells[i],
                             construct_well, blow_out=True)

        pipette.transfer(T4_LIGASE_VOL_10X,
                         tube_rack.wells_by_name()[reagents['T4Ligase10X']],
                         construct_well)
        pipette.transfer(T4_LIGASE_VOL,
                         tube_rack.wells_by_name()[reagents['T4Ligase']],
                         construct_well, mix_after=(5, 10))

        # rescue the rest of the digests
        pipette.transfer(48, dest_plate_digest_wells[0],
                         tube_rack.wells_by_name()[reagents['upstream']],
                         blow_out=True)

        pipette.transfer(48, dest_plate_digest_wells[1],
                         tube_rack.wells_by_name()[reagents['downstream']],
                         blow_out=True)

        pipette.transfer(48, dest_plate_digest_wells[2],
                         tube_rack.wells_by_name()[reagents['plasmid']],
                         blow_out=True)

        tc_mod.close_lid()
        profile2 = [{'temperature': 25, 'hold_time_seconds': 600},
                    {'temperature': 80, 'hold_time_seconds': 1200}]
        tc_mod.execute_profile(steps=profile2, repetitions=1)
        tc_mod.open_lid()

    bbassemble(source_wells, reagent_tubes, destination_wells)
