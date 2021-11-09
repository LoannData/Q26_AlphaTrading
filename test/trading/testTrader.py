#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jul 12 09:55:52 2021

@author: loann
"""

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os, sys 
import time 
import datetime as dt 
import importlib


# API connector importation 
# quanTradePath = "../"
# sys.path.append(quanTradePath)
from alphatrading.trading.trader.trader import TRADER






t = TRADER()

# t.set_trading_log("./outputExample.txt", replace = True)

t.set_client(name                 = "MT4", 
             client_connect_path  = "./client_connection.json", 
             client_contract_path = "./client_contracts.json")

t.set_strategy(strategy_name = "strategyExample", 
               strategy_path = "./") 

t.client.newContract("EUR.USD")

t.strategy.volumeFactor = 1. 

tables = []

t.set_database(name="Example_simu", 
               path="./", 
               model="sqlite3", 
               log = True, 
               tables = tables)

time.sleep(10)


t.client.connect()

t.run(latency = 60)


