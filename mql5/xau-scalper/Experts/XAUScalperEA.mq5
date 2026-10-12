//+------------------------------------------------------------------+
//|                                                 XAUScalperEA.mq5 |
//|                                  XAUUSD M1 scalper (confluence)  |
//|  M15 trend filter -> M1 pullback confluence -> market entry       |
//|  Fixed-fractional risk, partial TP + BE + ATR trailing,           |
//|  hard daily-loss / max-drawdown guards. NO martingale, NO grid.   |
//|                                                                   |
//|  NOTE ON DIGITS: every distance input is in US DOLLARS (price     |
//|  units), so this EA is digit-agnostic. Digits are auto-detected   |
//|  (3-digit XAUUSD -> _Point = 0.001) and only used for price        |
//|  normalization and deviation-in-points.                           |
//+------------------------------------------------------------------+
#property copyright "Arena.ai Agent Mode"
#property link      "https://arena.ai"
#property version   "1.00"
#property description "XAUUSD scalper: M15 trend + M1 pullback confluence, fixed-fractional risk, partial TP, ATR trailing, hard DD guards."

#include <Trade/Trade.mqh>

//+------------------------------------------------------------------+
//| Enumerations                                                     |
//+------------------------------------------------------------------+
enum ENUM_SESSION_MODE
  {
   SESSION_OFF    = 0, // 0 - Off (24/5)
   SESSION_GMT    = 1, // 1 - GMT window (broker offset auto-detected)
   SESSION_SERVER = 2  // 2 - Broker server time window
  };

enum ENUM_DD_ACTION
  {
   DD_STOP_ONLY      = 0, // 0 - Stop opening new trades
   DD_CLOSE_AND_STOP = 1  // 1 - Close all positions and stop
  };

enum ENUM_NEWS_IMP
  {
   NEWS_LOW    = 1, // 1 - Low and above
   NEWS_MEDIUM = 2, // 2 - Medium and above
   NEWS_HIGH   = 3  // 3 - High only
  };

//+------------------------------------------------------------------+
//| Inputs                                                           |
//+------------------------------------------------------------------+
input group "=== Symbol & Identification ==="
input string InpSymbol          = "XAUUSD";  // Symbol (auto-suffix search if missing)
input int    InpDigitsOverride  = 0;         // Digits override (0 = auto-detect, 3 for 3-digit XAUUSD)
input long   InpMagic           = 260113;    // Magic number
input string InpTradeComment    = "XSCALP";  // Order comment (keep short, <= 12 chars)

input group "=== Risk & Money Management ==="
input double InpRiskPerTradePct = 0.5;   // Risk per trade (% of equity)
input double InpMaxLot          = 5.00;  // Max lot per trade
input double InpMaxDailyLossPct = 2.0;   // Max daily loss (% of day-start balance) -> stop for the day
input double InpDailyTargetPct  = 0.0;   // Daily profit target (% -> stop for the day, 0 = off)
input double InpMaxDrawdownPct  = 6.0;   // Max equity drawdown (%) -> trigger DD action
input ENUM_DD_ACTION InpDDAction = DD_CLOSE_AND_STOP; // Action when max DD is reached
input double InpMaxMarginUsePct = 75.0;  // Max free-margin usage per trade (%)

input group "=== Sessions & Calendar ==="
input ENUM_SESSION_MODE InpSessionMode   = SESSION_GMT; // Session filter mode
input string InpSessionStartGMT          = "08:00"; // Session start (GMT)
input string InpSessionEndGMT            = "20:00"; // Session end (GMT)
input string InpSessionStartSrv          = "10:00"; // Session start (server time)
input string InpSessionEndSrv            = "22:00"; // Session end (server time)
input bool   InpCloseAtSessionEnd        = true;   // Close open positions at session end
input bool   InpNoTradeFriday            = true;   // Stop trading Friday after hour
input int    InpFridayCloseHourGMT       = 19;     // Friday close hour (GMT)
input bool   InpUseNewsFilter            = true;   // Use economic calendar filter
input ENUM_NEWS_IMP InpNewsMinImp        = NEWS_MEDIUM; // Min news importance to block
input string InpNewsCurrency             = "USD";  // Currency filter ("" = all)
input int    InpNewsPauseBefore          = 20;     // Pause before news (minutes)
input int    InpNewsPauseAfter           = 20;     // Pause after news (minutes)

input group "=== Costs & Execution Filters ==="
input double InpMaxSpreadUSD    = 0.45;  // Max spread (USD, e.g. 0.45 = 45 cents)
input double InpMaxDeviationUSD = 0.15;  // Max deviation / slippage (USD)
input int    InpMaxPositions    = 2;     // Max simultaneous positions (total)
input int    InpMaxPerDirection = 1;     // Max positions per direction
input int    InpMaxTradesPerDay = 8;     // Max new trades per day
input int    InpCooldownBars    = 3;     // Cooldown after a loss (M1 bars)
input int    InpMaxBarsInTrade  = 90;    // Force close after N signal-TF bars (0 = off)

input group "=== Trend Filter (higher TF) ==="
input ENUM_TIMEFRAMES InpTrendTF   = PERIOD_M15; // Trend timeframe
input int    InpTrendFast          = 20;   // Fast MA period
input int    InpTrendSlow          = 50;   // Slow MA period
input ENUM_MA_METHOD InpTrendMethod = MODE_EMA; // MA method
input bool   InpUseADX             = true;  // Require ADX strength
input int    InpADXPeriod          = 14;   // ADX period
input double InpADXMin             = 18.0; // Min ADX value

input group "=== Entry Signal (M1) ==="
input ENUM_TIMEFRAMES InpSignalTF = PERIOD_M1;  // Signal timeframe
input int    InpPullbackMAPeriod  = 21;   // Pullback MA period (M1)
input ENUM_MA_METHOD InpPullbackMAMethod = MODE_EMA; // Pullback MA method
input double InpPullbackTolMult   = 0.05; // Touch tolerance (x ATR)
input double InpWickRatio         = 0.25; // Min rejection wick / candle range
input int    InpRSIPeriod         = 14;   // RSI period
input double InpRSIBuyMin         = 45.0; // RSI buy zone: min
input double InpRSIBuyMax         = 85.0; // RSI buy zone: max
input double InpRSISellMin        = 15.0; // RSI sell zone: min
input double InpRSISellMax        = 55.0; // RSI sell zone: max
input int    InpConfluenceMin     = 4;    // Min confluence score (max 5 with ADX, 4 without)
input bool   InpAllowBuy          = true;  // Allow long
input bool   InpAllowSell         = true;  // Allow short

input group "=== Volatility & Stop Loss ==="
input int    InpATRPeriod         = 14;   // ATR period
input ENUM_TIMEFRAMES InpATRTF    = PERIOD_M1; // ATR timeframe
input double InpATRMinUSD         = 0.15; // Min ATR (USD) - skip dead market
input double InpATRMaxUSD         = 4.00; // Max ATR (USD) - skip news spikes
input int    InpSLLookback        = 5;    // Swing lookback (bars) for structural SL
input double InpSLBufferMult      = 0.25; // Structural SL buffer (x ATR)
input double InpSLMinUSD          = 0.80; // Min SL distance (USD)
input double InpSLMaxUSD          = 4.00; // Max SL distance (USD)

input group "=== Exit Management ==="
input double InpTP1_R             = 1.00; // TP1 distance (R multiple)
input double InpTP1Pct            = 50.0; // Volume closed at TP1 (%)
input double InpTP2_R             = 2.50; // Runner target (R multiple, 0 = trail only)
input double InpBEOffsetR         = 0.10; // Break-even offset (R multiple)
input bool   InpUseTrailing       = true;  // Enable ATR trailing
input double InpTrailStartR       = 1.00; // Start trailing after (R multiple)
input double InpTrailATRMult      = 1.20; // Trail distance (x ATR)

input group "=== Optimization (OnTester) ==="
input int    InpOptMinTrades      = 200;  // Min trades before a run is scored

//+------------------------------------------------------------------+
//| Global state                                                     |
//+------------------------------------------------------------------+
CTrade  trade;

string g_symbol      = "";
int    g_digits      = 0;
double g_point       = 0.0;
double g_tickSize    = 0.0;
double g_tickValue   = 0.0;
double g_volMin      = 0.0;
double g_volMax      = 0.0;
double g_volStep     = 0.0;
int    g_volDec      = 2;
int    g_devPoints   = 10;
bool   g_netting     = false;

int    h_trendFast   = INVALID_HANDLE;
int    h_trendSlow   = INVALID_HANDLE;
int    h_adx         = INVALID_HANDLE;
int    h_ema         = INVALID_HANDLE;
int    h_rsi         = INVALID_HANDLE;
int    h_atr         = INVALID_HANDLE;

datetime g_lastBarTime  = 0;
datetime g_lastEntryBar = 0;
datetime g_lastLossTime = 0;
int      g_dayStamp     = 0;
double   g_dayStartBal  = 0.0;
double   g_peakEquity   = 0.0;
int      g_tradesToday  = 0;
bool     g_halted       = false;
bool     g_dayLossHit   = false;
bool     g_dayTargetHit = false;
int      g_gmtOffset    = 0;
datetime g_lastDash     = 0;
datetime g_newsChecked  = 0;
bool     g_newsBlocked  = false;
string   g_lastSignal   = "init";

//--- in-memory per-position bookkeeping (survives ticks, rebuilt on restart)
struct SPosState
  {
   ulong             ticket;
   double            initVol;
   bool              tp1Done;
  };
SPosState g_states[];
int       g_stateCount = 0;

//+------------------------------------------------------------------+
//| Small utilities                                                  |
//+------------------------------------------------------------------+
string Upper(string s)
{
   string out = "";
   int len = StringLen(s);
   for(int i = 0; i < len; i++)
   {
      ushort ch = StringGetChar(s, i);
      if(ch >= 'a' && ch <= 'z')
         ch = (ushort)(ch - 32);
      out += ShortToString(ch);
   }
   return out;
}

int ParseHHMM(const string s)
{
   int colon = StringFind(s, ":");
   if(colon < 0)
      return -1;
   int hh = (int)StringToInteger(StringSubstr(s, 0, colon));
   int mm = (int)StringToInteger(StringSubstr(s, colon + 1));
   if(hh < 0 || hh > 23 || mm < 0 || mm > 59)
      return -1;
   return hh * 60 + mm;
}

int MinuteOfDay(const datetime t)
{
   MqlDateTime st;
   TimeToStruct(t, st);
   return st.hour * 60 + st.min;
}

int DayStamp(const datetime t)
{
   MqlDateTime st;
   TimeToStruct(t, st);
   return st.year * 10000 + st.mon * 100 + st.day;
}

bool InWindow(const int nowMin, const int startMin, const int endMin)
{
   if(startMin == endMin)
      return true;
   if(startMin < endMin)
      return (nowMin >= startMin && nowMin < endMin);
   //--- window crosses midnight
   return (nowMin >= startMin || nowMin < endMin);
}

double NP(const double price)
{
   if(g_tickSize > 0.0)
      return NormalizeDouble(MathRound(price / g_tickSize) * g_tickSize, g_digits);
   return NormalizeDouble(price, g_digits);
}

void CalcVolumeDecimals()
{
   double s = g_volStep;
   g_volDec = 0;
   while(s < 1.0 && g_volDec < 8)
   {
      s = s * 10.0;
      g_volDec++;
   }
}

double NormVol(const double vol)
{
   double v = vol;
   if(g_volStep > 0.0)
      v = MathFloor(v / g_volStep + 0.0000001) * g_volStep;
   v = NormalizeDouble(v, g_volDec);
   if(v < g_volMin)
      v = g_volMin;
   if(v > g_volMax)
      v = g_volMax;
   return v;
}

int PointsFromUSD(const double usd)
{
   if(g_point <= 0.0)
      return 0;
   int p = (int)MathCeil(usd / g_point);
   if(p < 1)
      p = 1;
   return p;
}

double MinStopDist()
{
   long stops  = 0;
   long freeze = 0;
   if(!SymbolInfoInteger(g_symbol, SYMBOL_TRADE_STOPS_LEVEL, stops))
      stops = 0;
   if(!SymbolInfoInteger(g_symbol, SYMBOL_TRADE_FREEZE_LEVEL, freeze))
      freeze = 0;
   double d = MathMax((double)stops, (double)freeze) * g_point;
   if(d <= 0.0)
      d = g_point * 2.0;
   return d + g_point;
}

//+------------------------------------------------------------------+
//| Symbol resolution (handles broker suffixes: XAUUSD.m, XAUUSD# ..) |
//+------------------------------------------------------------------+
string ResolveSymbol(const string requested)
{
   if(requested == "")
      return _Symbol;

   ResetLastError();
   if(SymbolInfoInteger(requested, SYMBOL_EXIST) != 0)
   {
      if(SymbolSelect(requested, true))
         return requested;
   }

   string want = Upper(requested);
   int total = SymbolsTotal(false);
   for(int i = 0; i < total; i++)
   {
      string nm = SymbolName(i, false);
      if(StringFind(Upper(nm), want) == 0)
      {
         if(SymbolSelect(nm, true))
            return nm;
      }
   }
   //--- last resort: any gold vs USD symbol
   for(int i = 0; i < total; i++)
   {
      string nm = SymbolName(i, false);
      string up = Upper(nm);
      if(StringFind(up, "XAU") >= 0 && StringFind(up, "USD") >= 0)
      {
         if(SymbolSelect(nm, true))
            return nm;
      }
   }
   return "";
}

//+------------------------------------------------------------------+
//| Symbol specification                                             |
//+------------------------------------------------------------------+
bool SetupSymbolInfo()
{
   g_digits = (int)SymbolInfoInteger(g_symbol, SYMBOL_DIGITS);
   if(InpDigitsOverride > 0)
      g_digits = InpDigitsOverride;
   g_point = SymbolInfoDouble(g_symbol, SYMBOL_POINT);
   if(g_point <= 0.0)
      g_point = MathPow(10.0, -g_digits);

   g_tickSize  = SymbolInfoDouble(g_symbol, SYMBOL_TRADE_TICK_SIZE);
   g_tickValue = SymbolInfoDouble(g_symbol, SYMBOL_TRADE_TICK_VALUE);
   if(g_tickSize <= 0.0)
      g_tickSize = g_point;
   if(g_tickValue <= 0.0)
   {
      double contract = SymbolInfoDouble(g_symbol, SYMBOL_TRADE_CONTRACT_SIZE);
      if(contract <= 0.0)
         contract = 100.0;
      g_tickValue = contract * g_tickSize;
   }

   g_volMin  = SymbolInfoDouble(g_symbol, SYMBOL_VOLUME_MIN);
   g_volMax  = SymbolInfoDouble(g_symbol, SYMBOL_VOLUME_MAX);
   g_volStep = SymbolInfoDouble(g_symbol, SYMBOL_VOLUME_STEP);
   if(g_volMin <= 0.0)
      g_volMin = 0.01;
   if(g_volStep <= 0.0)
      g_volStep = 0.01;
   if(g_volMax <= 0.0)
      g_volMax = 100.0;
   CalcVolumeDecimals();

   g_devPoints = PointsFromUSD(InpMaxDeviationUSD);
   g_netting = (AccountInfoInteger(ACCOUNT_MARGIN_MODE) == ACCOUNT_MARGIN_MODE_RETAIL_NETTING);
   return true;
}

//+------------------------------------------------------------------+
//| Indicator handles                                                |
//+------------------------------------------------------------------+
bool CreateHandles()
{
   h_trendFast = iMA(g_symbol, InpTrendTF, InpTrendFast, 0, InpTrendMethod, PRICE_CLOSE);
   h_trendSlow = iMA(g_symbol, InpTrendTF, InpTrendSlow, 0, InpTrendMethod, PRICE_CLOSE);
   h_ema       = iMA(g_symbol, InpSignalTF, InpPullbackMAPeriod, 0, InpPullbackMAMethod, PRICE_CLOSE);
   h_rsi       = iRSI(g_symbol, InpSignalTF, InpRSIPeriod, PRICE_CLOSE);
   h_atr       = iATR(g_symbol, InpATRTF, InpATRPeriod);
   if(h_trendFast == INVALID_HANDLE || h_trendSlow == INVALID_HANDLE ||
      h_ema == INVALID_HANDLE || h_rsi == INVALID_HANDLE || h_atr == INVALID_HANDLE)
      return false;

   if(InpUseADX)
   {
      h_adx = iADX(g_symbol, InpTrendTF, InpADXPeriod);
      if(h_adx == INVALID_HANDLE)
         return false;
   }
   return true;
}

void ReleaseHandles()
{
   if(h_trendFast != INVALID_HANDLE) IndicatorRelease(h_trendFast);
   if(h_trendSlow != INVALID_HANDLE) IndicatorRelease(h_trendSlow);
   if(h_adx       != INVALID_HANDLE) IndicatorRelease(h_adx);
   if(h_ema       != INVALID_HANDLE) IndicatorRelease(h_ema);
   if(h_rsi       != INVALID_HANDLE) IndicatorRelease(h_rsi);
   if(h_atr       != INVALID_HANDLE) IndicatorRelease(h_atr);
   h_trendFast = INVALID_HANDLE;
   h_trendSlow = INVALID_HANDLE;
   h_adx       = INVALID_HANDLE;
   h_ema       = INVALID_HANDLE;
   h_rsi       = INVALID_HANDLE;
   h_atr       = INVALID_HANDLE;
}

bool IndicatorsReady()
{
   if(BarsCalculated(h_trendFast) < InpTrendSlow + 2)  return false;
   if(BarsCalculated(h_trendSlow) < InpTrendSlow + 2)  return false;
   if(BarsCalculated(h_ema)       < InpPullbackMAPeriod + 2) return false;
   if(BarsCalculated(h_rsi)       < InpRSIPeriod + 2)  return false;
   if(BarsCalculated(h_atr)       < InpATRPeriod + 2)  return false;
   if(InpUseADX && BarsCalculated(h_adx) < InpADXPeriod + 2) return false;
   return true;
}

//+------------------------------------------------------------------+
//| Data helpers                                                     |
//+------------------------------------------------------------------+
bool CopyBuf(const int handle, const int buffer, const int count, double &arr[])
{
   if(handle == INVALID_HANDLE)
      return false;
   ArrayResize(arr, count);
   ArraySetAsSeries(arr, true);
   int copied = CopyBuffer(handle, buffer, 0, count, arr);
   return (copied == count);
}

bool CopyRatesSafe(const string symbol, const ENUM_TIMEFRAMES tf, const int count, MqlRates &rates[])
{
   ArrayResize(rates, count);
   ArraySetAsSeries(rates, true);
   int copied = CopyRates(symbol, tf, 0, count, rates);
   return (copied == count);
}

double CurrentATR()
{
   double atr[];
   if(!CopyBuf(h_atr, 0, 3, atr))
      return 0.0;
   return atr[1];
}

double LowestLow(MqlRates &rates[], const int from, const int count)
{
   double v = rates[from].low;
   for(int i = from + 1; i < from + count; i++)
   {
      if(i >= ArraySize(rates))
         break;
      if(rates[i].low < v)
         v = rates[i].low;
   }
   return v;
}

double HighestHigh(MqlRates &rates[], const int from, const int count)
{
   double v = rates[from].high;
   for(int i = from + 1; i < from + count; i++)
   {
      if(i >= ArraySize(rates))
         break;
      if(rates[i].high > v)
         v = rates[i].high;
   }
   return v;
}

//+------------------------------------------------------------------+
//| Filling mode                                                     |
//+------------------------------------------------------------------+
ENUM_ORDER_TYPE_FILLING GetFillingMode(const string symbol)
{
   long mode = 0;
   if(!SymbolInfoInteger(symbol, SYMBOL_FILLING_MODE, mode))
      mode = 0;
   if((mode & SYMBOL_FILLING_FOK) != 0)
      return ORDER_FILLING_FOK;
   if((mode & SYMBOL_FILLING_IOC) != 0)
      return ORDER_FILLING_IOC;
   return ORDER_FILLING_RETURN;
}

//+------------------------------------------------------------------+
//| Session / calendar                                               |
//+------------------------------------------------------------------+
void UpdateGmtOffset()
{
   g_gmtOffset = (int)(TimeCurrent() - TimeGMT());
}

datetime GmtNow()
{
   return TimeCurrent() - g_gmtOffset;
}

bool IsFridayStop(const datetime nowGmt)
{
   if(!InpNoTradeFriday)
      return false;
   MqlDateTime st;
   TimeToStruct(nowGmt, st);
   if(st.day_of_week != 5)
      return false;
   return (st.hour >= InpFridayCloseHourGMT);
}

bool InSession()
{
   if(InpSessionMode == SESSION_OFF)
      return !IsFridayStop(GmtNow());

   int nowMin  = 0;
   int startMin = 0;
   int endMin   = 0;

   if(InpSessionMode == SESSION_GMT)
   {
      datetime nowGmt = GmtNow();
      nowMin   = MinuteOfDay(nowGmt);
      startMin = ParseHHMM(InpSessionStartGMT);
      endMin   = ParseHHMM(InpSessionEndGMT);
      if(startMin < 0 || endMin < 0)
         return true;
      if(IsFridayStop(nowGmt))
         return false;
   }
   else
   {
      datetime nowSrv = TimeCurrent();
      nowMin   = MinuteOfDay(nowSrv);
      startMin = ParseHHMM(InpSessionStartSrv);
      endMin   = ParseHHMM(InpSessionEndSrv);
      if(startMin < 0 || endMin < 0)
         return true;
      if(IsFridayStop(nowSrv))
         return false;
   }
   return InWindow(nowMin, startMin, endMin);
}

ENUM_CALENDAR_EVENT_IMPORTANCE MinImportance()
{
   if(InpNewsMinImp == NEWS_LOW)
      return CALENDAR_IMPORTANCE_LOW;
   if(InpNewsMinImp == NEWS_MEDIUM)
      return CALENDAR_IMPORTANCE_MEDIUM;
   return CALENDAR_IMPORTANCE_HIGH;
}

bool NewsBlocked()
{
   if(!InpUseNewsFilter)
      return false;

   //--- cache for 60 seconds: the calendar API is not meant for every tick
   if(TimeCurrent() - g_newsChecked < 60)
      return g_newsBlocked;
   g_newsChecked = TimeCurrent();

   MqlCalendarValue vals[];
   datetime now    = TimeCurrent();
   datetime from   = now - InpNewsPauseAfter * 60;
   datetime to     = now + InpNewsPauseBefore * 60;
   string   cur    = InpNewsCurrency;
   if(cur == "")
      cur = NULL;

   if(!CalendarValueHistory(vals, from, to, NULL, cur))
   {
      g_newsBlocked = false;   // no calendar available -> do not block
      return g_newsBlocked;
   }

   int minImp = (int)MinImportance();
   int n = ArraySize(vals);
   for(int i = 0; i < n; i++)
   {
      if((int)vals[i].impact_type < minImp)
         continue;
      datetime evt = vals[i].time;
      if(evt >= from && evt <= to)
      {
         g_newsBlocked = true;
         return g_newsBlocked;
      }
   }
   g_newsBlocked = false;
   return g_newsBlocked;
}

//+------------------------------------------------------------------+
//| Position bookkeeping helpers                                     |
//+------------------------------------------------------------------+
int FindState(const ulong ticket)
{
   for(int i = 0; i < g_stateCount; i++)
      if(g_states[i].ticket == ticket)
         return i;
   return -1;
}

void StateAdd(const ulong ticket, const double vol)
{
   int idx = FindState(ticket);
   if(idx >= 0)
   {
      g_states[idx].initVol = vol;
      g_states[idx].tp1Done = false;
      return;
   }
   ArrayResize(g_states, g_stateCount + 1);
   g_states[g_stateCount].ticket  = ticket;
   g_states[g_stateCount].initVol = vol;
   g_states[g_stateCount].tp1Done = false;
   g_stateCount++;
}

void StateMarkTp1(const ulong ticket)
{
   int idx = FindState(ticket);
   if(idx >= 0)
      g_states[idx].tp1Done = true;
}

bool StateTp1Done(const ulong ticket)
{
   int idx = FindState(ticket);
   if(idx < 0)
      return false;
   return g_states[idx].tp1Done;
}

void StatesPrune()
{
   for(int i = g_stateCount - 1; i >= 0; i--)
   {
      if(!PositionSelectByTicket(g_states[i].ticket))
      {
         for(int j = i; j < g_stateCount - 1; j++)
            g_states[j] = g_states[j + 1];
         g_stateCount--;
         ArrayResize(g_states, g_stateCount);
      }
   }
}

int CountOurPositions()
{
   int n = 0;
   for(int i = PositionsTotal() - 1; i >= 0; i--)
   {
      ulong ticket = PositionGetTicket(i);
      if(ticket == 0)
         continue;
      if(!PositionSelectByTicket(ticket))
         continue;
      if(PositionGetString(POSITION_SYMBOL) != g_symbol)
         continue;
      if(PositionGetInteger(POSITION_MAGIC) != InpMagic)
         continue;
      n++;
   }
   return n;
}

int CountOurDirection(const int dir)
{
   int n = 0;
   long want = (dir > 0) ? POSITION_TYPE_BUY : POSITION_TYPE_SELL;
   for(int i = PositionsTotal() - 1; i >= 0; i--)
   {
      ulong ticket = PositionGetTicket(i);
      if(ticket == 0)
         continue;
      if(!PositionSelectByTicket(ticket))
         continue;
      if(PositionGetString(POSITION_SYMBOL) != g_symbol)
         continue;
      if(PositionGetInteger(POSITION_MAGIC) != InpMagic)
         continue;
      if(PositionGetInteger(POSITION_TYPE) == want)
         n++;
   }
   return n;
}

//+------------------------------------------------------------------+
//| R-multiple recovery from order comment                           |
//+------------------------------------------------------------------+
double ParseR(const string comment)
{
   int p = StringFind(comment, "#", 0);
   if(p < 0)
      return -1.0;
   string num = StringSubstr(comment, p + 1);
   double v = StringToDouble(num);
   if(v <= 0.0)
      return -1.0;
   return v;
}

int StageOf(const bool isBuy, const double entry, const double sl)
{
   if(sl <= 0.0)
      return 0;
   if(isBuy)
      return (sl >= entry) ? 1 : 0;
   return (sl <= entry) ? 1 : 0;
}

//+------------------------------------------------------------------+
//| Risk / account state                                             |
//+------------------------------------------------------------------+
void RollDay()
{
   int stamp = DayStamp(TimeCurrent());
   if(stamp == g_dayStamp)
      return;
   g_dayStamp     = stamp;
   g_dayStartBal  = AccountInfoDouble(ACCOUNT_BALANCE);
   g_tradesToday  = 0;
   g_dayLossHit   = false;
   g_dayTargetHit = false;
   UpdateGmtOffset();
}

double DayLossPct()
{
   if(g_dayStartBal <= 0.0)
      return 0.0;
   double eq = AccountInfoDouble(ACCOUNT_EQUITY);
   return (g_dayStartBal - eq) / g_dayStartBal * 100.0;
}

double DayProfitPct()
{
   if(g_dayStartBal <= 0.0)
      return 0.0;
   double eq = AccountInfoDouble(ACCOUNT_EQUITY);
   return (eq - g_dayStartBal) / g_dayStartBal * 100.0;
}

double DrawdownPct()
{
   if(g_peakEquity <= 0.0)
      return 0.0;
   double eq = AccountInfoDouble(ACCOUNT_EQUITY);
   return (g_peakEquity - eq) / g_peakEquity * 100.0;
}

bool ClosePosition(const ulong ticket)
{
   if(!PositionSelectByTicket(ticket))
      return false;
   return trade.PositionClose(ticket, g_devPoints);
}

void CloseAllOur()
{
   for(int i = PositionsTotal() - 1; i >= 0; i--)
   {
      ulong ticket = PositionGetTicket(i);
      if(ticket == 0)
         continue;
      if(!PositionSelectByTicket(ticket))
         continue;
      if(PositionGetString(POSITION_SYMBOL) != g_symbol)
         continue;
      if(PositionGetInteger(POSITION_MAGIC) != InpMagic)
         continue;
      if(!ClosePosition(ticket))
         Print("CloseAllOur: failed to close ticket ", ticket, " retcode=", trade.ResultRetcode());
   }
}

void UpdateRiskState()
{
   RollDay();

   double eq  = AccountInfoDouble(ACCOUNT_EQUITY);
   double bal = AccountInfoDouble(ACCOUNT_BALANCE);
   if(g_dayStartBal <= 0.0)
      g_dayStartBal = bal;
   if(eq > g_peakEquity)
      g_peakEquity = eq;

   if(InpMaxDailyLossPct > 0.0 && !g_dayLossHit && DayLossPct() >= InpMaxDailyLossPct)
   {
      g_dayLossHit = true;
      Print("Daily loss limit reached (", DoubleToString(DayLossPct(), 2), "%). No new trades today.");
   }
   if(InpDailyTargetPct > 0.0 && !g_dayTargetHit && DayProfitPct() >= InpDailyTargetPct)
   {
      g_dayTargetHit = true;
      Print("Daily target reached (", DoubleToString(DayProfitPct(), 2), "%). No new trades today.");
   }
   if(InpMaxDrawdownPct > 0.0 && !g_halted && DrawdownPct() >= InpMaxDrawdownPct)
   {
      g_halted = true;
      Print("MAX DRAWDOWN reached (", DoubleToString(DrawdownPct(), 2), "%). Trading halted.");
      if(InpDDAction == DD_CLOSE_AND_STOP)
         CloseAllOur();
   }
}

double CalcLots(const double slDist)
{
   if(slDist <= 0.0)
      return 0.0;

   double riskMoney = AccountInfoDouble(ACCOUNT_EQUITY) * InpRiskPerTradePct / 100.0;
   double lossPerLot = (slDist / g_tickSize) * g_tickValue;
   if(lossPerLot <= 0.0)
      return 0.0;

   double lots = NormVol(riskMoney / lossPerLot);
   if(lots > InpMaxLot)
      lots = NormVol(InpMaxLot);
   if(lots < g_volMin)
      lots = g_volMin;

   //--- margin guard
   double price = SymbolInfoDouble(g_symbol, SYMBOL_ASK);
   double margin = 0.0;
   double free   = AccountInfoDouble(ACCOUNT_MARGIN_FREE) * InpMaxMarginUsePct / 100.0;
   while(lots > g_volMin)
   {
      if(!OrderCalcMargin(ORDER_TYPE_BUY, g_symbol, lots, price, margin))
         break;
      if(margin <= free)
         break;
      lots = NormVol(lots - g_volStep);
   }
   if(lots < g_volMin)
      lots = 0.0;
   return lots;
}

//+------------------------------------------------------------------+
//| Order execution                                                  |
//+------------------------------------------------------------------+
bool PartialClose(const ulong ticket, const double volume)
{
   if(!PositionSelectByTicket(ticket))
      return false;

   string sym = PositionGetString(POSITION_SYMBOL);
   long   type = PositionGetInteger(POSITION_TYPE);
   double posVol = PositionGetDouble(POSITION_VOLUME);

   double closeVol = NormVol(volume);
   if(closeVol <= 0.0 || closeVol >= posVol)
      return false;

   MqlTradeRequest req;
   MqlTradeResult  res;
   ZeroMemory(req);
   ZeroMemory(res);

   req.action    = TRADE_ACTION_DEAL;
   req.position  = ticket;
   req.symbol    = sym;
   req.volume    = closeVol;
   req.type      = (type == POSITION_TYPE_BUY) ? ORDER_TYPE_SELL : ORDER_TYPE_BUY;
   req.price     = (type == POSITION_TYPE_BUY) ? SymbolInfoDouble(sym, SYMBOL_BID) : SymbolInfoDouble(sym, SYMBOL_ASK);
   req.deviation = g_devPoints;
   req.magic     = InpMagic;
   req.comment   = "tp1";
   req.type_filling = GetFillingMode(sym);
   req.type_time    = ORDER_TIME_GTC;

   if(!OrderSend(req, res))
   {
      Print("PartialClose OrderSend failed. ticket=", ticket, " retcode=", res.retcode);
      return false;
   }
   if(res.retcode != TRADE_RETCODE_DONE && res.retcode != TRADE_RETCODE_PLACED &&
      res.retcode != TRADE_RETCODE_DONE_PARTIAL)
   {
      Print("PartialClose rejected. retcode=", res.retcode, " (", res.comment, ")");
      return false;
   }
   Print("TP1 partial close: ", closeVol, " of ", posVol, " on ticket ", ticket);
   return true;
}

bool ModifySLTP(const ulong ticket, const double sl, const double tp)
{
   if(!PositionSelectByTicket(ticket))
      return false;
   return trade.PositionModify(ticket, sl, tp);
}

bool ValidSL(const bool isBuy, const double sl, const double tp, const double refPrice)
{
   if(sl <= 0.0)
      return false;
   double minDist = MinStopDist();
   double d = isBuy ? (refPrice - sl) : (sl - refPrice);
   if(d < minDist)
      return false;
   if(tp > 0.0)
   {
      double dSLTP = isBuy ? (tp - sl) : (sl - tp);
      if(dSLTP < minDist)
         return false;
   }
   return true;
}

//+------------------------------------------------------------------+
//| Signal evaluation                                                |
//+------------------------------------------------------------------+
struct CSignal
{
   bool   valid;
   int    dir;
   double slDist;
   int    score;
   string why;
};

CSignal EvaluateSignal()
{
   CSignal s;
   s.valid  = false;
   s.dir    = 0;
   s.slDist = 0.0;
   s.score  = 0;
   s.why    = "";

   int bars = InpSLLookback + 8;
   MqlRates m1[];
   if(!CopyRatesSafe(g_symbol, InpSignalTF, bars, m1))
   {
      s.why = "no rates";
      return s;
   }

   double emaPB[], rsi[], atr[];
   if(!CopyBuf(h_ema, 0, 4, emaPB) || !CopyBuf(h_rsi, 0, 4, rsi) || !CopyBuf(h_atr, 0, 4, atr))
   {
      s.why = "no buffers";
      return s;
   }
   double trF[], trS[];
   if(!CopyBuf(h_trendFast, 0, 3, trF) || !CopyBuf(h_trendSlow, 0, 3, trS))
   {
      s.why = "no trend";
      return s;
   }

   double atr1 = atr[1];
   if(atr1 <= 0.0)
   {
      s.why = "atr=0";
      return s;
   }
   if(atr1 < InpATRMinUSD || atr1 > InpATRMaxUSD)
   {
      s.why = "ATR out of range";
      return s;
   }

   //--- bar 1 = last closed bar (index 0 = forming bar)
   double open1  = m1[1].open;
   double high1  = m1[1].high;
   double low1   = m1[1].low;
   double close1 = m1[1].close;
   double range1 = high1 - low1;
   if(range1 <= 0.0)
   {
      s.why = "zero range";
      return s;
   }

   //--- trend direction from higher timeframe
   bool trendUp = (trF[1] > trS[1]);
   bool trendDn = (trF[1] < trS[1]);

   int dir = 0;
   if(trendUp && InpAllowBuy)
      dir = 1;
   else
   {
      if(trendDn && InpAllowSell)
         dir = -1;
   }
   if(dir == 0)
   {
      s.why = "no trend alignment";
      return s;
   }

   int score = 1;   // component 1: trend alignment

   //--- component 2: ADX strength
   if(InpUseADX)
   {
      double adxv[];
      if(CopyBuf(h_adx, 0, 3, adxv) && adxv[1] >= InpADXMin)
         score += 1;
   }

   double ema = emaPB[1];
   double tol = atr1 * InpPullbackTolMult;
   double lowerWick = MathMin(open1, close1) - low1;
   double upperWick = high1 - MathMax(open1, close1);

   if(dir == 1)
   {
      bool touched  = (low1 <= ema + tol);
      bool rejected = (close1 > ema);
      bool pin      = (close1 > open1) && (lowerWick >= InpWickRatio * range1);
      bool rsiOK    = (rsi[1] >= InpRSIBuyMin && rsi[1] <= InpRSIBuyMax);

      if(touched && rejected) score += 1;   // component 3
      if(pin)                 score += 1;   // component 4
      if(rsiOK)               score += 1;   // component 5

      if(score < InpConfluenceMin)
      {
         s.why = "score low (buy)";
         s.score = score;
         return s;
      }

      double ll     = LowestLow(m1, 1, InpSLLookback);
      double slPrice = ll - atr1 * InpSLBufferMult;
      double entry  = SymbolInfoDouble(g_symbol, SYMBOL_ASK);
      double slDist = entry - slPrice;
      slDist = MathMax(slDist, InpSLMinUSD);
      slDist = MathMin(slDist, InpSLMaxUSD);
      slDist = MathMax(slDist, MinStopDist());

      s.valid  = true;
      s.dir    = 1;
      s.slDist = slDist;
      s.score  = score;
      s.why    = "buy setup";
      return s;
   }

   //--- dir == -1
   bool touched  = (high1 >= ema - tol);
   bool rejected = (close1 < ema);
   bool pin      = (close1 < open1) && (upperWick >= InpWickRatio * range1);
   bool rsiOK    = (rsi[1] >= InpRSISellMin && rsi[1] <= InpRSISellMax);

   if(touched && rejected) score += 1;
   if(pin)                 score += 1;
   if(rsiOK)               score += 1;

   if(score < InpConfluenceMin)
   {
      s.why = "score low (sell)";
      s.score = score;
      return s;
   }

   double hh      = HighestHigh(m1, 1, InpSLLookback);
   double slPrice = hh + atr1 * InpSLBufferMult;
   double entry   = SymbolInfoDouble(g_symbol, SYMBOL_BID);
   double slDist  = slPrice - entry;
   slDist = MathMax(slDist, InpSLMinUSD);
   slDist = MathMin(slDist, InpSLMaxUSD);
   slDist = MathMax(slDist, MinStopDist());

   s.valid  = true;
   s.dir    = -1;
   s.slDist = slDist;
   s.score  = score;
   s.why    = "sell setup";
   return s;
}

//+------------------------------------------------------------------+
//| Entry                                                            |
//+------------------------------------------------------------------+
bool GuardsOK(const int dir)
{
   if(g_halted)
      return false;
   if(!InSession())
      return false;

   double bid = SymbolInfoDouble(g_symbol, SYMBOL_BID);
   double ask = SymbolInfoDouble(g_symbol, SYMBOL_ASK);
   if(bid <= 0.0 || ask <= 0.0)
      return false;

   double spread = ask - bid;
   if(spread > InpMaxSpreadUSD)
      return false;

   if(NewsBlocked())
      return false;

   if(g_dayLossHit || g_dayTargetHit)
      return false;
   if(g_tradesToday >= InpMaxTradesPerDay)
      return false;

   int maxTotal = InpMaxPositions;
   if(g_netting)
      maxTotal = 1;
   if(CountOurPositions() >= maxTotal)
      return false;
   if(CountOurDirection(dir) >= InpMaxPerDirection)
      return false;

   if(InpCooldownBars > 0 && g_lastLossTime > 0)
   {
      int secs = (int)(InpCooldownBars * PeriodSeconds(InpSignalTF));
      if((int)(TimeCurrent() - g_lastLossTime) < secs)
         return false;
   }
   return true;
}

ulong FindNewestPosition(const long wantType)
{
   ulong best = 0;
   datetime bestTime = 0;
   for(int i = PositionsTotal() - 1; i >= 0; i--)
   {
      ulong t = PositionGetTicket(i);
      if(t == 0)
         continue;
      if(!PositionSelectByTicket(t))
         continue;
      if(PositionGetString(POSITION_SYMBOL) != g_symbol)
         continue;
      if(PositionGetInteger(POSITION_MAGIC) != InpMagic)
         continue;
      if(PositionGetInteger(POSITION_TYPE) != wantType)
         continue;
      datetime ot = (datetime)PositionGetInteger(POSITION_TIME);
      if(ot >= bestTime)
      {
         bestTime = ot;
         best = t;
      }
   }
   return best;
}

bool OpenTrade(const int dir, const double slDist)
{
   double bid = SymbolInfoDouble(g_symbol, SYMBOL_BID);
   double ask = SymbolInfoDouble(g_symbol, SYMBOL_ASK);
   if(bid <= 0.0 || ask <= 0.0)
      return false;

   double lots = CalcLots(slDist);
   if(lots <= 0.0)
   {
      Print("Lot size is 0 - trade skipped (equity/margin too small for this SL).");
      return false;
   }

   double price = (dir > 0) ? ask : bid;
   double sl    = (dir > 0) ? price - slDist : price + slDist;
   double tp    = 0.0;
   if(InpTP2_R > 0.0)
      tp = (dir > 0) ? price + InpTP2_R * slDist : price - InpTP2_R * slDist;

   sl = NP(sl);
   if(tp > 0.0)
      tp = NP(tp);

   if(!ValidSL(dir > 0, sl, tp, price))
   {
      Print("SL/TP rejected by broker stops level. price=", price, " sl=", sl, " tp=", tp);
      return false;
   }

   //--- comment carries the initial R so the EA can rebuild state after a restart
   string cmt = InpTradeComment + "#" + DoubleToString(slDist, 2);

   bool ok = false;
   if(dir > 0)
      ok = trade.Buy(lots, g_symbol, price, sl, tp, cmt);
   else
      ok = trade.Sell(lots, g_symbol, price, sl, tp, cmt);

   if(!ok || trade.ResultRetcode() != TRADE_RETCODE_DONE)
   {
      Print("Order failed: dir=", dir, " lots=", lots, " retcode=", trade.ResultRetcode(),
            " (", trade.ResultRetcodeDescription(), ")");
      return false;
   }

   //--- remember the position we just opened (newest position with our magic)
   ulong posTicket = FindNewestPosition((dir > 0) ? POSITION_TYPE_BUY : POSITION_TYPE_SELL);
   if(posTicket > 0)
      StateAdd(posTicket, lots);

   g_tradesToday++;
   string side = "BUY ";
   if(dir < 0)
      side = "SELL";
   Print("OPEN ", side, " lots=", DoubleToString(lots, 2),
         " sl=", DoubleToString(sl, g_digits), " tp=", DoubleToString(tp, g_digits),
         " R=", DoubleToString(slDist, 2), " score=", g_lastSignal);
   return true;
}

//+------------------------------------------------------------------+
//| Per-position management                                          |
//+------------------------------------------------------------------+
void ManageOne(const ulong ticket)
{
   if(!PositionSelectByTicket(ticket))
      return;

   string sym = PositionGetString(POSITION_SYMBOL);
   if(sym != g_symbol)
      return;

   double vol    = PositionGetDouble(POSITION_VOLUME);
   double entry  = PositionGetDouble(POSITION_PRICE_OPEN);
   double sl     = PositionGetDouble(POSITION_SL);
   double tp     = PositionGetDouble(POSITION_TP);
   long   type   = PositionGetInteger(POSITION_TYPE);
   string cmt    = PositionGetString(POSITION_COMMENT);
   datetime openTime = (datetime)PositionGetInteger(POSITION_TIME);

   bool isBuy = (type == POSITION_TYPE_BUY);
   double bid = SymbolInfoDouble(g_symbol, SYMBOL_BID);
   double ask = SymbolInfoDouble(g_symbol, SYMBOL_ASK);

   double R = ParseR(cmt);
   if(R <= 0.0)
   {
      double a = CurrentATR();
      if(a > 0.0)
         R = a * 1.2;
      else
         R = 0.0;
   }
   if(R <= 0.0)
      return;

   double profit = isBuy ? (bid - entry) : (entry - ask);
   int stage = StageOf(isBuy, entry, sl);
   if(stage == 0 && StateTp1Done(ticket))
      stage = 1;

   //--- 1) TP1: partial close + move to break-even
   if(stage == 0 && !StateTp1Done(ticket) && profit >= InpTP1_R * R)
   {
      double closeVol = NormVol(vol * InpTP1Pct / 100.0);
      double remain   = NormVol(vol - closeVol);
      if(closeVol >= g_volMin && remain >= g_volMin)
      {
         if(PartialClose(ticket, closeVol))
         {
            StateMarkTp1(ticket);
            double newSL = isBuy ? entry + InpBEOffsetR * R : entry - InpBEOffsetR * R;
            newSL = NP(newSL);
            if(ValidSL(isBuy, newSL, tp, isBuy ? bid : ask))
            {
               if(!ModifySLTP(ticket, newSL, tp))
                  Print("Break-even modify failed. retcode=", trade.ResultRetcode());
            }
         }
      }
      else
      {
         //--- position too small to split -> take the whole thing at TP1
         if(ClosePosition(ticket))
            Print("Position too small to split - closed fully at TP1. ticket=", ticket);
      }
      return;
   }

   //--- 2) ATR trailing on the runner
   if(InpUseTrailing && stage >= 1 && profit >= InpTrailStartR * R)
   {
      double a = CurrentATR();
      if(a > 0.0)
      {
         double buffer = a * InpTrailATRMult;
         double newSL  = isBuy ? (bid - buffer) : (ask + buffer);
         newSL = NP(newSL);
         bool better = isBuy ? (newSL > sl + g_point) : ((sl <= 0.0) || (newSL < sl - g_point));
         if(better && ValidSL(isBuy, newSL, tp, isBuy ? bid : ask))
            ModifySLTP(ticket, newSL, tp);
      }
   }

   //--- 3) Time stop
   if(InpMaxBarsInTrade > 0)
   {
      int secPerBar = (int)PeriodSeconds(InpSignalTF);
      if(secPerBar > 0)
      {
         int barsOpen = (int)((TimeCurrent() - openTime) / secPerBar);
         if(barsOpen >= InpMaxBarsInTrade && profit > 0.0)
         {
            if(ClosePosition(ticket))
               Print("Time stop after ", barsOpen, " bars. ticket=", ticket);
         }
      }
   }
}

void ManagePositions()
{
   StatesPrune();
   for(int i = PositionsTotal() - 1; i >= 0; i--)
   {
      ulong ticket = PositionGetTicket(i);
      if(ticket == 0)
         continue;
      if(!PositionSelectByTicket(ticket))
         continue;
      if(PositionGetString(POSITION_SYMBOL) != g_symbol)
         continue;
      if(PositionGetInteger(POSITION_MAGIC) != InpMagic)
         continue;
      ManageOne(ticket);
   }
}

//+------------------------------------------------------------------+
//| Loss tracking (for cooldown)                                     |
//+------------------------------------------------------------------+
void TrackClosedLosses()
{
   if(InpCooldownBars <= 0)
      return;
   static datetime lastChecked = 0;
   datetime to = TimeCurrent();
   if(to - lastChecked < 30)
      return;
   datetime from = to - 24 * 3600;
   if(!HistorySelect(from, to))
      return;
   int total = HistoryDealsTotal();
   for(int i = 0; i < total; i++)
   {
      ulong ticket = HistoryDealGetTicket(i);
      if(ticket == 0)
         continue;
      if(HistoryDealGetInteger(ticket, DEAL_MAGIC) != InpMagic)
         continue;
      if(HistoryDealGetString(ticket, DEAL_SYMBOL) != g_symbol)
         continue;
      long entryType = 0;
      if(!HistoryDealGetInteger(ticket, DEAL_ENTRY, entryType))
         continue;
      if(entryType != DEAL_ENTRY_OUT)
         continue;
      datetime dt = (datetime)HistoryDealGetInteger(ticket, DEAL_TIME);
      if(dt <= lastChecked)
         continue;
      double profit = HistoryDealGetDouble(ticket, DEAL_PROFIT);
      if(profit < 0.0)
         g_lastLossTime = dt;
   }
   lastChecked = to;
}

//+------------------------------------------------------------------+
//| Dashboard                                                        |
//+------------------------------------------------------------------+
void ShowDashboard()
{
   if(TimeCurrent() - g_lastDash < 1)
      return;
   g_lastDash = TimeCurrent();

   string txt = "";
   txt += "XAUScalperEA v1.00\n";
   txt += "Symbol: " + g_symbol + "  digits=" + IntegerToString(g_digits) +
          "  point=" + DoubleToString(g_point, g_digits) + "\n";
   string mode = "hedging";
   if(g_netting)
      mode = "netting";
   txt += "Account mode: " + mode + "\n";
   string session = "closed";
   if(InSession())
      session = "OPEN";
   string news = "no";
   if(NewsBlocked())
      news = "YES";
   txt += "Session: " + session + "   News block: " + news + "\n";
   txt += "Spread: " + DoubleToString(SymbolInfoDouble(g_symbol, SYMBOL_ASK) - SymbolInfoDouble(g_symbol, SYMBOL_BID), g_digits) +
          " USD (max " + DoubleToString(InpMaxSpreadUSD, 2) + ")\n";
   txt += "ATR(M1): " + DoubleToString(CurrentATR(), g_digits) + "\n";
   txt += "Positions: " + IntegerToString(CountOurPositions()) + "/" + IntegerToString(InpMaxPositions) +
          "   Trades today: " + IntegerToString(g_tradesToday) + "/" + IntegerToString(InpMaxTradesPerDay) + "\n";
   txt += "Day P/L: " + DoubleToString(DayProfitPct(), 2) + "%   DD: " + DoubleToString(DrawdownPct(), 2) +
          "% (max " + DoubleToString(InpMaxDrawdownPct, 2) + "%)\n";
   string state = "running";
   if(g_dayTargetHit)
      state = "paused (daily target)";
   if(g_dayLossHit)
      state = "paused (daily loss)";
   if(g_halted)
      state = "HALTED (max DD)";
   txt += "State: " + state + "\n";
   txt += "Last signal: " + g_lastSignal + "\n";
   Comment(txt);
}

//+------------------------------------------------------------------+
//| Expert initialization                                            |
//+------------------------------------------------------------------+
int OnInit()
{
   g_symbol = ResolveSymbol(InpSymbol);
   if(g_symbol == "")
   {
      Print("ERROR: symbol '", InpSymbol, "' not found on this terminal.");
      return INIT_FAILED;
   }
   if(!SymbolSelect(g_symbol, true))
   {
      Print("ERROR: cannot select symbol ", g_symbol);
      return INIT_FAILED;
   }
   if(!SetupSymbolInfo())
   {
      Print("ERROR: cannot read symbol specification for ", g_symbol);
      return INIT_FAILED;
   }

   if(InpConfluenceMin < 1 || InpConfluenceMin > 5)
   {
      Print("ERROR: InpConfluenceMin must be between 1 and 5.");
      return INIT_PARAMETERS_INCORRECT;
   }
   if(InpTP1Pct <= 0.0 || InpTP1Pct >= 100.0)
   {
      Print("ERROR: InpTP1Pct must be > 0 and < 100.");
      return INIT_PARAMETERS_INCORRECT;
   }
   if(InpRiskPerTradePct <= 0.0)
   {
      Print("ERROR: InpRiskPerTradePct must be > 0.");
      return INIT_PARAMETERS_INCORRECT;
   }

   if(!CreateHandles())
   {
      Print("ERROR: indicator handle creation failed. GetLastError=", GetLastError());
      ReleaseHandles();
      return INIT_FAILED;
   }

   trade.SetExpertMagicNumber(InpMagic);
   trade.SetDeviationInPoints(g_devPoints);
   trade.SetTypeFillingBySymbol(g_symbol);
   trade.SetAsyncMode(false);

   UpdateGmtOffset();
   RollDay();
   g_peakEquity = AccountInfoDouble(ACCOUNT_EQUITY);
   g_lastBarTime = 0;

   Print("----------------------------------------------------");
   Print("XAUScalperEA initialized");
   Print("  symbol      : ", g_symbol);
   Print("  digits      : ", g_digits, "   point=", DoubleToString(g_point, g_digits),
         "   tickSize=", DoubleToString(g_tickSize, g_digits),
         "   tickValue=", DoubleToString(g_tickValue, 4));
   Print("  lot step    : ", DoubleToString(g_volStep, g_volDec), "  min=", DoubleToString(g_volMin, g_volDec),
         "  max=", DoubleToString(g_volMax, g_volDec));
   Print("  deviation   : ", g_devPoints, " points");
   Print("  GMT offset  : ", g_gmtOffset / 3600, " h  (server time - GMT)");
   string mode = "hedging";
   if(g_netting)
      mode = "netting";
   Print("  account     : ", mode, "  currency=", AccountInfoString(ACCOUNT_CURRENCY));
   Print("----------------------------------------------------");
   return INIT_SUCCEEDED;
}

//+------------------------------------------------------------------+
//| Expert deinitialization                                          |
//+------------------------------------------------------------------+
void OnDeinit(const int reason)
{
   ReleaseHandles();
   Comment("");
}

//+------------------------------------------------------------------+
//| Expert tick function                                             |
//+------------------------------------------------------------------+
void OnTick()
{
   if(!TerminalInfoInteger(TERMINAL_TRADE_ALLOWED) || !TerminalInfoInteger(TERMINAL_CONNECTED))
      return;

   UpdateRiskState();
   ManagePositions();
   TrackClosedLosses();

   //--- flatten when session ends (scalper: no overnight exposure)
   if(InpCloseAtSessionEnd && InpSessionMode != SESSION_OFF && !InSession())
   {
      if(CountOurPositions() > 0)
      {
         Print("Session ended - closing all positions.");
         CloseAllOur();
      }
   }

   if(g_halted)
   {
      ShowDashboard();
      return;
   }

   //--- new bar gate: evaluate entries once per closed signal bar
   datetime barTime = iTime(g_symbol, InpSignalTF, 0);
   if(barTime == 0)
      return;
   bool newBar = (barTime != g_lastBarTime);
   g_lastBarTime = barTime;
   if(!newBar)
   {
      ShowDashboard();
      return;
   }

   if(!IndicatorsReady())
   {
      g_lastSignal = "warming up";
      ShowDashboard();
      return;
   }

   CSignal sig = EvaluateSignal();
   g_lastSignal = sig.why + " score=" + IntegerToString(sig.score);
   if(!sig.valid)
   {
      ShowDashboard();
      return;
   }

   if(!GuardsOK(sig.dir))
   {
      ShowDashboard();
      return;
   }

   OpenTrade(sig.dir, sig.slDist);
   ShowDashboard();
}

//+------------------------------------------------------------------+
//| Custom optimization criterion                                    |
//| Rewards profit per unit of drawdown, kills low-sample overfits.   |
//+------------------------------------------------------------------+
double OnTester()
{
   double trades = TesterStatistics(STAT_TRADES);
   if(trades < (double)InpOptMinTrades)
      return -1000000.0;

   double dd = TesterStatistics(STAT_EQUITY_DDREL_PERCENT);
   if(dd < 1.0)
      dd = 1.0;
   double pf = TesterStatistics(STAT_PROFIT_FACTOR);
   if(pf > 10.0)
      pf = 10.0;
   if(pf <= 0.0)
      return -1000000.0;

   double profit = TesterStatistics(STAT_PROFIT);
   double recovery = TesterStatistics(STAT_RECOVERY_FACTOR);
   return (profit / dd) * pf + recovery * 100.0;
}
//+------------------------------------------------------------------+
