import plateo
import plateo.containers
import plateo.tools
import pandas as pd
# import sys
import math
# sys.path.append("C:/Users/gabri/Documents/Uni/iGEM/sbol_parser_api")
# import sbolParserApiv2

'''
    Example of how to use the class BBInput:
    sbolParsedFile = sbolParserApiv2.ParserSBOL(sbolFile)
    constructPlate, partPlate, constructDf, \
        partDf = sbolParsedFile.generateCsv_for_BioBricks(listOfNonCombUris,
                                                 listOfCombUris, partFile)
    BBInput = BioBricksInput(constructPlate, partPlate, constructDf, partDf)
'''


class Plate24(plateo.Plate):
    '''
        Creates Plateo plate class with 24 wells (3 x 8)
        https://labware.opentrons.com/opentrons_24_tuberack_nest_1.5ml_snapcap/
    '''
    num_rows = 3
    num_cols = 8

    class PlateWell(plateo.Well):
        '''
            Specifies capacity of each well
            1.5 mL cap -> 1.2 mL cap for safety
        '''
        capacity = 12e-4


class BioBricksInput:

    def __init__(
        self,
        constructPlate: plateo.Plate,
        partPlate: plateo.Plate,
        constructDf: pd.DataFrame,
        partDf: pd.DataFrame,
        partConcentration: int = 500
    ):
        '''
            Initialises BioBricks class with 4 required and 1 optional input
            argument.
            constructPlate = the Plateo plate containing the construct wells
            partPlate = the Plateo plate containing the part wells
            constructDf = pandas dataframe containing information on constructs
            partDf = pandas dataframe containing information on parts including
            counts (total, upstream, downstream, and plasmid)
            partConcentration specifies part concentration in ng/uL, and by
            default is 500 ng/uL -> 1 uL of part per digest.
        '''
        self.constructPlate = constructPlate
        self.partPlate = partPlate
        self.constructDf = constructDf
        self.partDf = partDf
        self.partPerDigest = 500  # 500 ng of part per digest

        # volume in uL to transfer to digest
        self.partVolPerDigest = math.ceil(partConcentration/self.partPerDigest)

        # list of enzymes
        self.enzymes = ['EcoRI-HF', 'SpeI', 'XbaI', 'PstI']

        # Adding empty columns to parts dataframe
        self.partDf["Part concentration (ng/uL)"] = pd.Series(
            [partConcentration] * len(self.partDf.index))
        self.partDf["Volume"] = pd.Series([] * len(self.partDf.index))
        self.partDf["noDigests"] = pd.Series([] * len(self.partDf.index))

        # create reagents plate (24 wells)
        self.reagentPlate = Plate24(name='Reagent')
        # construct reagents dataframe
        self.reagentsDf = self.initialiseReagents()
        # construct digests dataframe
        self.digestDf = self.initialiseDigests()

        # converts column of well names into list
        listofConstructWells = list(self.constructDf['Well'])

        # finds empty wells in construct plate and stores as list of well names
        freeConstructPlateWells = [
            well for well in self.constructPlate.wells.keys() if well not in
            listofConstructWells]

        if len(freeConstructPlateWells) < len(self.digestDf.index):
            # More digest wells required than empty wells on construct plate
            # New 96 well plate needed
            self.digestPlate = plateo.containers.Plate96(name='Digest')
            self.availDigestWells = self.digestPlate.wells.keys()
            self.digestToStorage = False
        else:
            # Digest and construct wells can both fit on one plate
            self.digestPlate = self.constructPlate
            self.availDigestWells = freeConstructPlateWells
            self.digestToStorage = True
            self.storagePlate = plateo.containers.Plate96(name='Storage')
            self.availStorageWells = self.storagePlate.wells.keys()

        self.addPartContent()  # fill part well contents
        self.findDigestWells()  # assign well to each digest
        self.fillReagentWells()  # fill reagent well contents

        '''
            Get list of dictionaries containing information on transfers
            between wells (part wells to digest wells, reagent wells to digest
            wells, digest wells to construct wells, digest wells to storage
            wells, used if the digest wells are on the same plate as the
            construct wells, and reagent wells to construct wells):
        '''
        self.assemblyDicts = self.getAssemblyDicts()

    def intialiseReagents(self):
        '''
            Returns dataframe of reagents.
            Upstream, Downstream, Plasmid, and Ligation entries become 0s and
            1s in the dataframe, and are used to indicate true (reagent used
            for this instance) or false (reagent not used)
            True for Upstream means for example that the reagent is added to
            digests of parts inserted in the upstream position of constructs
            Based on info from NEB kit:
            https://international.neb.com/products/e0546-biobrick-assembly-kit#Product%20Information
        '''
        reagentsList = [pd.DataFrame(
            data={'Name': ['water-1'], 'Well': [], 'Upstream': [1],
                  'Downstream': [1], 'Plasmid': [1], 'Ligation': [1],
                  'TotalVol': [], 'VolPerDigest': [43 - self.partVolPerDigest],
                  'VolPerLigation': [11]}),
                        pd.DataFrame(
            data={'Name': ['EcoRI-HF'], 'Well': [], 'Upstream': [1],
                  'Downstream': [0], 'Plasmid': [1], 'Ligation': [0],
                  'TotalVol': [], 'VolPerDigest': [1],
                  'VolPerLigation': [0]}),
                        pd.DataFrame(
            data={'Name': ['SpeI'], 'Well': [], 'Upstream': [1],
                  'Downstream': [0], 'Plasmid': [0], 'Ligation': [0],
                  'TotalVol': [], 'VolPerDigest': [1],
                  'VolPerLigation': [0]}),
                        pd.DataFrame(
            data={'Name': ['XbaI'], 'Well': [], 'Upstream': [0],
                  'Downstream': [1], 'Plasmid': [0], 'Ligation': [0],
                  'TotalVol': [], 'VolPerDigest': [1],
                  'VolPerLigation': [0]}),
                        pd.DataFrame(
            data={'Name': ['PstI'], 'Well': [], 'Upstream': [0],
                  'Downstream': [1], 'Plasmid': [1], 'Ligation': [0],
                  'TotalVol': [], 'VolPerDigest': [1],
                  'VolPerLigation': [0]}),
                        pd.DataFrame(
            data={'Name': ['NEBBuffer10X'], 'Well': [], 'Upstream': [1],
                  'Downstream': [1], 'Plasmid': [1], 'Ligation': [0],
                  'TotalVol': [], 'VolPerDigest': [5],
                  'VolPerLigation': [0]}),
                        pd.DataFrame(
            data={'Name': ['T4Ligase10X'], 'Well': [], 'Upstream': [0],
                  'Downstream': [0], 'Plasmid': [0], 'Ligation': [1],
                  'TotalVol': [], 'VolPerDigest': [0],
                  'VolPerLigation': [2]}),
                        pd.DataFrame(
            data={'Name': ['T4Ligase'], 'Well': [], 'Upstream': [0],
                  'Downstream': [0], 'Plasmid': [0], 'Ligation': [1],
                  'TotalVol': [], 'VolPerDigest': [0],
                  'VolPerLigation': [1]})]

        reagentsDf = pd.concat(reagentsList, ignore_index=True)
        return reagentsDf

    def initialiseDigests(self):
        '''
            Returns dataframe of digests.
        '''
        digestsList = []
        for index, row in self.partDf.iterrows():
            # part is used in upstream position of construct
            if row['upstreamCounts'] > 0:
                # 1 digest per every 23 uses in construct, leaves 2 uL dead vol
                no = math.ceil(row['upstreamCounts']/23)
                remCounts = row['upstreamCounts']
                for i in range(no):
                    if remCounts > 23:
                        constructCounts = 23
                        remCounts = remCounts - constructCounts
                    else:
                        constructCounts = remCounts
                    digestDict = {'Name': [
                        str(row['Part/linker']) + '-upstream-' + str(i+1)],
                        'Part': [row['Part/linker']], 'Role': ['upstream'],
                        'Well': [], 'partWell': [row['Well']],
                        'noConstructs': [constructCounts]}
                    digestsList.append(pd.DataFrame.from_dict(digestDict))

            # part is used in downstream position of construct
            if row['downstreamCounts'] > 0:
                no = math.ceil(row['downstreamCounts']/23)
                remCounts = row['downstreamCounts']
                for i in range(no):
                    if remCounts > 23:
                        constructCounts = 23
                        remCounts = remCounts - constructCounts
                    else:
                        constructCounts = remCounts
                    digestDict = {'Name': [
                        str(row['Part/linker']) + '-downstream-' + str(i+1)],
                        'Part': [row['Part/linker']], 'Role': ['downstream'],
                        'Well': [], 'partWell': [row['Well']],
                        'noConstructs': [constructCounts]}
                    digestsList.append(pd.DataFrame.from_dict(digestDict))

            # part is used as plasmid in construct
            elif row['plasmidCounts'] > 0:
                no = math.ceil(row['plasmidCounts']/23)
                remCounts = row['plasmidCounts']
                for i in range(no):
                    if remCounts > 23:
                        constructCounts = 23
                        remCounts = remCounts - constructCounts
                    else:
                        constructCounts = remCounts
                    digestDict = {'Name': [
                        str(row['Part/linker']) + '-plasmid-' + str(i+1)],
                        'Part': [row['Part/linker']], 'Role': ['plasmid'],
                        'Well': [], 'partWell': [row['Well']],
                        'noConstructs': [constructCounts]}
                    digestsList.append(pd.DataFrame.from_dict(digestDict))

        digestDf = pd.concat(digestsList, ignore_index=True)
        return digestDf

    def addPartContent(self):
        '''
            Adds volume and number of digests information to parts dataframe
            and adds the content to each part well using add_content()
        '''
        noDigests = []
        partVolumes = []
        for index, row in self.partDf.iterrows():
            upstreamDigests = math.ceil(row['upstreamCounts']/23)
            downstreamDigests = math.ceil(row['downstreamCounts']/23)
            plasmidDigests = math.ceil(row['plasmidCounts']/23)
            totDigests = upstreamDigests + downstreamDigests + plasmidDigests
            noDigests.append(totDigests)
            partVol = totDigests + 2  # add 2 for dead vol
            quantity = 500*(totDigests + 2)
            partVolumes.append(partVol)
            well = self.partPlate.wells[row['Well']]
            partDef = well.data['Part']
            well.add_content({partDef: quantity}, partVol)
        self.partDf['Volume'] = partVolumes
        self.partDf['noDigests'] = noDigests

    def findDigestWells(self):
        '''
            Assigns well to each digest
        '''
        digestWells = self.availDigestWells[0:len(self.digestDf.index)-1]
        self.digestDf['Well'] = digestWells
        for index, row in self.digestDf.iterrows():
            self.digestPlate.wells[row['Well']].data = {'Digest': row['Name']}

    def newWaterWell(self, i, vol):
        '''
            Returns dataframe to be appended to reagents dataframe.
            Creates a new water well with a name 'water-i' and volume vol.
        '''
        waterDf = pd.DataFrame(
            data={'Name': ['water-' + str(i+1)], 'Well': [], 'Upstream': [1],
                  'Downstream': [1], 'Plasmid': [1], 'Ligation': [1],
                  'TotalVol': [], 'VolPerDigest': [43 - self.partVolPerDigest],
                  'VolPerLigation': [11]})
        return waterDf

    def fillReagentWells(self):
        availReagentWells = self.reagentPlate.wells.keys()
        upstreamDigests = [
            row['Name'] for index, row in self.digestDf.iterrows()
            if row['Role'] == 'upstream']
        downstreamDigests = [
            row['Name'] for index, row in self.digestDf.iterrows()
            if row['Role'] == 'downstream']
        plasmidDigests = [
            row['Name'] for index, row in self.digestDf.iterrows()
            if row['Role'] == 'plasmid']
        totalWaterVol = 42*(len(upstreamDigests) + len(downstreamDigests) +
                            len(plasmidDigests)) + 11*len(
                                self.constructDf.index)
        remWaterVol = totalWaterVol
        waterVol = []
        totalVol = []
        if totalWaterVol > 1200:
            waterVol.append(1200)
            for i in range(1, 5):
                if remWaterVol > 1200:
                    waterVol.append(1200)
                    remWaterVol = remWaterVol - 1200
                    newWaterDf = self.newWaterWell(i, 1200)
                    self.reagentsDf.append(newWaterDf)
                elif remWaterVol > 0:
                    waterVol.append(remWaterVol)
                    newWaterDf = self.newWaterWell(i, remWaterVol)
                    self.reagentsDf.append(newWaterDf)
                    remWaterVol = 0
                else:
                    break
        else:
            waterVol.append(totalWaterVol)

        reagentWells = availReagentWells[0:len(self.reagentsDf.index)]
        self.reagentsDf['Well'] = reagentWells

        for index, row in self.reagentsDf.iterrows():
            if row['Name'][0:4] == 'water':
                totVol = waterVol[int(row['Name'][6]) - 1]
            else:
                digestCounts = upstreamDigests*row['Upstream'] + \
                    downstreamDigests*row['Downstream'] + \
                    plasmidDigests*row['Plasmid']
                totVol = 0
                if digestCounts > 0:
                    digestVol = (digestCounts + 2)*row['VolPerDigest']
                    totVol += digestVol
                ligationCounts = row['Ligation']*len(self.constructDf.index)
                if ligationCounts > 0:
                    ligationVol = (ligationCounts + 2)*row['VolPerLigation']
                    totVol += ligationVol
            well = self.reagentPlate.wells[row['Well']]
            well.data = {'Reagent': row['Name']}

            # add content, treating concentration as 1 unit
            well.add_content({row['Name']: totVol}, totVol)
            totalVol.append(totVol)

        self.reagentsDf['TotalVol'] = totalVol

    def assemblyDigestDicts(self, waterWellVol, waterWellNo):

        '''
            Returns all assembly dictionaries except reagentToConstruct
            Called by getAssemblyDicts()
            Also returns waterWellVol and waterWellNo
            waterWellNo = the current water well used as a source
            waterWellVol = the volume taken from the current
            water well
        '''

        # dictionaries
        sourceToDigest = {}
        reagentToDigest = {}
        digestToStorage = {}
        digestToConstruct = {}

        # find enzyme wells
        EcoRIHFindx = self.reagentsDf[self.reagentsDf['Name'] == 'EcoRI-HF'
                                      ].index.values[0]
        EcoRIHFwell = self.reagentsDf['Well'][EcoRIHFindx]
        PstIindx = self.reagentsDf[self.reagentsDf['Name'] == 'PstI'
                                   ].index.values[0]
        PstIwell = self.reagentsDf['Well'][PstIindx]
        XbaIindx = self.reagentsDf[self.reagentsDf['Name'] == 'XbaI'
                                   ].index.values[0]
        XbaIwell = self.reagentsDf['Well'][XbaIindx]
        SpeIindx = self.reagentsDf[
            self.reagentsDf['Name'] == 'SpeI'].index.values[0]
        SpeIwell = self.reagentsDf['Well'][SpeIindx]

        # iterate through each row of digest dataframe
        for index, row in self.digestDf.iterrows():
            sourceWell = row['partWell']
            if sourceWell in sourceToDigest.keys():
                sourceToDigest[sourceWell].append(
                    [row['Well'], self.partVolPerDigest])
            else:
                sourceToDigest[sourceWell] = [
                    [row['Well'], self.partVolPerDigest]]

            if row['Role'] == 'upstream':
                if EcoRIHFwell not in reagentToDigest.keys():
                    reagentToDigest[EcoRIHFwell] = [[row['Well'], 1]]
                else:
                    reagentToDigest[EcoRIHFwell].append([row['Well'], 1])

                if SpeIwell not in reagentToDigest.keys():
                    reagentToDigest[SpeIwell] = [[row['Well'], 1]]
                else:
                    reagentToDigest[SpeIwell].append([row['Well'], 1])

            elif row['Role'] == 'downstream':
                if XbaIwell not in reagentToDigest.keys():
                    reagentToDigest[XbaIwell] = [[row['Well'], 1]]
                else:
                    reagentToDigest[XbaIwell].append([row['Well'], 1])

                if PstIwell not in reagentToDigest.keys():
                    reagentToDigest[PstIwell] = [[row['Well'], 1]]
                else:
                    reagentToDigest[PstIwell].append([row['Well'], 1])

            elif row['Role'] == 'plasmid':
                if EcoRIHFwell not in reagentToDigest.keys():
                    reagentToDigest[EcoRIHFwell] = [[row['Well'], 1]]
                else:
                    reagentToDigest[EcoRIHFwell].append([row['Well'], 1])

                if PstIwell not in reagentToDigest.keys():
                    reagentToDigest[PstIwell] = [[row['Well'], 1]]
                else:
                    reagentToDigest[PstIwell].append([row['Well'], 1])

            waterWellVol += 42
            if waterWellVol > 1000:
                waterWellNo += 1
                waterWellVol = 42
                waterWellName = 'water-' + str(waterWellNo)
                wellIndx = self.reagentsDf[
                    self.reagentsDf['Name'] == waterWellName].index.values[0]
                waterWell = self.reagentsDf['Well'][wellIndx]
                if waterWell not in reagentToDigest.keys():
                    reagentToDigest[waterWell] = [[row['Well'], 42]]
                else:
                    reagentToDigest[waterWell].append([row['Well'], 42])
            NEBindx = self.reagentsDf[
                    self.reagentsDf['Name'] == 'NEBBuffer10x'].index.values[0]
            NEBWell = self.reagentsDf['Well'][NEBindx]
            if NEBWell not in reagentToDigest.keys():
                reagentToDigest[NEBWell] = [[row['Well'], 5]]
            else:
                reagentToDigest[NEBWell].append([row['Well'], 5])

            if row['Role'] == 'upstream':
                constructWellIndices = self.constructDf[
                    self.constructDf['upstream'] == row['Part']].index.values
            elif row['Role'] == 'downstream':
                constructWellIndices = self.constructDf[
                    self.constructDf['downstream'] == row['Part']].index.values
            else:
                constructWellIndices = self.constructDf[
                    self.constructDf['plasmid'] == row['Part']].index.values
            constructWells = self.constructDf['Well'][constructWellIndices]
            digestToConstruct[row['Well']] = [
                [constructWell, 2] for constructWell in constructWells]

            if self.digestToStorage:
                storageVol = 50 - row['noConstructs']*2
                digestToStorage[row['Well']] = [[
                    self.availStorageWells[index], storageVol]]

        if self.digestToStorage:
            return sourceToDigest, reagentToDigest, digestToConstruct, \
                digestToStorage, waterWellVol, waterWellNo
        else:
            return sourceToDigest, reagentToDigest, digestToConstruct, \
                waterWellVol, waterWellNo

    def getAssemblyDicts(self):
        '''
            Outputs a list of dictionaries directing well transfers.
            All dictionaries are in the format of key = source well,
            value = list of destination wells in form [destination well,
            volume to transfer]
            sourceToDigest: keys = part wells, dest = digest wells
            reagentToDigest: keys = reagent wells, dest = digest wells
            digestToConstruct: keys = digest wells, dest = construct wells
            digestToStorage: only used if the digest wells are on the
            same plate as the construct wells; for saving excess digests
            in a plate separate from the construct plate;
            keys = digest wells, dest = construct wells
            reagentToConstruct: keys = reagent wells, dest = construct wells
        '''
        reagentToConstruct = {}
        waterWellVol = 0
        waterWellNo = 1

        if self.digestToStorage:
            sourceToDigest, reagentToDigest, digestToConstruct, \
                digestToStorage, waterWellVolNew, \
                waterWellNoNew = self.assemblyDigestDicts(
                    waterWellVol, waterWellNo)
        else:
            sourceToDigest, reagentToDigest, digestToConstruct, \
                waterWellVolNew, waterWellNoNew = self.assemblyDigestDicts(
                    waterWellVol, waterWellNo)

        waterWellNo = waterWellNoNew
        waterWellVol = waterWellVolNew

        for index, row in self.constructDf.iterrows():
            waterWellVol += 11
            if waterWellVol > 1000:
                waterWellNo += 1
                waterWellVol = 11
                waterWellName = 'water-' + str(waterWellNo)
                wellIndx = self.reagentsDf[
                    self.reagentsDf['Name'] == waterWellName].index.values[0]
                waterWell = self.reagentsDf['Well'][wellIndx]
                if waterWell not in reagentToDigest.keys():
                    reagentToConstruct[waterWell] = [[row['Well'], 11]]
                else:
                    reagentToConstruct[waterWell].append([row['Well'], 11])
            T4Ligaseindx = self.reagentsDf[
                    self.reagentsDf['Name'] == 'T4Ligase'].index.values[0]
            T4LigaseWell = self.reagentsDf['Well'][T4Ligaseindx]
            if T4LigaseWell not in reagentToConstruct.keys():
                reagentToConstruct[T4LigaseWell] = [[row['Well'], 1]]
            else:
                reagentToConstruct[T4LigaseWell].append([row['Well'], 1])
            T4Ligase10Xindx = self.reagentsDf[
                    self.reagentsDf['Name'] == 'T4Ligase10X'].index.values[0]
            T4Ligase10XWell = self.reagentsDf['Well'][T4Ligase10Xindx]
            if T4Ligase10XWell not in reagentToConstruct.keys():
                reagentToConstruct[T4Ligase10XWell] = [[row['Well'], 2]]
            else:
                reagentToConstruct[T4Ligase10XWell].append([row['Well'], 2])

        if self.digestToStorage:
            assemblyDicts = [
                sourceToDigest, reagentToDigest, digestToConstruct,
                digestToStorage, reagentToConstruct]
        else:
            assemblyDicts = [
                sourceToDigest, reagentToDigest, digestToConstruct,
                reagentToConstruct]

        return assemblyDicts
