import pandas as pd
import numpy as np

class CandlestickPatternDetector:
    """
    Algorithmic pattern recognition for 30M confirmation patterns:
    - Bullish: Bull Flag Breakout, Bullish Engulfing, Hammer Pin Bar, Morning Star, Three White Soldiers
    - Bearish: Bear Flag Breakdown, Bearish Engulfing, Shooting Star Pin Bar, Evening Star, Three Black Crows
    """
    
    @staticmethod
    def is_hammer(open_p, high_p, low_p, close_p, atr=None):
        body = abs(close_p - open_p)
        total_range = high_p - low_p
        if total_range == 0:
            return False
        lower_wick = min(open_p, close_p) - low_p
        upper_wick = high_p - max(open_p, close_p)
        
        # Lower wick at least 2x body, upper wick small (<= 25% of total range)
        return (lower_wick >= 1.8 * body) and (upper_wick <= 0.25 * total_range) and (total_range > 0.3 * (atr if atr else total_range))

    @staticmethod
    def is_shooting_star(open_p, high_p, low_p, close_p, atr=None):
        body = abs(close_p - open_p)
        total_range = high_p - low_p
        if total_range == 0:
            return False
        upper_wick = high_p - max(open_p, close_p)
        lower_wick = min(open_p, close_p) - low_p
        
        # Upper wick at least 2x body, lower wick small (<= 25% of total range)
        return (upper_wick >= 1.8 * body) and (lower_wick <= 0.25 * total_range) and (total_range > 0.3 * (atr if atr else total_range))

    @staticmethod
    def is_bullish_engulfing(prev_open, prev_close, curr_open, curr_close):
        # Prev is bearish, Curr is bullish, Curr body engulfs Prev body
        prev_is_red = prev_close < prev_open
        curr_is_green = curr_close > curr_open
        if not (prev_is_red and curr_is_green):
            return False
        return curr_close > prev_open and curr_open < prev_close

    @staticmethod
    def is_bearish_engulfing(prev_open, prev_close, curr_open, curr_close):
        # Prev is bullish, Curr is bearish, Curr body engulfs Prev body
        prev_is_green = prev_close > prev_open
        curr_is_red = curr_close < curr_open
        if not (prev_is_green and curr_is_red):
            return False
        return curr_close < prev_open and curr_open > prev_close

    @staticmethod
    def is_strong_bull_breakout(open_p, high_p, low_p, close_p, level, atr=None):
        # Closes cleanly above level with strong body
        body = close_p - open_p
        total_range = high_p - low_p
        if total_range == 0 or body <= 0:
            return False
        return close_p > level and (body / total_range >= 0.55)

    @staticmethod
    def is_strong_bear_breakdown(open_p, high_p, low_p, close_p, level, atr=None):
        # Closes cleanly below level with strong body
        body = open_p - close_p
        total_range = high_p - low_p
        if total_range == 0 or body <= 0:
            return False
        return close_p < level and (body / total_range >= 0.55)

    @classmethod
    def detect_bullish_patterns(cls, df_30m, idx, breakout_level, atr=None):
        """Checks for bullish entry trigger at idx."""
        if idx < 2:
            return None
        c = df_30m.iloc[idx]
        p = df_30m.iloc[idx - 1]
        p2 = df_30m.iloc[idx - 2]
        
        # 1. Bull Flag / Level Breakout
        if cls.is_strong_bull_breakout(c['Open'], c['High'], c['Low'], c['Close'], breakout_level, atr):
            return "Bull Flag / Level Breakout Candle"
        # 2. Bullish Engulfing off zone
        if cls.is_bullish_engulfing(p['Open'], p['Close'], c['Open'], c['Close']) and c['Close'] >= breakout_level:
            return "Bullish Engulfing Retest"
        # 3. Hammer off zone
        if cls.is_hammer(c['Open'], c['High'], c['Low'], c['Close'], atr) and c['Close'] >= breakout_level:
            return "Hammer Support Rejection"
        # 4. Three White Soldiers (3 consecutive green candles closing above level)
        if (p2['Close'] > p2['Open'] and p['Close'] > p['Open'] and c['Close'] > c['Open'] and
            c['Close'] > p['Close'] > p2['Close'] and c['Close'] > breakout_level):
            return "Three White Soldiers Expansion"
        return None

    @classmethod
    def detect_bearish_patterns(cls, df_30m, idx, breakdown_level, atr=None):
        """Checks for bearish entry trigger at idx."""
        if idx < 2:
            return None
        c = df_30m.iloc[idx]
        p = df_30m.iloc[idx - 1]
        p2 = df_30m.iloc[idx - 2]
        
        # 1. Bear Flag / Level Breakdown
        if cls.is_strong_bear_breakdown(c['Open'], c['High'], c['Low'], c['Close'], breakdown_level, atr):
            return "Bear Flag / Level Breakdown Candle"
        # 2. Bearish Engulfing off zone
        if cls.is_bearish_engulfing(p['Open'], p['Close'], c['Open'], c['Close']) and c['Close'] <= breakdown_level:
            return "Bearish Engulfing Retest"
        # 3. Shooting Star off zone
        if cls.is_shooting_star(c['Open'], c['High'], c['Low'], c['Close'], atr) and c['Close'] <= breakdown_level:
            return "Shooting Star Resistance Rejection"
        # 4. Three Black Crows (3 consecutive red candles closing below level)
        if (p2['Close'] < p2['Open'] and p['Close'] < p['Open'] and c['Close'] < c['Open'] and
            c['Close'] < p['Close'] < p2['Close'] and c['Close'] < breakdown_level):
            return "Three Black Crows Contraction"
        return None
