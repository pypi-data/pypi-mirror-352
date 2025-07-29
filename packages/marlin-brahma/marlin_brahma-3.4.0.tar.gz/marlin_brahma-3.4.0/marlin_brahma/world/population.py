"""Population class for evolutionary algorithms
"""
import json, requests
import logging
from tqdm import tqdm as tq
import os, sys, random, pkgutil, math
logging.basicConfig(level=logging.CRITICAL)
#insert root dir into system path for python
#config core
# sys.path.append('../')
# from configCore import *

#import root bot
from marlin_brahma.bots.bot_root import *

# import bots
from custom_bots import *
# from custom_genes import *

import os


class Population(object):
    """
    Population is the container object for all bots/indis in the game/optimisation run.
    
    Arguments:
        object {root object} -- object class
    """

    def __init__(self, parms=None, name="vx_dm", gene_args = None, version="1_0_0"):
       
        # tb = testBot()
        """
        Create the Population class. This class holds all bots in the game.

        :param parms: optimisation parameters - from config file but passed through for now, defaults to None
        :type parms: key/value pairs, optional
        :param name: name root, defaults to "vx_dm"
        :type name: str, optional
        """

        
        
        self.name = name + str(random.randint(10,10000))
        self.parms = parms
        self.feature_version = version
        #bot names in list
        self.bots = []
        #species structure tagged by name
        self.species = {}
        #logger

        #self.logger = GetBrahmaLogger("Population")
        self.gene_args = gene_args
    def __exit__(self):
        del self.logger

    #edit march
    #kill bots not making decisions -> 0 fitness
    
    def KillDeadWood(self, tags = []):
        number = len(tags)
        splice_number = math.floor(number/2)
        for tag in tags[0:splice_number]:
            if tag in self.species:
                del (self.species[tag])
                self.bots.remove(tag)
   
    #edit march
    def Repopulate(self, species = "BotRoot", args = None):
        population_size = len(self.species)
        delta = self.parms['population_size'] - population_size
        
        for i in range(delta):
            self.CreateBot(species = species, args = args) 
            
        for i in range(2):
            self.CreateBot(species = species, args = args) 
           
        
    def Populate(self, species = "BotRoot", args = None):
        logging.debug('Building inside brahma pop ')
        if globals().get("AcousticBot") is not None:
            print ("We have bot creation dust! ")
            
       
        import pickle
        import os
        
        if args == None:
            # print ("new bots")
            if species != "tribal":
                # if DEBUG:
                #     print ("Size: " + str(self.parms['population_size']))
                # print ("Size: " + str(self.parms['population_size']))
                population_size = self.parms['population_size']
                print (self.gene_args)
                for i in tq(range(0, int(self.parms['population_size']))):
                    
                    logging.debug(f'building {i} of {population_size}')
                    self.CreateBot(species = species, args = args)   
                    logging.debug(f'built {i} of {population_size}')
                    
            else:

                self.CreateBot(species = species, args = args)

            
            # print ("populated")
            # self.logger(self.show())
            #self.Show()
            
            
            
            
            
            
        if args=="Living":
            
            BOT_SAVE_FOLDER = os.path.join(os.path.expanduser('~'), 'dev', 'app', 'tutorial-make-decisions', 'saved', '')
            # load all traders in bin folder
            listOfFiles = os.listdir(BOT_SAVE_FOLDER)
            
            for i in range(0, int(self.parms['population_size'])):
                
                #load saved bots
                filename = random.choice(listOfFiles)
                
                #pop from list
                indx = listOfFiles.index(filename)
                listOfFiles.pop(indx)
                
                try:
                    print (BOT_SAVE_FOLDER + filename)
                    pkl_binary = open(BOT_SAVE_FOLDER + filename , 'rb')
                   
                except:
                    print ("warning, bot not found")
                    exit()
                    continue
            
                try:
                    _bot = pickle.load(pkl_binary)
                    self.ResetTrader(_bot)
                    self.bots.append(_bot.name)
                    self.species[_bot.name] = _bot
                except Exception as e:
                    print (e)
                    
                
                # print (_bot.name)
                # print (_bot)
                
                
                    
    def ResetTrader(self,  trader):
        for dnaTag, dna in trader.dNA.items():
            dna.expressionTable = {}
            

    def test(self):
        pass


    # def LoadBot():
        

    def CreateBot(self, species = None, args = None):
        self.botStr = {}
        self.botStr[species] = eval(species)
        
        logging.debug(f'creating bot')
        #build the bot here - general
        
        bot_tmp = self.botStr[species](self.parms["env"], myspecies = species, myargs = args, version=self.feature_version)
        logging.debug(f'tmp bot build')
        bot_tmp.BuildBot(parms=self.parms, gene_args = self.gene_args)
        logging.debug(f'tmp bot build 2')
        #bot_tmp.printAll()
        self.bots.append(bot_tmp.name)
        self.species[bot_tmp.name] = bot_tmp
        
        '''
        print ("Building.. " + species)
        bot_tmp = trader_template(self.Parms['market'])
        bot_tmp.build_trader(parms=self.Parms)
        self.Bots.append(bot_tmp.Name)
        self.Species[bot_tmp.Name] = bot_tmp
        bot_tmp = None
        '''

    def Show(self):
        
        for key, value in self.species.items():
            # print (value)
            value.printAll()

            
    def save_bots(self):
        for bot_id, bot in self.species.items():
            BOT_SAVE_FOLDER = "bots/"
            #serialise bot to local file.
            print (f'saving ... {bot_id}')
            bot.save(save_folder=BOT_SAVE_FOLDER)
            self.recordWinningBot(bot)
            
    
    def recordWinningBot(self, bot):
        """Record optimisation winners to db

        Arguments:
            botlist {[type]} -- [description]
        """
        #logger.info('Winning bots recorded')
        botStr = bot
        botID = bot.name
        #--build data for posting
        dataSend = {}
        dataSend["action"] = "record_bot"
        dataSend["user"] = self.parms['uid']
        dataSend["botID"] = botID
        dataSend["botStructure"] = botStr.printStr()
        dataSend["market"] = self.parms['env']
        dataSend["direction"] = ""
        dataSend["optimisationID"] = ""
        dataSend["parent"] = "Eve"
        dataSend["scope"] = "global"
       
        
        dataSendJSON = json.dumps(dataSend)
      
        #--post data
        try:
            API_ENDPOINT = "https://www.vixencapital.com/api/optimisation/"
            try:
                r = requests.post(url = API_ENDPOINT, data = dataSendJSON)
                response = r.text
            except:
                print("request error")

        except:
            #logger.critical('Error recording winning bot')
            pass


        #print (response)
    


if __name__ == "__main__":
    pass
    '''
    pop = Population(parms={'PopulationSize' : '100'}, name = "demo")
    pop.populate('trader')
    '''

