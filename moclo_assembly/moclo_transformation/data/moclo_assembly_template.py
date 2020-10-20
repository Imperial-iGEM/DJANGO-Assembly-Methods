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
        p10_single = protocol.load_instrument(p10_type,
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
        print('combinations_to_make', combinations_to_make)

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
            protocol.pause()

        protocol.comment('Remove the Input_DNA_Plate from the Deck Space.')
        protocol.comment(
            'Remaining DNA may be saved by sealing the Input_DNA_Plate with adhesive film and storing at -20°C')
        protocol.comment(
            'Insert the reaction plate into deck positon 7')

    moclo_protocol(dna_plate_map_dict, combinations_to_make, thermocycle,
                   reaction_plate_type, reagent_plate_type, trough_type)
