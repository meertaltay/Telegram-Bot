"""
Advanced Chart Generator Utils
Gelişmiş matplotlib ile kripto grafikleri
"""

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.gridspec import GridSpec
from io import BytesIO
import pandas as pd
import numpy as np
from config import *
from utils.technical_analysis import *

# Matplotlib ayarları
plt.style.use('dark_background')

def create_advanced_chart(df, symbol, analysis_data, timeframe="1d"):
    """Gelişmiş analiz grafiği oluştur"""
    try:
        fig = plt.figure(figsize=(20, 12), facecolor='#0f1419')
        fig.patch.set_alpha(0.0)
        gs = GridSpec(4, 3, height_ratios=[3, 1, 1, 1], width_ratios=[4, 1, 1])
        
        # Ana fiyat grafiği
        ax1 = fig.add_subplot(gs[0, :2])
        ax1.set_facecolor('#1a1d29')
        
        # Candlestick verisi hazırla
        create_candlestick_chart(ax1, df, symbol, timeframe)
        
        # Teknik indikatörleri ekle
        add_technical_indicators(ax1, df, analysis_data)
        
        # Support/Resistance seviyeleri
        add_support_resistance_levels(ax1, df, analysis_data)
        
        # Fibonacci seviyeleri
        if analysis_data.get('fib_levels'):
            add_fibonacci_levels(ax1, analysis_data['fib_levels'])
        
        ax1.set_title(f'{symbol} - Gelişmiş Analiz ({timeframe.upper()})', 
                      fontsize=18, color='white', fontweight='bold', pad=20)
        ax1.legend(loc='upper left', fontsize=10, framealpha=0.9)
        ax1.grid(True, alpha=0.2, color='gray')
        ax1.set_ylabel('Fiyat ($)', color='white', fontsize=12)
        
        # RSI grafiği
        ax2 = fig.add_subplot(gs[1, :2])
        create_rsi_chart(ax2, df, analysis_data)
        
        # MACD grafiği
        ax3 = fig.add_subplot(gs[2, :2])
        create_macd_chart(ax3, df, analysis_data)
        
        # Volume grafiği
        ax4 = fig.add_subplot(gs[3, :2])
        create_volume_chart(ax4, df)
        
        # Bilgi paneli (sağ taraf)
        ax_info = fig.add_subplot(gs[:2, 2])
        create_info_panel(ax_info, analysis_data)
        
        # Sinyal paneli
        ax_signals = fig.add_subplot(gs[2:, 2])
        create_signals_panel(ax_signals, analysis_data)
        
        plt.tight_layout()
        
        # Grafik kaydet
        img = BytesIO()
        plt.savefig(img, format='png', dpi=200, bbox_inches='tight', 
                    facecolor='#0f1419', edgecolor='none')
        img.seek(0)
        plt.close()
        
        return img
    except Exception as e:
        print(f"Gelişmiş grafik oluşturma hatası: {e}")
        plt.close()
        return None

def create_candlestick_chart(ax, df, symbol, timeframe):
    """Candlestick grafiği oluştur"""
    try:
        # Basit çizgi grafiği (candlestick için ek kütüphane gerekli)
        ax.plot(df.index, df['close'], color='#00e676', linewidth=2.5, label='Fiyat', alpha=0.9)
        
        # Yüksek/düşük gölgelendirme
        ax.fill_between(df.index, df['high'], df['low'], alpha=0.1, color='gray')
        
        # Son fiyat vurgulama
        current_price = df['close'].iloc[-1]
        ax.axhline(y=current_price, color='#ffffff', linestyle='-', alpha=0.8, linewidth=2.5)
        
        # Fiyat etiketi
        ax.text(0.02, 0.95, f'${current_price:,.4f}', transform=ax.transAxes,
                fontsize=16, color='white', fontweight='bold',
                bbox=dict(boxstyle="round,pad=0.3", facecolor='#2d3748', alpha=0.8))
        
        return ax
    except Exception as e:
        print(f"Candlestick grafik hatası: {e}")
        return ax

def add_technical_indicators(ax, df, analysis_data):
    """Teknik indikatörleri grafiğe ekle"""
    try:
        # Hareketli ortalamalar
        sma20 = df['close'].rolling(20).mean()
        sma50 = df['close'].rolling(50).mean()
        ema12 = df['close'].ewm(span=12).mean()
        
        ax.plot(df.index, sma20, color='#ffeb3b', linestyle='--', linewidth=2, 
                label='SMA20', alpha=0.8)
        ax.plot(df.index, sma50, color='#f44336', linestyle='--', linewidth=2, 
                label='SMA50', alpha=0.8)
        ax.plot(df.index, ema12, color='#2196f3', linestyle=':', linewidth=1.5, 
                label='EMA12', alpha=0.7)
        
        # Bollinger Bands
        bb_data = calculate_bollinger_bands(df['close'])
        ax.fill_between(df.index, bb_data['upper'], bb_data['lower'], 
                       color='#9c27b0', alpha=0.1, label='Bollinger Bands')
        ax.plot(df.index, bb_data['upper'], color='#9c27b0', linestyle=':', 
                linewidth=1, alpha=0.6)
        ax.plot(df.index, bb_data['lower'], color='#9c27b0', linestyle=':', 
                linewidth=1, alpha=0.6)
        
        # Ichimoku (eğer varsa)
        if 'ichimoku_data' in analysis_data and analysis_data['ichimoku_data']:
            ichimoku = analysis_data['ichimoku_data']
            if 'conversion_line' in ichimoku:
                ax.plot(df.index, ichimoku['conversion_line'], 
                       color='#ff5722', linewidth=1, label='Tenkan', alpha=0.7)
            if 'base_line' in ichimoku:
                ax.plot(df.index, ichimoku['base_line'], 
                       color='#607d8b', linewidth=1, label='Kijun', alpha=0.7)
        
    except Exception as e:
        print(f"Teknik indikatör hatası: {e}")

def add_support_resistance_levels(ax, df, analysis_data):
    """Destek/Direnç seviyelerini ekle"""
    try:
        current_price = df['close'].iloc[-1]
        
        # Destek seviyeleri
        support_levels = find_support_levels(df, current_price)
        for i, support in enumerate(support_levels[:3]):
            alpha = 0.8 - (i * 0.2)
            ax.axhline(y=support, color='#4caf50', linestyle='-', 
                      alpha=alpha, linewidth=2 + (2-i), 
                      label=f'Destek {i+1}: ${support:.4f}' if i == 0 else '')
        
        # Direnç seviyeleri
        resistance_levels = find_resistance_levels(df, current_price)
        for i, resistance in enumerate(resistance_levels[:3]):
            alpha = 0.8 - (i * 0.2)
            ax.axhline(y=resistance, color='#f44336', linestyle='-', 
                      alpha=alpha, linewidth=2 + (2-i), 
                      label=f'Direnç {i+1}: ${resistance:.4f}' if i == 0 else '')
        
    except Exception as e:
        print(f"Destek/Direnç hatası: {e}")

def add_fibonacci_levels(ax, fib_levels):
    """Fibonacci seviyelerini ekle"""
    try:
        colors = ['#ff9800', '#ff5722', '#e91e63', '#9c27b0', '#673ab7', '#3f51b5', '#2196f3']
        
        for i, (level, price) in enumerate(fib_levels.items()):
            color = colors[i % len(colors)]
            ax.axhline(y=price, color=color, linestyle=':', alpha=0.6, linewidth=1)
            ax.text(0.98, price, f'{level}', transform=ax.get_yaxis_transform(),
                   fontsize=8, color=color, ha='right', va='center')
        
    except Exception as e:
        print(f"Fibonacci hatası: {e}")

def create_rsi_chart(ax, df, analysis_data):
    """RSI grafiği oluştur"""
    try:
        ax.set_facecolor('#1a1d29')
        
        rsi = calculate_rsi(df['close'])
        current_rsi = rsi.iloc[-1]
        
        # RSI çizgisi
        ax.plot(df.index, rsi, color='#9c27b0', linewidth=2.5, label='RSI')
        
        # Overbought/Oversold seviyeleri
        ax.axhline(y=70, color='#f44336', linestyle='--', alpha=0.8, linewidth=2)
        ax.axhline(y=30, color='#4caf50', linestyle='--', alpha=0.8, linewidth=2)
        ax.axhline(y=50, color='#ffeb3b', linestyle=':', alpha=0.5, linewidth=1)
        
        # RSI bölgeleri
        ax.fill_between(df.index, 70, 100, alpha=0.1, color='red', label='Aşırı Alım')
        ax.fill_between(df.index, 0, 30, alpha=0.1, color='green', label='Aşırı Satım')
        
        # Mevcut RSI değeri
        ax.text(0.02, 0.85, f'RSI: {current_rsi:.1f}', transform=ax.transAxes,
                fontsize=12, color='white', fontweight='bold',
                bbox=dict(boxstyle="round,pad=0.3", facecolor='#2d3748', alpha=0.8))
        
        ax.set_title('RSI (14)', fontsize=12, color='white', fontweight='bold')
        ax.set_ylim(0, 100)
        ax.grid(True, alpha=0.2)
        ax.set_ylabel('RSI', color='white')
        
    except Exception as e:
        print(f"RSI grafik hatası: {e}")

def create_macd_chart(ax, df, analysis_data):
    """MACD grafiği oluştur"""
    try:
        ax.set_facecolor('#1a1d29')
        
        macd_data = calculate_macd(df['close'])
        
        # MACD çizgileri
        ax.plot(df.index, macd_data['macd'], color='#2196f3', linewidth=2, label='MACD')
        ax.plot(df.index, macd_data['signal'], color='#ff9800', linewidth=2, label='Signal')
        
        # MACD histogram
        colors = ['#4caf50' if val >= 0 else '#f44336' for val in macd_data['histogram']]
        ax.bar(df.index, macd_data['histogram'], color=colors, alpha=0.6, width=0.8)
        
        # Sıfır çizgisi
        ax.axhline(y=0, color='white', linestyle='-', alpha=0.3, linewidth=1)
        
        # Mevcut değerler
        current_macd = macd_data['macd'].iloc[-1]
        current_signal = macd_data['signal'].iloc[-1]
        
        signal_status = "BULLISH" if current_macd > current_signal else "BEARISH"
        signal_color = "#4caf50" if current_macd > current_signal else "#f44336"
        
        ax.text(0.02, 0.85, f'MACD: {signal_status}', transform=ax.transAxes,
                fontsize=12, color=signal_color, fontweight='bold',
                bbox=dict(boxstyle="round,pad=0.3", facecolor='#2d3748', alpha=0.8))
        
        ax.set_title('MACD', fontsize=12, color='white', fontweight='bold')
        ax.grid(True, alpha=0.2)
        ax.set_ylabel('MACD', color='white')
        ax.legend(loc='upper right', fontsize=8)
        
    except Exception as e:
        print(f"MACD grafik hatası: {e}")

def create_volume_chart(ax, df):
    """Volume grafiği oluştur"""
    try:
        ax.set_facecolor('#1a1d29')
        
        # Volume renklendirme (fiyat artış/azalış)
        colors = []
        for i in range(len(df)):
            if i == 0:
                colors.append('#2196f3')
            else:
                color = '#4caf50' if df['close'].iloc[i] >= df['close'].iloc[i-1] else '#f44336'
                colors.append(color)
        
        ax.bar(df.index, df['volume'], color=colors, alpha=0.7, width=0.8)
        
        # Volume ortalaması
        volume_sma = df['volume'].rolling(20).mean()
        ax.plot(df.index, volume_sma, color='#ffeb3b', linewidth=2, alpha=0.8, label='Volume SMA')
        
        # Mevcut volume bilgisi
        current_volume = df['volume'].iloc[-1]
        avg_volume = volume_sma.iloc[-1]
        volume_ratio = current_volume / avg_volume if avg_volume > 0 else 1
        
        ax.text(0.02, 0.85, f'Volume: {volume_ratio:.1f}x', transform=ax.transAxes,
                fontsize=12, color='white', fontweight='bold',
                bbox=dict(boxstyle="round,pad=0.3", facecolor='#2d3748', alpha=0.8))
        
        ax.set_title('Volume', fontsize=12, color='white', fontweight='bold')
        ax.grid(True, alpha=0.2)
        ax.set_ylabel('Volume', color='white')
        
        # Volume formatı
        ax.ticklabel_format(style='scientific', axis='y', scilimits=(0,0))
        
    except Exception as e:
        print(f"Volume grafik hatası: {e}")

def create_info_panel(ax, analysis_data):
    """Bilgi paneli oluştur"""
    try:
        ax.set_facecolor('#1a1d29')
        ax.axis('off')
        
        # Analiz bilgileri
        price = analysis_data.get('price', 0)
        rsi = analysis_data.get('rsi', 50)
        overall_score = analysis_data.get('overall_score', 5)
        recommendation = analysis_data.get('recommendation', 'BEKLE')
        
        # Fiyat formatı
        if price < 0.01:
            price_str = f"${price:.8f}"
        elif price < 1:
            price_str = f"${price:.6f}"
        else:
            price_str = f"${price:,.4f}"
        
        info_text = f"""
GÜNCEL BİLGİLER

💰 Fiyat: {price_str}
📊 RSI: {rsi:.1f}
⭐ Skor: {overall_score:.1f}/10
💡 Öneri: {recommendation}

TEKNİK DURUM
"""
        
        # MACD durumu
        if 'macd_data' in analysis_data:
            macd_data = analysis_data['macd_data']
            macd_current = macd_data['macd'].iloc[-1]
            macd_signal = macd_data['signal'].iloc[-1]
            macd_status = "↗️ Bullish" if macd_current > macd_signal else "↘️ Bearish"
            info_text += f"MACD: {macd_status}\n"
        
        # Bollinger Bands pozisyonu
        if 'bb_data' in analysis_data:
            bb_data = analysis_data['bb_data']
            bb_upper = bb_data['upper'].iloc[-1]
            bb_lower = bb_data['lower'].iloc[-1]
            bb_middle = bb_data['middle'].iloc[-1]
            
            if price > bb_upper:
                bb_pos = "🔴 Üst band üzerinde"
            elif price < bb_lower:
                bb_pos = "🟢 Alt band altında"
            elif price > bb_middle:
                bb_pos = "🟡 Orta üst bölge"
            else:
                bb_pos = "🟡 Orta alt bölge"
            
            info_text += f"BB: {bb_pos}\n"
        
        # Trend bilgisi
        if 'trend_strength' in analysis_data:
            trend = analysis_data['trend_strength']
            trend_dir = trend.get('direction', 'NEUTRAL')
            trend_emoji = "📈" if trend_dir == 'BULLISH' else "📉" if trend_dir == 'BEARISH' else "➡️"
            info_text += f"Trend: {trend_emoji} {trend_dir}\n"
        
        # Risk bilgisi
        if 'risk_analysis' in analysis_data:
            risk = analysis_data['risk_analysis']
            risk_level = risk.get('risk_description', 'Orta')
            risk_emoji = "🔴" if risk_level == 'Yüksek' else "🟡" if risk_level == 'Orta' else "🟢"
            info_text += f"Risk: {risk_emoji} {risk_level}\n"
        
        ax.text(0.05, 0.95, info_text, transform=ax.transAxes, 
                fontsize=10, color='white', verticalalignment='top',
                bbox=dict(boxstyle="round,pad=0.5", facecolor='#2d3748', alpha=0.9))
        
    except Exception as e:
        print(f"Bilgi paneli hatası: {e}")

def create_signals_panel(ax, analysis_data):
    """Sinyal paneli oluştur"""
    try:
        ax.set_facecolor('#1a1d29')
        ax.axis('off')
        
        signals = analysis_data.get('signals', [])
        entry_exit = analysis_data.get('entry_exit', {})
        
        signals_text = "🎯 SİNYALLER\n\n"
        
        # En güçlü sinyaller
        strong_signals = [s for s in signals if s['strength'] >= 6]
        if strong_signals:
            for signal in strong_signals[:4]:
                strength_emoji = "🔥" if signal['strength'] >= 8 else "⚡" if signal['strength'] >= 7 else "💫"
                type_emoji = "🟢" if signal['type'] == 'BUY' else "🔴"
                
                signals_text += f"{strength_emoji} {type_emoji} {signal['type']}\n"
                signals_text += f"   📝 {signal['reason']}\n"
                signals_text += f"   💪 Güç: {signal['strength']}/10\n\n"
        else:
            signals_text += "⚖️ Güçlü sinyal yok\n"
            signals_text += "📊 Beklemede kal\n\n"
        
        # Entry/Exit bilgileri
        if entry_exit and entry_exit.get('action') != 'HOLD':
            action = entry_exit['action']
            
            signals_text += f"💼 ENTRY/EXIT\n\n"
            signals_text += f"🎯 Aksiyon: {action}\n"
            
            if action == 'BUY' and entry_exit.get('entry_points'):
                entry_price = entry_exit['entry_points'][0]['price']
                stop_loss = entry_exit.get('stop_loss', 0)
                take_profit = entry_exit.get('take_profit', 0)
                
                signals_text += f"🟢 Entry: ${entry_price:.4f}\n"
                signals_text += f"🔴 Stop: ${stop_loss:.4f}\n"
                signals_text += f"🎯 Target: ${take_profit:.4f}\n"
            
            # Risk/Reward
            if 'risk_reward' in entry_exit:
                rr = entry_exit['risk_reward']
                signals_text += f"⚖️ R/R: {rr:.1f}\n"
        
        ax.text(0.05, 0.95, signals_text, transform=ax.transAxes, 
                fontsize=9, color='white', verticalalignment='top',
                bbox=dict(boxstyle="round,pad=0.5", facecolor='#2d3748', alpha=0.9))
        
    except Exception as e:
        print(f"Sinyal paneli hatası: {e}")

def create_multi_timeframe_chart(symbol, timeframe_results):
    """Çoklu timeframe karşılaştırma grafiği"""
    try:
        fig, axes = plt.subplots(2, 2, figsize=(16, 10), facecolor='#0f1419')
        fig.suptitle(f'{symbol} - Çoklu Timeframe Analizi', fontsize=16, color='white', fontweight='bold')
        
        timeframes = ['1h', '4h', '1d', '1w']
        
        for i, tf in enumerate(timeframes):
            ax = axes[i // 2, i % 2]
            ax.set_facecolor('#1a1d29')
            
            if tf in timeframe_results:
                result = timeframe_results[tf]
                score = result.get('overall_score', 5)
                
                # Skor göstergesi
                colors = ['#f44336', '#ff5722', '#ff9800', '#ffeb3b', '#cddc39', 
                         '#8bc34a', '#4caf50', '#009688', '#2196f3', '#3f51b5', '#9c27b0']
                color = colors[min(int(score), 10)]
                
                # Dairesel skor göstergesi
                circle = plt.Circle((0.5, 0.5), 0.3, color=color, alpha=0.7)
                ax.add_patch(circle)
                
                # Skor metni
                ax.text(0.5, 0.5, f'{score:.1f}', ha='center', va='center',
                       fontsize=24, color='white', fontweight='bold')
                
                ax.text(0.5, 0.2, f'{tf.upper()}', ha='center', va='center',
                       fontsize=14, color='white', fontweight='bold')
                
                # Trend bilgisi
                trend = result.get('trend', 'NEUTRAL')
                trend_color = '#4caf50' if trend == 'BULLISH' else '#f44336' if trend == 'BEARISH' else '#ffeb3b'
                ax.text(0.5, 0.1, trend, ha='center', va='center',
                       fontsize=12, color=trend_color, fontweight='bold')
            else:
                ax.text(0.5, 0.5, 'Veri Yok', ha='center', va='center',
                       fontsize=16, color='gray')
                ax.text(0.5, 0.3, f'{tf.upper()}', ha='center', va='center',
                       fontsize=14, color='white')
            
            ax.set_xlim(0, 1)
            ax.set_ylim(0, 1)
            ax.axis('off')
        
        plt.tight_layout()
        
        # Grafik kaydet
        img = BytesIO()
        plt.savefig(img, format='png', dpi=150, bbox_inches='tight', 
                    facecolor='#0f1419', edgecolor='none')
        img.seek(0)
        plt.close()
        
        return img
    except Exception as e:
        print(f"Multi timeframe grafik hatası: {e}")
        plt.close()
        return None

def create_fibonacci_chart(df, symbol, fib_levels):
    """Fibonacci retracement grafiği"""
    try:
        fig, ax = plt.subplots(1, 1, figsize=(14, 8), facecolor='#0f1419')
        ax.set_facecolor('#1a1d29')
        
        # Fiyat çizgisi
        ax.plot(df.index, df['close'], color='#00e676', linewidth=2.5, label='Fiyat')
        
        # Fibonacci seviyeleri
        colors = ['#ff9800', '#ff5722', '#e91e63', '#9c27b0', '#673ab7', '#3f51b5', '#2196f3']
        
        for i, (level, price) in enumerate(fib_levels.items()):
            color = colors[i % len(colors)]
            ax.axhline(y=price, color=color, linestyle='--', alpha=0.8, linewidth=2)
            
            # Seviye etiketi
            ax.text(df.index[-1], price, f'  {level} (${price:.4f})', 
                   color=color, fontweight='bold', va='center')
        
        # Mevcut fiyat
        current_price = df['close'].iloc[-1]
        ax.axhline(y=current_price, color='white', linewidth=3, alpha=0.9)
        
        ax.set_title(f'{symbol} - Fibonacci Retracement', 
                    fontsize=16, color='white', fontweight='bold')
        ax.grid(True, alpha=0.2)
        ax.set_ylabel('Fiyat ($)', color='white')
        
        plt.tight_layout()
        
        # Grafik kaydet
        img = BytesIO()
        plt.savefig(img, format='png', dpi=150, bbox_inches='tight', 
                    facecolor='#0f1419', edgecolor='none')
        img.seek(0)
        plt.close()
        
        return img
    except Exception as e:
        print(f"Fibonacci grafik hatası: {e}")
        plt.close()
        return None

def create_signals_summary_chart(signals_data):
    """Sinyal özeti grafiği"""
    try:
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6), facecolor='#0f1419')
        
        # Sinyal gücü pasta grafiği
        ax1.set_facecolor('#1a1d29')
        
        buy_strength = signals_data.get('bullish_strength', 0)
        sell_strength = signals_data.get('bearish_strength', 0)
        neutral_strength = max(0, 10 - buy_strength - sell_strength)
        
        sizes = [buy_strength, sell_strength, neutral_strength]
        labels = ['BULLISH', 'BEARISH', 'NEUTRAL']
        colors = ['#4caf50', '#f44336', '#ffeb3b']
        
        # Sıfır olmayan değerleri filtrele
        non_zero_data = [(size, label, color) for size, label, color in zip(sizes, labels, colors) if size > 0]
        
        if non_zero_data:
            sizes, labels, colors = zip(*non_zero_data)
            wedges, texts, autotexts = ax1.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%',
                                              startangle=90, textprops={'color': 'white'})
        
        ax1.set_title('Sinyal Gücü Dağılımı', color='white', fontweight='bold')
        
        # Sinyal sayısı bar grafiği
        ax2.set_facecolor('#1a1d29')
        
        signals = signals_data.get('signals', [])
        buy_signals = [s for s in signals if s['type'] == 'BUY']
        sell_signals = [s for s in signals if s['type'] == 'SELL']
        
        categories = ['BUY\nSinyalleri', 'SELL\nSinyalleri']
        counts = [len(buy_signals), len(sell_signals)]
        bar_colors = ['#4caf50', '#f44336']
        
        bars = ax2.bar(categories, counts, color=bar_colors, alpha=0.8)
        
        # Bar değerlerini göster
        for bar, count in zip(bars, counts):
            height = bar.get_height()
            ax2.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                    f'{count}', ha='center', va='bottom', color='white', fontweight='bold')
        
        ax2.set_title('Sinyal Sayıları', color='white', fontweight='bold')
        ax2.set_ylabel('Sinyal Sayısı', color='white')
        ax2.grid(True, alpha=0.2, axis='y')
        
        # Eksen renklerini ayarla
        ax2.tick_params(colors='white')
        ax2.spines['bottom'].set_color('white')
        ax2.spines['left'].set_color('white')
        ax2.spines['top'].set_visible(False)
        ax2.spines['right'].set_visible(False)
        
        plt.tight_layout()
        
        # Grafik kaydet
        img = BytesIO()
        plt.savefig(img, format='png', dpi=150, bbox_inches='tight', 
                    facecolor='#0f1419', edgecolor='none')
        img.seek(0)
        plt.close()
        
        return img
    except Exception as e:
        print(f"Sinyal özeti grafik hatası: {e}")
        plt.close()
        return None

# Eski fonksiyonları da koru (geriye uyumluluk için)
def create_price_chart(df, symbol, analysis_data=None, timeframe="1d"):
    """Eski create_price_chart fonksiyonu - geriye uyumluluk"""
    return create_advanced_chart(df, symbol, analysis_data or {}, timeframe)

def create_simple_price_chart(symbol, price_data):
    """Basit fiyat grafiği (veri olmadığında)"""
    try:
        fig, ax = plt.subplots(1, 1, figsize=(12, 6), facecolor='#0f1419')
        ax.set_facecolor('#1a1d29')
        
        # Basit fiyat bilgisi göster
        price = price_data.get('usd', 0)
        change_24h = price_data.get('usd_24h_change', 0)
        
        # Renk belirle
        color = '#4caf50' if change_24h >= 0 else '#f44336'
        
        # Metin göster
        ax.text(0.5, 0.6, f'${price:,.4f}', 
                horizontalalignment='center', verticalalignment='center',
                transform=ax.transAxes, fontsize=48, color=color, fontweight='bold')
        
        ax.text(0.5, 0.4, f'{change_24h:+.2f}% (24h)', 
                horizontalalignment='center', verticalalignment='center',
                transform=ax.transAxes, fontsize=24, color=color)
        
        ax.text(0.5, 0.8, symbol.upper(), 
                horizontalalignment='center', verticalalignment='center',
                transform=ax.transAxes, fontsize=32, color='white', fontweight='bold')
        
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.axis('off')
        
        plt.tight_layout()
        
        # Grafik kaydet
        img = BytesIO()
        plt.savefig(img, format='png', dpi=150, bbox_inches='tight', 
                    facecolor='#0f1419', edgecolor='none')
        img.seek(0)
        plt.close()
        
        return img
    except Exception as e:
        print(f"Basit grafik oluşturma hatası: {e}")
        plt.close()
        return None

if DEBUG_MODE:
    print("📊 Advanced chart generator utils yüklendi!")
