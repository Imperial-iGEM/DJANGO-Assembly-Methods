from opentrons import protocol_api

metadata = {'apiLevel': '2.2',
            'protocolName': 'Thermocycle template (optional)',
            'author': 'Gabrielle Johnston',
            'description': 'Optional thermocycle template for after clip'}


def run(protocol: protocol_api.ProtocolContext):

    def thermocycler(well_plate_type='biorad_96_wellplate_200ul_pcr'):

        protocol.comment('Insert the thermocycler module to the opentrons.')
        protocol.comment(
            'Place the clip reaction plate in the opentrons module')
        tc_mod = protocol.load_module('thermocycler')
        tc_mod.open_lid()
        clip_plate = tc_mod.load_labware(well_plate_type)

        tc_mod.close_lid()
        profile1 = [
            {'temperature': 37, 'hold_time_seconds': 120},
            {'temperature': 20, 'hold_time_seconds': 60}]
        profile2 = [
            {'temperature': 50, 'hold_time_seconds': 300},
            {'temperature': 80, 'hold_time_seconds': 1200}]

        tc_mod.execute_profile(steps=profile1, repetitions=20)
        tc_mod.execute_profile(steps=profile2, repetitions=1)
        tc_mod.open_lid()
        protocol.comment(
            'Remove the clip reaction plate and proceed with purification.')
        tc_mod.deactivate()

    thermocycler(well_plate_type=well_plate_type)
