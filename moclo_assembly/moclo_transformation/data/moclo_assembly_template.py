from opentrons import protocol_api

metadata = {'apiLevel': '2.2',
            'protocolName': 'Generalised MoClo Protocol for OT-2 v2',
            'author': 'Gabrielle Johnston',
            'description': 'Generalised DAMP Lab MoClo protocol for OT-2 v2'}


def run(protocol: protocol_api.ProtocolContext):

    def define_master_mix(no_assemblies, parts_per_assembly, wells_open,
                          pipette, reaction_plate, water, ligase, buffer,
                          restriction_enzyme):
        TOT_VOL_PER_ASSEMBLY = 20
        BUFFER_VOL_PER_ASSEMBLY = 2
        LIGASE_VOL_PER_ASSEMBLY = 0.5
        ENZYME_VOL_PER_ASSEMBLY = 1
        MAX_ASSEMBLIES_PER_MM_WELL = 11  # take into account dead vol
        PART_VOL = 2
        mm_dict_list = []
        mm_vol_per_assembly = TOT_VOL_PER_ASSEMBLY - \
            parts_per_assembly*PART_VOL
        if mm_vol_per_assembly < 4:
            raise ValueError('Too many parts in one step assembly')
        rem_assemblies = no_assemblies
        for i in range(7):
            mm_dict = {}
            if rem_assemblies > MAX_ASSEMBLIES_PER_MM_WELL:
                mm_dict['well'] = wells_open[i]
                mm_dict['no_assemblies'] = MAX_ASSEMBLIES_PER_MM_WELL
                no = MAX_ASSEMBLIES_PER_MM_WELL + 1
                mm_dict['buffer_vol'] = BUFFER_VOL_PER_ASSEMBLY*no
                mm_dict['ligase_vol'] = LIGASE_VOL_PER_ASSEMBLY*no
                mm_dict['enzyme_vol'] = ENZYME_VOL_PER_ASSEMBLY*no
                mm_dict['water_vol'] = mm_vol_per_assembly*no - \
                    mm_dict['buffer_vol'] - mm_dict['ligase_vol'] - \
                    mm_dict['enzyme_vol']
                mm_dict_list.append(mm_dict)
                rem_assemblies = rem_assemblies - MAX_ASSEMBLIES_PER_MM_WELL
            else:
                mm_dict['well'] = wells_open[i]
                mm_dict['no_assemblies'] = rem_assemblies
                no = rem_assemblies + 1
                if no % 2 != 0:
                    no += 1
                mm_dict['buffer_vol'] = BUFFER_VOL_PER_ASSEMBLY*no
                mm_dict['ligase_vol'] = LIGASE_VOL_PER_ASSEMBLY*no
                mm_dict['enzyme_vol'] = ENZYME_VOL_PER_ASSEMBLY*no
                mm_dict['water_vol'] = mm_vol_per_assembly*no - \
                    mm_dict['buffer_vol'] - mm_dict['ligase_vol'] - \
                    mm_dict['enzyme_vol']
                mm_dict_list.append(mm_dict)
                break

        for i, mm_dict in enumerate(mm_dict_list):
            pipette.pick_up_tip()
            pipette.transfer(mm_dict['water_vol'], water.bottom(),
                             reaction_plate.wells()[
                                 mm_dict['well']].bottom(0.5),
                             new_tip='never')  # Water
            pipette.blow_out()
            pipette.drop_tip()

            pipette.pick_up_tip()
            pipette.transfer(mm_dict['buffer_vol'], buffer.bottom(),
                             reaction_plate.wells()[
                                 mm_dict['well']].bottom(0.5),
                             new_tip='never')  # Water
            pipette.mix(2, 10, reaction_plate.wells()[
                mm_dict['well']].bottom(0.5))
            pipette.blow_out()
            pipette.drop_tip()

            pipette.pick_up_tip()
            pipette.transfer(mm_dict['ligase_vol'], ligase.bottom(),
                             reaction_plate.wells()[
                                 mm_dict['well']].bottom(0.5),
                             new_tip='never')  # Water
            pipette.mix(2, 10, reaction_plate.wells()[
                mm_dict['well']].bottom(0.5))
            pipette.blow_out()
            pipette.drop_tip()

            pipette.pick_up_tip()
            pipette.transfer(mm_dict['enzyme_vol'],
                             restriction_enzyme.bottom(),
                             reaction_plate.wells()[
                                 mm_dict['well']].bottom(0.5),
                             new_tip='never')  # Water
            pipette.mix(2, 10, reaction_plate.wells()[
                mm_dict['well']].bottom(0.5))
            pipette.blow_out()
            pipette.drop_tip()

        return mm_dict_list, mm_vol_per_assembly

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
                       thermocycle=False):

        num_rxns = len(combinations_to_make)

        # Load in Bio-Rad 96 Well Plate on temp deck for moclos,
        # transformation, and outgrowth.
        if thermocycle:
            tc_mod = protocol.load_module('thermocycler')
            tc_mod.open_lid()
            reaction_plate = tc_mod.load_labware(
                'biorad_96_wellplate_200ul_pcr')
            tc_mod.set_block_temperature(10)
        else:
            temp_deck = protocol.load_module('tempdeck', 10)
            reaction_plate = temp_deck.load_labware(
                'biorad_96_wellplate_200ul_pcr')
            temp_deck.set_temperature(10)

        # Load in 2 10ul tipracks and 2 300ul tipracks
        tr_10 = [protocol.load_labware('opentrons_96_tiprack_10ul', '3'),
                 protocol.load_labware('opentrons_96_tiprack_10ul', '6')]

        # Load in pipettes
        p10_single = protocol.load_instrument('p10_single',
                                              mount=pipetteMount10,
                                              tip_racks=tr_10)

        ''' Need to provide the instructions for loading reagent'''
        reagents_plate = protocol.load_labware('biorad_96_wellplate_200ul_pcr',
                                               '4', 'Reagents Plate')
        ligase = reagents_plate.wells_by_name()['H12']  # MoClo
        restriction_enzyme = reagents_plate.wells_by_name()['G12']  # MoClo
        buffer = reagents_plate.wells_by_name()['F12']  # MoClo

        '''
            This deck slot location is dedicated for the reaction plate after
            MoClo protocol is completed, so at the beginning of the protocol
            there isn't an actual plate existing in this slot location.
        '''
        #post_moclo_reaction_plate = protocol.load_labware(
            #'biorad_96_wellplate_200ul_pcr', '9', 'Post-MoClo Reaction Plate')

        # Load in water, SOC, and wash trough (USA Scientific 12 Well Reservoir
        # 22ml)
        trough = protocol.load_labware('usascientific_12_reservoir_22ml', '5',
                                       'Reagents trough')
        water = trough.wells()[0]  # Well 1
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
                'biorad_96_wellplate_200ul_pcr', '1', 'Input DNA Plate')

        no_assemblies_dict = {}
        for combinations in combinations_to_make:
            no_parts = len(combinations['parts'])
            if str(no_parts) in no_assemblies_dict.keys():
                no_assemblies_dict[str(no_parts)] += 1
            else:
                no_assemblies_dict[str(no_parts)] = 1

        wells_open_mm = list(range(95, num_rxns-2, -1))
        wells_assembly = get_combination_well_no_parts(combinations_to_make)
        for no_parts, no_assemblies in no_assemblies_dict.items():
            protocol.comment("--------------------------------------------")
            protocol.comment(
                "Creating mm for {0}-part assembly.".format(no_parts))
            protocol.comment("--------------------------------------------")
            mm_dict_list, mm_vol_per_assembly = define_master_mix(
                no_assemblies, int(no_parts), wells_open_mm, p10_single,
                reaction_plate, water, ligase, buffer,
                restriction_enzyme)
            for i in range(len(mm_dict_list)):
                wells_open_mm.pop(0)

            wells_open_assembly = wells_assembly[no_parts]
            protocol.comment("--------------------------------------------")
            protocol.comment(
                "Transferring mm for {0}-part assembly.".format(no_parts))
            protocol.comment("--------------------------------------------")
            for i, entries in enumerate(mm_dict_list):
                p10_single.pick_up_tip()
                mm_well = reagents_plate.wells()[entries['well']]
                if i == 0:
                    no_assemblies_mm = entries['no_assemblies']
                    dest_wells = wells_open_assembly[0:no_assemblies_mm-1]
                elif i == len(entries) - 1:
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

    moclo_protocol(dna_plate_map_dict, combinations_to_make, thermocycle)
