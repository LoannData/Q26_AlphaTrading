"""! 
=============================================================
Q26 - QuanTester Python File
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

import matplotlib.pyplot as plt 
import numpy as np
import datetime as dt 

class ANALYSIS : 
    """!
    ===============================================================
    Q26 - QuanTester module - ANALYSIS herited class 
    ===============================================================
    ### Description :
        
        This class is an heritage of the SIMULATION class so the 
        member functions can be directly used on SIMULATION() objects. 
        
    ### Examples :
    
    ### Planned developments :
    
    ### Known bugs :
    
    \dontinclude[
    Do do list : 
    ] 
        

    """ 



    def showEquityCurve(self, 
                        index     = [], 
                        labels    = list(),
                        xTime     = False,
                        y_scale   = "linear", # See : https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.yscale.html
                        y_lim     = None, 
                        x_lim     = None,
                        x_label   = "# of transaction", 
                        y_label   = "Equity Curve", 
                        x_rotation= 45, 
                        subCurve  = None, 
                        linestyle = "-",
                        marker    = None
                        ) :
        """! 
        **Description :** 
            
            This function allows to show the equity curves as a function of 
            the trade number or the time. 
        
        **Parameters :** 
            
            - index [list(int)] = list() : 
                List of index of portfolios one want to plot their equity curve 
            - labels [list(int)] = list() : 
                List of labels associated to the indexes 
            - xTime [bool] = False : 
                If True, the x-axis correspond to the time at which every position 
                have been closed. False correspond to the number of transaction. 
            - y_scale [string] = "linear" : 
                See https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.yscale.html for more 
            - y_lim [list(float)] = None : 
                y_lim = [y_min, y_max] price axis limits 
            - x_lim [list(float if !xTime else datetime)] = None : 
                x_lim = [x_min, x_max] time/#of transaction axis limits 
            - x_label [str] = "# of transaction" 
            - y_label [str] = "Equity curve" 
            - x_rotation [int] = 45 : 
                x labels rotation in degrees 
            - subCurve [list(int)] = None: 
                subCurve = [y_min, y_max] variable which allows to cut the y values. 
            - linestyle [str] = "-" 
            - marker [str] = None 
        
        **Returns :** 
            
            - fig : The figure which can be saved. 
            - ax 
        """
        
        
        fig, ax = plt.subplots()
        
        if len(index) == 0 : 
            index = list(np.linspace(0, len(self.portfolio)-1, num = len(self.portfolio)-1, dtype = int))
        for i in range(len(index)) : 
            y = self.portfolio[index[i]].equityCurve.copy()
            if subCurve is not None : 
                y = y[subCurve[0] : subCurve[1]]
            
            x = list(np.linspace(0, len(y), len(y)))
            if xTime : 
                x = list()
                for j in range(len(self.portfolio[index[i]].closedPositions)) : 
                    if self.portfolio[index[i]].closedPositions[j].closed : 
                        x.append(self.portfolio[index[i]].closedPositions[j].possibleCloseDate)
                del y[0]
            
            if len(labels) > 0 and i < len(labels): 
                l1, = ax.plot(x, y, ls = linestyle, marker = marker, label = labels[i])
            else : 
                l1, = ax.plot(x, y, ls = linestyle, marker = marker)

        if y_lim is not None : 
            ax.set_ylim(y_lim[0], y_lim[1])
        if x_lim is not None : 
            ax.set_xlim(x_lim[0], x_lim[1])

        ax.set_yscale(y_scale)

        ax.set_xlabel(x_label)
        ax.set_ylabel(y_label) 
        

        for tick in ax.get_xticklabels():
            tick.set_rotation(x_rotation)
        
        if len(labels) > 0 : 
            ax.legend()
            
        return fig, ax 
        # plt.show()
    
    def get_basic_results(self, 
                          client_id = 0):
    # def get_basic_results(self, client): 
        
        # We retrieve the indexed refered portfolio 
        client = self.portfolio[client_id] 

        # Number of Winners/Loosers 
        n_winners = 0 
        n_winners_long = 0 
        n_winners_short = 0
        n_loosers = 0 
        n_loosers_long = 0 
        n_loosers_short = 0
        for position in client.closedPositions: 
            if position.closed: 
                if position.profit > 0: 
                    n_winners += 1 
                    if position.action == "long": 
                        n_winners_long += 1 
                    elif position.action == "short": 
                        n_winners_short += 1
                elif position.profit < 0: 
                    n_loosers += 1 
                    if position.action == "long": 
                        n_loosers_long += 1 
                    elif position.action == "short": 
                        n_loosers_short += 1

        
        # Trades duration 
        trades_duration = [] 
        for position in client.closedPositions: 
            if position.closed: 
                trades_duration.append(position.possibleCloseDate - position.executionDate)
        avg_trade_duration = np.mean(trades_duration)
        min_trade_duration = np.min(trades_duration)
        max_trade_duration = np.max(trades_duration)

        # Profit factor 
        cumulated_gains = 0 
        cumulated_losses = 0
        for position in client.closedPositions: 
            if position.closed: 
                if position.profit > 0: 
                    cumulated_gains += position.profit
                elif position.profit < 0:  
                    cumulated_losses += position.profit
        PF = cumulated_gains/cumulated_losses
        winners_ratio = cumulated_gains/(cumulated_gains + abs(cumulated_losses))
        loosers_ratio = abs(cumulated_losses)/(cumulated_gains + abs(cumulated_losses))

        # Average gains 
        average_winners = cumulated_gains / n_winners 
        average_winners_percentage = average_winners / client.initialDeposit * 100 
        average_loosers = cumulated_losses / n_loosers
        average_loosers_percentage = average_loosers / client.initialDeposit * 100 

        # P&L global 
        PL = 0 
        for position in client.closedPositions:
            if position.closed:
                PL += position.profit

        # P&L per symbol 
        # symbol_list = list(client.symbols.keys())
        # PL_per_symbol = np.zeros(len(symbol_list)) 
        # Equity_per_symbol = [client.initialDeposit]

        # for position in client.closedPositions:
        #     if position.closed: 
        #         index = 0 
        #         while symbol_list[index] != position.symbol: 
        #             index += 1 
        #         PL_per_symbol[index] += position.profit 
        #         Equity_per_symbol.append(Equity_per_symbol[-1] + position.profit)
        
        # Equity_per_symbol = Equity_per_symbol[1:]
        
        # print (PL_per_symbol)



        # Shapr ratio per ticker 
        # strategy_yield_percentage = PL/client.initialDeposit*100
        # strategy_volatility_percentage = np.std((np.array(client.equityCurve) - client.initialDeposit)/client.initialDeposit*100)

        # strategy_yield_percentage_per_symbol = [] 
        # strategy_volatility_percentage_per_symbol = []
        # for i in range(len(list(client.symbols.keys()))): 
        #     symbol = list(client.symbols.keys())[i]
        #     strategy_yield_percentage_per_symbol.append(PL_per_symbol[i] / client.initialDeposit * 100)
        #     strategy_yield_percentage_per_symbol.append(np.std((np.array(Equity_per_symbol) - client.initialDeposit)/client.initialDeposit*100))

        # tickers_yield_percentage = [] 

        # pricer_start = self.priceTable.iloc(self.startIndex)
        # pricer_end   = self.priceTable.iloc(self.stopIndex)
        # for key in list(pricer_start.keys()): 
        #     start_price = pricer_start[key]["askopen"]
        #     stop_price  = pricer_end[key]["askclose"] 
        #     tickers_yield_percentage.append((stop_price - start_price)/start_price)
        

        

        # sharp_ratio_per_symbol = [] 
        # for i in range(len(client.symbols.keys())): 
        #     sharp_ratio_per_symbol.append((strategy_yield_percentage - tickers_yield_percentage[i])/strategy_volatility_percentage)

        # print (sharp_ratio_per_symbol)
        # start_price = self.priceTable.priceList


        results = {
            "Symbols"                        : [x for x in client.symbols.keys()], 
            "Start date"                     : str(self.priceTable.priceList[0].date[self.startIndex]),
            "End date"                       : str(client.getLastPrice(list(client.symbols.keys())[0])["date"]),
            "Initial Deposit"                : client.initialDeposit,
            "P&L"                            : PL, #client.balance - client.initialDeposit, 
            "P&L in percentage"              : PL/client.initialDeposit*100,
            "Cumulated gains"                : cumulated_gains, 
            "Cumulated losses"               : cumulated_losses,
            "Profit factor"                  : PF,
            "Winners ratio"                  : winners_ratio,
            "Loosers ratio"                  : loosers_ratio,
            "Number of transactions"         : len(client.closedPositions), 
            "Number of winners"              : n_winners, 
            "Number of winners long"         : n_winners_long, 
            "Number of winners short"        : n_winners_short, 
            "Winners average gain"           : average_winners, 
            "Winners average gain percentage": average_winners_percentage, 
            "Number of loosers"              : n_loosers, 
            "Number of loosers long"         : n_loosers_long, 
            "Number of loosers short"        : n_loosers_short, 
            "Loosers average loss"           : average_loosers, 
            "Loosers average loss percentage": average_loosers_percentage,
            "Average trade duration"         : str(avg_trade_duration), 
            "Min trade duration"             : str(min_trade_duration), 
            "Max trade duration"             : str(max_trade_duration), 
            "Number trades still open"       : len(client.openPositions), 
            "Maximum drawdown"               : client.currentDrawDown, 
            # "Sharp ratio per symbol"         : sharp_ratio_per_symbol, 
            # "Sharp ratio"                    : np.mean(sharp_ratio_per_symbol)

        }

        return results 
