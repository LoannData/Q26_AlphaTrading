#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
#############################################################
TRADING CONFIGURATION FILE
#############################################################
This file contains all the header informations necessary to 
initialize and run the trader

Please, read carefully all the explanations and report any 
bugs found in this file. 

WARNING! Do not run this file on a live trading account until 
         you are absolutely sure your system is working fine! 
"""


""" 
===============================================================================
MODULE IMPORTATION STEP
===============================================================================
This step is dedicated to import some important Python modules and the 
TRADER module from the Python Alpha-Trading library
"""
# Usual modules importations 
import os, sys 
import time 
import datetime as dt 
import importlib

# TRADER class object importation 
from alphatrading.trading.trader.trader import TRADER


""" 
===============================================================================
TRADER INSTANCE INITIALIZATION
===============================================================================
This step allows you to instanciate your TRADER object. 
"""
t = TRADER()


""" 
===============================================================================
CLIENT SELECTION STEP
===============================================================================
Once your TRADER object is instanciated, you can define which trading 
plateform you want to use thanks to the TRADER method 'self.set_client' 
"""
# Some important points: 
# - You have to prepare a 'client_connection' and a  
#   'client_contract' JSON files in which you will specify 
#   the way the TRADER instance will connect to the specific 
#   client you specified in the 'name' parameter and what are 
#   the contracts you want to trade and their identity in the 
#   system of your prefered broker. 
# - Then you have to specify the relative/absolute paths to the 
#   so-called files.  
t.set_client(name                 = "MT4", 
             client_connect_path  = "./client_connection.json", 
             client_contract_path = "./client_contracts.json")

"""
===============================================================================
STRATEGY IMPORTATION STEP
===============================================================================
This step is dedicated, as in the backtest simulation header file, to import 
your prefered trading strategy by specifying the name of the python script 
(without the extension .py) and the relative/absolute local associated path. 
"""
t.set_strategy(strategy_name = "strategyExample", 
               strategy_path = "./") 

""" 
===============================================================================
CONTRACT IMPORTATION STEP
===============================================================================
This step is dedicated to add the contract(s) you're interested in into the 
client's object instance. Then your strategy file will be able to execute order 
by calling the contracts with the name you filled here. Notice that the contract 
name has to be able in the 'client_contracts.json' file (Alpha-Trading side).  
"""
t.client.newContract("GBP.JPY")

"""
===============================================================================
STRATEGY PREPARATION STEP
===============================================================================
Once your trading strategy file is imported you can edit here some global 
parameters which can be dependent of the broker you use such as a trading 
volume factor for example. You can also pass external functions as attributes 
of the strategy which will be used to risk manage your system. It's up to your 
imagination!  
"""
t.strategy.volumeFactor = 1. 

"""
===============================================================================
DATABASE PREPARATION STEP
===============================================================================
As for the backtest simulation case, you can prepare a log database which will 
retrieve run informations from your strategy. This happen through the method 
function 'self.set_database'
"""
tables = []
t.set_database(name="sma_crossover_strategy_logfile", 
               path="./", 
               model="sqlite3", 
               log = True, 
               tables = tables)


# Depending on the broker algorithmic system's infrastructure, 
# one can be wise to wait for some seconds until your system is 
# fully ready to start asking trading servers. 
time.sleep(3)

# Afterwhile you can connect to the client 
t.client.connect()

""" 
===============================================================================
STRATEGY RUN STEP
===============================================================================
Finally you can run your whole system by using the method 'self.run'. You 
have to specify a latency value (in seconds) which will lead to execute the 
STRATEGY.run (and show) functions each 'latency' seconds. 

Note: According your broker's architecture, use too small latencies can lead 
      to server errors and reduce your strategy efficiency. I suggest you to 
      try different latency parameters in paper trading before going live. 
"""
t.run(latency = 10)


