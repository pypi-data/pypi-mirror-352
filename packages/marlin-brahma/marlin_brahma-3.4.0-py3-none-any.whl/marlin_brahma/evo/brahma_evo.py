"""

BrahmA Evolution Module
=======================================
written by Rahul Tandon c/o Vixen Intelligence

"""

import os, sys, time, random, copy


#--config core import--
# sys.path.append('../')
# from configCore import *

#import root bot
from marlin_brahma.bots.bot_root import *

# import bots
from custom_bots import *


#-----------------------------MATE-----------------------------------------------


class Mate(object):
  '''
  Class to mate individuals. Static and class routines provided to mate bots. This is 
  the default version.

  Procedure:
  1. Create a child bot
  2. Combine parent DNA
  3. Add randomly chosen tradnscription DNA from parents.
  3. Return child

  '''

  def __init__(self):
    pass

  @staticmethod
  def Mate(maleBot, femaleBot):

    
    active_species = maleBot.species
    active_env = femaleBot.env
    direction = femaleBot.direction
    child_args = {'direction' : direction, 'parent' : femaleBot.name}
    botStr = eval(active_species)
    childBot = botStr(active_env, myspecies = active_species, myargs = child_args)
    
    mom_tmp = copy.deepcopy(femaleBot)
    dad_tmp = copy.deepcopy(maleBot)

    #determine number of dna strands
    import math
    numberMaleDNA = math.floor(maleBot.numberDNA)
    numberMaleDNA = max(1, numberMaleDNA)
    numberFemaleDNA = math.floor(femaleBot.numberDNA)
    numberFemaleDNA = max(1, numberFemaleDNA)

    #determine which DNA strands

    #forward or reverse

    #addDNAStrand(self, dna):
    for i in range(numberMaleDNA):
        # print (f'number genes: {len(dad_tmp.dNA)}')
        if len(dad_tmp.dNA) < 1:
          continue
        dnaTag = random.choice(list(dad_tmp.dNA.keys()))
        Mate.addDNAStrand(dad_tmp.dNA[dnaTag], childBot)
        del dad_tmp.dNA[dnaTag]

    #forward or reverse
    
    # for i in range(numberFemaleDNA):
    #     print (f'number genes: {len(mom_tmp.dNA)}')
    #     if len(mom_tmp.dNA) < 1:
    #       continue
    #     dnaTag = random.choice(list(mom_tmp.dNA.keys()))
    #     Mate.addDNAStrand(mom_tmp.dNA[dnaTag], childBot)
    #     del mom_tmp.dNA[dnaTag]

    #transcription DNA
    Mate.addTranscription(random.choice([femaleBot.transcriptionDNA,maleBot.transcriptionDNA]),  childBot)

    
   
    
    del mom_tmp
    del dad_tmp

    #return child
    return childBot

  """
  Evolutionary procedures. These can be overritten, but these are provided 
  by BrahmA in the root bot class.
  """

  @staticmethod
  def addTranscription(transcription, patient):
    '''
    Add a transcription to a child bot  (or possibkly adult)

    Arguments:
        transcription {Transcription} -- Protein transcription algorithm.

    '''
    newTanscription = copy.deepcopy(transcription)
    patient.transcriptionDNA = newTanscription
    
    return patient

  @staticmethod
  def addDNAStrand(dna, patient):
    '''Copy DNAStrand to bot

    Arguments:
        dna {[VixenDNA]} -- DNAStrand
    '''

    patient.numberDNA+=1
    newDNA = copy.deepcopy(dna)
    newDNATag = random.randint(100,100000)
    newDNA.Name = newDNATag

    patient.dNA[newDNATag] = newDNA
    patient.dNAExpression[newDNATag] = 0.0
    

    return patient

  @staticmethod
  def removeDNAStrand(patient):

    if len(patient.dNA > 1):
          #get key from dnaStrands and del from bot
        randomKey = random.choice(list(patient.dNA.keys()))
        del patient.dNA[randomKey]
        del patient.dNAExpression[randomKey]
    
    return patient
    


#--------------------------TOURNAMENT--------------------------------------------


class RootTournament(object):
  def __init__(self, generationEval = None, population = None, dataManager = None):
    self.population = population
    #ranking by name
    self.rankings = []
    #evaluations
    self.evaluations = generationEval
    #optimisation data manager

    if (len(self.population.bots) < 4):
      print ("Critical Error! Need more bots. Exiting.")
      exit()

  def Rank(self):
    pass

  def Regenerate(self):
    pass

class SimpleTournamentRegenerate(RootTournament):
  """
  A simple tournament (ranking algorithm) shipped with BrahmA for rapid develpment.s
  This class 

  :param RootTournament: [description]
  :type RootTournament: [type]
  """

  def __init__(self, generationEval = None, population = None, dataManager = None):
    super().__init__(generationEval = generationEval, population = population, dataManager = dataManager)
    if generationEval != None:
        #evaluations (EvaluateDecisions) by bot Tag
        #self.evaluations = generationEval
        #need the population data as this class will kill and create new population members
        #edited Nov 2020. Taken care in root
        #self.population = population
        #ranking by name
        #self.rankings = []
        pass

    else:
        print ("critical error initialising tournament.")
        exit()


  def Zeros(self):
    zeros = []

    for k, v in self.evaluations.items():
      if v.fitnessValue == 0.0 or v.fitnessValue == -1000:
        #we have no decisions, return
        zeros.append(k)

    number_zeros = len(zeros)
    # print (f'Number of dead wood: {number_zeros}')
    return zeros


  def RankPopulation(self, output = 0 ):

    import operator
    # print ("evaluations")
    # print (self.evaluations)
   
    rankedEvals = sorted(self.evaluations.items(), key=lambda x: x[1].fitnessValue, reverse=True)
    # print ("Ranked")
    #print (rankedEvals)
    #reset rankings
    
    self.rankings = []
    for key, value in rankedEvals:
        
        # print (f'val: {value.fitnessValue}')
        if value.fitnessValue != 0.0 or value.fitnessValue != 0:
          self.rankings.append(key)
          # print (f'{key} : {value.fitnessValue}')
          # print (f'added: {value.fitnessValue} ')
        #print (botID)
    # print (self.rankings)
    if len(self.rankings) < 5:
      self.rankings = []
      #n = len(self.rankings)
      for key, value in rankedEvals:
        #print (f'val: {value.fitnessValue}')
        self.rankings.append(key)
        #print (f'added: {value.fitnessValue} ')

    # print (self.rankings)
 

    if output == -1:
      winners = []
      for botID, value in self.evaluations.items():
        winners.append(botID)
      
      return winners


    if output == 1:
        import random

        winners = []
        unique_names = []
        for botID, value in self.evaluations.items():
            if value.fitnessValue > 0:

                uniqueName = botID + "_" + str(random.randint(10,1000000))
                unique_names.append(uniqueName)
                winners.append(botID)

            #logger.info('Optimisation: %d', generation)

        return winners
        
  def RegeneratePopulation(self):

    #select 2 parents...

    #best bot structure 1
    maleParent = self.population.species[self.rankings[0]]
    # print (f'parent : {maleParent.name}')
    #best bot structure 2
    femaleParent = self.population.species[self.rankings[1]]
    # print (f'parent : {femaleParent.name}')


    
    
    #mom_tmp = copy.deepcopy(femaleParent)
    #dad_tmp = copy.deepcopy(maleParent)
    childOne = Mate.Mate(maleParent, femaleParent)

    #best bot structure 3
    maleParent = self.population.species[self.rankings[2]]
    # print (f'parent : {maleParent.name}')
    
    #best bot structure 4
    femaleParent = self.population.species[self.rankings[3]]
    # print (f'parent : {femaleParent.name}')

    childTwo = Mate.Mate(maleParent, femaleParent)

    #kill bottom 2
    populationSize = len(self.population.species)
    #edit rankings as ranking vevtor now not as long as population  as zero decision makers removed
    deathTagOne = self.rankings[len(self.rankings)-1]
    deathTagTwo = self.rankings[len(self.rankings)-2]

    del (self.population.species[deathTagOne])
    
    self.population.bots.remove(deathTagOne)
    del (self.population.species[deathTagTwo])
    
    self.population.bots.remove(deathTagTwo)

    #add children
    self.population.species[childOne.name] = childOne
    self.population.bots.append(childOne.name)
    self.population.species[childTwo.name] = childTwo
    self.population.bots.append(childTwo.name)


    mom_tmp = None
    dad_tmp = None

#-------------------------- GENETIC SHUFFLE -------------------------------

class RootMutate(object):
    

  """
  Root Mutate Class
  =============================
  Individual (gene) mutation is taken care of the root bot class. The mutation routine
  can of course be overridden. 
  """



  def __init__(self,  population = None, config = None):
    self.population = population
    #edit nov 2020 - read directly from optimisation parameters
    self.config = config


  def mutate(self, args = {}):
    '''
    Mutate according to mutation rate.
    '''

    for indTag, ind in self.population.species.items():
        chance = random.random()
        if chance < self.config['mutation_rate']:
            #print (f'Mutating...[{indTag}]')
            ind.Mutate(args)



#========================================================================
#                 Evolve                                                =
#========================================================================
class Evolve(object):
  """
  Main callable evolve class for BrahmA
  """
  def __init__(self):
    pass

#=======================================================================


#========================================================================
#                 Evolve Data                                               =
#========================================================================
class EvolveData(object):
  """
  Main callable evolve class for BrahmA
  """
  def __init__(self):
    pass

#=======================================================================