//+------------------------------------------------------------------+
//|                                                  ApexScalper.mq5 |
//|                                     Multi-Confluence Scalping EA  |
//|                                             https://www.mql5.com |
//+------------------------------------------------------------------+
#property copyright "ApexScalper"
#property link      "https://www.mql5.com"
#property version   "1.00"
#property description "Multi-confluence SCALPING EA for MetaTrader 5."
#property description "HTF trend bias + EMA pullback entry + ADX/RSI/ATR/spread/session filters."
#property description "ATR-based SL & TP, ATR trailing stop with breakeven, time stop, daily risk guard."
#property description "DIGIT-AGNOSTIC: all math in price units -> safe on 3, 4 and 5 digit brokers."

#include <Trade/Trade.mqh>

//+------------------------------------------------------------------+
//| Trailing stop distance mode                                      |
//+------------------------------------------------------------------+
enum ENUM_TRAIL_MODE
  {
   TRAIL_ATR    = 0,  // 0 - ATR based distance
   TRAIL_POINTS = 1   // 1 - Fixed points distance
  };

//+------------------------------------------------------------------+
//| ------------------------- TIMEFRAMES ---------------------------- |
//+------------------------------------------------------------------+
input ENUM_TIMEFRAMES  InpSignalTF           = PERIOD_M5;  // Signal timeframe (run chart on this TF)
input ENUM_TIMEFRAMES  InpTrendTF            = PERIOD_H1;  // Higher timeframe for trend bias
input bool             InpUseTrendFilter     = true;       // Use higher timeframe trend filter
input int              InpTrendEMAFast       = 50;         // HTF EMA fast period
input int              InpTrendEMASlow       = 200;        // HTF EMA slow period

//+------------------------------------------------------------------+
//| ----------------------- ENTRY LOGIC ----------------------------- |
//+------------------------------------------------------------------+
input int              InpEMA_Fast           = 8;          // Fast EMA period (momentum)
input int              InpEMA_Pullback       = 21;         // Pullback EMA period (entry line)
input int              InpEMA_Trend          = 50;         // Trend EMA period (structure)
input bool             InpUseStackFilter     = true;       // Require EMA stack alignment
input double           InpRejectionClose     = 0.55;       // Rejection bar min close position (0=off)
input double           InpMaxPenetrationATR  = 1.00;       // Max pullback past EMA (x ATR), 0=off
input int              InpRSI_Period         = 14;         // RSI period
input double           InpRSI_BuyMin         = 50.0;       // RSI min for BUY
input double           InpRSI_BuyMax         = 78.0;       // RSI max for BUY
input double           InpRSI_SellMin        = 22.0;       // RSI min for SELL
input double           InpRSI_SellMax        = 50.0;       // RSI max for SELL
input bool             InpRSI_RisingOnly     = true;       // Require RSI rising (buy) / falling (sell)
input int              InpADX_Period         = 14;         // ADX period
input bool             InpUseADXFilter       = true;       // Use ADX trend-strength filter
input double           InpADX_Min            = 18.0;       // Minimum ADX value (0-100)
input double           InpMaxDistFromEMA_ATR = 1.2;        // Max entry distance from EMA (x ATR)

//+------------------------------------------------------------------+
//| --------------------- STOP LOSS / TAKE PROFIT ------------------- |
//+------------------------------------------------------------------+
input double           InpSL_ATR             = 2.2;        // Stop loss distance (x ATR)
input double           InpRR                 = 1.5;        // Take profit = risk x R:R
input bool             InpUseSwingSL         = true;       // Use swing high/low for stop loss
input int              InpSwingLookback      = 12;         // Swing lookback (bars)
input double           InpSwingBufferATR     = 0.40;       // Swing buffer (x ATR)
input double           InpSL_MinATR          = 1.2;        // Minimum stop distance (x ATR)
input double           InpSL_MaxATR          = 5.0;        // Max stop distance (x ATR) - skip if wider

//+------------------------------------------------------------------+
//| ------------------------ MONEY MANAGEMENT ----------------------- |
//+------------------------------------------------------------------+
input double           InpRiskPercent        = 1.0;        // Risk per trade (% of equity)
input double           InpFixedLot           = 0.0;        // Fixed lot (0 = use risk %)
input int              InpMaxSlippagePoints  = 0;          // Max slippage / deviation (points), 0 = auto
input bool             InpUseMarginCheck     = true;       // Check free margin before opening

//+------------------------------------------------------------------+
//| -------------------------- TRAILING STOP ------------------------ |
//+------------------------------------------------------------------+
input bool             InpUseTrailing        = true;        // Enable trailing stop
input ENUM_TRAIL_MODE  InpTrailMode          = TRAIL_ATR;   // Trailing distance mode
input double           InpTrailStartATR      = 1.2;         // Start trailing at profit (x ATR)
input double           InpTrailDistATR       = 1.2;         // Trailing distance (x ATR) if ATR mode
input int              InpTrailDistPoints    = 200;         // Trailing distance (points) if points mode
input double           InpTrailStepATR       = 0.05;        // Min improvement (x ATR) before modifying
input bool             InpUseTrailTighten    = true;        // Tighten the trail deep in profit
input double           InpTightenStartATR    = 3.0;         // Tighten trigger at profit (x ATR)
input double           InpTightenDistATR     = 0.8;         // Tightened trail distance (x ATR)
input bool             InpDebugTrailing      = false;       // Log every trailing decision (troubleshooting)
input int              InpDebugSeconds       = 5;           // Debug log throttle (seconds)
input bool             InpUseBreakeven       = true;        // Move to breakeven
input double           InpBE_StartATR        = 1.0;         // Breakeven trigger at profit (x ATR)
input double           InpBE_OffsetATR       = 0.10;        // Breakeven offset (x ATR, covers spread+costs)

//+------------------------------------------------------------------+
//| ---------------------------- FILTERS ---------------------------- |
//+------------------------------------------------------------------+
input int              InpATR_Period         = 14;          // ATR period
input double           InpATR_MinPct         = 0.020;       // Min ATR as % of price (dead market)
input double           InpATR_MaxPct         = 0.500;       // Max ATR as % of price (chaos)
input int              InpMaxSpreadPoints    = 0;           // Max spread (points), 0 = auto
input bool             InpUseSessionFilter   = true;        // Use trading session filter
input int              InpSessionStartHour   = 7;           // Session start (server time, hour)
input int              InpSessionEndHour     = 20;          // Session end (server time, hour)
input bool             InpTradeFriday        = true;        // Allow trading on Friday
input int              InpMaxHoldBars        = 12;          // Time stop: max bars in trade (0 = off)
input int              InpCooldownBars       = 3;           // Bars to wait after a trade closes

//+------------------------------------------------------------------+
//| -------------------------- PROTECTION --------------------------- |
//+------------------------------------------------------------------+
input double           InpMaxDailyLossPct    = 3.0;         // Max daily loss (% of day-start equity)
input int              InpMaxDailyTrades     = 12;          // Max trades per day (0 = off)
input ulong            InpMagic              = 8801201;     // Magic number
input string           InpTradeComment       = "ApexScalper";// Order comment
input bool             InpShowPanel          = true;        // Show on-chart info panel

//+------------------------------------------------------------------+
//| --------------------------- GLOBALS ----------------------------- |
//+------------------------------------------------------------------+
CTrade   trade;

int      g_hATR       = INVALID_HANDLE;
int      g_hEMAPull   = INVALID_HANDLE;
int      g_hEMAFast   = INVALID_HANDLE;
int      g_hEMATrend  = INVALID_HANDLE;
int      g_hRSI       = INVALID_HANDLE;
int      g_hADX       = INVALID_HANDLE;
int      g_hTrendFast = INVALID_HANDLE;
int      g_hTrendSlow = INVALID_HANDLE;

datetime g_lastBarTime      = 0;      // last processed signal bar
datetime g_lastDbgTime      = 0;      // trailing debug log throttle
datetime g_lastEntryBarTime = 0;      // signal bar time of the last entry (cooldown)
double   g_dayStartEquity   = 0.0;
int      g_dayStamp         = -1;
int      g_tradesToday      = 0;
int      g_maxSpreadPoints  = 0;
double   g_pointValue       = 0.0;    // money per 1.0 price move per 1 lot
bool     g_initOK           = false;

//+------------------------------------------------------------------+
//| --------------------------- HELPERS ----------------------------- |
//+------------------------------------------------------------------+

//+------------------------------------------------------------------+
//| Fill a dynamic array from an indicator buffer (as series)         |
//+------------------------------------------------------------------+
bool FillBuffer(int handle, int bufferNum, int count, double &arr[])
  {
   if(handle == INVALID_HANDLE)
      return(false);
   ArraySetAsSeries(arr, true);
   ResetLastError();
   int copied = CopyBuffer(handle, bufferNum, 0, count, arr);
   if(copied != count)
      return(false);
   return(true);
  }

//+------------------------------------------------------------------+
//| Broker minimum stop distance in price units                       |
//+------------------------------------------------------------------+
double MinStopDistance()
  {
   long stops  = SymbolInfoInteger(_Symbol, SYMBOL_TRADE_STOPS_LEVEL);
   long freeze = SymbolInfoInteger(_Symbol, SYMBOL_TRADE_FREEZE_LEVEL);
   if(stops  < 0) stops  = 0;
   if(freeze < 0) freeze = 0;
   double lvl = MathMax((double)stops, (double)freeze);
   return(lvl * _Point);
  }

//+------------------------------------------------------------------+
//| Normalize a lot size to symbol min / max / step                   |
//+------------------------------------------------------------------+
double NormalizeVolume(double lots)
  {
   double minLot = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_MIN);
   double maxLot = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_MAX);
   double step   = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_STEP);

   if(minLot <= 0.0) minLot = 0.01;
   if(maxLot <= 0.0) maxLot = 100.0;
   if(step   <= 0.0) step   = 0.01;

   double v = MathFloor(lots / step) * step;
   v = NormalizeDouble(v, 8);

   if(v < minLot) v = minLot;
   if(v > maxLot) v = maxLot;

   return(NormalizeDouble(v, 8));
  }

//+------------------------------------------------------------------+
//| Money value of a 1.0 price unit move, per 1 lot                   |
//| Works on 3, 4 and 5 digit brokers (uses tick size / tick value)   |
//+------------------------------------------------------------------+
double PointValuePerLot()
  {
   if(g_pointValue > 0.0)
      return(g_pointValue);

   double tickSize  = SymbolInfoDouble(_Symbol, SYMBOL_TRADE_TICK_SIZE);
   double tickValue = SymbolInfoDouble(_Symbol, SYMBOL_TRADE_TICK_VALUE);

   if(tickSize > 0.0 && tickValue > 0.0)
      g_pointValue = tickValue / tickSize;
   else
     {
      //--- fallback for exotic / mis-configured symbols
      double contract = SymbolInfoDouble(_Symbol, SYMBOL_TRADE_CONTRACT_SIZE);
      if(contract <= 0.0) contract = 100000.0;
      g_pointValue = contract;
     }
   return(g_pointValue);
  }

//+------------------------------------------------------------------+
//| Calculate lot size from a risk % and a stop distance in price     |
//+------------------------------------------------------------------+
double CalcLots(double stopDistancePrice)
  {
   if(stopDistancePrice <= 0.0)
      return(0.0);

   if(InpFixedLot > 0.0)
      return(NormalizeVolume(InpFixedLot));

   double equity = AccountInfoDouble(ACCOUNT_EQUITY);
   if(equity <= 0.0)
      equity = AccountInfoDouble(ACCOUNT_BALANCE);
   if(equity <= 0.0)
      return(0.0);

   double riskMoney = equity * (InpRiskPercent / 100.0);
   double valuePerPrice = PointValuePerLot();

   if(valuePerPrice <= 0.0)
      return(0.0);

   double lots = riskMoney / (stopDistancePrice * valuePerPrice);
   return(NormalizeVolume(lots));
  }

//+------------------------------------------------------------------+
//| Free margin check                                                 |
//+------------------------------------------------------------------+
bool HasEnoughMargin(ENUM_ORDER_TYPE otype, double lots, double price)
  {
   if(!InpUseMarginCheck)
      return(true);

   double margin = 0.0;
   if(!OrderCalcMargin(otype, _Symbol, lots, price, margin))
      return(true);                       // cannot calculate -> let the server decide

   double freeMargin = AccountInfoDouble(ACCOUNT_MARGIN_FREE);
   return(freeMargin > margin * 1.2);
  }

//+------------------------------------------------------------------+
//| Find the ticket of our own position on the current symbol         |
//+------------------------------------------------------------------+
ulong GetOurPositionTicket()
  {
   int total = PositionsTotal();
   for(int i = total - 1; i >= 0; i--)
     {
      ulong ticket = PositionGetTicket(i);
      if(ticket == 0)
         continue;
      if(!PositionSelectByTicket(ticket))
         continue;
      if(PositionGetString(POSITION_SYMBOL) != _Symbol)
         continue;
      if((long)PositionGetInteger(POSITION_MAGIC) != (long)InpMagic)
         continue;
      return(ticket);
     }
   return(0);
  }

//+------------------------------------------------------------------+
//| Do we already have an open position from this EA?                 |
//+------------------------------------------------------------------+
bool HasOpenPosition()
  {
   return(GetOurPositionTicket() != 0);
  }

//+------------------------------------------------------------------+
//| New bar detection on the signal timeframe                         |
//+------------------------------------------------------------------+
bool IsNewBar()
  {
   datetime t = iTime(_Symbol, InpSignalTF, 0);
   if(t <= 0)
      return(false);
   if(t != g_lastBarTime)
     {
      g_lastBarTime = t;
      return(true);
     }
   return(false);
  }

//+------------------------------------------------------------------+
//| Spread filter                                                     |
//+------------------------------------------------------------------+
bool SpreadOK()
  {
   if(g_maxSpreadPoints <= 0)
      return(true);
   long spread = SymbolInfoInteger(_Symbol, SYMBOL_SPREAD);
   if(spread < 0)
      return(true);
   return((int)spread <= g_maxSpreadPoints);
  }

//+------------------------------------------------------------------+
//| Session filter (server time)                                      |
//+------------------------------------------------------------------+
bool InSession()
  {
   if(!InpUseSessionFilter)
      return(true);

   MqlDateTime dt;
   TimeCurrent(dt);

   if(!InpTradeFriday && dt.day_of_week == 5)
      return(false);

   int h = dt.hour;
   if(InpSessionStartHour == InpSessionEndHour)
      return(true);
   if(InpSessionStartHour < InpSessionEndHour)
      return(h >= InpSessionStartHour && h < InpSessionEndHour);
   //--- overnight session (e.g. 22 -> 5)
   return(h >= InpSessionStartHour || h < InpSessionEndHour);
  }

//+------------------------------------------------------------------+
//| Daily loss / trade count guard                                    |
//+------------------------------------------------------------------+
bool DailyGuardOK()
  {
   MqlDateTime dt;
   TimeCurrent(dt);
   int stamp = dt.year * 10000 + dt.mon * 100 + dt.day;

   if(stamp != g_dayStamp)
     {
      g_dayStamp       = stamp;
      g_dayStartEquity = AccountInfoDouble(ACCOUNT_EQUITY);
      g_tradesToday    = 0;
     }

   if(InpMaxDailyLossPct > 0.0 && g_dayStartEquity > 0.0)
     {
      double equity  = AccountInfoDouble(ACCOUNT_EQUITY);
      double lossPct = (g_dayStartEquity - equity) / g_dayStartEquity * 100.0;
      if(lossPct >= InpMaxDailyLossPct)
         return(false);
     }

   if(InpMaxDailyTrades > 0 && g_tradesToday >= InpMaxDailyTrades)
      return(false);

   return(true);
  }

//+------------------------------------------------------------------+
//| Higher timeframe trend bias: 1 = up, -1 = down, 0 = none          |
//+------------------------------------------------------------------+
int GetTrendBias()
  {
   if(!InpUseTrendFilter)
      return(0);

   double fast[];
   double slow[];
   if(!FillBuffer(g_hTrendFast, 0, 1, fast))
      return(0);
   if(!FillBuffer(g_hTrendSlow, 0, 1, slow))
      return(0);

   double price = iClose(_Symbol, InpTrendTF, 1);
   if(price <= 0.0)
      return(0);

   if(price > fast[0] && fast[0] > slow[0])
      return(1);
   if(price < fast[0] && fast[0] < slow[0])
      return(-1);

   return(0);
  }

//+------------------------------------------------------------------+
//| Would this candidate stop be an improvement?                      |
//+------------------------------------------------------------------+
bool IsBetterSL(long posType, double candidate, double currentSL)
  {
   if(candidate <= 0.0)
      return(false);
   if(posType == POSITION_TYPE_BUY)
      return(currentSL == 0.0 ? true : (candidate > currentSL));
   return(currentSL == 0.0 ? true : (candidate < currentSL));
  }

//+------------------------------------------------------------------+
//| MAIN SIGNAL: returns 1 = buy, -1 = sell, 0 = no trade             |
//| slDistance -> stop distance in PRICE units                        |
//+------------------------------------------------------------------+
int CheckEntry(double &slDistance)
  {
   slDistance = 0.0;

   int need   = 4;
   int look   = InpSwingLookback > 0 ? InpSwingLookback : 1;
   int barsNeeded = look + 4;

   MqlRates r[];
   ArraySetAsSeries(r, true);
   if(CopyRates(_Symbol, InpSignalTF, 0, barsNeeded, r) < barsNeeded)
      return(0);

   double atr[];
   double emaPull[];
   double emaFast[];
   double emaTrend[];
   double rsi[];
   double adx[];

   if(!FillBuffer(g_hATR,     0, need, atr))      return(0);
   if(!FillBuffer(g_hEMAPull, 0, need, emaPull))  return(0);
   if(!FillBuffer(g_hEMAFast, 0, need, emaFast))  return(0);
   if(!FillBuffer(g_hEMATrend, 0, need, emaTrend)) return(0);
   if(!FillBuffer(g_hRSI,     0, need, rsi))      return(0);
   if(!FillBuffer(g_hADX,     0, need, adx))      return(0);

   //--- we trade on the last CLOSED bar (index 1)
   int    i      = 1;
   double close1 = r[i].close;
   double open1  = r[i].open;
   double a      = atr[i];

   if(close1 <= 0.0 || a <= 0.0)
      return(0);

   //--- volatility filter: ATR as a percentage of price
   double atrPct = (a / close1) * 100.0;
   if(atrPct < InpATR_MinPct || atrPct > InpATR_MaxPct)
      return(0);

   //--- ADX trend-strength filter
   if(InpUseADXFilter && adx[i] < InpADX_Min)
      return(0);

   //--- EMA structure. Three distinct EMAs, three distinct jobs:
   //---   emaFast  (8)  - short term momentum
   //---   emaPull  (21) - the line price must pull back to and reject
   //---   emaTrend (50) - the structure the pullback must not break
   //--- emaPull > emaTrend keeps us buying dips inside an uptrend rather
   //--- than catching a falling knife. emaFast > emaTrend confirms
   //--- momentum has not rolled over while price was pulling back; it is
   //--- deliberately looser than emaFast > emaPull, which would reject
   //--- exactly the deeper pullbacks we want to buy.
   bool stackUp   = true;
   bool stackDown = true;
   if(InpUseStackFilter)
     {
      stackUp   = (emaPull[i] > emaTrend[i] && emaFast[i] > emaTrend[i]);
      stackDown = (emaPull[i] < emaTrend[i] && emaFast[i] < emaTrend[i]);
     }

   //--- RSI state
   bool rsiUp   = (rsi[i] >  InpRSI_BuyMin  && rsi[i] <  InpRSI_BuyMax);
   bool rsiDown = (rsi[i] >  InpRSI_SellMin && rsi[i] <  InpRSI_SellMax);
   if(InpRSI_RisingOnly)
     {
      rsiUp   = rsiUp   && (rsi[i] >  rsi[i + 1]);
      rsiDown = rsiDown && (rsi[i] <  rsi[i + 1]);
     }

   //--- pullback geometry
   double distEMA     = MathAbs(close1 - emaPull[i]);
   bool   notChasing  = (distEMA <= InpMaxDistFromEMA_ATR * a);

   //--- When the filter is OFF, GetTrendBias() returns 0 and both directions are allowed.
   //--- When it is ON, we must demand a clear bias: 0 (flat/choppy) blocks both directions.
   int  bias        = GetTrendBias();
   bool biasOKLong  = (InpUseTrendFilter ? (bias ==  1) : true);
   bool biasOKShort = (InpUseTrendFilter ? (bias == -1) : true);

   //---------------------------- BUY ---------------------------------
   if(biasOKLong && stackUp && rsiUp && notChasing)
     {
      double range1 = r[i].high - r[i].low;

      //--- the bar must actually reach the pullback line
      bool touched = (r[i].low <= emaPull[i]);

      //--- but not blow straight through it. A deep penetration is a
      //--- breakdown, not a pullback.
      bool controlled = true;
      if(InpMaxPenetrationATR > 0.0)
         controlled = (r[i].low >= emaPull[i] - InpMaxPenetrationATR * a);

      //--- closed back above the line, on a bullish bar
      bool rejected = (close1 > emaPull[i] && close1 > open1);

      //--- rejection quality: the bar must close in the upper part of its
      //--- range. A bounce that closes back near its low is a weak
      //--- rejection and is exactly the setup that fails.
      bool decisive = true;
      if(InpRejectionClose > 0.0 && range1 > 0.0)
         decisive = ((close1 - r[i].low) / range1 >= InpRejectionClose);

      if(touched && controlled && rejected && decisive)
        {
         double stop = InpSL_ATR * a;
         if(InpUseSwingSL)
           {
            double swingLow = r[i].low;
            for(int k = 1; k <= look; k++)
               swingLow = MathMin(swingLow, r[k].low);
            stop = close1 - (swingLow - InpSwingBufferATR * a);
           }
         double minD = InpSL_MinATR * a;
         double maxD = InpSL_MaxATR * a;
         if(stop < minD) stop = minD;
         if(stop > maxD) return(0);          // stop too wide -> skip
         if(stop > 0.0)
           {
            slDistance = stop;
            return(1);
           }
        }
     }

   //---------------------------- SELL --------------------------------
   if(biasOKShort && stackDown && rsiDown && notChasing)
     {
      double range1 = r[i].high - r[i].low;

      bool touched = (r[i].high >= emaPull[i]);

      bool controlled = true;
      if(InpMaxPenetrationATR > 0.0)
         controlled = (r[i].high <= emaPull[i] + InpMaxPenetrationATR * a);

      bool rejected = (close1 < emaPull[i] && close1 < open1);

      bool decisive = true;
      if(InpRejectionClose > 0.0 && range1 > 0.0)
         decisive = ((r[i].high - close1) / range1 >= InpRejectionClose);

      if(touched && controlled && rejected && decisive)
        {
         double stop = InpSL_ATR * a;
         if(InpUseSwingSL)
           {
            double swingHigh = r[i].high;
            for(int k = 1; k <= look; k++)
               swingHigh = MathMax(swingHigh, r[k].high);
            stop = (swingHigh + InpSwingBufferATR * a) - close1;
           }
         double minD = InpSL_MinATR * a;
         double maxD = InpSL_MaxATR * a;
         if(stop < minD) stop = minD;
         if(stop > maxD) return(0);          // stop too wide -> skip
         if(stop > 0.0)
           {
            slDistance = stop;
            return(-1);
           }
        }
     }

   return(0);
  }

//+------------------------------------------------------------------+
//| Open a market position                                            |
//+------------------------------------------------------------------+
void OpenTrade(int dir, double stopPriceDistance)
  {
   if(dir == 0 || stopPriceDistance <= 0.0)
      return;

   int    digits  = (int)SymbolInfoInteger(_Symbol, SYMBOL_DIGITS);
   double ask     = SymbolInfoDouble(_Symbol, SYMBOL_ASK);
   double bid     = SymbolInfoDouble(_Symbol, SYMBOL_BID);

   if(ask <= 0.0 || bid <= 0.0)
      return;

   double entry   = (dir > 0) ? ask : bid;
   double minStop = MinStopDistance();

   double dist = MathMax(stopPriceDistance, minStop + _Point);
   double sl   = (dir > 0) ? entry - dist        : entry + dist;
   double tp   = (dir > 0) ? entry + dist * InpRR : entry - dist * InpRR;

   sl = NormalizeDouble(sl, digits);
   tp = NormalizeDouble(tp, digits);

   double lots = CalcLots(dist);
   if(lots <= 0.0)
      return;

   ENUM_ORDER_TYPE otype = (dir > 0) ? ORDER_TYPE_BUY : ORDER_TYPE_SELL;
   if(!HasEnoughMargin(otype, lots, entry))
     {
      Print("OpenTrade: not enough free margin for ", DoubleToString(lots, 2), " lots");
      return;
     }

   bool ok = false;
   if(dir > 0)
      ok = trade.Buy(lots, _Symbol, 0.0, sl, tp, InpTradeComment);
   else
      ok = trade.Sell(lots, _Symbol, 0.0, sl, tp, InpTradeComment);

   if(!ok)
     {
      Print("OpenTrade failed. retcode=", trade.ResultRetcode(),
            " (", trade.ResultRetcodeDescription(), ")");
      return;
     }

   //--- Safety net: some brokers strip SL/TP from the deal request.
   //--- Verify the levels are really there, otherwise modify them in.
   ulong ticket = GetOurPositionTicket();
   if(ticket != 0)
     {
      PositionSelectByTicket(ticket);
      double curSL = PositionGetDouble(POSITION_SL);
      double curTP = PositionGetDouble(POSITION_TP);
      if(curSL == 0.0 || curTP == 0.0)
         trade.PositionModify(ticket, sl, tp);

      g_tradesToday++;
      g_lastEntryBarTime = iTime(_Symbol, InpSignalTF, 0);
      string sDir = "SELL";
      if(dir > 0)
         sDir = "BUY";
      Print("OPEN ", sDir, " lots=", DoubleToString(lots, 2),
            " entry=", DoubleToString(PositionGetDouble(POSITION_PRICE_OPEN), digits),
            " sl=", DoubleToString(sl, digits), " tp=", DoubleToString(tp, digits));
     }
  }

//+------------------------------------------------------------------+
//| Throttled diagnostics for the trailing logic                      |
//| Turn InpDebugTrailing on when a stop is not moving and you need   |
//| to see which gate is blocking it.                                 |
//+------------------------------------------------------------------+
void TrailDebug(string msg)
  {
   if(!InpDebugTrailing)
      return;
   datetime now = TimeCurrent();
   if(InpDebugSeconds > 0 && g_lastDbgTime != 0 && (long)(now - g_lastDbgTime) < (long)InpDebugSeconds)
      return;
   g_lastDbgTime = now;
   Print("TRAILDBG ", msg);
  }

//+------------------------------------------------------------------+
//| Trailing stop + breakeven (runs on every tick)                    |
//+------------------------------------------------------------------+
void ManageTrailing()
  {
   if(!InpUseTrailing && !InpUseBreakeven)
      return;

   ulong ticket = GetOurPositionTicket();
   if(ticket == 0)
     {
      //--- Nothing matched. Most often a magic number mismatch: the position
      //--- was opened manually or by another EA, so this EA deliberately
      //--- leaves it alone. List what actually IS on the symbol.
      int    onSym = 0;
      string found = "";
      for(int k = PositionsTotal() - 1; k >= 0; k--)
        {
         ulong tk = PositionGetTicket(k);
         if(tk == 0)
            continue;
         if(!PositionSelectByTicket(tk))
            continue;
         if(PositionGetString(POSITION_SYMBOL) != _Symbol)
            continue;
         onSym++;
         found += IntegerToString(PositionGetInteger(POSITION_MAGIC)) + " ";
        }
      TrailDebug("no position matches magic " + IntegerToString(InpMagic)
                 + " | open on " + _Symbol + " = " + IntegerToString(onSym)
                 + " | magic(s) found: " + found);
      return;
     }
   if(!PositionSelectByTicket(ticket))
     {
      TrailDebug("ticket found but PositionSelectByTicket failed");
      return;
     }

   int    digits  = (int)SymbolInfoInteger(_Symbol, SYMBOL_DIGITS);
   long   type    = PositionGetInteger(POSITION_TYPE);
   double open    = PositionGetDouble(POSITION_PRICE_OPEN);
   double curSL   = PositionGetDouble(POSITION_SL);
   double curTP   = PositionGetDouble(POSITION_TP);
   double bid     = SymbolInfoDouble(_Symbol, SYMBOL_BID);
   double ask     = SymbolInfoDouble(_Symbol, SYMBOL_ASK);

   if(bid <= 0.0 || ask <= 0.0)
      return;

   double atr[];
   if(!FillBuffer(g_hATR, 0, 3, atr))
      return;
   double a = atr[1];                       // ATR of the last closed bar (stable)
   if(a <= 0.0)
      return;

   double price      = (type == POSITION_TYPE_BUY) ? bid : ask;
   double profitDist = (type == POSITION_TYPE_BUY) ? (price - open) : (open - price);

   double newSL  = curSL;
   double minStp = MinStopDistance();

   //---------------------- BREAKEVEN --------------------------------
   //--- The offset is expressed in ATR (price units), not points, so it behaves
   //--- identically on 3, 4 and 5 digit brokers.
   if(InpUseBreakeven && profitDist >= InpBE_StartATR * a)
     {
      double offset  = InpBE_OffsetATR * a;
      double beLevel = (type == POSITION_TYPE_BUY) ? (open + offset) : (open - offset);
      if(IsBetterSL(type, beLevel, newSL))
         newSL = beLevel;
     }

   //---------------------- TRAILING ---------------------------------
   double trailDist = 0.0;
   double armAt     = 0.0;

   if(InpUseTrailing)
     {
      if(InpTrailMode == TRAIL_ATR)
        {
         trailDist = InpTrailDistATR * a;

         //--- Ratchet: deep in profit, pull the trail in so more of the
         //--- move gets banked. This is what makes a WIDE initial stop
         //--- affordable - we give the trade room to breathe at entry,
         //--- then progressively take that room away as it works.
         if(InpUseTrailTighten && profitDist >= InpTightenStartATR * a)
            trailDist = InpTightenDistATR * a;
        }
      else
         trailDist = InpTrailDistPoints * _Point;

      trailDist = MathMax(trailDist, minStp);

      //--- Invariant: a trail must not arm before it trails by at least its
      //--- own distance. If it did, the first update would place the stop at
      //--- price - trailDist while profit is smaller than trailDist, i.e.
      //--- BELOW the entry price. With a wide initial stop that snaps the
      //--- stop from several ATR away to just under entry and the trade
      //--- dies on the next ordinary retrace.
      armAt = MathMax(InpTrailStartATR * a, trailDist);

      if(profitDist >= armAt)
        {
         double cand = (type == POSITION_TYPE_BUY) ? (price - trailDist) : (price + trailDist);
         if(IsBetterSL(type, cand, newSL))
            newSL = cand;
        }
     }

   TrailDebug("ticket=" + IntegerToString(ticket)
              + " " + ((type == POSITION_TYPE_BUY) ? "BUY" : "SELL")
              + " open=" + DoubleToString(open, digits)
              + " price=" + DoubleToString(price, digits)
              + " curSL=" + DoubleToString(curSL, digits)
              + " | profit=" + DoubleToString(profitDist, digits)
              + " (" + DoubleToString(profitDist / a, 2) + "xATR)"
              + " | atr=" + DoubleToString(a, digits)
              + " armAt=" + DoubleToString(armAt, digits)
              + " (" + DoubleToString(armAt / a, 2) + "xATR)"
              + " trailDist=" + DoubleToString(trailDist, digits)
              + " minStp=" + DoubleToString(minStp, digits)
              + " (" + DoubleToString(minStp / a, 2) + "xATR)"
              + " | newSL=" + DoubleToString(newSL, digits)
              + (profitDist < armAt ? "  <== NOT ARMED" : "  <== armed")
              + (minStp > trailDist ? "  <== BROKER MINIMUM OVERRODE TRAIL DISTANCE" : ""));

   if(newSL == curSL)
      return;

   //--- only modify if the improvement is meaningful (ATR relative -> digit agnostic)
   if(curSL != 0.0 && MathAbs(newSL - curSL) < InpTrailStepATR * a)
      return;

   //--- never place the stop closer than the broker allows
   if(type == POSITION_TYPE_BUY)
     {
      double limit = bid - minStp - _Point;
      if(newSL > limit)
         newSL = limit;
     }
   else
     {
      double limit = ask + minStp + _Point;
      if(newSL < limit)
         newSL = limit;
     }

   newSL = NormalizeDouble(newSL, digits);

   if(curSL != 0.0 && MathAbs(newSL - NormalizeDouble(curSL, digits)) < _Point)
      return;

   if(type == POSITION_TYPE_BUY  && newSL >= bid) return;
   if(type == POSITION_TYPE_SELL && newSL <= ask) return;

   if(!trade.PositionModify(ticket, newSL, curTP))
      Print("PositionModify failed. retcode=", trade.ResultRetcode(),
            " (", trade.ResultRetcodeDescription(), ")");
  }

//+------------------------------------------------------------------+
//| Time based exit (scalps should not be held forever)               |
//+------------------------------------------------------------------+
void CheckTimeExit()
  {
   if(InpMaxHoldBars <= 0)
      return;

   ulong ticket = GetOurPositionTicket();
   if(ticket == 0)
      return;
   if(!PositionSelectByTicket(ticket))
      return;

   datetime openTime = (datetime)PositionGetInteger(POSITION_TIME);
   if(openTime <= 0)
      return;

   int shift = iBarShift(_Symbol, InpSignalTF, openTime);
   if(shift < 0)
      return;

   if(shift >= InpMaxHoldBars)
     {
      if(!trade.PositionClose(ticket))
         Print("Time stop close failed. retcode=", trade.ResultRetcode(),
               " (", trade.ResultRetcodeDescription(), ")");
      else
         Print("TIME STOP: position closed after ", shift, " bars");
     }
  }

//+------------------------------------------------------------------+
//| Cooldown after the last entry                                     |
//+------------------------------------------------------------------+
bool CooldownOK()
  {
   if(InpCooldownBars <= 0 || g_lastEntryBarTime == 0)
      return(true);

   int shift = iBarShift(_Symbol, InpSignalTF, g_lastEntryBarTime);
   if(shift < 0)
      return(true);

   return(shift >= InpCooldownBars);
  }

//+------------------------------------------------------------------+
//| On-chart information panel                                        |
//+------------------------------------------------------------------+
void UpdatePanel()
  {
   if(!InpShowPanel)
      return;

   long   spread = SymbolInfoInteger(_Symbol, SYMBOL_SPREAD);
   string sSpread;
   if(spread >= 0)
      sSpread = IntegerToString(spread);
   else
      sSpread = "n/a";

   //--- Resolve every boolean to a plain string BEFORE it is concatenated.
   //--- In MQL5 "text" + (cond ? "A" : "B") is a precedence trap: + binds
   //--- tighter than ?:, so a missing grouping parses as ("text" + bool)
   //--- and silently coerces the bool into a string.
   string sBias = "OFF";
   if(InpUseTrendFilter)
     {
      int b = GetTrendBias();
      if(b > 0)      sBias = "UP";
      else if(b < 0) sBias = "DOWN";
      else           sBias = "FLAT";
     }

   string sSession = "CLOSED";
   if(InSession())
      sSession = "OPEN";

   string sGuard = "BLOCKED";
   if(DailyGuardOK())
      sGuard = "OK";

   string sPos = "none";
   if(HasOpenPosition())
      sPos = "OPEN";

   string txt = "";
   txt += "=== ApexScalper v1.00 ===\n";
   txt += "Symbol        : " + _Symbol + "  (digits: " + IntegerToString((int)SymbolInfoInteger(_Symbol, SYMBOL_DIGITS)) + ")\n";
   txt += "Signal TF     : " + EnumToString(InpSignalTF) + "\n";
   txt += "Trend TF      : " + EnumToString(InpTrendTF) + "   bias: " + sBias + "\n";
   txt += "Spread        : " + sSpread + " pts  (max " + IntegerToString(g_maxSpreadPoints) + ")\n";
   txt += "Session       : " + sSession + "\n";
   txt += "Daily guard   : " + sGuard + "   trades today: " + IntegerToString(g_tradesToday) + "\n";
   txt += "Position      : " + sPos + "\n";

   Comment(txt);
  }

//+------------------------------------------------------------------+
//| Expert initialization                                             |
//+------------------------------------------------------------------+
int OnInit()
  {
   //---------------- input sanity -----------------------------------
   if(InpSL_ATR <= 0.0 || InpRR <= 0.0)
     {
      Print("OnInit: InpSL_ATR and InpRR must be > 0");
      return(INIT_PARAMETERS_INCORRECT);
     }
   if(InpRiskPercent < 0.0)
     {
      Print("OnInit: InpRiskPercent must be >= 0");
      return(INIT_PARAMETERS_INCORRECT);
     }
   if(InpTrendEMAFast >= InpTrendEMASlow)
     {
      Print("OnInit: InpTrendEMAFast must be smaller than InpTrendEMASlow");
      return(INIT_PARAMETERS_INCORRECT);
     }
   if(InpRejectionClose < 0.0 || InpRejectionClose >= 1.0)
     {
      Print("OnInit: InpRejectionClose must be 0 (off) or between 0 and 1");
      return(INIT_PARAMETERS_INCORRECT);
     }
   if(InpSL_MinATR > InpSL_MaxATR)
     {
      Print("OnInit: InpSL_MinATR must not exceed InpSL_MaxATR");
      return(INIT_PARAMETERS_INCORRECT);
     }
   if(InpUseTrailing && InpTrailMode == TRAIL_ATR && InpTrailDistATR <= 0.0)
     {
      Print("OnInit: InpTrailDistATR must be > 0 in ATR trailing mode");
      return(INIT_PARAMETERS_INCORRECT);
     }
   if(InpUseTrailTighten && InpTightenDistATR <= 0.0)
     {
      Print("OnInit: InpTightenDistATR must be > 0 when tightening is on");
      return(INIT_PARAMETERS_INCORRECT);
     }

   //---------------- symbol -----------------------------------------
   if(!SymbolInfoInteger(_Symbol, SYMBOL_SELECT))
      SymbolSelect(_Symbol, true);

   if(!SymbolInfoInteger(_Symbol, SYMBOL_TRADE_MODE))
     {
      Print("OnInit: trading is disabled for ", _Symbol);
      return(INIT_FAILED);
     }

   int digits = (int)SymbolInfoInteger(_Symbol, SYMBOL_DIGITS);

   //---------------- auto max spread + slippage ----------------------
   //--- A "point" means something different on every digit type, so the
   //--- tolerances are scaled to the quote precision the broker actually uses.
   //---   5/6 digits -> 1 point = 0.00001 (0.1 pip) -> allow 20 points = 2.0 pip
   //---   3/4 digits -> 1 point = 0.001/0.0001     -> allow  3 points
   if(InpMaxSpreadPoints > 0)
      g_maxSpreadPoints = InpMaxSpreadPoints;
   else
      g_maxSpreadPoints = (digits == 5 || digits == 6) ? 20 : 3;

   int maxSlippage = InpMaxSlippagePoints;
   if(maxSlippage <= 0)
      maxSlippage = (digits == 5 || digits == 6) ? 20 : 3;

   //---------------- trade object -----------------------------------
   trade.SetExpertMagicNumber(InpMagic);
   trade.SetDeviationInPoints((ulong)maxSlippage);
   trade.SetTypeFillingBySymbol(_Symbol);
   trade.SetAsyncMode(false);

   //---------------- indicator handles ------------------------------
   g_hATR       = iATR(_Symbol,  InpSignalTF, InpATR_Period);
   g_hEMAPull   = iMA(_Symbol,   InpSignalTF, InpEMA_Pullback, 0, MODE_EMA, PRICE_CLOSE);
   g_hEMAFast   = iMA(_Symbol,   InpSignalTF, InpEMA_Fast,     0, MODE_EMA, PRICE_CLOSE);
   g_hEMATrend  = iMA(_Symbol,   InpSignalTF, InpEMA_Trend,    0, MODE_EMA, PRICE_CLOSE);
   g_hRSI       = iRSI(_Symbol,  InpSignalTF, InpRSI_Period,   PRICE_CLOSE);
   g_hADX       = iADX(_Symbol,  InpSignalTF, InpADX_Period);
   g_hTrendFast = iMA(_Symbol,   InpTrendTF,  InpTrendEMAFast, 0, MODE_EMA, PRICE_CLOSE);
   g_hTrendSlow = iMA(_Symbol,   InpTrendTF,  InpTrendEMASlow, 0, MODE_EMA, PRICE_CLOSE);

   if(g_hATR       == INVALID_HANDLE || g_hEMAPull   == INVALID_HANDLE ||
      g_hEMAFast   == INVALID_HANDLE || g_hEMATrend  == INVALID_HANDLE ||
      g_hRSI       == INVALID_HANDLE || g_hADX       == INVALID_HANDLE ||
      g_hTrendFast == INVALID_HANDLE || g_hTrendSlow == INVALID_HANDLE)
     {
      Print("OnInit: failed to create one or more indicator handles. Error=", GetLastError());
      return(INIT_FAILED);
     }

   //---------------- status -----------------------------------------
   double tickSize  = SymbolInfoDouble(_Symbol, SYMBOL_TRADE_TICK_SIZE);
   double tickValue = SymbolInfoDouble(_Symbol, SYMBOL_TRADE_TICK_VALUE);

   //--- resolve to plain strings first, see the note in UpdatePanel()
   string sDigitsNote = "standard";
   if(digits == 3)
      sDigitsNote = "3-DIGIT BROKER detected";

   string sTrailing = "OFF";
   if(InpUseTrailing)
      sTrailing = "ON";

   PrintFormat("ApexScalper v1.00 initialized on %s", _Symbol);
   PrintFormat("  digits=%d  point=%.8f  digits-aware: %s",
               digits, _Point, sDigitsNote);
   PrintFormat("  tick size=%.8f  tick value=%.4f  value per 1.0 price move/lot=%.2f",
               tickSize, tickValue, PointValuePerLot());
   PrintFormat("  signal TF=%s  trend TF=%s  max spread=%d points",
               EnumToString(InpSignalTF), EnumToString(InpTrendTF), g_maxSpreadPoints);
   PrintFormat("  risk=%.2f%%  SL=%.2fx ATR (clamped %.1f-%.1f)  R:R=1:%.2f",
               InpRiskPercent, InpSL_ATR, InpSL_MinATR, InpSL_MaxATR, InpRR);

   string sTighten = "OFF";
   if(InpUseTrailing && InpUseTrailTighten)
      sTighten = StringFormat("ON at %.1fx ATR -> %.1fx ATR",
                              InpTightenStartATR, InpTightenDistATR);

   PrintFormat("  trailing=%s  start=%.1fx ATR  dist=%.1fx ATR  tighten=%s",
               sTrailing, InpTrailStartATR, InpTrailDistATR, sTighten);

   //--- Broker minimum stop distance vs our ATR scaled distances. On a
   //--- 3 digit broker this is the usual reason a trailing stop appears to
   //--- do nothing: if the broker refuses stops closer than N points and
   //--- that floor is wider than the ATR distance we asked for, the trail
   //--- cannot arm until profit exceeds the broker minimum.
   double atrNow[];
   double atrVal = 0.0;
   if(FillBuffer(g_hATR, 0, 2, atrNow))
      atrVal = atrNow[1];

   double initMinStp = MinStopDistance();
   PrintFormat("  ATR(%d)=%.8f   broker min stop distance=%.8f (%.1f points)",
               InpATR_Period, atrVal, initMinStp, initMinStp / _Point);

   if(atrVal > 0.0)
     {
      PrintFormat("  broker min stop distance = %.2f x ATR", initMinStp / atrVal);

      if(initMinStp > InpTrailDistATR * atrVal)
         PrintFormat("  WARNING: broker min stop %.8f is WIDER than trail distance %.8f",
                     initMinStp, InpTrailDistATR * atrVal);

      if(initMinStp > InpSL_MinATR * atrVal)
         PrintFormat("  WARNING: broker min stop %.8f is WIDER than InpSL_MinATR %.8f",
                     initMinStp, InpSL_MinATR * atrVal);
     }

   g_initOK      = true;
   g_lastBarTime = iTime(_Symbol, InpSignalTF, 0);

   //--- draw the panel immediately, the first OnTick will not see a new bar
   UpdatePanel();

   return(INIT_SUCCEEDED);
  }

//+------------------------------------------------------------------+
//| Expert deinitialization                                           |
//+------------------------------------------------------------------+
void OnDeinit(const int reason)
  {
   if(g_hATR       != INVALID_HANDLE) IndicatorRelease(g_hATR);
   if(g_hEMAPull   != INVALID_HANDLE) IndicatorRelease(g_hEMAPull);
   if(g_hEMAFast   != INVALID_HANDLE) IndicatorRelease(g_hEMAFast);
   if(g_hEMATrend  != INVALID_HANDLE) IndicatorRelease(g_hEMATrend);
   if(g_hRSI       != INVALID_HANDLE) IndicatorRelease(g_hRSI);
   if(g_hADX       != INVALID_HANDLE) IndicatorRelease(g_hADX);
   if(g_hTrendFast != INVALID_HANDLE) IndicatorRelease(g_hTrendFast);
   if(g_hTrendSlow != INVALID_HANDLE) IndicatorRelease(g_hTrendSlow);

   Comment("");
  }

//+------------------------------------------------------------------+
//| Expert tick function                                              |
//+------------------------------------------------------------------+
void OnTick()
  {
   if(!g_initOK)
      return;

   //--- Trailing stop must react to price, so it runs on EVERY tick.
   ManageTrailing();

   //--- Everything below is bar based: it only needs to run once per signal bar.
   if(!IsNewBar())
      return;

   CheckTimeExit();
   UpdatePanel();

   if(!InSession())
      return;
   if(!SpreadOK())
      return;
   if(!DailyGuardOK())
      return;
   if(!CooldownOK())
      return;

   if(HasOpenPosition())
      return;

   double stopDistance = 0.0;
   int    dir = CheckEntry(stopDistance);

   if(dir != 0)
      OpenTrade(dir, stopDistance);
  }
//+------------------------------------------------------------------+
