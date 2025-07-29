import os, sys
from marlin_brahma.genes import *

# this must be defined in application calling library
from custom_genes import *
import logging

modulename = 'custom_genes'
    #print (sys.path)
if modulename not in sys.modules:
    print('You have not imported the {} module'.format(modulename))
    


class VixenGenome(object):

    """
    Genome for Vixen's DNA. The genome, located within the DNA structure, 
    defines the genes within the individual. Each gene interacts with the data vector
    of discretised environmental conditions and will ultimately adopt an on/off state.
    These differing states will provide an excitement level/expression for the genome
    in which they sit. The expression level (e) of the genome will satisfy {0 < e < 1}
    
    IMPORTANT: Genomes within the same DNA structure will all recieve the same 
    size vector of data and resident genes must be able to adopt a state with any 
    given data vector sizes. 

    This 'VixenGenome' is considered the root of all genome structures. Genomes must be
    able to,  at the very minimum, build & express the genome.
    
    Arguments:
        object {[type]} -- [description]

    Returns:
        [type] -- [description]
    """
   

    def __init__(self, minSize=1, maxSize=1, envName="undef", genomeType="", gene_args = None):
        """
        Creates a genome structure

        Args:
            minSize (int, optional): min number of genes. Defaults to 1.
            maxSize (int, optional): max number of genes. Defaults to 1.
            envName (str, optional): name of environment. Defaults to "test".
            genomeType (str, optional): [description]. Defaults to "".
        """
        import random
        logging.debug(f'genome init')
        self.expressionLevel = 0    #expression level of the genome
        self.genomeSize=random.randint(int(minSize), int(maxSize)) #number of genes in the genome
        self.envName = envName #environment within which the genome interacts {e.g. EURUSD}
        self.genomeTag = "genome" + str(random.randint(100, 10000)) #unique id of the genome
        self.genome = {} #hashtag of all genes in the genome
        self.genomeExpression = {} #expression of gene tagged by geneID
        self.geneticSelectionDict = {} #dict of gene types from which to select TODO: apply number contraints
        self.gene_args = gene_args
        #nov 2020
        
        self.riskGeneticSelectionDict = {} #dict of risk genes from which to select 
        self.genomeType = genomeType  #type of genome { normal, risk }  NOTE: will depracate soon  
        logging.debug(f'genome init end')

        #self.logger = GetBrahmaLogger("GENOME")


    def __str__(self):
        """
        Override print method for description of Genome and all genes ( or conditions )

        Returns:
            string: Description of genome (can be used in logging / debugging)
        """
        returnStr = ""
        returnStr += ("Tag: {2} Size: {0} ; Environment {1}".format(self.genomeSize, self.envName, self.genomeTag)) + "\n"
        returnStr += "*************** DETAILS ************ \n"

        for geneTag, gene in self.genome.items():
            returnStr += ("Tag: {0} Type: {1}".format(gene.i_D, gene.condition)) + "\n"

        return returnStr

    def __exit__(self):
        del self.logger
    
    def Reset(self):
        for geneTag, gene in self.genome.items():
            gene.Reset()    
    
    def GetMemory(self):
        
        max_memory = -1
        for geneTag, gene in self.genome.items():
            memory = gene.GetMemory()  
            # print (memory)  
            max_memory = max(memory,0)
           
        # print (max_memory) 
        return max_memory
    
    def BuildGenome(self):
        
        """
        Build a genome >
        >. determine type of genome
        >. build a selection vector of available genes
        >. build and attach the genes to the genome.
        """
        
        counter = {}

        if self.genomeType=="risk":
            
            
            # self.logger.info("Building Risk Genome - Gene count: {0}".format(self.genomeSize))
            # #build list of avilable risk genes
            self.BuildRiskGeneSelectionDict()
            
            for geneCnt in range(0, self.genomeSize):
            #for geneCnt in range(0, 1):

                
                
                geneType = self.SelectRiskGeneFromSelectionDict()
                print (f'gene {geneType}')
                # logger.info("Risk gene selected: {0}".format(geneType))
                geneStructureTmp = self.BuildGeneStructure(geneType, self.riskGeneticSelectionDict)
                self.genome[geneStructureTmp.i_D] = geneStructureTmp
                #self.logger.info("Gene built: {0}".format(geneType))
                #attach to genome
                #kill tmp structure
                geneStructureTmp = None
                



            return
       
        logging.debug(f'building genome inside')
       
        #self.logger.info("Building Normal Genome - Gene count: {0}".format(self.genomeSize))
        self.BuildGeneSelectionDict()
        logging.debug(f'gene dictionary built')
        #print (self.geneticSelectionDict)
        for geneCnt in range(0, self.genomeSize):
            #select
            valid_gene = False
            while not valid_gene:
                geneType = self.SelectGeneFromSelectionDict()
                # print (self.gene_args)
                # print (geneType)
                if geneType in counter:
                    if counter[geneType] < self.gene_args[geneType]:
                        valid_gene = True
                        counter[geneType] += 1
                else:
                    if self.gene_args[geneType] != 0:
                        counter[geneType] = 1
                        valid_gene = True
                    
            
            
            logging.debug("Normal gene selected: {0}".format(geneType))

            #build & get tagID
            # print (self.gene_args)
            geneStructureTmp = self.BuildGeneStructure(geneType,  self.geneticSelectionDict, gene_args=self.gene_args)
            #self.logger.info("Gene built: {0}".format(geneType))
            #attach to genome
            #print (f'gene added : {geneType}')
            self.genome[geneStructureTmp.i_D] = geneStructureTmp
            #kill tmp structure
            geneStructureTmp = None
            

        return

    def BuildRiskGeneSelectionDict(self):

        import os
        genetic_material_folder  = os.getenv('GENETIC_DATA_FOLDER_USR')
        geneFileList = os.listdir(genetic_material_folder)
        for fileName in geneFileList:
            #print (fileName)
            if fileName.endswith('.py'):
                fnArray = fileName.split('.')
                geneType = fnArray[0]
                if geneType != "dnaroot":
                    prefix = geneType.split('_')
                    prefixStr = prefix[0]
                    if prefixStr == "risk":
                        geneName = prefix[1]
                        #print (geneName)
                        #.info("Adding Gene to Selection: {0}".format(geneName))
                        self.riskGeneticSelectionDict[geneName] = eval(geneName)

    def SelectRiskGeneFromSelectionDict(self):
        import random
        
        try:
            #self.logger.debug("Trying to grab a random risk gene tag.")
            randomGeneTag = random.choice(list(self.riskGeneticSelectionDict))
            #self.logger.debug("Random gene tag: {0}".format(randomGeneTag))
            #print 
            return randomGeneTag

        except Exception as e:
            #self.logger.critical("type error: " + str(e))
            #self.logger.critical(traceback.format_exc())
            #self.logger.critical("Error selecting risk gene")
            print (e)
            exit(0)
        return -1

    def BuildGeneSelectionDict(self):
        """Build gene type selection lists
        """


        import os
        #local genes loaded {todo: custom genes}
        #geneFileList = os.listdir(BRAHMA_GENETIC_DATA_FOLDER_LCL)
        #edit
        
        genetic_material_folder  = os.getenv('GENETIC_DATA_FOLDER_USR')
        logging.debug(f'{genetic_material_folder}')
        geneFileList = os.listdir(genetic_material_folder)
        logging.debug(f'{geneFileList}')
        for fileName in geneFileList:
            
            if fileName.endswith('.py'):
                
                fnArray = fileName.split('.')
                geneType = fnArray[0]
                if geneType != "dnaroot":
                    
                    prefix = geneType.split('_')
                    prefixStr = prefix[0]
                    
                    if prefixStr == "g":
                        geneName = prefix[1]
                        
                        # logger.debug("Adding Gene to Selection: {0}".format(geneName))
                        self.geneticSelectionDict[geneName] = eval(f'{geneName}')
        
        
                    
    def SelectGeneFromSelectionDict(self):
        """Select a genetype from the list
        and return to caller
        """
        import random
        try:
            #self.logger.debug("Trying to grab a random gene tag.")
            
            randomGeneTag = random.choice(list(self.geneticSelectionDict))
            #self.logger.debug("Random gene tag: {0}".format(randomGeneTag))
            
            return randomGeneTag

        except Exception as e:
            
            #self.logger.critical("Error selecting gene")
            exit(-1)
        return -1

    def BuildGeneStructure(self, gene_type = "", classCollection=None, gene_args = {}):
        if gene_type != "":
            pass
        else:
            #self.logger.critical("No genetic material found for gene_type: {0}".format(gene_type))
            exit("No genetic material")

        
        
        tmpGene = None
        #self.logger.debug("attempting to create gene from new selection approach: {0}".format(gene_type))
        try:
            #print (gene_type)
            #print (self.geneticSelectionDict)
            #tmpGene = self.geneticSelectionDict[gene_type]("test")
            #'test' being passed as env changed  feb '21
            # print ("***")
            # print (classCollection)
            gene_args_pass = gene_args
            tmpGene = classCollection[gene_type](self.envName, gene_args=gene_args_pass)
            # print ("---")
            # print (f'temp : {tmpGene}')
        except Exception as e:
            #self.logger.critical("Attempting to create gene from new selection approach: FAIL")
            
            exit(0)

        return tmpGene

        ''' lets get rid of this...
        if gene_type == "direction_negative_alpha":
            tmpGene = DirectionNegativeAlpha(mkt=self.envName)

        if gene_type == "direction_positive_alpha":
            tmpGene = DirectionPositiveAlpha(mkt=self.envName)

        if gene_type == "down_fractal_present":
            tmpGene = DownFractalPresent(mkt=self.envName)

        if gene_type == "up_fractal_present":
            tmpGene = UpFractalPresent(mkt=self.Market)

        if gene_type == "risk_alpha":
            tmpGene =  RiskGeneAlpha(mkt=self.Market)

        if gene_type == "risk_beta":
            tmpGene =  RiskGeneBeta(mkt=self.Market)
        '''



       

    def express(self ,data):
        """[summary]

        :param data: [description]
        :type data: [type]
        :return: [description]
        :rtype: [type]
        """
        expressSum = 0
        
      

        for geneTag, gene in self.genome.items():
            
            #get express value
            expression = 0
            
            expression = gene.run(data)
            
            self.genomeExpression[geneTag] = expression
           
            expressSum = expressSum + expression
           
        



     
        #edit expression -> expressSunm Nov 2020
        if expressSum != 0:
            self.ExpressionLevel = float(expressSum/self.genomeSize)

          
        else:
            self.ExpressionLevel = 0

      
        return self.ExpressionLevel




    def print_genome_expression(self):
        for geneTag, expressionVal in self.genomeExpression.items():
            print ("Gene Tag: {0} ; GeneExpression {1}".format(geneTag, expressionVal))
    def get_structure(self):
        structure = {}
        genome_structure = {}
        genome_structure['numberGenes'] = self.genomeSize
        gene_structures = {}
        for geneTag, gene in self.genome.items():
            pt_structures = {}
            pt_structures['condition'] = gene.condition
            pt_structures['id'] = gene.i_D
            pt_structures['dob'] = gene.DOB
            pt_structures['data'] = gene.__str__()
            gene_structures[geneTag] = pt_structures

        structure['genome_meta'] = genome_structure
        structure['genes'] = gene_structures

        return structure

