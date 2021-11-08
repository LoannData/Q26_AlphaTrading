#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Mar 26 15:24:37 2021

@author: loann
"""

import sys, os 


import quanTrade.utils as utils

from quanTrade.system import SYSTEM


class CLIENT_MAIN(SYSTEM) : 
    
    def __init__(self, 
                 brokerName, 
                 accountNumber = 0) : 
        self.broker           = brokerName    # Broker Name
        self.refNumber        = accountNumber # Broker's reference number 
        self.api              = None # Broker's api object 
        self.contractsList    = {}   # List of the available contracts for the current instance
                                     # Here a contract is a contract object compatible with the broker api 
        self.configFile_connexion = None 
        self.configFile_contract  = None
        self.trading_log_path     = None 
        
        # Distant communication parameters 
        self.enabled_telegram_bot         = False 
        self.telegram_bot_mode            = None    # "read", "write"
        self.telegram_bot                 = None 
        self.telegram_message             = None 
        
        # Local client initialisation 
        if self.broker == "IBKR" : 
            dirname  = os.path.dirname(__file__)
            filename = os.path.join(dirname,".")
            sys.path.append(filename)
            import quanTrade.client_IBKR as client
            # IBKR API initialisation 
            self.api = client.CLIENT_IBKR()  
        
        if self.broker == "MT4" : 
            dirname  = os.path.dirname(__file__)
            filename = os.path.join(dirname,".")
            sys.path.append(filename)
            import quanTrade.client_MT4 as client
            # IBKR API initialisation 
            self.api = client.CLIENT_MT4() 
            
        
        return 
    
    #########################################################################################
    # LISTEN METHODS 
    #########################################################################################

    
    #########################################################################################
    # CONNECTION METHODS 
    #########################################################################################
    def connect(self, 
                configFile = None) :
        """
        Function that connect the instance to the broker's API and 
        fill the associated api object. 
        Variables : 
            brokerName [str]  : Name of the broker to connect 
            configFile [dict] : Dictionnary that contains the broker's connection informations 
        """
        if configFile is None : 
            configFile = self.configFile_connexion
        
        if self.broker == "IBKR" : 
            # Connection to the client API
            self.api.connection_(utils.getClientConnectionInfo(file = configFile, 
                                                               brokerName = self.broker, 
                                                               referenceNumber = self.refNumber))
        
        if self.broker == "MT4" : 
            # Connection to the client API 
            self.api.connection(utils.getClientConnectionInfo(file = configFile, 
                                                              brokerName = self.broker, 
                                                              referenceNumber = self.refNumber))
            
        
        return 
    
    def checkConnection(self) : 
        """ 
        Function that check if the Broker's api object is connected to the broker. 
        """
        if self.broker == "IBKR" : 
            return self.api.checkConnection()
        
        if self.broker == "MT4" : 
            return 
        
        return 
    
    def disconnect(self) : 
        """ 
        If connected, this function disconnect the broker's API object from the server. 
        """
        if self.broker == "IBKR" : 
            self.api.disconnect()
            
        if self.broker == "MT4" : 
            return 
            
        return 
    
    #########################################################################################
    # CONTRACT DEFINITION METHODS
    #########################################################################################
    def newContract(self, 
                    contractName, 
                    configFile = None) : 
        """
        Function that allows to define a new contract object compatible with a selected 
        broker. 
        """
        if configFile is None : 
            configFile = self.configFile_contract 
        
        if self.broker == "IBKR" : 
            self.contractsList[contractName] = utils.getContractInfo(file         = configFile, 
                                                                     brokerName   = self.broker, 
                                                                     contractName = contractName)
        
        if self.broker == "MT4" : 
            self.contractsList[contractName] = utils.getContractInfo(file         = configFile, 
                                                                     brokerName   = self.broker, 
                                                                     contractName = contractName)
            
        return 
    
    def removeContract(self, 
                       contractName) : 
        """ 
        Function that allows to remove a contract existing in the contractsList object. 
        """
        if self.broker == "IBKR" : 
            del self.contractsList[contractName] 
            
        if self.broker == "MT4" : 
            del self.contractsList[contractName] 
    #########################################################################################
    # CONTRACT DATA METHODS 
    #########################################################################################
    @SYSTEM.get_historical_data
    def getHistoricalData(self, contractName, dateIni, dateEnd, timeframe, onlyOpen = True) : 
        """ 
        Function that returns an historical dataset for the selected contract. 
        """
        if self.broker == "IBKR" : 
            contract = self.contractsList.get(contractName)
            return self.api.getHistoricalData_(contract, dateIni, dateEnd, timeframe, onlyOpen = onlyOpen)
        
        if self.broker == "MT4" : 
            contract = self.contractsList.get(contractName)
            return self.api.getHistoricalData(contract, dateIni, dateEnd, timeframe, onlyOpen = onlyOpen)
            
        return 
    
    @SYSTEM.get_last_price
    def getLastPrice(self, contractName) : 
        """ 
        Function that returns the last existing price for the selected contract. 
        """
        if self.broker == "IBKR" : 
            contract = self.contractsList.get(contractName)
            return self.api.getLastPrice_(contract)
        
        if self.broker == "MT4" : 
            contract = self.contractsList.get(contractName)
            return self.api.getLastPrice(contract)
            
        
        return

    #########################################################################################
    # TRADING ORDER METHODS
    #########################################################################################
    @SYSTEM.place_order
    def placeOrder(self, 
                   contractName,
                   action     = "long", # "long" or "short". 
                   orderType  = "bracket", # Order kind : "bracket" 
                   volume     = 0.1, # Volume of the asset to trade in the asset unit 
                   stoploss   = None, # Stoploss value
                   takeprofit = None, # Take profit value 
                   lmtPrice   = None, # Order executed if price reaches the lmtPrice 
                   auxPrice   = None) : 
        """
        Function that allows to place an order with a selected contract object, on a selected 
        broker.  
        This function returns a list of 3 orders (with respect to the following order): 
            - A market order 
            - The limit takeprofit order 
            - The stoploss order 
        """
        configFile = {
            "contract"  : self.contractsList.get(contractName), 
            "action"    : action, 
            "orderType" : orderType, 
            "volume"    : volume, 
            "stoploss"  : stoploss, 
            "takeprofit": takeprofit, 
            "lmtPrice"  : lmtPrice, 
            "auxPrice"  : auxPrice
            }

        if self.broker == "IBKR" : 
            orderList = self.api.createOrder(configFile) 
            self.api.placeOrderList(configFile.get("contract"), orderList)
        
        if self.broker == "MT4" : 
            orderList = self.api.placeOrder_(configFile)
            
        # A good thing could be to normalize the borker's response to get it properly in the log 
        return orderList  
    
    @SYSTEM.edit_SL_order
    def editSLOrder(self, 
                    contractName, 
                    order, 
                    stoploss = None) : 
        """ 
        Function that allows to edit the stoploss of a bracket order 
        """
        if stoploss is not None : 
            
            if self.broker == "IBKR" : 
                self.api.editLimitOrder(self.contractsList.get(contractName), order, stoploss)
                
            if self.broker == "MT4" : 
                self.api.editPosition(order, stoploss = stoploss)
                
    @SYSTEM.edit_TP_order
    def editTPOrder(self, 
                    contractName, 
                    order, 
                    takeprofit = None) : 
        """ 
        Function that allows to edit the takeprofit of a bracket order 
        """
        if takeprofit is not None : 
            
            if self.broker == "IBKR" : 
                self.api.editLimitOrder(self.contractsList.get(contractName), order, takeprofit)
                
            if self.broker == "MT4" : 
                self.api.editPosition(order, takeprofit = takeprofit)
    
    @SYSTEM.cancel_order
    def cancelOrder(self, 
                    contractName, 
                    order) : 
        """
        Function that allows to cancel an order that have been previously placed but not 
        executed yet on a given contract and to a given broker.  
        """
        if self.broker == "IBKR" : 
            self.api.cancelOrder__(order = order) 
            
        if self.broker == "MT4" : 
            self.api.cancelOrder(order)
            
        return
    
    def cancelLastOrder(self, n = 1) : 
        """  
        Function that cancel the last-n specific order. 
        """
        # if self.broker == "IBKR" : 
        #     self.api.cancelOrder_(option = n) 
        return 
    
    def readPositions(self) : 
        """
        Function that returns the positions informations opened by the current client account.  
        """
        return 
    
    @SYSTEM.close_position
    def closePosition(self, 
                      contractName, 
                      order = None) : 
        """ 
        Function that close a specific position on a given contract. 
        """
        if self.broker == "IBKR" : 
            self.api.closePosition_(self.contractsList.get(contractName), order = order)
            
        if self.broker == "MT4" : 
            symbolName = self.contractsList.get(contractName).get("symbol")
            self.api.closePosition(symbolName, order)
        return 

    def closeAllPositions(self) : 
        """ 
        Function that close positions for every existing contract 
        """
        return 
    
    def getPositionInfo(self, contractName) : 
        """ 
        Function that returns informations on a global position for a specified contract. 
        """ 
        return 
    

    
    
    


