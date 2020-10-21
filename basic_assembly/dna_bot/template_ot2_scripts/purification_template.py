from opentrons import protocol_api

metadata = {'apiLevel': '2.2',
            'protocolName': 'Purification Template v2',
            'author': 'Gabrielle Johnston',
            'description': 'DNABot updated purification template'}


def run(protocol: protocol_api.ProtocolContext):
    def magbead(
        sample_number,
        ethanol_well,
        elution_buffer_well,
        sample_volume=30,
        bead_ratio=1.8,
        elution_buffer_volume=40,
        incubation_time=5,
        settling_time=2,
        drying_time=5,
        elution_time=2,
        sample_offset=0,
        tiprack_type='opentrons_96_tiprack_300ul',
        p300_mount='left',
        p300_type='p300_multi',
        well_plate_type='biorad_96_wellplate_200ul_pcr',
        reagent_plate_type='usascientific_12_reservoir_22ml',
        bead_container_type='usascientific_96_wellplate_2.4ml_deep',
        multi=True):
        """Implements magbead purification reactions for BASIC assembly using an opentrons OT-2.

        Selected args:
            ethanol_well (str): well in reagent container containing ethanol.
            elution_buffer_well (str): well in reagent container containing elution buffer.
            sample_offset (int): offset the intial sample column by the specified value.

        """

        # Constants
        # PIPETTE_MOUNT = 'left'
        PIPETTE_MOUNT = p300_mount
        PIPETTE_ASPIRATE_RATE = 25
        PIPETTE_DISPENSE_RATE = 150
        TIPS_PER_SAMPLE = 9
        CANDIDATE_TIPRACK_SLOTS = ['3', '6', '9', '2', '5']
        MAGDECK_POSITION = '1'
        # MIX_PLATE_TYPE = 'biorad_96_wellplate_200ul_pcr'
        MIX_PLATE_TYPE = well_plate_type
        MIX_PLATE_POSITION = '4'
        # REAGENT_CONTAINER_TYPE = 'usascientific_12_reservoir_22ml'
        REAGENT_CONTAINER_TYPE = reagent_plate_type
        REAGENT_CONTAINER_POSITION = '7'
        # BEAD_CONTAINER_TYPE = 'usascientific_96_wellplate_2.4ml_deep'
        BEAD_CONTAINER_TYPE = bead_container_type
        BEAD_CONTAINER_POSITION = '8'
        LIQUID_WASTE_WELL = 'A12'
        BEADS_WELL = 'A1'
        DEAD_TOTAL_VOL = 5
        SLOW_HEAD_SPEEDS = {'x': 600 // 4, 'y': 400 // 4,
                            'z': 125 // 10, 'a': 125 // 10}
        DEFAULT_HEAD_SPEEDS = {'x': 400, 'y': 400, 'z': 125, 'a': 100}
        IMMOBILISE_MIX_REPS = 10
        MAGDECK_HEIGHT = 20
        AIR_VOL_COEFF = 0.1
        ETHANOL_VOL = 150
        WASH_TIME = 0.5
        ETHANOL_DEAD_VOL = 50
        ELUTION_MIX_REPS = 20
        ELUTANT_SEP_TIME = 1
        ELUTION_DEAD_VOL = 2

        # Errors
        if sample_number > 48:
            raise ValueError('sample number cannot exceed 48')

        # Tips and pipette
        if multi:
            total_tips = sample_number * 2 * TIPS_PER_SAMPLE
        else:
            if sample_number % 8 > 0:
                tip_mult = 8*((sample_number // 8) + 1)
            else:
                tip_mult = sample_number
            total_tips = tip_mult * 2 * TIPS_PER_SAMPLE
        total_tips = sample_number * 2 * TIPS_PER_SAMPLE
        tiprack_num = total_tips // 96 + (1 if total_tips % 96 > 0 else 0)
        slots = CANDIDATE_TIPRACK_SLOTS[:tiprack_num]
        tipracks = [protocol.load_labware(tiprack_type, slot)
                    for slot in slots]
        pipette = protocol.load_instrument(p300_type, PIPETTE_MOUNT,
                                           tip_racks=tipracks)

        pipette.flow_rate.aspirate = PIPETTE_ASPIRATE_RATE
        pipette.flow_rate.dispense = PIPETTE_DISPENSE_RATE

        # Define labware
        mag_mod = protocol.load_module('magnetic module', MAGDECK_POSITION)
        mag_mod.disengage()

        mag_plate = mag_mod.load_labware(MIX_PLATE_TYPE)
        mix_plate = protocol.load_labware(MIX_PLATE_TYPE, MIX_PLATE_POSITION,
                                          label='mixing plate')
        reagent_container = protocol.load_labware(
            REAGENT_CONTAINER_TYPE, REAGENT_CONTAINER_POSITION)
        bead_container = protocol.load_labware(BEAD_CONTAINER_TYPE,
                                               BEAD_CONTAINER_POSITION)
        col_num = sample_number // 8 + (1 if sample_number % 8 > 0 else 0)

        if multi:
            samples = [col for col in mag_plate.rows()[0][
                sample_offset:sample_offset+col_num]]
            mixing = [col for col in mix_plate.rows()[0][
                sample_offset:sample_offset+col_num]]
            output = [col for col in mag_plate.rows()[0][
                sample_offset+6:sample_offset+6+col_num]]
        else:
            start = sample_offset
            stop = start + sample_number
            samples = mag_plate.wells()[start:stop]
            mixing = mix_plate.wells()[start:stop]
            start = sample_offset + 6*8
            stop = start + sample_number
            output = mag_plate.wells()[start:stop]

        # Define reagents and liquid waste
        liquid_waste = reagent_container.wells_by_name()[LIQUID_WASTE_WELL]
        beads = bead_container.wells_by_name()[BEADS_WELL]
        ethanol = reagent_container.wells_by_name()[ethanol_well]
        elution_buffer = reagent_container.wells_by_name()[elution_buffer_well]

        # Define bead and mix volume
        bead_volume = sample_volume * bead_ratio
        if bead_volume / 2 > pipette.max_volume:
            mix_vol = pipette.max_volume
        else:
            mix_vol = bead_volume / 2
        total_vol = bead_volume + sample_volume + DEAD_TOTAL_VOL

        # Mix beads and PCR samples and incubate
        for target, dest in zip(samples, mixing):
            # Aspirate beads
            pipette.pick_up_tip()
            pipette.mix(5, mix_vol, beads)
            pipette.transfer(bead_volume, beads, dest, new_tip='never')
            pipette.move_to(target.bottom())

            for key in SLOW_HEAD_SPEEDS.keys():
                protocol.max_speeds[key] = SLOW_HEAD_SPEEDS[key]
            pipette.aspirate(sample_volume + DEAD_TOTAL_VOL, target.bottom())
            pipette.move_to(dest.top())
            for key in DEFAULT_HEAD_SPEEDS.keys():
                protocol.max_speeds[key] = DEFAULT_HEAD_SPEEDS[key]
            pipette.dispense(sample_volume + DEAD_TOTAL_VOL, dest)
            pipette.mix(IMMOBILISE_MIX_REPS, mix_vol, dest)
            pipette.touch_tip(dest)
            pipette.blow_out()
            pipette.drop_tip()

        # Immobilise sample
        protocol.delay(minutes=incubation_time)

        # Transfer sample back to magdeck
        for target in range(int(len(samples))):
            pipette.transfer(total_vol, mixing[target], samples[target],
                             blow_out=True)

        # Engagae MagDeck and incubate
        mag_mod.engage(height=MAGDECK_HEIGHT)
        protocol.delay(minutes=settling_time)

        # Remove supernatant from magnetic beads
        for target in samples:
            pipette.transfer(total_vol, target, liquid_waste, blow_out=True)

        # Wash beads twice with 70% ethanol
        air_vol = pipette.max_volume * AIR_VOL_COEFF
        for cycle in range(2):
            for target in samples:
                pipette.transfer(ETHANOL_VOL, ethanol, target, air_gap=air_vol)
            protocol.delay(minutes=WASH_TIME)
            for target in samples:
                pipette.transfer(ETHANOL_VOL + ETHANOL_DEAD_VOL, target,
                                 liquid_waste, air_gap=air_vol)

        # Dry at RT
        protocol.delay(minutes=drying_time)

        # Disengage MagDeck
        mag_mod.disengage()

        # Mix beads with elution buffer
        if elution_buffer_volume / 2 > pipette.max_volume:
            mix_vol = pipette.max_volume
        else:
            mix_vol = elution_buffer_volume / 2
        for target in samples:
            pipette.transfer(elution_buffer_volume, elution_buffer,
                             target, mix_after=(ELUTION_MIX_REPS, mix_vol))

        # Incubate at RT for "elution_time" minutes
        protocol.delay(minutes=elution_time)

        # Engagae MagDeck for 1 minute and remain engaged for DNA elution
        mag_mod.engage(height=MAGDECK_HEIGHT)
        protocol.delay(minutes=ELUTANT_SEP_TIME)

        # Transfer clean PCR product to a new well
        for target, dest in zip(samples, output):
            pipette.pick_up_tip()
            pipette.move_to(target.bottom())
            for key in SLOW_HEAD_SPEEDS.keys():
                protocol.max_speeds[key] = SLOW_HEAD_SPEEDS[key]
            pipette.aspirate(elution_buffer_volume - ELUTION_DEAD_VOL,
                             target.bottom())
            pipette.move_to(dest.top())
            for key in DEFAULT_HEAD_SPEEDS.keys():
                protocol.max_speeds[key] = DEFAULT_HEAD_SPEEDS[key]
            pipette.dispense(elution_buffer_volume - ELUTION_DEAD_VOL, dest)
            pipette.touch_tip(dest)
            pipette.drop_tip()

        # Disengage MagDeck
        mag_mod.disengage()


    magbead(sample_number=sample_number,
            ethanol_well=ethanol_well, elution_buffer_well='A1',
            p300_mount=p300_mount, p300_type=p300_type,
            well_plate_type=well_plate_type, reagent_plate_type=reagent_plate_type,
            bead_container_type=bead_container_type, multi=multi)
