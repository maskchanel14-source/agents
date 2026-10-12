//+------------------------------------------------------------------+
//|                                                XauUsdScalper.mq5 |
//|                     XAUUSD scalping EA (M1/M5, session-aware)     |
//+------------------------------------------------------------------+
//| Strategy (spec.md D1): EMA(9/21) cross + RSI(7) confirmation on   |
//| CLOSED bars, ATR volatility gate, London/NY session filter,       |
//| ATR-scaled SL/TP (1.5x / 2.25x = 1.5R), break-even at +1R,        |
//| ATR trailing after BE, stale-trade time exit (before BE only).    |
//|                                                                   |
//| Risk layer (spec.md D2, llm-trading-agent-security):              |
//|   - fixed-fractional risk sizing (default 0.5%/trade)             |
//|   - daily-loss circuit breaker (equity vs day-start, per tick)    |
//|   - consecutive-loss circuit breaker (4)                           |
//|   - max 10 entries/day, max 1 position, max spread gate           |
//|   - pre-send margin simulation, slippage cap, magic isolation     |
//|   - audit log of every decision (entries, exits, halts, failures) |
//|                                                                   |
//| Built under the GAN harness (planner -> generator -> ruthless     |
//| evaluator) and gated by the Santa Method (two independent         |
//| reviewers, both must pass). See spec.md, REVIEW.md, README.md.    |
//+------------------------------------------------------------------+
#property copyright   "maskchanel14"
#property version     "1.00"
#property description "XAUUSD scalping EA: EMA cross + RSI confirm + ATR gate, session filter,"
#property description "ATR SL/TP, break-even, trailing, daily-loss circuit breaker, R-multiple stats."

#include <Trade\Trade.mqh>

//=== Strategy ======================================================
input group "=== Strategy ==="
input ENUM_TIMEFRAMES InpTimeframe       = PERIOD_CURRENT; // Timeframe (M5 recommended)
input int             InpEmaFast         = 9;              // Fast EMA period
input int             InpEmaSlow         = 21;             // Slow EMA period
input int             InpRsiPeriod       = 7;              // RSI period
input int             InpRsiLevel        = 50;             // RSI confirmation level
input int             InpAtrPeriod       = 14;             // ATR period
input double          InpAtrMin          = 0.30;           // Min ATR ($) - skip dead market
input double          InpAtrMax          = 4.00;           // Max ATR ($) - skip spikes
input double          InpSlAtrMult       = 1.50;           // Stop loss = ATR x mult
input double          InpTpAtrMult       = 2.25;           // Take profit = ATR x mult
input bool            InpUseBreakEven    = true;           // Break-even stop
input double          InpBreakEvenR      = 1.00;           // Move to BE after +N R
input double          InpTrailAtrMult    = 1.50;           // Trailing = ATR x mult (after BE)
input int             InpTimeExitBars    = 12;             // Time exit after N bars (0=off, before BE only)

//=== Session & Filters =============================================
input group "=== Session & Filters ==="
input int             InpSessionStart    = 7;              // Session start hour (server, 0-23)
input int             InpSessionEnd      = 16;             // Session end hour (server, 0-23)
input double          InpMaxSpreadPts    = 45;             // Max spread (points) to enter
input int             InpFridayBlockHour = 20;             // No new entries Friday >= hour (0=off)

//=== Risk & Circuit Breakers =======================================
input group "=== Risk & Circuit Breakers ==="
input double          InpRiskPercent     = 0.50;           // Risk per trade (% of equity)
input double          InpMaxDailyLossPct = 2.00;           // Daily loss halt (% of day-start equity)
input int             InpMaxConsecLosses = 4;              // Halt after N consecutive losses
input int             InpMaxDailyTrades  = 10;             // Max entries per day
input double          InpMaxLot          = 5.00;           // Max lot cap
input int             InpSlippagePts     = 20;             // Max slippage (points)

//=== General =======================================================
input group "=== General ==="
input long            InpMagic           = 20261012;       // Magic number
input string          InpComment         = "XAUUSD-SCALP"; // Order comment
input bool            InpVerbose         = false;          // Log every skipped gate

//--- objects & handles
CTrade trade;
int    hEmaFast = INVALID_HANDLE;
int    hEmaSlow = INVALID_HANDLE;
int    hRsi     = INVALID_HANDLE;
int    hAtr     = INVALID_HANDLE;

ENUM_TIMEFRAMES g_tf        = PERIOD_CURRENT;
int      g_periodSec        = 0;

//--- day / circuit-breaker state
int      g_dayKey           = 0;
double   g_dayStartEquity   = 0.0;
int      g_dayTrades        = 0;
int      g_consecLosses     = 0;
bool     g_haltedToday      = false;
string   g_haltReason       = "";

//--- per-trade state
datetime g_lastBarTime      = 0;
datetime g_entryTime        = 0;
double   g_r0               = 0.0;   // initial SL distance (price units)
double   g_riskAmount       = 0.0;   // risk of current/last trade in account currency
bool     g_beDone           = false;

//--- session stats (risk-metrics-calculation: multiple metrics)
int      g_totalClosed      = 0;
int      g_wins             = 0;
double   g_sumWinR          = 0.0;
double   g_sumLossR         = 0.0;   // positive magnitude of losses, in R
int      g_maxConsecLoss    = 0;

//+------------------------------------------------------------------+
//| Read one indicator value at a bar shift (as-series safe).        |
//+------------------------------------------------------------------+
double Buf1(const int handle, const int shift)
  {
   double b[];
   ArraySetAsSeries(b, true);
   if(CopyBuffer(handle, 0, shift, 1, b) != 1)
      return(EMPTY_VALUE);
   return(b[0]);
  }

//+------------------------------------------------------------------+
//| Loss in account currency for 1.0 lot if price moves `dist`.      |
//+------------------------------------------------------------------+
double LossPerLot(const double dist)
  {
   double tickSize  = SymbolInfoDouble(_Symbol, SYMBOL_TRADE_TICK_SIZE);
   double tickValue = SymbolInfoDouble(_Symbol, SYMBOL_TRADE_TICK_VALUE);
   if(tickSize <= 0.0 || tickValue <= 0.0 || dist <= 0.0)
      return(0.0);
   return(dist / tickSize * tickValue);
  }

//+------------------------------------------------------------------+
//| Position sizing: fixed-fractional risk (risk-manager skill).     |
//| Returns 0.0 when the risk would be below the minimum lot.        |
//+------------------------------------------------------------------+
double CalcLots(const double slDist)
  {
   double riskMoney  = AccountInfoDouble(ACCOUNT_EQUITY) * InpRiskPercent / 100.0;
   double lossPerLot = LossPerLot(slDist);
   if(lossPerLot <= 0.0 || riskMoney <= 0.0)
      return(0.0);

   double lots = riskMoney / lossPerLot;
   double minL = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_MIN);
   double maxL = MathMin(SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_MAX), InpMaxLot);
   double step = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_STEP);
   if(step > 0.0)
      lots = MathFloor(lots / step) * step;
   lots = NormalizeDouble(lots, 2);

   if(lots > maxL)
     {
      Print("WARNING: risk-based lot ", DoubleToString(riskMoney / lossPerLot, 2),
            " exceeds cap ", DoubleToString(maxL, 2),
            " - capping (actual risk will be > InpRiskPercent)");
      lots = maxL;
     }
   if(lots < minL)
      return(0.0);
   return(lots);
  }

//+------------------------------------------------------------------+
//| Pre-send simulation (llm-trading-agent-security skill).          |
//| Every check that can make the order fail is run BEFORE sending.  |
//+------------------------------------------------------------------+
bool PreFlightCheck(const ENUM_ORDER_TYPE type, const double lots,
                    const double price, const double sl, const double tp)
  {
   long mode = SymbolInfoInteger(_Symbol, SYMBOL_TRADE_MODE);
   if(mode != SYMBOL_TRADE_MODE_FULL)
     {
      Skip("symbol trade mode != FULL");
      return(false);
     }
   if(!MQLInfoInteger(MQL_TRADE_ALLOWED) || !TerminalInfoInteger(TERMINAL_TRADE_ALLOWED))
     {
      Skip("trading disabled (terminal or EA algo-trading checkbox)");
      return(false);
     }
   double margin = 0.0;
   if(!OrderCalcMargin(type, _Symbol, lots, price, margin))
     {
      Skip("OrderCalcMargin failed");
      return(false);
     }
   double freeMargin = AccountInfoDouble(ACCOUNT_MARGIN_FREE);
   if(margin > freeMargin * 0.5)
     {
      Skip(StringFormat("simulated margin %.2f would exceed 50%% of free margin %.2f",
                        margin, freeMargin));
      return(false);
     }
   double stopsDist = (double)SymbolInfoInteger(_Symbol, SYMBOL_TRADE_STOPS_LEVEL) * _Point;
   if(MathAbs(price - sl) < stopsDist || MathAbs(tp - price) < stopsDist)
     {
      Skip("SL/TP inside broker stops level");
      return(false);
     }
   if(lots < SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_MIN) ||
      lots > SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_MAX))
     {
      Skip("lot outside broker volume limits");
      return(false);
     }
   return(true);
  }

//+------------------------------------------------------------------+
//| Verbose-only gate logging.                                        |
//+------------------------------------------------------------------+
void Skip(const string reason)
  {
   if(InpVerbose)
      Print("SKIP: ", reason);
  }

//+------------------------------------------------------------------+
//| Server-time session window with overnight wrap support.          |
//+------------------------------------------------------------------+
bool InSession(const int hour)
  {
   if(InpSessionStart == InpSessionEnd)
      return(true);
   if(InpSessionStart < InpSessionEnd)
      return(hour >= InpSessionStart && hour < InpSessionEnd);
   return(hour >= InpSessionStart || hour < InpSessionEnd);
  }

//+------------------------------------------------------------------+
//| Filling mode negotiated from broker capability flags.            |
//+------------------------------------------------------------------+
ENUM_ORDER_TYPE_FILLING GetFillingMode()
  {
   long fm = SymbolInfoInteger(_Symbol, SYMBOL_FILLING_MODE);
   if((fm & SYMBOL_FILLING_FOK) == SYMBOL_FILLING_FOK)
      return(ORDER_FILLING_FOK);
   if((fm & SYMBOL_FILLING_IOC) == SYMBOL_FILLING_IOC)
      return(ORDER_FILLING_IOC);
   return(ORDER_FILLING_RETURN);
  }

ENUM_TIMEFRAMES EaTf()
  {
   return(g_tf);
  }

//+------------------------------------------------------------------+
//| Count this EA's open positions on this symbol.                   |
//+------------------------------------------------------------------+
int CountPositions()
  {
   int n = 0;
   for(int i = PositionsTotal() - 1; i >= 0; i--)
     {
      if(PositionGetTicket(i) == 0)
         continue;
      if(PositionGetString(POSITION_SYMBOL) != _Symbol)
         continue;
      if((long)PositionGetInteger(POSITION_MAGIC) != InpMagic)
         continue;
      n++;
     }
   return(n);
  }

//+------------------------------------------------------------------+
//| Daily rollover: reset day counters (server date).                |
//+------------------------------------------------------------------+
void UpdateDay()
  {
   MqlDateTime dt;
   TimeToStruct(TimeCurrent(), dt);
   int dayKey = dt.year * 10000 + dt.mon * 100 + dt.day;
   if(dayKey != g_dayKey)
     {
      g_dayKey         = dayKey;
      g_dayStartEquity = AccountInfoDouble(ACCOUNT_EQUITY);
      g_dayTrades      = 0;
      g_consecLosses   = 0;
      g_haltedToday    = false;
      g_haltReason     = "";
      Print("=== New trading day ", TimeToString(TimeCurrent(), TIME_DATE),
            " | day-start equity: ", DoubleToString(g_dayStartEquity, 2), " ===");
     }
  }

//+------------------------------------------------------------------+
//| Circuit breakers, evaluated EVERY TICK on live equity            |
//| (llm-trading-agent-security: breakers halt on drawdown/state).   |
//+------------------------------------------------------------------+
void UpdateHaltState()
  {
   if(g_haltedToday)
      return;
   double equity = AccountInfoDouble(ACCOUNT_EQUITY);
   if(g_dayStartEquity > 0.0)
     {
      double dayPnlPct = (equity - g_dayStartEquity) / g_dayStartEquity * 100.0;
      if(dayPnlPct <= -InpMaxDailyLossPct)
        {
         g_haltedToday = true;
         g_haltReason  = StringFormat("daily loss %.2f%% <= -%.2f%%",
                                      dayPnlPct, InpMaxDailyLossPct);
         Print("CIRCUIT BREAKER: halt new entries today - ", g_haltReason);
         return;
        }
     }
   if(g_consecLosses >= InpMaxConsecLosses)
     {
      g_haltedToday = true;
      g_haltReason  = StringFormat("%d consecutive losses >= %d",
                                   g_consecLosses, InpMaxConsecLosses);
      Print("CIRCUIT BREAKER: halt new entries today - ", g_haltReason);
     }
  }

//+------------------------------------------------------------------+
//| Entry evaluation - runs once per new EA-timeframe bar.           |
//+------------------------------------------------------------------+
void TryEnterOnNewBar()
  {
   if(CountPositions() > 0)
     {
      Skip("position already open");
      return;
     }
   if(g_haltedToday)
     {
      Skip("halted: " + g_haltReason);
      return;
     }
   if(g_dayTrades >= InpMaxDailyTrades)
     {
      Skip("max daily trades reached");
      return;
     }

   MqlDateTime dt;
   TimeToStruct(TimeCurrent(), dt);
   if(dt.day_of_week == 0 || dt.day_of_week == 6)
     {
      Skip("weekend");
      return;
     }
   if(!InSession(dt.hour))
     {
      Skip("outside session");
      return;
     }
   if(InpFridayBlockHour > 0 && dt.day_of_week == 5 && dt.hour >= InpFridayBlockHour)
     {
      Skip("Friday block hour");
      return;
     }

   long spread = SymbolInfoInteger(_Symbol, SYMBOL_SPREAD);
   if(spread > (long)InpMaxSpreadPts)
     {
      Skip(StringFormat("spread %d > max %d pts", (int)spread, (int)InpMaxSpreadPts));
      return;
     }

   //--- volatility gate on the LAST CLOSED bar (no look-ahead)
   double atr = Buf1(hAtr, 1);
   if(atr == EMPTY_VALUE || atr <= 0.0)
     {
      Skip("ATR not ready");
      return;
     }
   if(atr < InpAtrMin)
     {
      Skip(StringFormat("ATR %.2f < min %.2f (dead market)", atr, InpAtrMin));
      return;
     }
   if(atr > InpAtrMax)
     {
      Skip(StringFormat("ATR %.2f > max %.2f (spike/news)", atr, InpAtrMax));
      return;
     }

   //--- signal on CLOSED bars only (shift 1 = last closed, shift 2 = before)
   double emaF1 = Buf1(hEmaFast, 1);
   double emaF2 = Buf1(hEmaFast, 2);
   double emaS1 = Buf1(hEmaSlow, 1);
   double emaS2 = Buf1(hEmaSlow, 2);
   double rsi1  = Buf1(hRsi, 1);
   if(emaF1 == EMPTY_VALUE || emaF2 == EMPTY_VALUE || emaS1 == EMPTY_VALUE ||
      emaS2 == EMPTY_VALUE || rsi1 == EMPTY_VALUE)
     {
      Skip("indicators not ready");
      return;
     }

   bool upCross   = (emaF2 <= emaS2 && emaF1 > emaS1);
   bool downCross = (emaF2 >= emaS2 && emaF1 < emaS1);
   if(!upCross && !downCross)
     {
      Skip("no EMA cross");
      return;
     }
   if(upCross && rsi1 <= InpRsiLevel)
     {
      Skip("RSI confirm missing (long)");
      return;
     }
   if(downCross && rsi1 >= InpRsiLevel)
     {
      Skip("RSI confirm missing (short)");
      return;
     }

   double ask = SymbolInfoDouble(_Symbol, SYMBOL_ASK);
   double bid = SymbolInfoDouble(_Symbol, SYMBOL_BID);
   if(ask <= 0.0 || bid <= 0.0)
     {
      Skip("invalid quotes");
      return;
     }

   double stopsDist = MathMax((double)SymbolInfoInteger(_Symbol, SYMBOL_TRADE_STOPS_LEVEL) * _Point,
                              10.0 * _Point);
   double slDist = MathMax(InpSlAtrMult * atr, stopsDist);
   double tpDist = MathMax(InpTpAtrMult * atr, stopsDist);

   if(upCross)
     {
      double sl   = NormalizeDouble(ask - slDist, _Digits);
      double tp   = NormalizeDouble(ask + tpDist, _Digits);
      double lots = CalcLots(slDist);
      if(lots <= 0.0)
        {
         Skip("risk too small for min lot");
         return;
        }
      if(!PreFlightCheck(ORDER_TYPE_BUY, lots, ask, sl, tp))
         return;

      g_entryTime  = TimeCurrent();
      g_r0         = slDist;
      g_beDone     = false;
      g_riskAmount = LossPerLot(slDist) * lots;
      if(trade.Buy(lots, _Symbol, 0.0, sl, tp, InpComment))
         Print(StringFormat("OPEN BUY %.2f @ ask %.2f | SL %.2f (-%.2f) | TP %.2f (+%.2f) | risk %.2f (%.2f%% of equity)",
                            lots, ask, sl, slDist, tp, tpDist, g_riskAmount,
                            (AccountInfoDouble(ACCOUNT_EQUITY) > 0.0 ?
                             g_riskAmount / AccountInfoDouble(ACCOUNT_EQUITY) * 100.0 : 0.0)));
      else
        {
         // No blind re-send by design: REQUOTE/price moved -> this signal is
         // skipped; the next bar is re-evaluated fresh (REVIEW.md, B1).
         Print("BUY FAILED retcode=", trade.ResultRetcode(), " ",
               trade.ResultRetcodeDescription(), " - state reset");
         ResetTradeState();
        }
     }
   else
     {
      double sl   = NormalizeDouble(bid + slDist, _Digits);
      double tp   = NormalizeDouble(bid - tpDist, _Digits);
      double lots = CalcLots(slDist);
      if(lots <= 0.0)
        {
         Skip("risk too small for min lot");
         return;
        }
      if(!PreFlightCheck(ORDER_TYPE_SELL, lots, bid, sl, tp))
         return;

      g_entryTime  = TimeCurrent();
      g_r0         = slDist;
      g_beDone     = false;
      g_riskAmount = LossPerLot(slDist) * lots;
      if(trade.Sell(lots, _Symbol, 0.0, sl, tp, InpComment))
         Print(StringFormat("OPEN SELL %.2f @ bid %.2f | SL %.2f (+%.2f) | TP %.2f (-%.2f) | risk %.2f (%.2f%% of equity)",
                            lots, bid, sl, slDist, tp, tpDist, g_riskAmount,
                            (AccountInfoDouble(ACCOUNT_EQUITY) > 0.0 ?
                             g_riskAmount / AccountInfoDouble(ACCOUNT_EQUITY) * 100.0 : 0.0)));
      else
        {
         // No blind re-send by design: REQUOTE/price moved -> this signal is
         // skipped; the next bar is re-evaluated fresh (REVIEW.md, B1).
         Print("SELL FAILED retcode=", trade.ResultRetcode(), " ",
               trade.ResultRetcodeDescription(), " - state reset");
         ResetTradeState();
        }
     }
  }

//+------------------------------------------------------------------+
//| Defensive per-trade state reset (failed send / stale state).     |
//+------------------------------------------------------------------+
void ResetTradeState()
  {
   g_beDone     = false;
   g_r0         = 0.0;
   g_riskAmount = 0.0;
   g_entryTime  = 0;
  }

//+------------------------------------------------------------------+
//| Per-tick management: time exit, break-even, ATR trailing.        |
//+------------------------------------------------------------------+
void ManageOpenPositions()
  {
   for(int i = PositionsTotal() - 1; i >= 0; i--)
     {
      if(PositionGetTicket(i) == 0)
         continue;
      if(PositionGetString(POSITION_SYMBOL) != _Symbol)
         continue;
      if((long)PositionGetInteger(POSITION_MAGIC) != InpMagic)
         continue;

      long   ptype = PositionGetInteger(POSITION_TYPE);
      double open  = PositionGetDouble(POSITION_PRICE_OPEN);
      double curSl = PositionGetDouble(POSITION_SL);
      double curTp = PositionGetDouble(POSITION_TP);
      double atr   = Buf1(hAtr, 0);
      if(atr == EMPTY_VALUE || atr <= 0.0)
         continue;

      double bid     = SymbolInfoDouble(_Symbol, SYMBOL_BID);
      double ask     = SymbolInfoDouble(_Symbol, SYMBOL_ASK);
      double minStep = MathMax(_Point,
                               0.5 * (double)SymbolInfoInteger(_Symbol, SYMBOL_TRADE_STOPS_LEVEL) * _Point);
      double beBuf   = 2.0 * _Point;

      if(ptype == POSITION_TYPE_BUY)
        {
         //--- 1) stale-trade time exit (spec D3: only before break-even)
         if(InpTimeExitBars > 0 && !g_beDone && g_entryTime > 0 &&
            (long)(TimeCurrent() - g_entryTime) >= (long)InpTimeExitBars * (long)g_periodSec)
           {
            Print("TIME EXIT: closing buy (stale ", IntegerToString(InpTimeExitBars),
                  " bars, not at BE)");
            if(!trade.PositionClose(_Symbol))
               Print("TIME EXIT FAILED retcode=", trade.ResultRetcode(), " ",
                     trade.ResultRetcodeDescription());
            continue;
           }
         //--- 2) break-even at +N R (keeps original TP!)
         if(InpUseBreakEven && !g_beDone && g_r0 > 0.0 &&
            (bid - open) >= InpBreakEvenR * g_r0)
           {
            double newSl = NormalizeDouble(open + beBuf, _Digits);
            if(curSl == 0.0 || newSl > curSl + minStep)
              {
               if(trade.PositionModify(_Symbol, newSl, curTp))
                 {
                  g_beDone = true;
                  Print("BREAK-EVEN: SL ", DoubleToString(curSl, _Digits), " -> ",
                        DoubleToString(newSl, _Digits));
                 }
               else
                  Print("BE MODIFY FAILED retcode=", trade.ResultRetcode(), " ",
                        trade.ResultRetcodeDescription());
              }
           }
         //--- 3) ATR trailing, only after break-even
         if(InpUseBreakEven && g_beDone)
           {
            double trail = NormalizeDouble(bid - InpTrailAtrMult * atr, _Digits);
            if(trail > open + beBuf && (curSl == 0.0 || trail > curSl + minStep))
              {
               if(trade.PositionModify(_Symbol, trail, curTp))
                  Print("TRAIL: SL -> ", DoubleToString(trail, _Digits));
               else
                  Print("TRAIL MODIFY FAILED retcode=", trade.ResultRetcode(), " ",
                        trade.ResultRetcodeDescription());
              }
           }
        }
      else // POSITION_TYPE_SELL - mirror
        {
         if(InpTimeExitBars > 0 && !g_beDone && g_entryTime > 0 &&
            (long)(TimeCurrent() - g_entryTime) >= (long)InpTimeExitBars * (long)g_periodSec)
           {
            Print("TIME EXIT: closing sell (stale ", IntegerToString(InpTimeExitBars),
                  " bars, not at BE)");
            if(!trade.PositionClose(_Symbol))
               Print("TIME EXIT FAILED retcode=", trade.ResultRetcode(), " ",
                     trade.ResultRetcodeDescription());
            continue;
           }
         if(InpUseBreakEven && !g_beDone && g_r0 > 0.0 &&
            (open - ask) >= InpBreakEvenR * g_r0)
           {
            double newSl = NormalizeDouble(open - beBuf, _Digits);
            if(curSl == 0.0 || newSl < curSl - minStep)
              {
               if(trade.PositionModify(_Symbol, newSl, curTp))
                 {
                  g_beDone = true;
                  Print("BREAK-EVEN: SL ", DoubleToString(curSl, _Digits), " -> ",
                        DoubleToString(newSl, _Digits));
                 }
               else
                  Print("BE MODIFY FAILED retcode=", trade.ResultRetcode(), " ",
                        trade.ResultRetcodeDescription());
              }
           }
         if(InpUseBreakEven && g_beDone)
           {
            double trail = NormalizeDouble(ask + InpTrailAtrMult * atr, _Digits);
            if(trail < open - beBuf && (curSl == 0.0 || trail < curSl - minStep))
              {
               if(trade.PositionModify(_Symbol, trail, curTp))
                  Print("TRAIL: SL -> ", DoubleToString(trail, _Digits));
               else
                  Print("TRAIL MODIFY FAILED retcode=", trade.ResultRetcode(), " ",
                        trade.ResultRetcodeDescription());
              }
           }
        }
     }
  }

//+------------------------------------------------------------------+
//| Record a closed trade in R-multiples (risk-manager skill).       |
//+------------------------------------------------------------------+
void RecordClosedTrade(const double profit)
  {
   double r = (g_riskAmount > 0.0 ? profit / g_riskAmount : 0.0);

   g_totalClosed++;
   if(profit > 0.0)
     {
      g_wins++;
      if(g_riskAmount > 0.0)
         g_sumWinR += r;
      g_consecLosses = 0;
     }
   else
     {
      if(g_riskAmount > 0.0)
         g_sumLossR += -r;
      g_consecLosses++;
      if(g_consecLosses > g_maxConsecLoss)
         g_maxConsecLoss = g_consecLosses;
     }

   Print(StringFormat("CLOSED: P/L %+.2f (%+.2f R) | dayTrades %d/%d | consecLoss %d | closed %d | win%% %.1f",
                      profit, r, g_dayTrades, InpMaxDailyTrades, g_consecLosses,
                      g_totalClosed, (g_totalClosed > 0 ? 100.0 * g_wins / g_totalClosed : 0.0)));

   ResetTradeState();
  }

//+------------------------------------------------------------------+
//| Trade transaction handler: entry counting + close stats.         |
//+------------------------------------------------------------------+
void OnTradeTransaction(const MqlTradeTransaction &trans,
                        const MqlTradeRequest &request,
                        const MqlTradeResult &result)
  {
   if(trans.type != TRADE_TRANSACTION_DEAL_ADD)
      return;
   if(!HistoryDealSelect(trans.deal))
      return;
   if(HistoryDealGetString(trans.deal, DEAL_SYMBOL) != _Symbol)
      return;
   if((long)HistoryDealGetInteger(trans.deal, DEAL_MAGIC) != InpMagic)
      return;

   long entry = HistoryDealGetInteger(trans.deal, DEAL_ENTRY);
   if(entry == DEAL_ENTRY_IN)
     {
      g_dayTrades++;
      return;
     }
   if(entry != DEAL_ENTRY_OUT && entry != DEAL_ENTRY_OUT_BY && entry != DEAL_ENTRY_INOUT)
      return;

   double profit = HistoryDealGetDouble(trans.deal, DEAL_PROFIT)
                 + HistoryDealGetDouble(trans.deal, DEAL_SWAP)
                 + HistoryDealGetDouble(trans.deal, DEAL_COMMISSION);
   RecordClosedTrade(profit);
  }

//+------------------------------------------------------------------+
//| Chart dashboard.                                                  |
//+------------------------------------------------------------------+
void UpdateComment()
  {
   string s = "XauUsdScalper | " + _Symbol + " " + EnumToString(g_tf) + "\n";
   s += "Halted: " + (g_haltedToday ? "YES (" + g_haltReason + ")" : "no") + "\n";
   s += "Day trades: " + IntegerToString(g_dayTrades) + "/" + IntegerToString(InpMaxDailyTrades)
        + " | Consec losses: " + IntegerToString(g_consecLosses) + "/"
        + IntegerToString(InpMaxConsecLosses) + "\n";
   double a1 = Buf1(hAtr, 1);
   s += "Spread: " + IntegerToString((int)SymbolInfoInteger(_Symbol, SYMBOL_SPREAD))
        + " pts (max " + IntegerToString((int)InpMaxSpreadPts) + ")"
        + " | ATR: " + (a1 == EMPTY_VALUE ? "n/a" : DoubleToString(a1, 2)) + "\n";
   if(g_totalClosed > 0)
     {
      double expectancyR = (g_sumWinR - g_sumLossR) / (double)g_totalClosed;
      s += StringFormat("Closed: %d | Win%%: %.1f | Expectancy: %+.3f R/trade | MaxConsecLoss: %d\n",
                        g_totalClosed, 100.0 * g_wins / g_totalClosed,
                        expectancyR, g_maxConsecLoss);
     }
   Comment(s);
  }

//+------------------------------------------------------------------+
//| Custom tester metric: expectancy in R per trade.                 |
//+------------------------------------------------------------------+
double OnTester()
  {
   if(g_totalClosed == 0)
      return(0.0);
   return((g_sumWinR - g_sumLossR) / (double)g_totalClosed);
  }

//+------------------------------------------------------------------+
//| Expert initialization function.                                   |
//+------------------------------------------------------------------+
int OnInit()
  {
   if(StringFind(_Symbol, "XAU") < 0)
      Print("WARNING: EA is tuned for XAUUSD; current symbol is ", _Symbol, ".");

   if(InpEmaFast <= 0 || InpEmaSlow <= 0 || InpEmaFast >= InpEmaSlow)
     {
      Print("ERROR: require 0 < InpEmaFast < InpEmaSlow");
      return(INIT_PARAMETERS_INCORRECT);
     }
   if(InpRsiPeriod <= 0 || InpRsiLevel <= 0 || InpRsiLevel >= 100)
     {
      Print("ERROR: bad RSI inputs");
      return(INIT_PARAMETERS_INCORRECT);
     }
   if(InpAtrPeriod <= 0 || InpAtrMin < 0.0 || InpAtrMax <= InpAtrMin)
     {
      Print("ERROR: bad ATR gate inputs (require InpMax > InpMin >= 0)");
      return(INIT_PARAMETERS_INCORRECT);
     }
   if(InpSlAtrMult <= 0.0 || InpTpAtrMult <= 0.0)
     {
      Print("ERROR: ATR multipliers must be > 0");
      return(INIT_PARAMETERS_INCORRECT);
     }
   if(InpRiskPercent <= 0.0 || InpRiskPercent > 5.0)
     {
      Print("ERROR: InpRiskPercent must be in (0, 5]");
      return(INIT_PARAMETERS_INCORRECT);
     }
   if(InpMaxDailyLossPct <= 0.0 || InpMaxConsecLosses <= 0 || InpMaxDailyTrades <= 0)
     {
      Print("ERROR: bad circuit-breaker inputs");
      return(INIT_PARAMETERS_INCORRECT);
     }
   if(InpSessionStart < 0 || InpSessionStart > 23 || InpSessionEnd < 0 || InpSessionEnd > 23 ||
      InpFridayBlockHour < 0 || InpFridayBlockHour > 23)
     {
      Print("ERROR: hours must be 0-23");
      return(INIT_PARAMETERS_INCORRECT);
     }
   if(InpMaxLot <= 0.0 || InpSlippagePts < 0)
     {
      Print("ERROR: bad InpMaxLot / InpSlippagePts");
      return(INIT_PARAMETERS_INCORRECT);
     }
   if(InpRiskPercent * InpMaxDailyTrades > 10.0)
      Print("WARNING: InpRiskPercent x InpMaxDailyTrades = ",
            DoubleToString(InpRiskPercent * InpMaxDailyTrades, 1),
            "% theoretical max daily risk > 10% - tighten one of them");

   g_tf        = (InpTimeframe == PERIOD_CURRENT ? _Period : InpTimeframe);
   g_periodSec = PeriodSeconds(g_tf);

   hEmaFast = iMA(_Symbol, g_tf, InpEmaFast, 0, MODE_EMA, PRICE_CLOSE);
   hEmaSlow = iMA(_Symbol, g_tf, InpEmaSlow, 0, MODE_EMA, PRICE_CLOSE);
   hRsi     = iRSI(_Symbol, g_tf, InpRsiPeriod, PRICE_CLOSE);
   hAtr     = iATR(_Symbol, g_tf, InpAtrPeriod);
   if(hEmaFast == INVALID_HANDLE || hEmaSlow == INVALID_HANDLE ||
      hRsi == INVALID_HANDLE || hAtr == INVALID_HANDLE)
     {
      Print("ERROR: failed to create indicator handles");
      if(hEmaFast != INVALID_HANDLE)
         IndicatorRelease(hEmaFast);
      if(hEmaSlow != INVALID_HANDLE)
         IndicatorRelease(hEmaSlow);
      if(hRsi != INVALID_HANDLE)
         IndicatorRelease(hRsi);
      if(hAtr != INVALID_HANDLE)
         IndicatorRelease(hAtr);
      return(INIT_FAILED);
     }

   trade.SetExpertMagicNumber((ulong)InpMagic);
   trade.SetDeviationInPoints((ulong)InpSlippagePts);
   trade.SetTypeFilling(GetFillingMode());
   trade.SetAsyncMode(false);

   g_dayStartEquity = AccountInfoDouble(ACCOUNT_EQUITY);
   Print("XauUsdScalper initialized on ", _Symbol, " ", EnumToString(g_tf),
         " | risk ", DoubleToString(InpRiskPercent, 2), "%/trade",
         " | SL ", DoubleToString(InpSlAtrMult, 2), "xATR",
         " | TP ", DoubleToString(InpTpAtrMult, 2), "xATR",
         " | session ", IntegerToString(InpSessionStart), "h-",
         IntegerToString(InpSessionEnd), "h (server)");
   return(INIT_SUCCEEDED);
  }

//+------------------------------------------------------------------+
//| Expert deinitialization function.                                 |
//+------------------------------------------------------------------+
void OnDeinit(const int reason)
  {
   if(hEmaFast != INVALID_HANDLE)
      IndicatorRelease(hEmaFast);
   if(hEmaSlow != INVALID_HANDLE)
      IndicatorRelease(hEmaSlow);
   if(hRsi != INVALID_HANDLE)
      IndicatorRelease(hRsi);
   if(hAtr != INVALID_HANDLE)
      IndicatorRelease(hAtr);
   Comment("");
   Print("XauUsdScalper deinitialized, reason=", reason);
  }

//+------------------------------------------------------------------+
//| Expert tick function.                                             |
//+------------------------------------------------------------------+
void OnTick()
  {
   UpdateDay();
   UpdateHaltState();

   if(CountPositions() > 0)
      ManageOpenPositions();

   datetime barTime = iTime(_Symbol, EaTf(), 0);
   if(barTime > 0 && barTime != g_lastBarTime)
     {
      g_lastBarTime = barTime;
      TryEnterOnNewBar();
     }

   UpdateComment();
  }
//+------------------------------------------------------------------+
