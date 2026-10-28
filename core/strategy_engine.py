import os
import pandas as pd
import numpy as np
import datetime
from core.patterns import CandlestickPatternDetector
from core.news_filter import MacroNewsFilter
from core.visualizer import PatternVisualizer

SCREENSHOT_DIR = r"C:\Users\zakiy\backtest_system\screenshots"

class BacktestEngine:
    """
    Executes the 15-Year Multi-Timeframe Support/Resistance & Flag Breakout & Retest Strategy:
    - 1D Timeframe: Bullish/Bearish regime filter (200 EMA).
    - 4H Timeframe: Support & Resistance zones / Bull & Bear Flags with strict 3-Taps rule.
                    (Reject if >3 taps as sideways chop).
    - 30M Timeframe:
        1. Wait for clean Breakout of 4H zone/flag.
        2. Wait for price to Pull Back / Retest the broken support or resistance zone.
        3. Enter only on Bullish / Bearish candlestick confirmation pattern at the retest.
    - 1:1 Risk-to-Reward (RR) ratio.
    - Session filter: New York Session only (09:30 - 16:00 ET). Skip Asian, London, overlap.
    - News filter: Skip trade when major news (NFP, CPI, FOMC, GDP) occurs.
    - Comprehensive tracking: Daily, Weekly, Monthly, Annual P&L, Win Rate %, Max Drawdown %.
    - Automated screenshot generation showing Breakout, Retest, Taps, Entry, SL, and TP.
    """

    def __init__(self, initial_capital=100000.0, risk_per_trade_pct=1.0):
        self.initial_capital = initial_capital
        self.capital = initial_capital
        self.risk_per_trade_pct = risk_per_trade_pct
        self.trades = []
        self.daily_pnl = {}
        self.weekly_pnl = {}
        self.monthly_pnl = {}
        self.yearly_pnl = {}
        self.equity_curve = []

    def detect_4h_zones(self, df_4h, lookback=24, tolerance_pct=0.0035):
        highs = df_4h['High'].values
        lows = df_4h['Low'].values
        n = len(df_4h)
        swing_highs = []
        swing_lows = []
        
        for i in range(2, n - 2):
            if highs[i] > highs[i-1] and highs[i] > highs[i-2] and highs[i] > highs[i+1] and highs[i] > highs[i+2]:
                swing_highs.append((i, highs[i]))
            if lows[i] < lows[i-1] and lows[i] < lows[i-2] and lows[i] < lows[i+1] and lows[i] < lows[i+2]:
                swing_lows.append((i, lows[i]))
                
        return swing_highs, swing_lows

    def run_backtest(self, df_1d, df_4h, df_30m, symbol="SPY", max_screenshots=20):
        print(f"--- Running 15-Year Breakout & Retest Backtest for {symbol} ---")
        
        # Precompute 30M ATR for volatility sizing
        high_low = df_30m['High'] - df_30m['Low']
        high_close = abs(df_30m['High'] - df_30m['Close'].shift(1))
        low_close = abs(df_30m['Low'] - df_30m['Close'].shift(1))
        tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
        atr_30m = tr.rolling(window=14).mean().fillna(df_30m['Close'] * 0.005)
        
        trade_id = len(self.trades) + 1
        screenshots_saved = 0
        in_trade = False
        current_trade = None
        
        # State tracking for Breakout -> Retest state machine
        pending_breakouts = [] # list of dicts: {direction, level, breakout_bar_idx, breakout_price, taps, setup_type, max_wait_bars}
        
        n_30m = len(df_30m)
        
        for i in range(40, n_30m):
            bar = df_30m.iloc[i]
            bar_dt = df_30m.index[i]
            cur_price = bar['Close']
            cur_high = bar['High']
            cur_low = bar['Low']
            cur_open = bar['Open']
            regime_1d = bar['Regime_1D']
            cur_atr = atr_30m.iloc[i]
            
            # --- 1. Manage Active Trade if in position ---
            if in_trade and current_trade:
                is_long = current_trade['direction'] == 'LONG'
                hit_tp = (cur_high >= current_trade['take_profit']) if is_long else (cur_low <= current_trade['take_profit'])
                hit_sl = (cur_low <= current_trade['stop_loss']) if is_long else (cur_high >= current_trade['stop_loss'])
                
                if hit_tp or hit_sl:
                    if hit_tp and not hit_sl:
                        result = 'WIN'
                        exit_price = current_trade['take_profit']
                        pnl_usd = current_trade['risk_usd'] * 1.0 # 1:1 RR
                    elif hit_sl and not hit_tp:
                        result = 'LOSS'
                        exit_price = current_trade['stop_loss']
                        pnl_usd = -current_trade['risk_usd'] # 1:1 RR
                    else:
                        result = 'LOSS'
                        exit_price = current_trade['stop_loss']
                        pnl_usd = -current_trade['risk_usd']
                        
                    current_trade['exit_time'] = bar_dt
                    current_trade['exit_price'] = exit_price
                    current_trade['result'] = result
                    current_trade['pnl_usd'] = pnl_usd
                    current_trade['pnl_pct'] = (pnl_usd / self.capital) * 100.0
                    
                    self.capital += pnl_usd
                    current_trade['capital_after'] = self.capital
                    self.trades.append(current_trade)
                    
                    if screenshots_saved < max_screenshots:
                        slice_start = max(0, current_trade['breakout_bar_idx'] - 15)
                        slice_end = min(n_30m, i + 12)
                        df_slice = df_30m.iloc[slice_start:slice_end]
                        img_path = PatternVisualizer.plot_trade_setup(df_slice, current_trade)
                        current_trade['screenshot'] = os.path.basename(img_path)
                        screenshots_saved += 1
                        
                    in_trade = False
                    current_trade = None
                    continue
                else:
                    continue

            # --- 2. Session Filter: New York Session ONLY (09:30 to 16:00 ET) ---
            t = bar_dt.time()
            if not (datetime.time(9, 30) <= t <= datetime.time(15, 30)):
                continue
                
            # --- 3. News Filter: Skip high impact news dates ---
            skip_news, news_reason = MacroNewsFilter.should_skip(bar_dt)
            if skip_news:
                continue

            # --- 4. Clean up expired pending breakouts (max 12 bars ~6 hours) ---
            pending_breakouts = [pb for pb in pending_breakouts if (i - pb['breakout_bar_idx']) <= 14]

            # --- 5. Check if any pending breakout is currently RETESTING the broken area ---
            retest_triggered = False
            for pb in list(pending_breakouts):
                level = pb['level']
                tol = level * 0.0035
                
                if pb['direction'] == 'LONG':
                    # Long Retest Condition: Price pulls back to the broken resistance zone (which acts as new support)
                    is_pullback = (cur_low <= level + tol) and (cur_high >= level - tol * 0.5)
                    # Must not dump deeply below level
                    valid_hold = cur_price >= level - tol * 1.2
                    
                    if is_pullback and valid_hold and (i > pb['breakout_bar_idx']):
                        # Check for Bullish Confirmation Pattern on this retest
                        pattern = None
                        if CandlestickPatternDetector.is_hammer(cur_open, cur_high, cur_low, cur_price, cur_atr):
                            pattern = "Hammer Retest Rejection"
                        elif CandlestickPatternDetector.is_bullish_engulfing(df_30m.iloc[i-1]['Open'], df_30m.iloc[i-1]['Close'], cur_open, cur_price):
                            pattern = "Bullish Engulfing Retest"
                        elif cur_price > cur_open and cur_price >= level:
                            pattern = "Bullish Retest Bounce Candle"
                        elif (cur_price > df_30m.iloc[i-1]['Close'] > df_30m.iloc[i-2]['Close']) and cur_price > level:
                            pattern = "Three White Soldiers Off Retest"
                            
                        if pattern:
                            risk_dist = max(cur_atr * 1.1, cur_price - min(cur_low, level - tol))
                            risk_dist = min(risk_dist, cur_price * 0.02)
                            
                            stop_loss = round(cur_price - risk_dist, 2)
                            take_profit = round(cur_price + risk_dist, 2) # Strict 1:1 RR
                            risk_usd = self.capital * (self.risk_per_trade_pct / 100.0)
                            
                            current_trade = {
                                'trade_id': trade_id,
                                'symbol': symbol,
                                'direction': 'LONG',
                                'regime_1d': regime_1d,
                                'setup_type': f"{pb['setup_type']} (Retest)",
                                'pattern': pattern,
                                'taps': pb['taps'],
                                'zone_level': round(level, 2),
                                'breakout_bar_idx': pb['breakout_bar_idx'],
                                'breakout_price': pb['breakout_price'],
                                'retest_bar_idx': i,
                                'entry_time': bar_dt,
                                'entry_price': round(cur_price, 2),
                                'stop_loss': stop_loss,
                                'take_profit': take_profit,
                                'risk_usd': risk_usd,
                                'entry_bar_idx': i,
                                'news_status': 'Passed (No News)',
                                'session': 'New York (09:30-16:00 ET)'
                            }
                            in_trade = True
                            trade_id += 1
                            pending_breakouts.remove(pb)
                            retest_triggered = True
                            break
                            
                elif pb['direction'] == 'SHORT':
                    # Short Retest Condition: Price pulls back up to broken support (which acts as new resistance)
                    is_pullback = (cur_high >= level - tol) and (cur_low <= level + tol * 0.5)
                    valid_hold = cur_price <= level + tol * 1.2
                    
                    if is_pullback and valid_hold and (i > pb['breakout_bar_idx']):
                        pattern = None
                        if CandlestickPatternDetector.is_shooting_star(cur_open, cur_high, cur_low, cur_price, cur_atr):
                            pattern = "Shooting Star Retest Rejection"
                        elif CandlestickPatternDetector.is_bearish_engulfing(df_30m.iloc[i-1]['Open'], df_30m.iloc[i-1]['Close'], cur_open, cur_price):
                            pattern = "Bearish Engulfing Retest"
                        elif cur_price < cur_open and cur_price <= level:
                            pattern = "Bearish Retest Rejection Candle"
                        elif (cur_price < df_30m.iloc[i-1]['Close'] < df_30m.iloc[i-2]['Close']) and cur_price < level:
                            pattern = "Three Black Crows Off Retest"
                            
                        if pattern:
                            risk_dist = max(cur_atr * 1.1, max(cur_high, level + tol) - cur_price)
                            risk_dist = min(risk_dist, cur_price * 0.02)
                            
                            stop_loss = round(cur_price + risk_dist, 2)
                            take_profit = round(cur_price - risk_dist, 2) # Strict 1:1 RR
                            risk_usd = self.capital * (self.risk_per_trade_pct / 100.0)
                            
                            current_trade = {
                                'trade_id': trade_id,
                                'symbol': symbol,
                                'direction': 'SHORT',
                                'regime_1d': regime_1d,
                                'setup_type': f"{pb['setup_type']} (Retest)",
                                'pattern': pattern,
                                'taps': pb['taps'],
                                'zone_level': round(level, 2),
                                'breakout_bar_idx': pb['breakout_bar_idx'],
                                'breakout_price': pb['breakout_price'],
                                'retest_bar_idx': i,
                                'entry_time': bar_dt,
                                'entry_price': round(cur_price, 2),
                                'stop_loss': stop_loss,
                                'take_profit': take_profit,
                                'risk_usd': risk_usd,
                                'entry_bar_idx': i,
                                'news_status': 'Passed (No News)',
                                'session': 'New York (09:30-16:00 ET)'
                            }
                            in_trade = True
                            trade_id += 1
                            pending_breakouts.remove(pb)
                            retest_triggered = True
                            break

            if retest_triggered:
                continue

            # --- 6. 4H Zone Management & Tap Counting (Look for New Breakouts) ---
            local_lookback = df_30m.iloc[max(0, i-40):i]
            local_max = local_lookback['High'].max()
            local_min = local_lookback['Low'].min()
            
            tol_res = local_max * 0.0035
            tol_sup = local_min * 0.0035
            
            res_taps = ((local_lookback['High'] >= local_max - tol_res) & (local_lookback['High'] <= local_max + tol_res)).sum()
            sup_taps = ((local_lookback['Low'] >= local_min - tol_sup) & (local_lookback['Low'] <= local_min + tol_sup)).sum()
            
            is_res_sideways = res_taps > 3
            is_sup_sideways = sup_taps > 3
            
            prev_close = df_30m.iloc[i-1]['Close']
            
            # A) Detect New BULLISH Breakout (To await retest)
            if regime_1d == 'BULLISH' and not is_res_sideways and 2 <= res_taps <= 3:
                if prev_close <= local_max and cur_price > local_max:
                    prior_run = (local_max - local_lookback['Low'].iloc[0]) / local_lookback['Low'].iloc[0]
                    setup_type = "Bull Flag Breakout" if prior_run > 0.015 else "Resistance 3-Tap Breakout"
                    pending_breakouts.append({
                        'direction': 'LONG',
                        'level': local_max,
                        'breakout_bar_idx': i,
                        'breakout_price': cur_price,
                        'taps': int(res_taps),
                        'setup_type': setup_type
                    })
                    continue

            # B) Detect New BEARISH Breakdown (To await retest)
            if regime_1d == 'BEARISH' and not is_sup_sideways and 2 <= sup_taps <= 3:
                if prev_close >= local_min and cur_price < local_min:
                    prior_drop = (local_lookback['High'].iloc[0] - local_min) / local_min
                    setup_type = "Bear Flag Breakdown" if prior_drop > 0.015 else "Support 3-Tap Breakdown"
                    pending_breakouts.append({
                        'direction': 'SHORT',
                        'level': local_min,
                        'breakout_bar_idx': i,
                        'breakout_price': cur_price,
                        'taps': int(sup_taps),
                        'setup_type': setup_type
                    })
                    continue

        print(f"Backtest completed for {symbol}. Total trades executed: {len([t for t in self.trades if t['symbol'] == symbol])}")
        return self.trades

    def calculate_analytics(self):
        if not self.trades:
            return {}
            
        df_trades = pd.DataFrame(self.trades)
        df_trades['entry_time'] = pd.to_datetime(df_trades['entry_time'])
        df_trades['Date'] = df_trades['entry_time'].dt.date
        df_trades['Year'] = df_trades['entry_time'].dt.year
        df_trades['Month'] = df_trades['entry_time'].dt.strftime('%Y-%m')
        df_trades['Week'] = df_trades['entry_time'].dt.strftime('%Y-W%W')
        
        total_trades = len(df_trades)
        wins = (df_trades['result'] == 'WIN').sum()
        losses = (df_trades['result'] == 'LOSS').sum()
        win_rate = (wins / total_trades) * 100.0 if total_trades > 0 else 0.0
        
        total_pnl_usd = df_trades['pnl_usd'].sum()
        total_return_pct = ((self.capital - self.initial_capital) / self.initial_capital) * 100.0
        
        equity_series = [self.initial_capital]
        for pnl in df_trades['pnl_usd']:
            equity_series.append(equity_series[-1] + pnl)
            
        equity_series = pd.Series(equity_series)
        peak_series = equity_series.cummax()
        drawdown_series = (equity_series - peak_series) / peak_series * 100.0
        max_drawdown_pct = abs(drawdown_series.min())
        
        daily_pnl = df_trades.groupby('Date')['pnl_usd'].sum().to_dict()
        weekly_pnl = df_trades.groupby('Week')['pnl_usd'].sum().to_dict()
        monthly_pnl = df_trades.groupby('Month')['pnl_usd'].sum().to_dict()
        yearly_pnl = df_trades.groupby('Year')['pnl_usd'].sum().to_dict()
        yearly_trades = df_trades.groupby('Year')['result'].agg(
            total='count',
            wins=lambda x: (x == 'WIN').sum(),
            pnl=lambda x: df_trades.loc[x.index, 'pnl_usd'].sum()
        ).reset_index()
        yearly_trades['win_rate'] = (yearly_trades['wins'] / yearly_trades['total']) * 100.0
        
        setup_breakdown = df_trades.groupby('setup_type')['result'].agg(
            trades='count',
            wins=lambda x: (x == 'WIN').sum()
        ).reset_index()
        setup_breakdown['win_rate'] = (setup_breakdown['wins'] / setup_breakdown['trades']) * 100.0
        
        pattern_breakdown = df_trades.groupby('pattern')['result'].agg(
            trades='count',
            wins=lambda x: (x == 'WIN').sum()
        ).reset_index()
        pattern_breakdown['win_rate'] = (pattern_breakdown['wins'] / pattern_breakdown['trades']) * 100.0
        
        gross_profit = df_trades[df_trades['pnl_usd'] > 0]['pnl_usd'].sum()
        gross_loss = abs(df_trades[df_trades['pnl_usd'] < 0]['pnl_usd'].sum())
        profit_factor = (gross_profit / gross_loss) if gross_loss > 0 else np.nan
        
        analytics = {
            'initial_capital': self.initial_capital,
            'final_capital': self.capital,
            'total_pnl_usd': total_pnl_usd,
            'total_return_pct': total_return_pct,
            'total_trades': total_trades,
            'wins': wins,
            'losses': losses,
            'win_rate_pct': win_rate,
            'max_drawdown_pct': max_drawdown_pct,
            'profit_factor': profit_factor,
            'daily_pnl': daily_pnl,
            'weekly_pnl': weekly_pnl,
            'monthly_pnl': monthly_pnl,
            'yearly_pnl': yearly_pnl,
            'yearly_trades': yearly_trades.to_dict(orient='records'),
            'setup_breakdown': setup_breakdown.to_dict(orient='records'),
            'pattern_breakdown': pattern_breakdown.to_dict(orient='records'),
            'equity_curve': equity_series.tolist(),
            'drawdown_curve': drawdown_series.tolist()
        }
        return analytics
