//+------------------------------------------------------------------+
//|                                              XAUUSD_AgentEA.mq5  |
//|            xauusd-factory v1 - Gold Session Trend-Pullback (GSTP) |
//|                                                                  |
//|  Strategy (see pipeline/03-strategy-spec.md):                    |
//|   Regime  : H1 EMA50/EMA200 alignment + EMA50 slope + ADX >= 20  |
//|   Setup   : M15 pullback into the EMA20 zone (last 6 closed bars)|
//|   Trigger : close beyond EMA20 and prior bar extreme, RSI side   |
//|   Filters : London+NY session (GMT), spread/ATR, ATR regime band,|
//|             high-impact USD news blackout (live only), daily caps |
//|   Exits   : structural SL clamped to 1.0-2.5 ATR, TP = 2R,       |
//|             break-even at +1R, ATR trail from +1.5R, time exit,  |
//|             Friday flat                                          |
//|   Risk    : fixed-fractional % of equity, floored lots, skip if  |
//|             below min lot, daily loss cap, equity kill switch    |
//|                                                                  |
//|  Safety: no DLL, no #import, no WebRequest, no file I/O.         |
//|  No martingale / grid / averaging. One position per magic.       |
//|                                                                  |
//|  DISCLAIMER: research software. Not verified on a live account.  |
//|  Trading leveraged gold can lose more than your deposit.         |
//+------------------------------------------------------------------+
#property copyright   "xauusd-factory (maskchanel14-source/agents)"
#property link        "https://github.com/maskchanel14-source/agents"
#property version     "1.00"
#property description "XAUUSD Gold Session Trend-Pullback EA (v1). Regime-gated, ATR-normalised, fixed-fractional risk."

#include <Trade\Trade.mqh>

//--- Inputs --------------------------------------------------------
input group "Timeframes"
input ENUM_TIMEFRAMES InpSignalTF        = PERIOD_M15; // Signal timeframe
input ENUM_TIMEFRAMES InpRegimeTF        = PERIOD_H1;  // Regime timeframe (must be higher than signal TF)

input group "Regime (higher timeframe)"
input int    InpEmaFastRegime   = 50;    // Regime fast EMA period
input int    InpEmaSlowRegime   = 200;   // Regime slow EMA period
input int    InpSlopeBars       = 3;     // Fast EMA slope lookback (regime bars)
input int    InpAdxPeriod       = 14;    // ADX period
input double InpAdxMin          = 20.0;  // Minimum ADX for a trending regime

input group "Setup & trigger (signal timeframe)"
input int    InpEmaSignal       = 20;    // Signal EMA period (pullback zone)
input int    InpRsiPeriod       = 14;    // RSI period (momentum side filter, 50 line)
input int    InpAtrPeriod       = 14;    // ATR period
input int    InpPullbackBars    = 6;     // Bars to look back for the EMA touch / swing
input double InpTouchATR        = 0.25;  // EMA touch tolerance (x ATR)
input double InpMaxChaseATR     = 1.0;   // Max distance close-to-EMA at trigger (x ATR)

input group "Volatility & cost filters"
input int    InpAtrAvgBars      = 100;   // Bars for average ATR (regime band)
input double InpVolRatioMin     = 0.6;   // Min ATR / avgATR (skip dead markets)
input double InpVolRatioMax     = 2.5;   // Max ATR / avgATR (skip spikes)
input double InpMaxSpreadATR    = 0.15;  // Max spread as fraction of ATR
input int    InpMaxSpreadPoints = 0;     // Max spread in points (0 = off)

input group "Exits"
input double InpSlBufferATR     = 0.25;  // SL buffer beyond swing (x ATR)
input double InpSlMinATR        = 1.0;   // Min SL distance (x ATR)
input double InpSlMaxATR        = 2.5;   // Max SL distance (x ATR)
input double InpTpRR            = 2.0;   // Take profit in R (0 = no TP)
input double InpBeTriggerR      = 1.0;   // Move SL to break-even at +R (0 = off)
input double InpBeBufferR       = 0.1;   // Break-even buffer (x R)
input double InpTrailStartR     = 1.5;   // Start ATR trailing at +R (0 = off)
input double InpTrailATR        = 1.0;   // Trailing distance (x ATR)
input int    InpMaxBarsInTrade  = 48;    // Time exit after N signal bars (0 = off)

input group "Session (GMT)"
input bool   InpAutoGMTOffset   = true;  // Live: detect server GMT offset automatically
input int    InpServerGMTOffset = 2;     // Server GMT offset in hours (tester / fallback)
input int    InpSessionStartGMT = 7;     // First entry hour (GMT, inclusive)
input int    InpSessionEndGMT   = 20;    // Last entry hour (GMT, exclusive)
input int    InpFridayLastEntry = 18;    // Friday: no new entries from this GMT hour
input int    InpFridayCloseGMT  = 20;    // Friday: close positions from this GMT hour (-1 = off)

input group "News filter (live only; MT5 calendar)"
input bool   InpUseNewsFilter   = true;  // Block entries around high-impact USD events
input int    InpNewsMinsBefore  = 30;    // Minutes before event
input int    InpNewsMinsAfter   = 30;    // Minutes after event

input group "Risk management"
input double InpRiskPercent     = 0.5;   // Risk per trade (% of equity)
input double InpMaxLots         = 5.0;   // Hard cap on lot size
input int    InpMaxTradesPerDay = 3;     // Max entries per server day
input double InpDailyLossPct    = 2.0;   // Daily loss cap (% of day-start balance)
input double InpKillSwitchDDPct = 15.0;  // Equity kill switch: DD from peak (%)
input bool   InpResetKillSwitch = false; // Reset a tripped kill switch on init

input group "Execution"
input ulong  InpMagic           = 26101201; // Magic number
input int    InpSlippagePoints  = 30;    // Max slippage (points)
input int    InpRetryCooldownSec= 60;    // Cooldown after a failed trade request (s)
input bool   InpAllowNonGold    = false; // Allow running on non-gold symbols
input string InpComment         = "XAUUSD_AgentEA v1"; // Order comment

//--- Globals -------------------------------------------------------
CTrade   g_trade;
int      g_hEmaSig   = INVALID_HANDLE;
int      g_hAtrSig   = INVALID_HANDLE;
int      g_hRsiSig   = INVALID_HANDLE;
int      g_hEmaFast  = INVALID_HANDLE;
int      g_hEmaSlow  = INVALID_HANDLE;
int      g_hAdx      = INVALID_HANDLE;

datetime g_lastSignalBar  = 0;
datetime g_lastFailTime   = 0;
datetime g_lastModifyFail = 0;
datetime g_lastCloseFail  = 0;
datetime g_newsWarned     = 0;
datetime g_newsRefreshed  = 0;
datetime g_newsTimes[];
bool     g_isTester       = false;
string   g_gvPrefix       = "";

//+------------------------------------------------------------------+
//| Helpers                                                          |
//+------------------------------------------------------------------+
string GvName(const string key) { return g_gvPrefix + key; }

double NormalizePrice(const double price)
  {
   double tick = SymbolInfoDouble(_Symbol, SYMBOL_TRADE_TICK_SIZE);
   if(tick <= 0.0)
      return NormalizeDouble(price, _Digits);
   return NormalizeDouble(MathRound(price / tick) * tick, _Digits);
  }

int VolumeDigits(const double step)
  {
   if(step <= 0.0)
      return 2;
   int d = (int)MathCeil(-MathLog10(step) - 1e-9);
   return (int)MathMax(0, d);
  }

bool ReadBuffer(const int handle, const int buffer, const int shift, const int count, double &out[])
  {
   ArraySetAsSeries(out, true);
   int copied = CopyBuffer(handle, buffer, shift, count, out);
   return (copied == count);
  }

double ReadValue(const int handle, const int buffer, const int shift)
  {
   double v[];
   if(!ReadBuffer(handle, buffer, shift, 1, v))
      return EMPTY_VALUE;
   return v[0];
  }

int ServerGMTOffsetSeconds()
  {
   if(InpAutoGMTOffset && !g_isTester)
     {
      long diff = (long)(TimeTradeServer() - TimeGMT());
      int hours = (int)MathRound((double)diff / 3600.0);
      if(hours >= -12 && hours <= 14)
         return hours * 3600;
     }
   return InpServerGMTOffset * 3600;
  }

void GmtNow(MqlDateTime &dt)
  {
   datetime gmt = TimeCurrent() - ServerGMTOffsetSeconds();
   TimeToStruct(gmt, dt);
  }

bool IsNewSignalBar()
  {
   datetime t = iTime(_Symbol, InpSignalTF, 0);
   if(t == 0 || t == g_lastSignalBar)
      return false;
   g_lastSignalBar = t;
   return true;
  }

bool IsMyPosition()
  {
   return (PositionGetString(POSITION_SYMBOL) == _Symbol &&
           (ulong)PositionGetInteger(POSITION_MAGIC) == InpMagic);
  }

int CountMyPositions()
  {
   int n = 0;
   for(int i = PositionsTotal() - 1; i >= 0; i--)
     {
      ulong ticket = PositionGetTicket(i);
      if(ticket == 0)
         continue;
      if(IsMyPosition())
         n++;
     }
   return n;
  }

bool ForeignPositionOnSymbol()
  {
   for(int i = PositionsTotal() - 1; i >= 0; i--)
     {
      ulong ticket = PositionGetTicket(i);
      if(ticket == 0)
         continue;
      if(PositionGetString(POSITION_SYMBOL) == _Symbol &&
         (ulong)PositionGetInteger(POSITION_MAGIC) != InpMagic)
         return true;
     }
   return false;
  }

bool TradingPermitted()
  {
   if(!TerminalInfoInteger(TERMINAL_CONNECTED) && !g_isTester)
      return false;
   if(!TerminalInfoInteger(TERMINAL_TRADE_ALLOWED))
      return false;
   if(!MQLInfoInteger(MQL_TRADE_ALLOWED))
      return false;
   if(!AccountInfoInteger(ACCOUNT_TRADE_ALLOWED))
      return false;
   if(!AccountInfoInteger(ACCOUNT_TRADE_EXPERT))
      return false;
   long mode = SymbolInfoInteger(_Symbol, SYMBOL_TRADE_MODE);
   if(mode == SYMBOL_TRADE_MODE_DISABLED || mode == SYMBOL_TRADE_MODE_CLOSEONLY)
      return false;
   return true;
  }

bool SideAllowedBySymbol(const int side)
  {
   long mode = SymbolInfoInteger(_Symbol, SYMBOL_TRADE_MODE);
   if(side > 0 && mode == SYMBOL_TRADE_MODE_SHORTONLY)
      return false;
   if(side < 0 && mode == SYMBOL_TRADE_MODE_LONGONLY)
      return false;
   return true;
  }

//+------------------------------------------------------------------+
//| Daily statistics (restart-safe: derived from deal history)       |
//+------------------------------------------------------------------+
void TodayStats(int &entries, double &closedPnl)
  {
   entries   = 0;
   closedPnl = 0.0;
   datetime dayStart = iTime(_Symbol, PERIOD_D1, 0);
   if(dayStart == 0)
     {
      MqlDateTime dt;
      TimeToStruct(TimeCurrent(), dt);
      dt.hour = 0;
      dt.min  = 0;
      dt.sec  = 0;
      dayStart = StructToTime(dt);
     }
   if(!HistorySelect(dayStart, TimeCurrent() + 60))
      return;
   int total = HistoryDealsTotal();
   for(int i = 0; i < total; i++)
     {
      ulong deal = HistoryDealGetTicket(i);
      if(deal == 0)
         continue;
      if(HistoryDealGetString(deal, DEAL_SYMBOL) != _Symbol)
         continue;
      if((ulong)HistoryDealGetInteger(deal, DEAL_MAGIC) != InpMagic)
         continue;
      long entry = HistoryDealGetInteger(deal, DEAL_ENTRY);
      if(entry == DEAL_ENTRY_IN)
         entries++;
      closedPnl += HistoryDealGetDouble(deal, DEAL_PROFIT)
                   + HistoryDealGetDouble(deal, DEAL_SWAP)
                   + HistoryDealGetDouble(deal, DEAL_COMMISSION);
     }
  }

double FloatingPnl()
  {
   double pnl = 0.0;
   for(int i = PositionsTotal() - 1; i >= 0; i--)
     {
      ulong ticket = PositionGetTicket(i);
      if(ticket == 0 || !IsMyPosition())
         continue;
      pnl += PositionGetDouble(POSITION_PROFIT) + PositionGetDouble(POSITION_SWAP);
     }
   return pnl;
  }

bool DailyLimitsHit()
  {
   int    entries   = 0;
   double closedPnl = 0.0;
   TodayStats(entries, closedPnl);
   if(entries >= InpMaxTradesPerDay)
      return true;
   double dayStartBalance = AccountInfoDouble(ACCOUNT_BALANCE) - closedPnl;
   if(dayStartBalance <= 0.0)
      return true;
   double dayPnl = closedPnl + FloatingPnl();
   return (dayPnl <= -InpDailyLossPct / 100.0 * dayStartBalance);
  }

//+------------------------------------------------------------------+
//| Equity kill switch (persisted in a terminal global variable)     |
//+------------------------------------------------------------------+
bool KillSwitchTripped()
  {
   if(GlobalVariableCheck(GvName("KILL")) && GlobalVariableGet(GvName("KILL")) > 0.5)
      return true;
   double equity = AccountInfoDouble(ACCOUNT_EQUITY);
   double peak   = GlobalVariableCheck(GvName("PEAK")) ? GlobalVariableGet(GvName("PEAK")) : 0.0;
   if(equity > peak)
     {
      peak = equity;
      GlobalVariableSet(GvName("PEAK"), peak);
     }
   if(peak > 0.0 && equity <= peak * (1.0 - InpKillSwitchDDPct / 100.0))
     {
      GlobalVariableSet(GvName("KILL"), 1.0);
      PrintFormat("KILL SWITCH: equity %.2f is %.1f%% below peak %.2f. New entries disabled until reset.",
                  equity, InpKillSwitchDDPct, peak);
      return true;
     }
   return false;
  }

//+------------------------------------------------------------------+
//| News blackout (MT5 economic calendar, live only)                 |
//+------------------------------------------------------------------+
void RefreshNews()
  {
   datetime now = TimeTradeServer();
   if(g_newsRefreshed != 0 && now - g_newsRefreshed < 900)
      return;
   g_newsRefreshed = now;
   ArrayResize(g_newsTimes, 0);
   MqlCalendarValue values[];
   int n = CalendarValueHistory(values, now - 3600 * 2, now + 3600 * 24, NULL, "USD");
   if(n <= 0)
     {
      // audit M-2: filter is fail-open; make that visible (at most once per hour)
      if(now - g_newsWarned >= 3600)
        {
         g_newsWarned = now;
         PrintFormat("WARNING: economic calendar returned no USD events (err %d). News filter inactive.", GetLastError());
        }
      return;
     }
   for(int i = 0; i < n; i++)
     {
      MqlCalendarEvent ev;
      if(!CalendarEventById(values[i].event_id, ev))
         continue;
      if(ev.importance != CALENDAR_IMPORTANCE_HIGH)
         continue;
      int sz = ArraySize(g_newsTimes);
      ArrayResize(g_newsTimes, sz + 1);
      g_newsTimes[sz] = values[i].time;
     }
  }

bool InNewsBlackout()
  {
   if(!InpUseNewsFilter || g_isTester)
      return false;
   RefreshNews();
   datetime now = TimeTradeServer();
   for(int i = 0; i < ArraySize(g_newsTimes); i++)
     {
      if(now >= g_newsTimes[i] - InpNewsMinsBefore * 60 &&
         now <= g_newsTimes[i] + InpNewsMinsAfter * 60)
         return true;
     }
   return false;
  }

//+------------------------------------------------------------------+
//| Session / weekend                                                |
//+------------------------------------------------------------------+
bool InEntrySession()
  {
   MqlDateTime g;
   GmtNow(g);
   if(g.day_of_week == 0 || g.day_of_week == 6)
      return false;
   if(g.hour < InpSessionStartGMT || g.hour >= InpSessionEndGMT)
      return false;
   if(g.day_of_week == 5 && g.hour >= InpFridayLastEntry)
      return false;
   return true;
  }

bool FridayFlatTime()
  {
   if(InpFridayCloseGMT < 0)
      return false;
   MqlDateTime g;
   GmtNow(g);
   return (g.day_of_week == 5 && g.hour >= InpFridayCloseGMT);
  }

//+------------------------------------------------------------------+
//| Position sizing: fixed-fractional, floored, skip below min lot   |
//+------------------------------------------------------------------+
double LotsForRisk(const double slDistance, const ENUM_ORDER_TYPE type, const double price)
  {
   if(slDistance <= 0.0)
      return 0.0;
   double tickSize  = SymbolInfoDouble(_Symbol, SYMBOL_TRADE_TICK_SIZE);
   double tickValue = SymbolInfoDouble(_Symbol, SYMBOL_TRADE_TICK_VALUE_LOSS);
   if(tickValue <= 0.0)
      tickValue = SymbolInfoDouble(_Symbol, SYMBOL_TRADE_TICK_VALUE);
   double step   = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_STEP);
   double minLot = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_MIN);
   double maxLot = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_MAX);
   if(tickSize <= 0.0 || tickValue <= 0.0 || step <= 0.0)
      return 0.0;

   double riskMoney  = AccountInfoDouble(ACCOUNT_EQUITY) * InpRiskPercent / 100.0;
   double lossPerLot = slDistance / tickSize * tickValue;
   if(lossPerLot <= 0.0)
      return 0.0;

   double lots = MathFloor((riskMoney / lossPerLot) / step + 1e-9) * step;   // always round DOWN
   lots = MathMin(lots, MathMin(maxLot, InpMaxLots));
   lots = NormalizeDouble(lots, VolumeDigits(step));
   if(lots < minLot)
     {
      PrintFormat("Skip: risk-based lot %.4f < broker min %.2f (risk %.2f, SL %.2f). Not rounding up.",
                  lots, minLot, riskMoney, slDistance);
      return 0.0;
     }

   double margin = 0.0;
   if(!OrderCalcMargin(type, _Symbol, lots, price, margin))
      return 0.0;
   if(margin > AccountInfoDouble(ACCOUNT_MARGIN_FREE) * 0.9)
     {
      PrintFormat("Skip: margin %.2f exceeds 90%% of free margin.", margin);
      return 0.0;
     }
   return lots;
  }

//+------------------------------------------------------------------+
//| Signal evaluation (closed bars only)                             |
//|   returns +1 long, -1 short, 0 none; fills ATR and swing extreme |
//+------------------------------------------------------------------+
int EvaluateSignal(double &atrOut, double &swingOut)
  {
   atrOut   = 0.0;
   swingOut = 0.0;

   //--- regime (shift 1 = last closed regime bar)
   double emaF[];
   if(!ReadBuffer(g_hEmaFast, 0, 1, InpSlopeBars + 1, emaF))
      return 0;
   double emaS = ReadValue(g_hEmaSlow, 0, 1);
   double adx  = ReadValue(g_hAdx, 0, 1);         // buffer 0 = MAIN_LINE
   double regClose = iClose(_Symbol, InpRegimeTF, 1);
   if(emaS == EMPTY_VALUE || adx == EMPTY_VALUE || regClose <= 0.0)
      return 0;

   bool bull = (regClose > emaF[0] && emaF[0] > emaS && emaF[0] > emaF[InpSlopeBars] && adx >= InpAdxMin);
   bool bear = (regClose < emaF[0] && emaF[0] < emaS && emaF[0] < emaF[InpSlopeBars] && adx >= InpAdxMin);
   if(!bull && !bear)
      return 0;

   //--- signal timeframe data (index 0 = shift 1)
   int n = InpPullbackBars;
   double ema[];
   double atr[];
   double rsi[];
   double hi[];
   double lo[];
   double cl[];
   if(!ReadBuffer(g_hEmaSig, 0, 1, n, ema))           return 0;
   if(!ReadBuffer(g_hAtrSig, 0, 1, InpAtrAvgBars, atr)) return 0;
   if(!ReadBuffer(g_hRsiSig, 0, 1, 1, rsi))           return 0;
   ArraySetAsSeries(hi, true);
   ArraySetAsSeries(lo, true);
   ArraySetAsSeries(cl, true);
   int cnt = (n > 2) ? n : 2;
   if(CopyHigh(_Symbol, InpSignalTF, 1, cnt, hi) != cnt) return 0;
   if(CopyLow(_Symbol, InpSignalTF, 1, cnt, lo)  != cnt) return 0;
   if(CopyClose(_Symbol, InpSignalTF, 1, 1, cl)  != 1)   return 0;

   double atr1 = atr[0];
   if(atr1 <= 0.0)
      return 0;

   //--- volatility band: ATR vs its average
   double sum = 0.0;
   for(int i = 0; i < InpAtrAvgBars; i++)
      sum += atr[i];
   double avgAtr = sum / InpAtrAvgBars;
   if(avgAtr <= 0.0)
      return 0;
   double ratio = atr1 / avgAtr;
   if(ratio < InpVolRatioMin || ratio > InpVolRatioMax)
      return 0;

   double close1 = cl[0];
   double ema1   = ema[0];

   if(bull)
     {
      double minGap = DBL_MAX;
      double swing  = DBL_MAX;
      for(int i = 0; i < n; i++)
        {
         minGap = MathMin(minGap, lo[i] - ema[i]);
         swing  = MathMin(swing, lo[i]);
        }
      bool touched = (minGap <= InpTouchATR * atr1);
      bool trigger = (close1 > ema1 && close1 > hi[1] && rsi[0] > 50.0 &&
                      (close1 - ema1) <= InpMaxChaseATR * atr1);
      if(touched && trigger)
        {
         atrOut   = atr1;
         swingOut = swing;
         return 1;
        }
     }
   if(bear)
     {
      double minGap = DBL_MAX;
      double swing  = -DBL_MAX;
      for(int i = 0; i < n; i++)
        {
         minGap = MathMin(minGap, ema[i] - hi[i]);
         swing  = MathMax(swing, hi[i]);
        }
      bool touched = (minGap <= InpTouchATR * atr1);
      bool trigger = (close1 < ema1 && close1 < lo[1] && rsi[0] < 50.0 &&
                      (ema1 - close1) <= InpMaxChaseATR * atr1);
      if(touched && trigger)
        {
         atrOut   = atr1;
         swingOut = swing;
         return -1;
        }
     }
   return 0;
  }

//+------------------------------------------------------------------+
//| Entry                                                            |
//+------------------------------------------------------------------+
bool SpreadOk(const double atr)
  {
   double ask = SymbolInfoDouble(_Symbol, SYMBOL_ASK);
   double bid = SymbolInfoDouble(_Symbol, SYMBOL_BID);
   double spread = ask - bid;
   if(spread <= 0.0 && !g_isTester)
      return false;
   if(InpMaxSpreadPoints > 0 && spread > InpMaxSpreadPoints * _Point)
      return false;
   return (spread <= InpMaxSpreadATR * atr);
  }

void TryEnter()
  {
   if(g_lastFailTime != 0 && TimeCurrent() - g_lastFailTime < InpRetryCooldownSec)
      return;
   if(!TradingPermitted())
      return;
   if(CountMyPositions() > 0)
      return;
   if(AccountInfoInteger(ACCOUNT_MARGIN_MODE) == ACCOUNT_MARGIN_MODE_RETAIL_NETTING && ForeignPositionOnSymbol())
      return;   // never merge into someone else's net position
   if(!InEntrySession() || InNewsBlackout())
      return;
   if(DailyLimitsHit())
      return;

   double atr = 0.0, swing = 0.0;
   int side = EvaluateSignal(atr, swing);
   if(side == 0 || !SideAllowedBySymbol(side))
      return;
   if(!SpreadOk(atr))
     {
      Print("Signal skipped: spread too wide relative to ATR.");
      return;
     }

   double ask = SymbolInfoDouble(_Symbol, SYMBOL_ASK);
   double bid = SymbolInfoDouble(_Symbol, SYMBOL_BID);
   double entry = (side > 0) ? ask : bid;

   double raw = (side > 0) ? entry - (swing - InpSlBufferATR * atr)
                           : (swing + InpSlBufferATR * atr) - entry;
   double slDist = MathMin(MathMax(raw, InpSlMinATR * atr), InpSlMaxATR * atr);
   double sl = NormalizePrice(entry - side * slDist);
   double tp = (InpTpRR > 0.0) ? NormalizePrice(entry + side * InpTpRR * slDist) : 0.0;

   //--- broker stop-level validation (SL/TP are triggered on the opposite price)
   double stopsLevel = (double)SymbolInfoInteger(_Symbol, SYMBOL_TRADE_STOPS_LEVEL) * _Point;
   double refPrice   = (side > 0) ? bid : ask;
   if(MathAbs(refPrice - sl) <= stopsLevel || (tp > 0.0 && MathAbs(tp - refPrice) <= stopsLevel))
     {
      Print("Signal skipped: SL/TP inside broker stops level.");
      return;
     }

   ENUM_ORDER_TYPE type = (side > 0) ? ORDER_TYPE_BUY : ORDER_TYPE_SELL;
   double lots = LotsForRisk(MathAbs(entry - sl), type, entry);
   if(lots <= 0.0)
      return;

   bool sent = (side > 0) ? g_trade.Buy(lots, _Symbol, ask, sl, tp, InpComment)
                          : g_trade.Sell(lots, _Symbol, bid, sl, tp, InpComment);
   uint rc = g_trade.ResultRetcode();
   if(!sent || (rc != TRADE_RETCODE_DONE && rc != TRADE_RETCODE_PLACED && rc != TRADE_RETCODE_DONE_PARTIAL))
     {
      g_lastFailTime = TimeCurrent();
      PrintFormat("Entry failed: retcode %u (%s). Cooldown %ds.", rc, g_trade.ResultRetcodeDescription(), InpRetryCooldownSec);
      return;
     }
   PrintFormat("%s %.2f lots @ %.2f  SL %.2f  TP %.2f  (ATR %.2f, R %.2f)",
               side > 0 ? "BUY" : "SELL", lots, entry, sl, tp, atr, MathAbs(entry - sl));
  }

//+------------------------------------------------------------------+
//| Position management: BE, ATR trail, time exit, Friday flat       |
//+------------------------------------------------------------------+
bool ModifySL(const ulong ticket, const long type, const double newSL, const double tp)
  {
   if(g_lastModifyFail != 0 && TimeCurrent() - g_lastModifyFail < 5)
      return false;
   double bid = SymbolInfoDouble(_Symbol, SYMBOL_BID);
   double ask = SymbolInfoDouble(_Symbol, SYMBOL_ASK);
   double stopsLevel  = (double)SymbolInfoInteger(_Symbol, SYMBOL_TRADE_STOPS_LEVEL) * _Point;
   double freezeLevel = (double)SymbolInfoInteger(_Symbol, SYMBOL_TRADE_FREEZE_LEVEL) * _Point;
   double curSL = PositionGetDouble(POSITION_SL);
   double ref   = (type == POSITION_TYPE_BUY) ? bid : ask;

   if(MathAbs(ref - newSL) <= MathMax(stopsLevel, freezeLevel))
      return false;
   if(curSL > 0.0 && MathAbs(ref - curSL) <= freezeLevel)
      return false;                         // position frozen near current SL
   if(tp > 0.0 && MathAbs(tp - ref) <= freezeLevel)
      return false;

   if(!g_trade.PositionModify(ticket, newSL, tp))
     {
      g_lastModifyFail = TimeCurrent();
      PrintFormat("Modify failed #%I64u: %u (%s)", ticket, g_trade.ResultRetcode(), g_trade.ResultRetcodeDescription());
      return false;
     }
   return true;
  }

double InitialRisk(const ulong ticket, const double openPrice, const double curSL, const double atr)
  {
   string key = GvName("R_" + IntegerToString((long)ticket));
   if(GlobalVariableCheck(key))
      return GlobalVariableGet(key);
   double r = (curSL > 0.0) ? MathAbs(openPrice - curSL) : 0.0;
   if(r < 0.5 * InpSlMinATR * atr)          // SL already moved (e.g. after restart): fall back to ATR
      r = InpSlMinATR * atr;
   if(r > 0.0)
      GlobalVariableSet(key, r);
   return r;
  }

void CleanupRiskVars()
  {
   if(CountMyPositions() == 0)
      GlobalVariablesDeleteAll(GvName("R_"));
  }

void ManagePositions()
  {
   double atr = ReadValue(g_hAtrSig, 0, 1);
   if(atr == EMPTY_VALUE || atr <= 0.0)
      return;
   bool fridayFlat = FridayFlatTime();
   double tickSize = SymbolInfoDouble(_Symbol, SYMBOL_TRADE_TICK_SIZE);
   double minMove  = MathMax(tickSize, 0.10 * atr);   // audit M-1: avoid modification spam

   for(int i = PositionsTotal() - 1; i >= 0; i--)
     {
      ulong ticket = PositionGetTicket(i);
      if(ticket == 0 || !IsMyPosition())
         continue;

      long   type  = PositionGetInteger(POSITION_TYPE);
      double open  = PositionGetDouble(POSITION_PRICE_OPEN);
      double sl    = PositionGetDouble(POSITION_SL);
      double tp    = PositionGetDouble(POSITION_TP);
      datetime opened = (datetime)PositionGetInteger(POSITION_TIME);
      int    side  = (type == POSITION_TYPE_BUY) ? 1 : -1;
      double price = (side > 0) ? SymbolInfoDouble(_Symbol, SYMBOL_BID) : SymbolInfoDouble(_Symbol, SYMBOL_ASK);

      //--- hard exits
      int barsHeld = iBarShift(_Symbol, InpSignalTF, opened, false);
      if(fridayFlat || (InpMaxBarsInTrade > 0 && barsHeld >= InpMaxBarsInTrade))
        {
         // audit H-1: never retry a failed close on every tick
         if(g_lastCloseFail != 0 && TimeCurrent() - g_lastCloseFail < 10)
            continue;
         if(!g_trade.PositionClose(ticket, InpSlippagePoints))
           {
            g_lastCloseFail = TimeCurrent();
            PrintFormat("Close failed #%I64u: %u (%s). Retry in 10s.", ticket,
                        g_trade.ResultRetcode(), g_trade.ResultRetcodeDescription());
           }
         continue;
        }

      double r = InitialRisk(ticket, open, sl, atr);
      if(r <= 0.0)
         continue;
      double gainR = (price - open) * side / r;
      double target = sl;

      if(InpBeTriggerR > 0.0 && gainR >= InpBeTriggerR)
        {
         double be = open + side * InpBeBufferR * r;
         if(sl <= 0.0 || (be - target) * side > 0.0)
            target = be;
        }
      if(InpTrailStartR > 0.0 && gainR >= InpTrailStartR)
        {
         double tr = price - side * InpTrailATR * atr;
         if(target <= 0.0 || (tr - target) * side > 0.0)
            target = tr;
        }
      target = NormalizePrice(target);
      if(target > 0.0 && (sl <= 0.0 || (target - sl) * side >= minMove))
         ModifySL(ticket, type, target, tp);
     }
  }

//+------------------------------------------------------------------+
//| Input validation                                                 |
//+------------------------------------------------------------------+
bool ValidateInputs()
  {
   bool ok = true;
   if(PeriodSeconds(InpRegimeTF) <= PeriodSeconds(InpSignalTF)) { Print("Regime TF must be higher than signal TF"); ok = false; }
   if(InpEmaFastRegime < 2 || InpEmaSlowRegime <= InpEmaFastRegime || InpEmaSlowRegime > 1000) { Print("Bad regime EMA periods"); ok = false; }
   if(InpSlopeBars < 1 || InpSlopeBars > 50)        { Print("InpSlopeBars out of range [1,50]"); ok = false; }
   if(InpAdxPeriod < 2 || InpAdxPeriod > 100)       { Print("InpAdxPeriod out of range"); ok = false; }
   if(InpAdxMin < 0.0 || InpAdxMin > 60.0)          { Print("InpAdxMin out of range [0,60]"); ok = false; }
   if(InpEmaSignal < 2 || InpEmaSignal > 500)       { Print("InpEmaSignal out of range"); ok = false; }
   if(InpRsiPeriod < 2 || InpRsiPeriod > 100)       { Print("InpRsiPeriod out of range"); ok = false; }
   if(InpAtrPeriod < 2 || InpAtrPeriod > 200)       { Print("InpAtrPeriod out of range"); ok = false; }
   if(InpPullbackBars < 2 || InpPullbackBars > 50)  { Print("InpPullbackBars out of range [2,50]"); ok = false; }
   if(InpTouchATR < 0.0 || InpTouchATR > 2.0)       { Print("InpTouchATR out of range [0,2]"); ok = false; }
   if(InpMaxChaseATR <= 0.0 || InpMaxChaseATR > 5.0){ Print("InpMaxChaseATR out of range (0,5]"); ok = false; }
   if(InpAtrAvgBars < 10 || InpAtrAvgBars > 1000)   { Print("InpAtrAvgBars out of range [10,1000]"); ok = false; }
   if(InpVolRatioMin < 0.0 || InpVolRatioMax <= InpVolRatioMin) { Print("Bad volatility band"); ok = false; }
   if(InpMaxSpreadATR <= 0.0 || InpMaxSpreadATR > 1.0) { Print("InpMaxSpreadATR out of range (0,1]"); ok = false; }
   if(InpMaxSpreadPoints < 0)                       { Print("InpMaxSpreadPoints must be >= 0"); ok = false; }
   if(InpSlBufferATR < 0.0 || InpSlBufferATR > 2.0) { Print("InpSlBufferATR out of range"); ok = false; }
   if(InpSlMinATR <= 0.0 || InpSlMaxATR < InpSlMinATR || InpSlMaxATR > 10.0) { Print("Bad SL clamps"); ok = false; }
   if(InpTpRR < 0.0 || InpTpRR > 10.0)              { Print("InpTpRR out of range [0,10]"); ok = false; }
   if(InpBeTriggerR < 0.0 || InpBeBufferR < 0.0 || (InpBeTriggerR > 0.0 && InpBeBufferR >= InpBeTriggerR)) { Print("Bad break-even settings"); ok = false; }
   if(InpTrailStartR < 0.0 || InpTrailATR <= 0.0)   { Print("Bad trailing settings"); ok = false; }
   if(InpMaxBarsInTrade < 0)                        { Print("InpMaxBarsInTrade must be >= 0"); ok = false; }
   if(InpServerGMTOffset < -12 || InpServerGMTOffset > 14) { Print("InpServerGMTOffset out of range"); ok = false; }
   if(InpSessionStartGMT < 0 || InpSessionStartGMT > 23 || InpSessionEndGMT < 1 || InpSessionEndGMT > 24 ||
      InpSessionEndGMT <= InpSessionStartGMT)       { Print("Bad session hours"); ok = false; }
   if(InpFridayLastEntry < 0 || InpFridayLastEntry > 24) { Print("Bad InpFridayLastEntry"); ok = false; }
   if(InpFridayCloseGMT < -1 || InpFridayCloseGMT > 23)  { Print("Bad InpFridayCloseGMT"); ok = false; }
   if(InpNewsMinsBefore < 0 || InpNewsMinsBefore > 720 || InpNewsMinsAfter < 0 || InpNewsMinsAfter > 720) { Print("Bad news window"); ok = false; }
   if(InpRiskPercent <= 0.0 || InpRiskPercent > 3.0) { Print("InpRiskPercent must be in (0,3]"); ok = false; }
   if(InpMaxLots <= 0.0)                            { Print("InpMaxLots must be > 0"); ok = false; }
   if(InpMaxTradesPerDay < 1 || InpMaxTradesPerDay > 20) { Print("InpMaxTradesPerDay out of range [1,20]"); ok = false; }
   if(InpDailyLossPct <= 0.0 || InpDailyLossPct > 20.0)  { Print("InpDailyLossPct out of range (0,20]"); ok = false; }
   if(InpKillSwitchDDPct <= 0.0 || InpKillSwitchDDPct > 50.0) { Print("InpKillSwitchDDPct out of range (0,50]"); ok = false; }
   if(InpMagic == 0)                                { Print("InpMagic must be non-zero"); ok = false; }
   if(InpSlippagePoints < 0 || InpSlippagePoints > 1000) { Print("InpSlippagePoints out of range"); ok = false; }
   if(InpRetryCooldownSec < 5)                      { Print("InpRetryCooldownSec must be >= 5"); ok = false; }
   if(StringLen(InpComment) > 31)                   { Print("InpComment too long (max 31)"); ok = false; }
   return ok;
  }

//+------------------------------------------------------------------+
//| Expert initialization                                            |
//+------------------------------------------------------------------+
int OnInit()
  {
   g_isTester = (bool)MQLInfoInteger(MQL_TESTER) || (bool)MQLInfoInteger(MQL_OPTIMIZATION);

   if(!ValidateInputs())
      return INIT_PARAMETERS_INCORRECT;

   string sym = _Symbol;
   StringToUpper(sym);
   if(!InpAllowNonGold && StringFind(sym, "XAU") < 0 && StringFind(sym, "GOLD") < 0)
     {
      PrintFormat("This EA is built for XAUUSD/GOLD. Symbol %s rejected (set InpAllowNonGold=true to override).", _Symbol);
      return INIT_PARAMETERS_INCORRECT;
     }

   g_gvPrefix = StringFormat("XAEA_%I64u_%I64d_", InpMagic, AccountInfoInteger(ACCOUNT_LOGIN));
   if(InpResetKillSwitch)
     {
      GlobalVariableDel(GvName("KILL"));
      GlobalVariableDel(GvName("PEAK"));
      Print("Kill switch and equity peak reset by input.");
     }
   if(g_isTester)
     {
      GlobalVariableDel(GvName("KILL"));      // fresh state per test pass
      GlobalVariableDel(GvName("PEAK"));
      GlobalVariablesDeleteAll(GvName("R_"));
     }

   g_hEmaSig  = iMA(_Symbol, InpSignalTF, InpEmaSignal, 0, MODE_EMA, PRICE_CLOSE);
   g_hAtrSig  = iATR(_Symbol, InpSignalTF, InpAtrPeriod);
   g_hRsiSig  = iRSI(_Symbol, InpSignalTF, InpRsiPeriod, PRICE_CLOSE);
   g_hEmaFast = iMA(_Symbol, InpRegimeTF, InpEmaFastRegime, 0, MODE_EMA, PRICE_CLOSE);
   g_hEmaSlow = iMA(_Symbol, InpRegimeTF, InpEmaSlowRegime, 0, MODE_EMA, PRICE_CLOSE);
   g_hAdx     = iADX(_Symbol, InpRegimeTF, InpAdxPeriod);
   if(g_hEmaSig == INVALID_HANDLE || g_hAtrSig == INVALID_HANDLE || g_hRsiSig == INVALID_HANDLE ||
      g_hEmaFast == INVALID_HANDLE || g_hEmaSlow == INVALID_HANDLE || g_hAdx == INVALID_HANDLE)
     {
      Print("Failed to create indicator handles: ", GetLastError());
      return INIT_FAILED;
     }

   g_trade.SetExpertMagicNumber(InpMagic);
   g_trade.SetDeviationInPoints(InpSlippagePoints);
   g_trade.SetTypeFillingBySymbol(_Symbol);
   g_trade.SetMarginMode();
   g_trade.LogLevel(LOG_LEVEL_ERRORS);

   PrintFormat("XAUUSD_AgentEA v1 ready on %s | signal %s regime %s | risk %.2f%% | GMT offset %dh%s",
               _Symbol, EnumToString(InpSignalTF), EnumToString(InpRegimeTF), InpRiskPercent,
               ServerGMTOffsetSeconds() / 3600, g_isTester ? " (tester: manual)" : "");
   return INIT_SUCCEEDED;
  }

//+------------------------------------------------------------------+
//| Expert deinitialization                                          |
//+------------------------------------------------------------------+
void OnDeinit(const int reason)
  {
   if(g_hEmaSig  != INVALID_HANDLE) IndicatorRelease(g_hEmaSig);
   if(g_hAtrSig  != INVALID_HANDLE) IndicatorRelease(g_hAtrSig);
   if(g_hRsiSig  != INVALID_HANDLE) IndicatorRelease(g_hRsiSig);
   if(g_hEmaFast != INVALID_HANDLE) IndicatorRelease(g_hEmaFast);
   if(g_hEmaSlow != INVALID_HANDLE) IndicatorRelease(g_hEmaSlow);
   if(g_hAdx     != INVALID_HANDLE) IndicatorRelease(g_hAdx);
  }

//+------------------------------------------------------------------+
//| Expert tick                                                      |
//+------------------------------------------------------------------+
void OnTick()
  {
   ManagePositions();              // every tick: protective logic only

   if(!IsNewSignalBar())           // entries: once per closed signal bar
      return;
   CleanupRiskVars();
   if(KillSwitchTripped())
      return;
   TryEnter();
  }

//+------------------------------------------------------------------+
//| Custom optimisation criterion                                    |
//|  rewards robustness: PF x sqrt(trades) x recovery / DD penalty   |
//+------------------------------------------------------------------+
double OnTester()
  {
   double trades = TesterStatistics(STAT_TRADES);
   if(trades < 30.0)
      return 0.0;
   double pf  = TesterStatistics(STAT_PROFIT_FACTOR);
   double rf  = TesterStatistics(STAT_RECOVERY_FACTOR);
   double ddp = TesterStatistics(STAT_EQUITY_DDREL_PERCENT);
   if(pf <= 1.0 || rf <= 0.0)
      return 0.0;
   return pf * MathSqrt(trades) * rf / (1.0 + ddp / 10.0);
  }
//+------------------------------------------------------------------+
