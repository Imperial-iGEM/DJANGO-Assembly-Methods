# /**
#  * @author Olivia Gallupová
#  * @email olivia.gallupova@gmail.com
#  * @create date 2020-08-15 12:12:36
#  * @modify date 2020-08-15 12:12:36
#  * @desc [Transformation protocol for BioBrick assembly
#  as described in Method 3.1 "DNA Cloning and Assembly Methods" by
#  Svein Valla, Rahmi Lale.]
#  */
from opentrons import protocol_api, labware, instruments, modules, robot
from typing import List


import opentrons
print(opentrons.__version__)


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
DESTINATION_PLATE_POSITION = '5'
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
        source_plate = protocol.load_labware(SOURCE_PLATE_TYPE, SOURCE_PLATE_POSITION)
        dest_plate = protocol.load_labware(DESTINATION_PLATE_TYPE, DESTINATION_PLATE_POSITION)
        tube_rack = protocol.load_labware(TUBE_RACK_TYPE, TUBE_RACK_POSITION)
        tip_rack = protocol.load_labware(TIPRACK_TYPE, CANDIDATE_TIPRACK_SLOT)
        pipette = protocol.load_instrument(PIPETTE_TYPE, PIPETTE_MOUNT,
                                           tip_racks=[tip_rack])

        # Calculate vols
        num_dna_parts = len(target_wells['cells'])
        total_cell_volume = sum(source_wells['cells'][i][1] for i in range(len(source_wells['cells'])))
        target_cell_vol = total_cell_volume / num_dna_parts
        """ Volume of target wells that the source competent cells will be transfered into.
        The cells in the source will be treated as one well for pipetting and split volumes when
        one container would become empty. """
        ## Same for control cells
        total_ctrl_volume = sum(source_wells['control_cells'][i][1] for i in range(len(source_wells['control_cells'])))
        target_ctrl_vol = total_ctrl_volume / len(target_wells['control_cells'])

        def transfer_cells(source_wells: List[List],
                           target_wells: List,
                           target_vol: int,
                           cell_vol_transfered: int,
                           idx_current_cells: int,
                           idx_target_wells: int) -> (int, int):
            """ Helper function to transfer 'cells' from 1 source well to
            target wells 
            Args:
                idx_target_wells: index to target_wells """

            would_empty_cells = ((cell_vol_transfered+target_cell_vol) >= source_wells[idx_current_cells][1])
            vol_remaining_cells = source_wells[idx_current_cells][1] - cell_vol_transfered+target_cell_vol

            # Distribute source cells into wells
            target_well = dest_plate.wells_by_name()[target_wells[idx_target_wells]] #
            if (vol_remaining_cells < target_cell_vol) or would_empty_cells:  # full volume across cells
                source_well = source_plate.wells_by_name()[source_wells[idx_current_cells][0]]
                pipette.transfer(vol_remaining_cells,
                                 source_well,  # well name
                                 target_well,
                                 new_tip='never')
                cell_vol_transfered += vol_remaining_cells

                idx_current_cells += 1
                source_well = source_plate.wells_by_name()[source_wells[idx_current_cells][0]]
                vol_to_transfer = target_cell_vol - vol_remaining_cells
                pipette.transfer(vol_to_transfer,
                                 source_well,
                                 target_well, 
                                 new_tip='never')
                cell_vol_transfered += vol_to_transfer
            else:  # pipetting full volume from same cell
                source_well = source_plate.wells_by_name()[source_wells[idx_current_cells][0]]
                pipette.transfer(target_cell_vol,
                                 source_well,
                                 target_well,
                                 new_tip='never')
                cell_vol_transfered += target_cell_vol

            return cell_vol_transfered, idx_current_cells

        '''
            Transfer DNA to competent cells
        '''
        cell_vol_transfered = 0
        idx_current_cells = 0  # index for the wells of the current cells
        for i_cell, _ in enumerate(target_wells['cells']):

            # Distribute source cells into wells
            pipette.pick_up_tip()
            cell_vol_transfered, idx_current_cells = transfer_cells(source_wells['cells'],
                                                                    target_wells['cells'],
                                                                    target_cell_vol,
                                                                    cell_vol_transfered,
                                                                    idx_current_cells,
                                                                    i_cell)

            # Put specific DNA part into well with cells
            pipette.transfer(DNA_VOL,
                             source_wells['cells'][idx_current_cells][0],
                             target_wells['cells'][i_cell])

            pipette.drop_tip()
                             

        '''
            Transfer dH2O to control competent cells
        '''
        ctrl_vol_transfered = 0
        idx_current_ctrl = 0
        for i_ctrl, _ in enumerate(target_wells['control_cells']):
            # Distribute source cells into wells
            ctrl_vol_transfered, idx_current_ctrl = transfer_cells(source_wells['cells'],
                                                                   target_wells['control_cells'],
                                                                   target_ctrl_vol,
                                                                   ctrl_vol_transfered,
                                                                   idx_current_ctrl,
                                                                   i_ctrl)

        print(protocol.deck)

    # "main"
    run_robot_inits(protocol)
    bb_transform(source_wells, target_wells)


# Test
# protocol = protocol_api.ProtocolContext()
# run(protocol)