# /**
#  * @author Olivia Gallupová
#  * @email olivia.gallupova@gmail.com
#  * @create date 2020-08-15 12:12:36
#  * @modify date 2020-08-15 12:12:36
#  * @desc [Transformation protocol for BioBrick assembly
#  as described in Method 3.1 "DNA Cloning and Assembly Methods" by 
#  Svein Valla, Rahmi Lale.]
#  */
from opentrons import protocol_api


""" Location of reagents and volumes in slot SOURCE_PLATE_POSITION """
source_wells = {'cells': [['A1', 500], ['A3', 200]],
                'control_cells': [['A2', 500]],
                'dna': [['B1', 500]],
                'dH2O': [['A3', 500]]}

""" Target location of reagents and volumes in slot SOURCE_PLATE_POSITION """
target_wells = {'cells': ['A1', 'B2', 'B3', 'C4'],
                'control_cells': ['A2', 'B4', 'C5']}


## Constants
### Labware constants
PIPETTE_TYPE = 'p10_single'
PIPETTE_MOUNT = 'right'
DESTINATION_PLATE_TYPE = 'biorad_96_wellplate_200ul_pcr'
SOURCE_PLATE_TYPE = 'biorad_96_wellplate_200ul_pcr'
TIPRACK_TYPE = 'opentrons_96_tiprack_10ul'
TUBE_RACK_TYPE = 'opentrons_24_tuberack_nest_1.5ml_snapcap'

### Plate position constants
CANDIDATE_TIPRACK_SLOT = '3'
SOURCE_PLATE_POSITION = '2'
TUBE_RACK_POSITION = '4'

### Reagent constants
DNA_VOL = 1  # 1 microL

PART_AMOUNT = 500  # 500 ng
FILL_VOL = 50
NEB_BUFFER_10X_VOL = 5
PLASMID_ENZYMES = ['EcoRI-HF', 'PstI']
DIGEST_COMB_VOL = 2
T4_LIGASE_VOL = 1
T4_LIGASE_VOL_10X = 2
WATER_VOL_LIG = 11


def run(protocol: protocol_api.ProtocolContext):

    def run_robot_inits(protocol: protocol_api.ProtocolContext):
        protocol.home()

    def bb_transform(source, target):

        # load labware
        source_plate = protocol.load_labware(SOURCE_PLATE_TYPE,
                                             SOURCE_PLATE_POSITION)
        tube_rack = protocol.load_labware(TUBE_RACK_TYPE, TUBE_RACK_POSITION)
        tip_rack = protocol.load_labware(TIPRACK_TYPE, CANDIDATE_TIPRACK_SLOT)
        pipette = protocol.load_instrument(PIPETTE_TYPE, PIPETTE_MOUNT,
                                           tip_racks=[tip_rack])

        # Calculate vols
        target_cell_vol = total_cell_volume / num_dna_parts
        """ Volume of target wells that the source competent cells will be transfered into """

        # Transfer DNA to competent cells
        cell_vol_transfered = 0
        idx_current_cells = 0  # index for the wells of the current cells
        for i, cell in enumerate(target_wells['cells']):
            # Distribute source cells into wells
            is_empty_cells = ((cell_vol_transfered+target_cell_vol) >= source_wells['cells'][idx_current_cells][1])
            vol_remaining_cells = source_wells['cells'][idx_current_cells][1] - cell_vol_transfered+target_cell_vol
            if vol_remaining_cells > target_cell_vol:
            if is_empty_cells:
                pipette.transfer(target_cell_vol,
                                 source_wells['cells'][idx_current_cells][0],
                                 target_wells['cells'][i])
                cell_vol_transfered += target_cell_vol
            else:
                idx_current_cells += 1

                pipette.transfer(target_cell_vol,
                                 source_wells['cells'][idx_current_cells][0],
                                 target_wells['cells'][i])
                cell_vol_transfered += target_cell_vol

            # Put specific DNA part into well with cells
            pipette.transfer(DNA_VOL,
                             source_wells['dna'][0],
                             target_wells['cells'][i])
        
        # Controls: Transfer dH2O to control competent cells
        for i, cell in enumerate(target_wells['control_cells']):
            # Distribute source cells into wells
            pipette.transfer(target_cell_vol,
                             source_wells['cells'][0],
                             target_wells['control_cells'][i])

        # Calculate volumes
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


    # "main"
    run_robot_inits(protocol)                                       

