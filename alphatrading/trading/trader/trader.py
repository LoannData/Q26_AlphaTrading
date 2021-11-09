"""! 
=============================================================
Q26 - QuanTrader Python File
=============================================================

\dontinclude[
    Every function need to have a description header following this 
    template : 
        
        **Description :** 
            
            None
        
        **Parameters :** 
            
            None 
        
        **Returns :** 
            
            None 
            
            ]

""" 

import importlib
import json 
import time 
import datetime as dt 
import sys, os 


from . import client 
from . import distant 

from ...system.database import DATABASE



class TRADER : 
    """!
    ===============================================================
    Q26 - QuanTrader module - SIMULATION(ANALYSIS, WRITER) object. 
    ===============================================================
    ### Description :
        
        Main class of the Q26 QuanTester module. This object is dedicated to 
        initialize the simulation parameters and output the simulation 
        results. 
        
    ### Examples :
    
    ### Planned developments :
    
    ### Known bugs :
    
    \dontinclude[
    Do do list : 
        - Add random ohlc model 
    ] 
        

    """  
    
    def __init__(self) :
        
        ## ### CLIENT class object 
        # **Type**: class CLIENT() \n 
        # **Description** : \n 
        # This object contains trading API client 
        # connexion informations.  
        self.client                       = None 

        ## ### Name of the client 
        # **Type**: string \n 
        # **Description** : \n 
        # Name of the client as defined in the local system. 
        self.client_name                  = None 

        ## ### Client connection path 
        # **Type**: string \n 
        # **Description**: \n 
        # Path to the "client_connection.json" file in which 
        # the client connexion informations are stored.
        self.client_connect_path          = None 

        ## ### Client contract path 
        # **Type**: string \n 
        # **Description**: \n 
        # Path to the "client_contracts.json" file in which 
        # every contract identity is stored.
        self.client_contract_path         = None 
        
        ## ### Strategy name 
        # **Type**: string \n 
        # **Description**: \n 
        # Name of the strategy to be run in live mode. 
        self.strategy_name                = None 

        ## ### Strategy path 
        # **Type**: string \n 
        # **Description**: \n 
        # Path to the strategy python file. 
        self.strategy_path                = None

        ## ### STRATEGY class object 
        # **Type**: class STRATEGY() \n 
        # **Description**: \n 
        # STRATEGY class stored in the strategy python file. 
        self.strategy                     = None
        

        

    def set_database(self, 
                     name      = "Unamed", 
                     path      = "./", 
                     model     = "sqlite3", 
                     log       = True, 
                     tables    = []): 
        
        # We first create the DATABASE object within the right client 
        self.client.database = DATABASE() 
        self.client.database.db_path = path
        self.client.database.db_name = name 
        self.client.database.db_model = model
        self.client.database.activate() 
        self.client.database.connect() 

        # We create the standard logging system 
        if log: 

            table_name = "log"

            structure = {
                "date"     : "str", 
                "action"   : "str", 
                "args"     : "str", 
                "kwargs"   : "str", 
                "response" : "str"
            }

            self.client.database.create_table(table_name, structure)
        
        for table in tables: 

            self.client.database.create_table(table["name"], table["structure"]) 
        
        
    
    def set_client(self, 
                   name                 = None, 
                   client_connect_path  = None, 
                   client_contract_path = None) : 
        """! 
        **Description :** 
            
            Function that allows to define the trading CLIENT object properties. 
        
        **Parameters :** 
            
            - name [str] : Name of the client as registered in the local system. The choices are : 
                - IBKR : Interactive Broker (Trading Workstation) 
                - MT4  : MetaTrader 4 
            - client_connect_path [str]  : Path to the "client_connection.json" file containing all the informations of connection to the selected client. 
            - client_contract_path [str] : Path to the "client_contracts.json" file containing all the identities of the different contracts whithin the different 
                                           trading platforms. 
        
        **Returns :** 
            
            None 
        
        Do be done : 

        
        """
        if name is not None : 
            self.client_name = name 
        if client_connect_path is not None : 
            self.client_connect_path = client_connect_path 
        if client_contract_path is not None : 
            self.client_contract_path = client_contract_path 
            
        
        assert self.client_name is not None, "No client selected. Please, provide a client name." 
        assert self.client_connect_path is not None, "No client connection file selected. Please, provide it."
        assert self.client_contract_path is not None, "No client contract file selected. Please, provide it"
        
        self.client = client.CLIENT_MAIN(self.client_name)
        self.client.configFile_connexion = self.client_connect_path 
        self.client.configFile_contract  = self.client_contract_path 
        
    
    def set_strategy(self, 
                     strategy_name = None, 
                     strategy_path = None) : 
        """! 
        **Description :** 
            
            Function that allows to define the trading STRATEGY object. 
        
        **Parameters :** 
            
            - strategy_name [str] : Name of the trading strategy file. 
            - strategy_path [str] : Path to the trading strategy file.  
        
        **Returns :** 
            
            None 
        
        Do be done : 

        
        """
        
        if strategy_name is not None : 
            self.strategy_name = strategy_name 
        if strategy_path is not None : 
            self.strategy_path = strategy_path 
        
        assert self.strategy_name is not None, "No strategy name provided. Please provide it" 
        assert self.strategy_path is not None, "No strategy path provided. Please, provide it" 
        
        sys.path.append(self.strategy_path) 
        strategy = importlib.import_module(self.strategy_name)
        self.strategy = strategy.STRATEGY()

        return 
    

    
    def run(self, latency = 60) : 
        """! 
        **Description :** 
            
            Function that allows to run a trading strategy.  
        
        **Parameters :** 
            
            - latency [int] = 60 : Latency time between two execution of the STRATEGY.run() and STRATEGY.show() functions.  
                                   The time is expressed in seconds. 
        
        **Returns :** 
            
            None 
        
        Do be done : 

        
        """
        intro_dict = {"New Trading Session" : str(dt.datetime.now())}
        
        step_number = 0 
        
        while True : 
            
            step_number += 1 
            local_time   = str(dt.datetime.now())
            
            step_dict    = {
                "Step"       : step_number, 
                "Local time" : local_time 
                }
            
            self.strategy.run(self.client) 
            self.strategy.show(self.client) 
            
            time.sleep(latency)
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
    
    