#!/usr/bin/env python3
"""
Static sanity checker for MQL5 source files.

MetaEditor/MetaTrader runs on Windows, so an MQL5 compiler is usually not
available in a CI/Linux sandbox. This script is NOT a compiler -- it is a
pre-compile lint that catches the failure modes that actually break a build
or silently change behaviour:

  1. unbalanced (), {}, []
  2. MQL4-only API leaking into MQL5 (OrderSend, MarketInfo, Digits, Point ...)
  3. functions used before they are declared (MQL5 has no implicit forward
     declaration, unlike MQL4)
  4. input/global typos (identifier used but never declared)
  5. an input variable called like a function  (e.g. InpMaxLot())
  6. StringFormat/PrintFormat with %s (not portable in MQL5 StringFormat)
  7. enum constants that are not known MQL5 constants
  8. use of `double == double` comparisons (precision trap)

Usage:  python3 check_mql5.py <file.mq5>
Exit code 0 = clean (warnings allowed), 1 = errors found.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

MQL4_ONLY = {
    "OrderSend", "OrderClose", "OrderModify", "OrderDelete", "OrderSelect",
    "OrdersTotal", "OrderClosePrice", "OrderOpenPrice", "OrderStopLoss",
    "OrderTakeProfit", "OrderLots", "OrderType", "OrderMagicNumber",
    "MarketInfo", "RefreshRates", "IsTradeAllowed", "IsTesting",
    "iHigh", "iLow", "iOpen", "iClose", "iVolume", "iTime",  # iTime exists in MQL5
    "Symbol", "Period", "Digits", "Point", "Bid", "Ask", "Bars",
    "ObjectCreate", "SetIndexBuffer", "IndicatorBuffers",
    "WindowRedraw", "PlaySound", "SendMail", "iBars", "iBarShift",
}
# iTime / ObjectCreate do exist in MQL5 -> remove from the hard list
MQL4_ONLY -= {"iTime", "ObjectCreate", "iBars", "iBarShift", "PlaySound",
              "SendMail", "OrderSend", "OrderSendAsync", "RefreshRates"}

EVENT_HANDLERS = {
    "OnInit", "OnDeinit", "OnTick", "OnTimer", "OnTrade", "OnTradeTransaction",
    "OnBookEvent", "OnChartEvent", "OnTester", "OnTesterInit", "OnTesterPass",
    "OnTesterDeinit", "OnStart", "OnCalculate", "OnBookEvent",
}

# Curated set of MQL5 constants/enums used by typical EAs. Unknown enum-looking
# identifiers (ALL_CAPS) are reported as warnings, not hard errors.
KNOWN_CONSTANTS = {
    # timeframe
    "PERIOD_CURRENT", "PERIOD_M1", "PERIOD_M5", "PERIOD_M15", "PERIOD_M30",
    "PERIOD_H1", "PERIOD_H4", "PERIOD_D1", "PERIOD_W1", "PERIOD_MN1",
    # enum type names
    "ENUM_TIMEFRAMES", "ENUM_MA_METHOD", "ENUM_APPLIED_PRICE",
    "ENUM_ORDER_TYPE_FILLING", "ENUM_ORDER_TYPE_TIME", "ENUM_ORDER_TYPE",
    "ENUM_CALENDAR_EVENT_IMPORTANCE", "ENUM_SYMBOL_INFO_INTEGER",
    "ENUM_SYMBOL_INFO_DOUBLE", "ENUM_ACCOUNT_INFO_INTEGER",
    "ENUM_ACCOUNT_INFO_DOUBLE", "ENUM_POSITION_PROPERTY_INTEGER",
    "ENUM_POSITION_PROPERTY_DOUBLE", "ENUM_POSITION_PROPERTY_STRING",
    "ENUM_DEAL_PROPERTY_INTEGER", "ENUM_DEAL_PROPERTY_DOUBLE",
    "ENUM_DEAL_PROPERTY_STRING", "ENUM_TRADE_REQUEST_ACTIONS",
    "ENUM_TRADE_RETCODE", "ENUM_STATISTICS", "ENUM_DAY_OF_WEEK",
    # MA
    "MODE_SMA", "MODE_EMA", "MODE_SMMA", "MODE_LWMA", "PRICE_CLOSE",
    "PRICE_OPEN", "PRICE_HIGH", "PRICE_LOW", "PRICE_MEDIAN", "PRICE_TYPICAL",
    "PRICE_WEIGHTED",
    # symbol info integer
    "SYMBOL_SELECT", "SYMBOL_VISIBLE", "SYMBOL_EXIST", "SYMBOL_CUSTOM",
    "SYMBOL_DIGITS", "SYMBOL_SPREAD", "SYMBOL_SPREAD_FLOAT",
    "SYMBOL_TRADE_STOPS_LEVEL", "SYMBOL_TRADE_FREEZE_LEVEL",
    "SYMBOL_TRADE_MODE", "SYMBOL_FILLING_MODE", "SYMBOL_TRADE_EXEMODE",
    "SYMBOL_VOLUME_MIN", "SYMBOL_VOLUME_MAX", "SYMBOL_VOLUME_STEP",
    "SYMBOL_SESSION_DEALS", "SYMBOL_BACKGROUND_COLOR",
    # symbol info double
    "SYMBOL_BID", "SYMBOL_ASK", "SYMBOL_POINT", "SYMBOL_TRADE_TICK_VALUE",
    "SYMBOL_TRADE_TICK_SIZE", "SYMBOL_TRADE_CONTRACT_SIZE",
    "SYMBOL_VOLUME_LIMIT", "SYMBOL_SWAP_LONG", "SYMBOL_SWAP_SHORT",
    "SYMBOL_MARGIN_INITIAL", "SYMBOL_MARGIN_MAINTENANCE",
    # filling / time / order types
    "ORDER_FILLING_FOK", "ORDER_FILLING_IOC", "ORDER_FILLING_RETURN",
    "ORDER_FILLING_BOC", "SYMBOL_FILLING_FOK", "SYMBOL_FILLING_IOC",
    "ORDER_TIME_GTC", "ORDER_TIME_DAY", "ORDER_TIME_SPECIFIED",
    "ORDER_TYPE_BUY", "ORDER_TYPE_SELL", "ORDER_TYPE_BUY_LIMIT",
    "ORDER_TYPE_SELL_LIMIT", "ORDER_TYPE_BUY_STOP", "ORDER_TYPE_SELL_STOP",
    # trade actions / retcodes
    "TRADE_ACTION_DEAL", "TRADE_ACTION_PENDING", "TRADE_ACTION_SLTP",
    "TRADE_ACTION_MODIFY", "TRADE_ACTION_REMOVE", "TRADE_ACTION_CLOSE_BY",
    "TRADE_RETCODE_DONE", "TRADE_RETCODE_PLACED", "TRADE_RETCODE_DONE_PARTIAL",
    "TRADE_RETCODE_REQUOTE", "TRADE_RETCODE_PRICE_OFF",
    "TRADE_RETCODE_INVALID_STOPS", "TRADE_RETCODE_NO_MONEY",
    "TRADE_RETCODE_MARKET_CLOSED", "TRADE_RETCODE_CONNECTION",
    # position/order/deal properties
    "POSITION_TYPE", "POSITION_MAGIC", "POSITION_TICKET", "POSITION_TIME",
    "POSITION_SYMBOL", "POSITION_VOLUME", "POSITION_PRICE_OPEN",
    "POSITION_SL", "POSITION_TP", "POSITION_PROFIT", "POSITION_COMMENT",
    "POSITION_IDENTIFIER", "POSITION_TYPE_BUY", "POSITION_TYPE_SELL",
    "DEAL_MAGIC", "DEAL_SYMBOL", "DEAL_TIME", "DEAL_PROFIT", "DEAL_ENTRY",
    "DEAL_ENTRY_IN", "DEAL_ENTRY_OUT", "DEAL_ENTRY_INOUT", "DEAL_POSITION_ID",
    "DEAL_TYPE", "DEAL_VOLUME",
    # account
    "ACCOUNT_BALANCE", "ACCOUNT_EQUITY", "ACCOUNT_MARGIN_FREE",
    "ACCOUNT_MARGIN", "ACCOUNT_MARGIN_MODE", "ACCOUNT_CURRENCY",
    "ACCOUNT_LEVERAGE", "ACCOUNT_MARGIN_MODE_RETAIL_HEDGING",
    "ACCOUNT_MARGIN_MODE_RETAIL_NETTING", "ACCOUNT_MARGIN_MODE_EXCHANGE",
    # terminal
    "TERMINAL_TRADE_ALLOWED", "TERMINAL_CONNECTED",
    # tester statistics
    "STAT_PROFIT", "STAT_PROFIT_FACTOR", "STAT_RECOVERY_FACTOR",
    "STAT_EXPECTED_PAYOFF", "STAT_EQUITY_DDREL_PERCENT", "STAT_TRADES",
    "STAT_SHARPE_RATIO", "STAT_DEALS",
    # calendar
    "CALENDAR_IMPORTANCE_NONE", "CALENDAR_IMPORTANCE_LOW",
    "CALENDAR_IMPORTANCE_MEDIUM", "CALENDAR_IMPORTANCE_HIGH",
    # init results
    "INIT_SUCCEEDED", "INIT_FAILED", "INIT_PARAMETERS_INCORRECT",
    "INVALID_HANDLE",
    # structs/other
    "NULL", "EMPTY_VALUE", "WRONG_VALUE",
}

BUILTIN_FUNCS = {
    # a pragmatic subset; unknown calls are warnings only
    "Print", "PrintFormat", "Comment", "Alert", "ArrayResize", "ArraySize",
    "ArraySetAsSeries", "ArrayGetAsSeries", "ArrayInitialize", "ArrayCopy",
    "ArrayMaximum", "ArrayMinimum", "ArrayFill", "ArrayFree", "MathAbs",
    "MathMax", "MathMin", "MathFloor", "MathCeil", "MathRound", "MathPow",
    "MathSqrt", "MathMod", "NormalizeDouble", "DoubleToString",
    "IntegerToString", "StringToDouble", "StringToInteger", "StringFormat",
    "StringLen", "StringFind", "StringSubstr", "StringGetChar",
    "StringSetChar", "ShortToString", "StringConcatenate", "StringReplace",
    "StringSplit", "StringTrimLeft", "StringTrimRight", "SymbolInfoDouble",
    "SymbolInfoInteger", "SymbolInfoString", "SymbolInfoTick", "SymbolSelect",
    "SymbolName", "SymbolsTotal", "AccountInfoDouble", "AccountInfoInteger",
    "AccountInfoString", "TerminalInfoInteger", "TerminalInfoDouble",
    "PositionSelect", "PositionSelectByTicket", "PositionGetTicket",
    "PositionGetDouble", "PositionGetInteger", "PositionGetString",
    "PositionsTotal", "OrderCalcMargin", "OrderSend", "OrderSendAsync",
    "HistorySelect", "HistorySelectByPosition", "HistoryDealsTotal",
    "HistoryDealGetTicket", "HistoryDealGetDouble", "HistoryDealGetInteger",
    "HistoryDealGetString", "HistoryOrdersTotal", "CopyBuffer", "CopyRates",
    "CopyTime", "CopyOpen", "CopyHigh", "CopyLow", "CopyClose", "iMA",
    "iRSI", "iATR", "iADX", "iMACD", "iBands", "iStochastic", "iCCI",
    "iMomentum", "iTime", "iOpen", "iHigh", "iLow", "iClose", "iBarShift",
    "iBars", "BarsCalculated", "IndicatorRelease", "IndicatorCreate",
    "TimeCurrent", "TimeGMT", "TimeLocal", "TimeToStruct", "StructToTime",
    "PeriodSeconds", "GetLastError", "ResetLastError", "ZeroMemory",
    "TesterStatistics", "GlobalVariableSet", "GlobalVariableGet",
    "GlobalVariableCheck", "GlobalVariableDel", "ObjectCreate",
    "ObjectsDeleteAll", "ChartRedraw", "Sleep", "SendNotification",
    "CalendarValueHistory", "CalendarEventById", "MqlInfoInteger",
    "MathArccos", "MathArcsin", "MathArctan", "MathCos", "MathSin",
    "MathExp", "MathLog", "MathLog10", "MathExpm1", "IsStopped",
}

TYPE_KEYWORDS = {
    "bool", "int", "uint", "long", "ulong", "short", "ushort", "char",
    "uchar", "double", "float", "string", "datetime", "color", "void",
    "struct", "class", "enum", "const", "input", "static", "return", "if",
    "else", "for", "while", "do", "break", "continue", "switch", "case",
    "default", "true", "false", "new", "delete", "this", "template",
    "typedef", "union", "public", "private", "protected", "virtual",
    "explicit", "operator", "sizeof", "using", "namespace", "try", "catch",
}


def strip_comments_and_strings(src: str) -> str:
    """Replace comments and string literals with spaces (keeps offsets).

    String literals are scanned BEFORE comments so that a '//' inside a
    string (e.g. "https://arena.ai") cannot start a fake comment.
    """
    out = list(src)
    i, n = 0, len(src)
    while i < n:
        c = src[i]
        if c == '"':
            out[i] = " "
            i += 1
            while i < n:
                if src[i] == "\\" and i + 1 < n:
                    out[i] = " "
                    out[i + 1] = " "
                    i += 2
                    continue
                if src[i] == '"':
                    out[i] = " "
                    i += 1
                    break
                if src[i] != "\n":
                    out[i] = " "
                i += 1
        elif c == "'":
            out[i] = " "
            i += 1
            while i < n and src[i] != "'":
                if src[i] != "\n":
                    out[i] = " "
                i += 1
            if i < n:
                out[i] = " "
                i += 1
        elif c == "/" and i + 1 < n and src[i + 1] == "/":
            while i < n and src[i] != "\n":
                out[i] = " "
                i += 1
        elif c == "/" and i + 1 < n and src[i + 1] == "*":
            while i < n and not (src[i] == "*" and i + 1 < n and src[i + 1] == "/"):
                if src[i] != "\n":
                    out[i] = " "
                i += 1
            for _ in range(2):
                if i < n:
                    out[i] = " "
                    i += 1
        else:
            i += 1
    return "".join(out)


def find_matching(src: str, open_idx: int) -> int:
    pairs = {"(": ")", "{": "}", "[": "]"}
    o = src[open_idx]
    c = pairs[o]
    depth = 0
    for i in range(open_idx, len(src)):
        if src[i] == o:
            depth += 1
        elif src[i] == c:
            depth -= 1
            if depth == 0:
                return i
    return -1


def main() -> int:
    if len(sys.argv) < 2:
        print("usage: check_mql5.py <file.mq5>")
        return 2
    path = Path(sys.argv[1])
    raw = path.read_text(encoding="utf-8", errors="replace")
    code = strip_comments_and_strings(raw)

    errors: list[str] = []
    warnings: list[str] = []

    # 1) balance check ----------------------------------------------------
    stack: list[tuple[str, int]] = []
    for idx, ch in enumerate(code):
        if ch in "({[":
            stack.append((ch, idx))
        elif ch in ")}]":
            if not stack:
                errors.append(f"unmatched closing '{ch}' at offset {idx}")
                continue
            o, start = stack.pop()
            if "({[".index(o) != ")}]".index(ch):
                errors.append(f"mismatched '{o}' (offset {start}) closed by '{ch}' (offset {idx})")
    for o, start in stack:
        line = raw[:start].count("\n") + 1
        errors.append(f"unclosed '{o}' opened at line {line}")

    # 2) MQL4-only API ----------------------------------------------------
    for name in sorted(MQL4_ONLY):
        for m in re.finditer(r"\b" + name + r"\s*\(", code):
            line = raw[: m.start()].count("\n") + 1
            errors.append(f"line {line}: MQL4-only call '{name}(' -> not valid in MQL5")

    # 5) input called like a function ------------------------------------
    inputs = re.findall(r"^[ \t]*input[ \t]+[A-Za-z_]\w*[ \t]+([A-Za-z_]\w*)[ \t]*[=;]", code, re.M)
    inputs = [i for i in inputs if i != "group"]
    for name in set(inputs):
        for m in re.finditer(r"\b" + name + r"\s*\(\s*\)", code):
            line = raw[: m.start()].count("\n") + 1
            errors.append(f"line {line}: input '{name}' is called like a function (drop the parentheses)")

    # 3) function declaration order --------------------------------------
    decl_re = re.compile(
        r"^\s*(?:(?:const|static|inline|virtual|template\s*<[^>]*>)\s+)*"
        r"(?:[A-Za-z_]\w*)\s+([A-Za-z_]\w*)\s*\(([^;{]*)\)\s*(?:const\s*)?\{",
        re.M,
    )
    funcs: dict[str, int] = {}
    func_spans: list[tuple[str, int, int]] = []
    for m in decl_re.finditer(code):
        name = m.group(1)
        if name in TYPE_KEYWORDS:
            continue
        line = raw[: m.start()].count("\n") + 1
        if name not in funcs:
            funcs[name] = line
        open_brace = code.index("{", m.end() - 1)
        close_brace = find_matching(code, open_brace)
        if close_brace > 0:
            func_spans.append((name, open_brace, close_brace))

    def owner_of(offset: int) -> str | None:
        for name, a, b in func_spans:
            if a <= offset <= b:
                return name
        return None

    for m in re.finditer(r"\b([A-Za-z_]\w*)\s*\(", code):
        name = m.group(1)
        if name not in funcs or name in TYPE_KEYWORDS or name in EVENT_HANDLERS:
            continue
        call_line = raw[: m.start()].count("\n") + 1
        decl_line = funcs[name]
        if call_line > decl_line or owner_of(m.start()) == name:
            continue
        errors.append(
            f"line {call_line}: '{name}()' is used before it is declared "
            f"(declared at line {decl_line}); MQL5 requires declaration before use"
        )

    # 4) undeclared Inp*/g_* identifiers ---------------------------------
    declared = set(inputs)
    declared |= set(re.findall(r"^\s*(?:static\s+)?(?:const\s+)?[A-Za-z_]\w*\s+(g_\w+)\s*[=;\[]", code, re.M))
    declared |= set(re.findall(r"^\s*(?:static\s+)?[A-Za-z_]\w*\s+(g_\w+)\s+[\w\[]", code, re.M))
    for m in re.finditer(r"\b(g_[A-Za-z_]\w*|Inp[A-Z]\w*)\b", code):
        name = m.group(1)
        if name not in declared:
            line = raw[: m.start()].count("\n") + 1
            errors.append(f"line {line}: identifier '{name}' is used but never declared")

    # 6) StringFormat with %s --------------------------------------------
    for m in re.finditer(r"(StringFormat|PrintFormat)\s*\(", code):
        seg = code[m.end() : m.end() + 200]
        if re.search(r"%[-0-9.]*[sl]", seg.split(")")[0] if ")" in seg else seg):
            line = raw[: m.start()].count("\n") + 1
            warnings.append(f"line {line}: StringFormat with %s/%S is not portable in MQL5 - use concatenation")

    # 7) unknown ALL_CAPS constants --------------------------------------
    local_enums = set(re.findall(r"\benum\s+(\w+)", raw))
    for m in re.finditer(r"\benum\s+\w+\s*\{([^}]*)\}", raw):
        for mem in re.findall(r"\b([A-Za-z_]\w*)\b", m.group(1)):
            local_enums.add(mem)
    used_consts = set(re.findall(r"\b([A-Z][A-Z0-9_]{3,})\b", code)) - local_enums
    for name in sorted(used_consts):
        if name in KNOWN_CONSTANTS or name in MQL4_ONLY:
            continue
        # enum member usage like ENUM_X.VALUE or struct.const
        warnings.append(f"constant '{name}' is not in the known MQL5 list - verify spelling")

    # 9) ternary operator returning string literals -----------------------
    for m in re.finditer(r"\?\s*\"[^\"]*\"\s*:\s*\"[^\"]*\"", code):
        line = raw[: m.start()].count("\n") + 1
        errors.append(
            f"line {line}: ternary operator with string operands - MQL5 restricts ?: "
            f"for complex types; use if/else"
        )

    # 8) float equality ---------------------------------------------------
    for m in re.finditer(r"\b([A-Za-z_]\w*)\s*==\s*0\.0\b", code):
        warnings.append(
            f"line {raw[: m.start()].count(chr(10)) + 1}: exact compare of '{m.group(1)}' to 0.0"
        )

    # report --------------------------------------------------------------
    print(f"=== check_mql5: {path.name} ===")
    print(f"lines            : {len(raw.splitlines())}")
    print(f"inputs detected  : {len(inputs)}")
    print(f"functions        : {len(funcs)}")
    print()
    if warnings:
        print(f"--- {len(warnings)} warning(s) ---")
        for w in warnings:
            print("  WARN ", w)
        print()
    if errors:
        print(f"--- {len(errors)} error(s) ---")
        for e in errors:
            print("  ERROR", e)
        print()
        print("RESULT: FAIL")
        return 1
    print("RESULT: PASS (no structural errors)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
