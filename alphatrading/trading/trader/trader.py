#!/usr/bin/env python3
# -*- coding: utf-8 -*-
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

dirname  = os.path.dirname(__file__)
filename = os.path.join(dirname,".")
sys.path.append(filename)
import quanTrade.client as client 
import quanTrade.distant as distant 
#from quanTrade.mbapi.system import SYSTEM

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
        
        ## ### Trading log path 
        # **Type**: string \n 
        # **Description**: \n 
        # Path to the trading log
        self.trading_log_path             = None 

        ## ### Trading log first write mode
        # **Type**: string \n 
        # **Description**: \n 
        # When restarting the live trading using an already written 
        # trading log, the user has two choices : either he overwrite 
        # the trading log file ("w"), either he append new data after the 
        # already existing data ("a").   
        self.trading_log_first_write_mode = None 
        
    
    def set_telegram_listen_mode(self) : 
        """! \private
        **Description :** 
            
            Function that allows to se the telegram robot in listen mode. 
            Note: this function is actualy not working because telegram doesn't 
            allow two robots to communicate together. 
        
        **Parameters :** 
            
            None 
        
        **Returns :** 
            
            None 
        
        Do be done : 

        
        """
        
        assert self.client.telegram_bot_mode == "listen", "error, bad telegram mode."
        
        self.client.telegram_bot.set_listen_mode()
        
        return 

    
    
    def initialize_telegram_bot(self, 
                                TOKEN = None, 
                                mode  = "write") : 
        """! \private
        **Description :** 
            
            Function that allows to initialize the telegram robot. 
            Note: this function is actualy not working because telegram doesn't 
            allow two robots to communicate together. 
        
        **Parameters :** 
            
            - TOKEN [str]          : Token associated with the Telegram bot 
            - mode [str] = "write" : Action mode of the Telegram bot, it can be "write" or "listen" 

        
        **Returns :** 
            
            None 
        
        Do be done : 

        
        """
        
        assert self.client is not None, "Error, client object have to be defined before"
        assert TOKEN is not None, "Error. No provided token."
        
        self.client.telegram_bot_mode = mode 
        self.client.telegram_bot = distant.TELEGRAM_BOT()
        self.client.telegram_bot.initialize() 
        
        return 
    
    def set_telegram_handler(self, 
                             action    = "place order", 
                             command   = "play") : 
        """! \private
        **Description :** 
            
            Function that allows to select Telegram bot action handler. 
            Note: this function is actualy not working because telegram doesn't 
            allow two robots to communicate together. 
        
        **Parameters :** 
            
            - action [str] = "place order" : Action to be sent to the Telegram bot. The choices are : 
                - "place order" 
                - "edit stoploss order" 
                - "edit takeprofit order" 
                - "cancel order" 
                - "close position" 
                - "transactions mode" : all the previous actions at the same time. 
            - command [str] = "play" : Command to be typed by a Telegram user to acces to the Telegram bot signals. 

        
        **Returns :** 
            
            None 
        
        Do be done : 

        
        """
        
        assert self.client is not None, "Error, client object have to be defined before"
        self.client.telegram_bot.set_telegram_handler(action  = action, 
                                               command = command)
        
        return 
    
    def enable_telegram_bot(self) : 
        """! \private
        **Description :** 
            
            Function that allows to enable de Telegram bot. 
            Note: this function is actualy not working because telegram doesn't 
            allow two robots to communicate together. 
        
        **Parameters :** 
            
            None
        
        **Returns :** 
            
            None 
        
        Do be done : 

        
        """
        
        assert self.client is not None, "Error, client object have to be defined before"
        self.client.enabled_telegram_bot = True 
        self.client.telegram_bot.start() 
        
        return 
        
        
    def set_trading_log(self, 
                        path    = None, 
                        replace = False) : 
        """! 
        **Description :** 
            
            Function allowing to define the trading log properties. 
        
        **Parameters :** 
            
            - path [str]             : Path to the trading log file. If the file doesn't exist yet, the program will create it. 
            - replace [bool] = False : If the trading log file already exists and replace = True, the program will overwrite the trading log file. 
        
        **Returns :** 
            
            None 
        
        Do be done : 

        
        """
        
        if path is not None : 
            self.trading_log_path = path 
        
        assert self.trading_log_path is not None, "Error while reading the trading log file. Please provide a path." 
        

        if replace : 
            self.trading_log_first_write_mode = "w"
        else : 
            self.trading_log_first_write_mode = "a"

        return 
        
        
    
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
        
        if self.trading_log_path is not None : 
            self.client.trading_log_path     = self.trading_log_path
        
    
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
        
        with open(self.trading_log_path, self.trading_log_first_write_mode) as json_file : 
            json.dump(intro_dict, json_file)
            json_file.write("\n")
        
        step_number = 0 
        
        while True : 
            
            step_number += 1 
            local_time   = str(dt.datetime.now())
            
            step_dict    = {
                "Step"       : step_number, 
                "Local time" : local_time 
                }
            
            with open(self.trading_log_path, "a") as json_file : 
                json.dump(step_dict, json_file)
                json_file.write("\n")
            
            self.strategy.run(self.client) 
            self.strategy.show(self.client) 
            
            time.sleep(latency)
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
    
    