from opentrons import protocol_api

metadata = {'apiLevel': '2.2',
            'protocolName': 'Generalised MoClo Transformation Protocol for OT-2 v2',
            'author': 'Gabrielle Johnston',
            'description': 'Generalised DAMP Lab MoClo transformation protocol for OT-2 v2'}


def run(protocol: protocol_api.ProtocolContext):

    def add_soc(reaction_plate, pipette, soc, multi, washes):

        num_cols = len(reaction_plate.columns())
        if multi:
            dest_wells = [reaction_plate.columns()[i][0]
                          for i in range(num_cols)]
        else:
            dest_wells = reaction_plate.wells()
        pipette.pick_up_tip()
        for dest_well in dest_wells:
            pipette.transfer(150, soc.bottom(), dest_well.bottom(1),
                             new_tip='never')
            pipette.mix(
                2, 150, dest_well.bottom(1))
            pipette.blow_out()
            pipette.mix(2, 300, washes[0].bottom())
            pipette.blow_out()
            pipette.mix(2, 300, washes[1].bottom())
            pipette.blow_out()
        # Two washing steps are added to allow recycling of the tips
        pipette.drop_tip()

    def dilution(reaction_plate, pipette, soc, multi, washes, waste):
        num_cols = len(reaction_plate.columns())
        if multi:
            dest_wells = [reaction_plate.columns()[i][0]
                          for i in range(num_cols)]
        else:
            dest_wells = reaction_plate.wells()
        pipette.pick_up_tip()
        for dest_well in dest_wells:
            pipette.transfer(157, dest_well.bottom(0.5), waste.bottom(),
                             new_tip='never')
            pipette.blow_out()
            pipette.mix(2, 300, washes[0].bottom())
            pipette.blow_out()
            pipette.mix(2, 300, washes[1].bottom())
            pipette.blow_out()
            # Two washing steps are added to allow recycling of the tips
            pipette.transfer(45, soc.bottom(), dest_well.bottom(0.5),
                             new_tip='never')
            pipette.mix(2, 50, dest_well)
            pipette.blow_out()
            pipette.mix(2, 300, washes[0].bottom())
            pipette.blow_out()
            pipette.mix(2, 300, washes[1].bottom())
            pipette.blow_out()
        # Two washing steps are added to allow recycling of the tips
        pipette.drop_tip()

    def plating(reaction_plate, agar_plate, pipette, multi, triplicate):
        num_cols = len(reaction_plate.columns())
        if multi:
            dest_wells = [reaction_plate.columns()[i][0]
                          for i in range(num_cols)]
            agar_wells = [agar_plate.columns()[i][0]
                          for i in range(num_cols)]
        else:
            dest_wells = reaction_plate.wells()
            agar_wells = agar_plate.wells()
        pipette.pick_up_tip()
        for i in range(len(dest_wells)):
            pipette.transfer(
                10, dest_wells[i].bottom(0.5),
                agar_wells[i].bottom(0.3),
                new_tip='never')
        if triplicate:
            count2 = 0
            for i in range(len(dest_wells)):
                pipette.transfer(1, dest_wells[i].bottom(0.5),
                                 agar_wells[i].bottom(-1), new_tip='never')
                pipette.transfer(9, dest_wells[i].bottom(0.5),
                                 agar_wells[i+count2].bottom(0.8),
                                 new_tip='never')
                pipette.transfer(1, dest_wells[i].bottom(0.5),
                                 agar_wells[i+count2].bottom(-1),
                                 new_tip='never')
                pipette.transfer(9, dest_wells[i].bottom(0.5),
                                 agar_wells[i+count2+1].bottom(0.8),
                                 new_tip='never')
                pipette.transfer(1, dest_wells[i].bottom(0.5),
                                 agar_wells[i+count2+1].bottom(-1),
                                 new_tip='never')
                pipette.transfer(9, dest_wells[i].bottom(0.5),
                                 agar_wells[i+count2+2].bottom(0.8),
                                 new_tip='never')
                pipette.transfer(1, dest_wells[i].bottom(0.5),
                                 agar_wells[i+count2+2].bottom(-1),
                                 new_tip='never')
                count2 += 2

            pipette.drop_tip()

    def transform_protocol(combinations_to_make, multi=False,
                           triplicate=False,
                           reaction_plate_type='biorad_96_wellplate_200ul_pcr',
                           trough_type='usascientific_12_reservoir_22ml',
                           agar_plate_type='thermofisher_96_wellplate_180ul'):
        num_rxns = len(combinations_to_make)

        '''
            For this protocol, the biorad_96_wellplate_200ul_pcr, is placed on the
            top of the TempDeck alone without the Opentrons 96 well aluminum block.
        '''

        # Load in Bio-Rad 96 Well Plate on temp deck for moclos,
        # transformation, and outgrowth.
        temp_deck = protocol.load_module('tempdeck', 10)
        protocol.comment(
            'Load in 10 ul of competent cells for new reaction plate wells 1 to {0}'.format(num_rxns))
        protocol.pause()
        reaction_plate = temp_deck.load_labware(
            'biorad_96_wellplate_200ul_pcr')
        temp_deck.set_temperature(10)

        # Load in 1 10ul tiprack and 2 300ul tipracks
        tr_10 = [protocol.load_labware('opentrons_96_tiprack_10ul', '3')]
        tr_300 = [protocol.load_labware('opentrons_96_tiprack_300ul', '6'),
                  protocol.load_labware('opentrons_96_tiprack_300ul', '9')]
        # for i in range(0, 1):
        #   tr_300.append(labware.load('tipone_96_tiprack_200ul', '9'))

        # Load in pipettes
        p10_single = protocol.load_instrument('p10_single',
                                              mount=pipetteMount10,
                                              tip_racks=tr_10)
        
        # reaction plate from assembly
        post_moclo_reaction_plate = protocol.load_labware(
            reaction_plate_type, '7', 'Post-MoClo Reaction Plate')

        # Load in water, SOC, and wash trough (USA Scientific 12 Well Reservoir
        # 22ml)
        trough = protocol.load_labware(trough_type, '5',
                                       'Reagents trough')

        # water = trough.wells()[0]  # Well 1
        wash_0 = trough.wells()[1]  # Well 2
        wash_1 = trough.wells()[2]  # Well 3
        soc = trough.wells()[3]  # Well 4
        liquid_waste = trough.wells()[4]  # Well 5

        # temporary: should use custom labware: thermofisher_96_wellplate_180ul
        agar_plate = protocol.load_labware(agar_plate_type,
                                           '2', 'Agar Plate')
                                   
        '''Use 10uL of competent cells with 2uL of each DNA rections from the MoClo
        protocol'''

        # At the beginning of this for loop, the Bio-Rad 96 Well Plate
        # (reaction_plate) now contains 10 uL of competent cells per wells
        # (well 1 through 88)
        p10_single.pick_up_tip()
        # Add 2 ul of rxns to comp cells
        for i in range(0, num_rxns):
            p10_single.transfer(
                2, post_moclo_reaction_plate.wells()[i].bottom(0.5),
                reaction_plate.wells()[i].bottom(0.5), new_tip='never')
            p10_single.mix(4, 10, reaction_plate.wells()[i].bottom(0.5))
            p10_single.blow_out()
            p10_single.mix(2, 10, wash_0.bottom(0.5))
            p10_single.blow_out()
            p10_single.mix(2, 10, wash_1.bottom(0.5))
            p10_single.blow_out()
        # Two washing steps are added to allow recycling of the tips
        p10_single.drop_tip()

        # Incubate at 4C, then heat shock.
        '''Be sure to un-pause the robot in between the heat shock'''
        temp_deck.set_temperature(4)
        protocol.delay(minutes=30)
        temp_deck.set_temperature(42)
        protocol.delay(minutes=1)
        temp_deck.set_temperature(4)
        protocol.delay(minutes=5)

        if pipetteMount10 == pipetteMount300:
            protocol.pause()
            protocol.comment(
                "Replace the p10 pipette with the p300 pipette, mounting in the same position.")
            rep = True  # tell opentrons that the p10 pipette is being replaced
        else:
            rep = False  # p10 pipette is not being replaced

        if multi:
            p300_multi = protocol.load_instrument('p300_multi',
                                                  mount=pipetteMount300,
                                                  tip_racks=tr_300,
                                                  replace=rep)
        else:
            p300_single = protocol.load_instrument('p300_single',
                                                   mount=pipetteMount300,
                                                   tip_racks=tr_300,
                                                   replace=rep)
        # add soc
        if multi:
            pipette300 = p300_multi
        else:
            pipette300 = p300_single
        add_soc(reaction_plate, pipette300, soc, multi, [wash_0, wash_1])

        # Grow for 1 hr, seal the plate with adhesive film to avoid evaporation
        temp_deck.set_temperature(37)
        protocol.delay(minutes=60)
        protocol.pause()
        temp_deck.deactivate()
        '''
            Remove the adhesive film from the Reaction Plate before perceeding to
            Cell Plating.
            Be sure to un-pause the robot after removing the adhesive film!
        '''

        # Dilute the recovered transformation reactions and start plating
        '''
            All recovered transformation reactions are diluted to 10% of its
            original concentration before plating
        '''
        # Dilution
        dilution(reaction_plate, pipette300, soc, multi, [wash_0, wash_1],
                 liquid_waste)

        plating(reaction_plate, agar_plate, pipette300, multi, triplicate)

    transform_protocol(combinations_to_make, multi, triplicate,
                       reaction_plate_type, trough_type, agar_plate_type)
