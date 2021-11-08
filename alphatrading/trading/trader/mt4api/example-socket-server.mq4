/* ###################################################################

Example socket server.
Code can be used as both MQ4 and MQ5 (on both 32-bit and 64-bit MT5)

Receives messages from the example client and simply writes them
to the Experts log.

Also contains functionality for handling files sent by the example 
file-sender script.

In addition, you can telnet into the server's port. Any CRLF-terminated
message you type is similarly printed to the Experts log. You
can also type in the commands "quote", to which the server reponds
with the current price of its chart, or "close", which causes the
server to shut down the connection.

As well as demonstrating server functionality, the use of Receive()
and the event-driven handling are also applicable to a client
which needs to receive data from the server as well as just sending it.

################################################################### */


#property strict

// --------------------------------------------------------------------
// Include socket library, asking for event handling
// --------------------------------------------------------------------

#define SOCKET_LIBRARY_USE_EVENTS
#include <socket-library-mt4-mt5.mqh>

// --------------------------------------------------------------------
// EA user inputs
// --------------------------------------------------------------------

input ushort  ServerPort = 15555;  // Server port

extern int    slippage   = 100; // Max price slippage
extern string comment    = "Q26 Signal"; // Comment    
extern int    magic      = 26; // Magic Number  
extern color  arrowColor = clrBlue; // Arrow Color 


// --------------------------------------------------------------------
// Global variables and constants
// --------------------------------------------------------------------

// Frequency for EventSetMillisecondTimer(). Doesn't need to 
// be very frequent, because it is just a back-up for the 
// event-driven handling in OnChartEvent()
#define TIMER_FREQUENCY_MS    1000

// Server socket
ServerSocket * glbServerSocket = NULL;

// Array of current clients
ClientSocket * glbClients[];

// Watch for need to create timer;
bool glbCreatedTimer = false;


// --------------------------------------------------------------------
// Initialisation - set up server socket
// --------------------------------------------------------------------

void OnInit()
{
   // If the EA is being reloaded, e.g. because of change of timeframe,
   // then we may already have done all the setup. See the 
   // termination code in OnDeinit.
   if (glbServerSocket) {
      Print("Reloading EA with existing server socket");
   } else {
      // Create the server socket
      glbServerSocket = new ServerSocket(ServerPort, false);
      if (glbServerSocket.Created()) {
         Print("Server socket created");
   
         // Note: this can fail if MT4/5 starts up
         // with the EA already attached to a chart. Therefore,
         // we repeat in OnTick()
         glbCreatedTimer = EventSetMillisecondTimer(TIMER_FREQUENCY_MS);
      } else {
         Print("Server socket FAILED - is the port already in use?");
      }
   }
}


// --------------------------------------------------------------------
// Termination - free server socket and any clients
// --------------------------------------------------------------------

void OnDeinit(const int reason)
{
   switch (reason) {
      case REASON_CHARTCHANGE:
         // Keep the server socket and all its clients if 
         // the EA is going to be reloaded because of a 
         // change to chart symbol or timeframe 
         break;
         
      default:
         // For any other unload of the EA, delete the 
         // server socket and all the clients 
         glbCreatedTimer = false;
         
         // Delete all clients currently connected
         for (int i = 0; i < ArraySize(glbClients); i++) {
            delete glbClients[i];
         }
         ArrayResize(glbClients, 0);
      
         // Free the server socket. *VERY* important, or else
         // the port number remains in use and un-reusable until
         // MT4/5 is shut down
         delete glbServerSocket;
         glbServerSocket = NULL;
         Print("Server socket terminated");
         break;
   }
}


// --------------------------------------------------------------------
// Timer - accept new connections, and handle incoming data from clients.
// Secondary to the event-driven handling via OnChartEvent(). Most
// socket events should be picked up faster through OnChartEvent()
// rather than being first detected in OnTimer()
// --------------------------------------------------------------------

void OnTimer()
{
   // Accept any new pending connections
   AcceptNewConnections();
   
   // Process any incoming data on each client socket,
   // bearing in mind that HandleSocketIncomingData()
   // can delete sockets and reduce the size of the array
   // if a socket has been closed

   for (int i = ArraySize(glbClients) - 1; i >= 0; i--) {
      HandleSocketIncomingData(i);
   }
}


// --------------------------------------------------------------------
// Accepts new connections on the server socket, creating new
// entries in the glbClients[] array
// --------------------------------------------------------------------

void AcceptNewConnections()
{
   // Keep accepting any pending connections until Accept() returns NULL
   ClientSocket * pNewClient = NULL;
   do {
      pNewClient = glbServerSocket.Accept();
      if (pNewClient != NULL) {
         int sz = ArraySize(glbClients);
         ArrayResize(glbClients, sz + 1);
         glbClients[sz] = pNewClient;
         Print("New client connection");
         
         //pNewClient.Send("Connection established with the MT4 server");
      }
      
   } while (pNewClient != NULL);
}


// --------------------------------------------------------------------
// Handles any new incoming data on a client socket, identified
// by its index within the glbClients[] array. This function
// deletes the ClientSocket object, and restructures the array,
// if the socket has been closed by the client
// --------------------------------------------------------------------

void HandleSocketIncomingData(int idxClient)
{
   ClientSocket * pClient = glbClients[idxClient];

   // Keep reading CRLF-terminated lines of input from the client
   // until we run out of new data
   bool bForceClose = false; // Client has sent a "close" message
   string strCommand;
   do {
      //strCommand = pClient.Receive("\r\n");
      strCommand = pClient.Receive();
      
      //Print(strCommand);

      if (strCommand != "") {
         Print (strCommand); 

         // Client ask to place an order 
         if (StringFind(strCommand, "placeOrder", 0) != -1){
            Print ("Client asked to place an order");

            int orderTicket = placeOrder(strCommand);
            string ServerResponse = StringConcatenate("Order ticket : ",IntegerToString(orderTicket)); 

            Print ("Server Response : ",ServerResponse);

            pClient.Send(ServerResponse);

         }

         // Client ask to close an open position 
         if (StringFind(strCommand, "closeOrder", 0) != -1){
            Print ("Client asked to close an open order"); 

            string closeState = closeOrder(strCommand);
            string ServerResponse = StringConcatenate("Closing State : ",closeState); 
            Print ("Server Response : ",ServerResponse);
            pClient.Send(ServerResponse);
         }

         // Client ask to modify an order 
         if (StringFind(strCommand, "modifyOrder", 0) != -1){
            Print ("Clisent asket to modify an order"); 

            string modifyState = modifyOrder(strCommand);
            string ServerResponse = StringConcatenate("Modification state : ",modifyState); 
            Print ("Server Response : ",ServerResponse);
            pClient.Send(ServerResponse); 
         }

         // Client ask to cancel an order 
         if (StringFind(strCommand, "cancelOrder", 0) != -1){
            Print ("Clisent asket to cancel an order"); 

            string cancelState = cancelOrder(strCommand);
            string ServerResponse = StringConcatenate("Cancel state : ",cancelState); 
            Print ("Server Response : ",ServerResponse);
            pClient.Send(ServerResponse); 
         }

         // Client ask last price info 
         if (StringFind(strCommand, "getPrice", 0) != -1){
            Print ("Client asked the last price"); 

            string ServerResponse; 
            ServerResponse = getLastPrice(strCommand); 

            Print ("Server Response : ",ServerResponse);
            pClient.Send(ServerResponse);
         }

         // Client ask for historical data 
         if (StringFind(strCommand, "getHst", 0) != -1){
            Print ("Client asked for historical data");

            string ServerResponse; 
            ServerResponse = getHstData(strCommand); 

            Print ("Server Response : ",ServerResponse);
            pClient.Send(ServerResponse);

         }




         
      }


   } while (strCommand != "");

   // If the socket has been closed, or the client has sent a close message,
   // release the socket and shuffle the glbClients[] array
   if (!pClient.IsSocketConnected() || bForceClose) {
      Print("Client has disconnected");

      // Client is dead. Destroy the object
      delete pClient;
      
      // And remove from the array
      int ctClients = ArraySize(glbClients);
      for (int i = idxClient + 1; i < ctClients; i++) {
         glbClients[i - 1] = glbClients[i];
      }
      ctClients--;
      ArrayResize(glbClients, ctClients);
   }
}


// --------------------------------------------------------------------
// Use OnTick() to watch for failure to create the timer in OnInit()
// --------------------------------------------------------------------

void OnTick()
{
   if (!glbCreatedTimer) glbCreatedTimer = EventSetMillisecondTimer(TIMER_FREQUENCY_MS);
}

// --------------------------------------------------------------------
// Event-driven functionality, turned on by #defining SOCKET_LIBRARY_USE_EVENTS
// before including the socket library. This generates dummy key-down
// messages when socket activity occurs, with lparam being the 
// .GetSocketHandle()
// --------------------------------------------------------------------

void OnChartEvent(const int id, const long& lparam, const double& dparam, const string& sparam)
{
   if (id == CHARTEVENT_KEYDOWN) {
      // If the lparam matches a .GetSocketHandle(), then it's a dummy
      // key press indicating that there's socket activity. Otherwise,
      // it's a real key press
         
      if (lparam == glbServerSocket.GetSocketHandle()) {
         // Activity on server socket. Accept new connections
         Print("New server socket event - incoming connection");
         AcceptNewConnections();

      } else {
         // Compare lparam to each client socket handle
         for (int i = 0; i < ArraySize(glbClients); i++) {
            if (lparam == glbClients[i].GetSocketHandle()) {
               HandleSocketIncomingData(i);
               return; // Early exit
            }
         }
         
         // If we get here, then the key press does not seem
         // to match any socket, and appears to be a real
         // key press event...
      }
   }
}



// --------------------------------------------------------------------
// Trading functionnalities 
// --------------------------------------------------------------------
int placeOrder(string strCommand){

   // Variables to fill in order to place the order 
   string symbol; 
   int    cmd; 
   double volume; 
   double price; 
   double PriceAsk, PriceBid;
   double lmtPrice; 
   double stoploss; 
   double takeprofit; 
   datetime pendingExpiration;

   int orderTicket;
 

   string orderProps[10]; 

   if (StringSplit(strCommand, StringGetCharacter("-", 0), orderProps) != -1){
      Print ("Place order. Correctly splitted the client command");

      string subCommand[2]; 

      if (StringSplit(orderProps[1], StringGetCharacter(":", 0), subCommand) == -1){
         Print ("Error getting symbol");
      }
      else {
         symbol = subCommand[1];
         PriceAsk = MarketInfo(symbol, MODE_ASK);
         PriceBid = MarketInfo(symbol, MODE_BID);
         Print ("Symbol : ",symbol);
      }




      if (StringSplit(orderProps[2], StringGetCharacter(":", 0), subCommand) == -1){
         Print ("Error getting action");
      }
      else {
         if (subCommand[1] == "long"){
            cmd = 0;
            price = PriceBid;
         }
         else if (subCommand[1] == "short"){
            cmd = 1;
            price = PriceAsk;
         }
         Print ("Price : ",price);

         if (StringSplit(orderProps[3], StringGetCharacter(":", 0), subCommand) == -1){
            Print ("Error getting order type");
         }
         else {
            if (subCommand[1] == "MKT" && cmd == 0){
               cmd = 0;
            }
            else if (subCommand[1] == "MKT" && cmd == 1){
               cmd = 1;
            }
            else if (subCommand[1] == "LMT" && cmd == 0){
               cmd = 2;
            }
            else if (subCommand[1] == "LMT" && cmd == 1){
               cmd = 3;
            }
            else if (subCommand[1] == "MIT" && cmd == 0){
               cmd = 4; 
            }
            else if (subCommand[1] == "MIT" && cmd == 1){
               cmd = 5;
            }
         }
         Print ("Cmd : ",cmd);
      }

      if (StringSplit(orderProps[4], StringGetCharacter(":", 0), subCommand) == -1){
         Print ("Error getting volume");
      }
      else {
         volume = subCommand[1];
         Print ("Volume : ",volume);
      }

      if (StringSplit(orderProps[5], StringGetCharacter(":", 0), subCommand) == -1){
         Print ("Error getting stoploss");
      }
      else {
         stoploss = subCommand[1];
         Print ("Stoploss : ",stoploss);
      }

      if (StringSplit(orderProps[6], StringGetCharacter(":", 0), subCommand) == -1){
         Print ("Error getting takeprofit");
      }
      else {
         takeprofit = subCommand[1];
         Print ("Takeprofit : ",takeprofit);
      }

      if (StringSplit(orderProps[7], StringGetCharacter(":", 0), subCommand) == -1){
         Print ("Error getting lmtPrice");
      }
      else {
         lmtPrice = subCommand[1];
         Print ("Limit Price : ",lmtPrice);
      }

      if (cmd != 0 && cmd != 1){
         price = lmtPrice;
      }


      if (StringSplit(orderProps[8], StringGetCharacter(":", 0), subCommand) == -1){
         Print ("Error getting pending expiration date");
      }
      else {
         pendingExpiration = StrToTime(subCommand[1]);
         Print ("Pending expiration : ",pendingExpiration);
      }

      orderTicket =   OrderSend(symbol,            // symbol
                                cmd,                 // operation
                                volume,              // volume
                                price,               // price
                                slippage,            // slippage
                                stoploss,            // stop loss
                                takeprofit,          // take profit
                                comment=comment,     // comment
                                magic,         // magic number
                                pendingExpiration,        // pending order expiration
                                arrowColor);

            
      if (orderTicket != -1){
         Print ("Order succesfully placed, ticket : ",orderTicket);
         return orderTicket; 
      }
      else {
         Print("OrderSend failed with error #",GetLastError());
         return -1;
      } 
      


   }
   else { 
      Print ("Place order. Error when splitting the client command.");
      return -1;
   }


}

string closeOrder(string strCommand){
   // Variables to fill in order to place the order 
   string symbol; 
   int ticket; 
   double lots; 
   double price, PriceAsk, PriceBid; 
   string direction; 

   bool orderState; 


   string orderProps[10]; 

   if (StringSplit(strCommand, StringGetCharacter("-", 0), orderProps) != -1){
      Print ("Place order. Correctly splitted the client command");

      string subCommand[2]; 

      if (StringSplit(orderProps[1], StringGetCharacter(":", 0), subCommand) == -1){
         Print ("Error getting ticket");
      }
      else {
         ticket = subCommand[1];
         Print ("Ticket to close : ",ticket);
      }

      if (StringSplit(orderProps[2], StringGetCharacter(":", 0), subCommand) == -1){
         Print ("Error getting ticket");
      }
      else {
         lots = subCommand[1];
         Print ("Lots : ",lots);
      }

      if (StringSplit(orderProps[3], StringGetCharacter(":", 0), subCommand) == -1){
         Print ("Error getting direction");
      }
      else {
         direction = subCommand[1];
         Print ("Direction : ",direction);
      }

      if (StringSplit(orderProps[4], StringGetCharacter(":", 0), subCommand) == -1){
         Print ("Error getting symbol");
      }
      else {
         symbol = subCommand[1];
         Print ("Symbol : ",symbol);
      }

      PriceAsk = MarketInfo(symbol, MODE_ASK);
      PriceBid = MarketInfo(symbol, MODE_BID);

      if (direction == "long"){price = PriceAsk;}
      if (direction == "short"){price = PriceBid;}

      orderState =  OrderClose(ticket,      // ticket
                               lots,        // volume
                               price,       // close price
                               slippage,    // slippage
                               arrowColor  // color
      );

      if (orderState){
         return "True";
      }
      else {
         return "False";
      }

   }

   return "False";



}


string modifyOrder(string strCommand){
//bool OrderModify(int ticket, double price, double stoploss, double takeprofit, datetime expiration, color arrow_color=CLR_NONE)
   int ticket; 
   double price; 
   double stoploss; 
   double takeprofit; 
   datetime expiration; 
   color arrow_color = clrRed; 

   bool orderState; 

   string orderProps[10]; 

   if (StringSplit(strCommand, StringGetCharacter("-", 0), orderProps) != -1){
      Print ("Place order. Correctly splitted the client command");

      string subCommand[2]; 

      if (StringSplit(orderProps[1], StringGetCharacter(":", 0), subCommand) == -1){
         Print ("Error getting ticket");
      }
      else {
         ticket = subCommand[1];
         Print ("Ticket to close : ",ticket);
      }

      if (StringSplit(orderProps[2], StringGetCharacter(":", 0), subCommand) == -1){
         Print ("Error getting stoploss");
      }
      else {
         stoploss = subCommand[1];
         Print ("Stoploss : ",stoploss);
      }

      if (StringSplit(orderProps[3], StringGetCharacter(":", 0), subCommand) == -1){
         Print ("Error getting takeprofit");
      }
      else {
         takeprofit = subCommand[1];
         Print ("Takeprofit : ",takeprofit);
      }

      if(OrderSelect(ticket, SELECT_BY_TICKET)==true){

         expiration = OrderExpiration(); 
         price      = OrderOpenPrice(); 

         orderState = OrderModify(ticket, 
                                  price,
                                  stoploss,
                                  takeprofit,
                                  expiration,
                                  arrow_color=arrow_color);

         if (orderState){
            return "True";
         }
         else {
            return "False";
         }


      }
      else {
         return "False"; 
      }





   
   }



   return "False";

}


string cancelOrder(string strCommand){

   int ticket; 
   bool orderState; 
   color arrow_color = clrGreen; 

   string orderProps[10]; 

   if (StringSplit(strCommand, StringGetCharacter("-", 0), orderProps) != -1){
      Print ("Cancel order. Correctly splitted the client command");

      string subCommand[2]; 

      if (StringSplit(orderProps[1], StringGetCharacter(":", 0), subCommand) == -1){
         Print ("Error getting ticket");
      }
      else {
         ticket = subCommand[1];
         Print ("Ticket to cancel : ",ticket);
      }

      orderState = OrderDelete(ticket,  arrow_color);

      if (orderState){
         return "True";
      }
      else {
         return "False";
      }

   }

   return "False";

}


string getLastPrice(string strCommand){

   datetime time; 
   datetime tradeServerTime = TimeCurrent(); 
   datetime timeLocal = TimeLocal(); 
   double tradeAllowed;
   double open; 
   double high; 
   double low; 
   double close; 
   double askPrice, bidPrice;
   long volume;

   int timeframe = 1;
   int shift     = 0;
   string symbol; 
   string orderProps[10];

   if (StringSplit(strCommand, StringGetCharacter("-", 0), orderProps) != -1){
      Print ("getLastPrice. Correctly splitted the client command");

      string subCommand[2]; 

      if (StringSplit(orderProps[1], StringGetCharacter(":", 0), subCommand) == -1){
         Print ("Error getting symbol");
      }
      else {
         symbol = subCommand[1];
         Print ("Symbol : ",symbol);
         tradeAllowed = MarketInfo(symbol, MODE_TRADEALLOWED);
      }

      if (StringSplit(orderProps[2], StringGetCharacter(":", 0), subCommand) == -1){
         Print ("Error getting symbol");
      }
      else {
         timeframe = subCommand[1];
         Print ("Timeframe : ",timeframe);
      }

      time     = iTime(symbol, timeframe, shift); 
      open  = iOpen(symbol, timeframe, shift); 
      high  = iHigh(symbol, timeframe, shift); 
      low   = iLow(symbol, timeframe, shift); 
      close = iClose(symbol, timeframe, shift); 
      volume   = iVolume(symbol, timeframe, shift); 
      askPrice = MarketInfo(symbol, MODE_ASK); 
      bidPrice = MarketInfo(symbol, MODE_BID); 

      string response = "getPrice-"; 

      response = response+"time@"+TimeToString(time);
      response = response+"-"; 
      response = response+"open@"+DoubleToString(open);
      response = response+"-";
      response = response+"high@"+DoubleToString(high);
      response = response+"-";
      response = response+"low@"+DoubleToString(low);
      response = response+"-";
      response = response+"close@"+DoubleToString(close);
      response = response+"-";
      response = response+"volume@"+DoubleToString(volume);
      response = response+"-";
      response = response+"askPrice@"+DoubleToString(askPrice);
      response = response+"-";
      response = response+"bidPrice@"+DoubleToString(bidPrice);
      response = response+"-"; 
      response = response+"tradeServerTime@"+TimeToString(tradeServerTime);
      response = response+"-"; 
      response = response+"timeLocal@"+TimeToString(timeLocal);
      response = response+"-"; 
      response = response+"tradeAllowed@"+DoubleToString(tradeAllowed);

      return response; 
   
   }

   return "Error";


                  }



string getHstData(string strCommand){

   string fileName;// = "Q26_hstData.csv"

   string orderProps[10];

   string symbol; 
   int start; 
   int stop; 
   int timeframe; 
   string path; 
   int dataCount; 

   if (StringSplit(strCommand, StringGetCharacter("-", 0), orderProps) != -1){
      Print ("getHstData. Correctly splitted the client command");

      string subCommand[2]; 

      if (StringSplit(orderProps[1], StringGetCharacter(":", 0), subCommand) == -1){
         Print ("Error getting symbol");
      }
      else {
         symbol = subCommand[1];
         Print ("Symbol : ",symbol);
      }

      if (StringSplit(orderProps[2], StringGetCharacter(":", 0), subCommand) == -1){
         Print ("Error getting start");
      }
      else {
         start = subCommand[1];
         Print ("Start: ",start);
      }

      if (StringSplit(orderProps[3], StringGetCharacter(":", 0), subCommand) == -1){
         Print ("Error getting stop");
      }
      else {
         stop = subCommand[1];
         Print ("Stop: ",stop);
      }

      if (StringSplit(orderProps[4], StringGetCharacter(":", 0), subCommand) == -1){
         Print ("Error getting timeframe");
      }
      else {
         timeframe = subCommand[1];
         Print ("Timeframe: ",timeframe);
      }

      if (StringSplit(orderProps[5], StringGetCharacter(":", 0), subCommand) == -1){
         Print ("Error getting path");
      }
      else {
         path = subCommand[1];
         Print ("Path: ",path);
      }

      if (StringSplit(orderProps[6], StringGetCharacter(":", 0), subCommand) == -1){
         Print ("Error getting fileName");
      }
      else {
         fileName = subCommand[1];
         Print ("FileName: ",fileName);
      }

      dataCount = start - stop;

      double open[]; 
      double high[]; 
      double low[]; 
      double close[]; 
      long volume[]; 
      datetime time[];

      // We refresh data before getting hst data
      RefreshRates();

      if (CopyOpen(symbol, timeframe, stop, dataCount, open) == -1){
         Print ("Error copying Open data"); 
      }
      if (CopyHigh(symbol, timeframe, stop, dataCount, high) == -1){
         Print ("Error copying High data"); 
      }
      if (CopyLow(symbol, timeframe, stop, dataCount, low) == -1){
         Print ("Error copying Low data"); 
      }
      if (CopyClose(symbol, timeframe, stop, dataCount, close) == -1){
         Print ("Error copying Close data"); 
      }
      if (CopyTickVolume(symbol, timeframe, stop, dataCount, volume) == -1){
         Print ("Error copying Volume data"); 
      }
      if (CopyTime(symbol, timeframe, stop, dataCount, time) == -1){
         Print ("Error copying Time data"); 
      }

      Print ("Time 0 : ",time[0]);

      //--- open the file for writing the indicator values (if the file is absent, it will be created automatically)
      ResetLastError();
      FileDelete(fileName);
      int file_handle=FileOpen(path+"//"+fileName,FILE_READ|FILE_WRITE|FILE_CSV,",");
      if(file_handle!=INVALID_HANDLE)
      {
         PrintFormat("%s file is available for writing","hstData");
         PrintFormat("File path: %s\\Files\\",TerminalInfoString(TERMINAL_DATA_PATH));
         // We writte the header of the file 
         FileWrite(file_handle, "time", "open", "high", "low", "close", "volume");
         //--- write the time and values of signals to the file
         for(int i=0;i<dataCount;i++)
            FileWrite(file_handle, time[i], open[i], high[i], low[i], close[i], volume[i]);
         //--- close the file
         FileClose(file_handle);
         PrintFormat("Data is written, %s file is closed",fileName);

         return "done";
      }
      else{
         PrintFormat("Failed to open %s file, Error code = %d",fileName,GetLastError());
         return "error";
      }
      
      return "error";




   }

   return "error";




}



