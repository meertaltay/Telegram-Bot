"""
Chart Generator Utils
Matplotlib ile kripto grafikleri oluştur
"""

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.gridspec import GridSpec
from io import BytesIO
import pandas as pd
from config import *
from .technical_analysis import *

# Matplotlib ayarları
plt.style.use('dark_background')

def create_price_chart(df, symbol, analysis_data=None):
    """Fiyat grafiği oluştur"""
    try:
        fig = plt.figure(figsize=(CHART_WIDTH, CHART_HEIGHT), facecolor='#0f1419')
        fig.patch.set_alpha(0.0)
        gs = GridSpec(3, 2, height_ratios=[2, 1, 1], width_ratios=[3, 1])
        
        # Ana fiyat grafiği
        ax1 = fig.add_subplot(gs[0, 0])
        ax1.set_facecolor('#1a1d29')
        
        # Fiyat çizgisi
        ax1.plot(df.index, df['close'], color='#00e676', linewidth=2, label='Fiyat')
        
        # Hareketli ortalamalar
        sma20 = calculate_sma(df['close'], 20)
        sma50 = calculate_sma(df['close'], 50)
        ax1.plot(df.index, sma20, color='#ffeb3b', linestyle='--', linewidth=1.5, label='SMA20')
        ax1.plot(df.index, sma50, color='#f44336', linestyle='--', linewidth=1.5, label='SMA50')
        
        # Bollinger Bands
        bb = calculate_bollinger_bands(df['close'])
        ax1.fill_between(df.index, bb['upper'], bb['lower'], color='gray', alpha=0.1)
        ax1.plot(df.index, bb['upper'], color='#ffeb3b', linestyle=':', linewidth=1)
        ax1.plot(df.index, bb['lower'], color='#ffeb3b', linestyle=':', linewidth=1)
        
        # Mevcut fiyat çizgisi
        current_price = df['close'].iloc[-1]
        ax1.axhline(y=current_price, color='#ffffff', linestyle='-', alpha=0.8, linewidth=2)
        
        ax1.set_title(f'{symbol} - Teknik Analiz', fontsize=16, color='white', fontweight='bold')
        ax1.legend(loc='upper left', fontsize=10)
        ax1.grid(True, alpha=0.2, color='gray')
        ax1.set_ylabel('Fiyat ($)', color='white', fontsize=12)
        
        # RSI grafiği
        ax2 = fig.add_subplot(gs[1, 0])
        ax2.set_facecolor('#1a1d29')
        rsi = calculate_rsi(df['close'])
        ax2.plot(df.index, rsi, color='#9c27b0', linewidth=2)
        ax2.axhline(y=70, color='#f44336', linestyle='--', alpha=0.8, linewidth=2)
        ax2.axhline(y=30, color='#4caf50', linestyle='--', alpha=0.8, linewidth=2)
        ax2.set_title('RSI (14)', fontsize=12, color='white')
        ax2.set_ylim(0, 100)
        ax2.grid(True, alpha=0.2)
        
        # Volume grafiği
        ax3 = fig.add_subplot(gs[2, 0])
        ax3.set_facecolor('#1a1d29')
        colors = ['#4caf50' if close >= open_price else '#f44336' 
                 for close, open_price in zip(df['close'], df['open'])]
        ax3.bar(df.index, df['volume'], color=colors, alpha=0.7)
        ax3.set_title('Volume', fontsize=12, color='white')
        ax3.grid(True, alpha=0.2)
        
        # Bilgi paneli
        ax_info = fig.add_subplot(gs[0:, 1])
        ax_info.set_facecolor('#1a1d29')
        ax_info.axis('off')
        
        # Analiz bilgileri
        if analysis_data:
            info_text = format_analysis_info(analysis_data, current_price)
        else:
            info_text = f"Güncel Fiyat: ${current_price:.4f}"
        
        ax_info.text(0.05, 0.95, info_text, transform=ax_info.transAxes, 
                     fontsize=11, color='white', verticalalignment='top',
                     bbox=dict(boxstyle="round,pad=0.5", facecolor='#2d3748', alpha=0.8))
        
        plt.tight_layout()
        
        # Grafik kaydet
        img = BytesIO()
        plt.savefig(img, format='png', dpi=CHART_DPI, bbox_inches='tight', 
                    facecolor='#0f1419', edgecolor='none')
        img.seek(0)
        plt.close()
        
        return img
    except Exception as e:
        print(f"Grafik oluşturma hatası: {e}")
        plt.close()
        return None

def format_analysis_info(analysis_data, current_price):
    """Analiz bilgilerini formatla"""
    try:
        info_text = f"""
GÜNCEL FİYAT
${current_price:.4f}

TEKNİK GÖSTERGELER
RSI: {analysis_data.get('rsi', 0):.1f}
MACD: {analysis_data.get('macd_signal', 'N/A')}
Trend: {analysis_data.get('trend', 'Belirsiz')}

DESTEK/DİRENÇ
Destek: ${analysis_data.get('support', 0):.4f}
Direnç: ${analysis_data.get('resistance', 0):.4f}

VOLUME
Oran: {analysis_data.get('volume_ratio', 1):.2f}x
Durum: {analysis_data.get('volume_analysis', 'Normal')}

SİNYALLER
{analysis_data.get('recommendation', 'Analiz yapılıyor...')}
        """
        return info_text.strip()
    except Exception as e:
        print(f"Bilgi formatla hatası: {e}")
        return f"Güncel Fiyat: ${current_price:.4f}"

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
        plt.savefig(img, format='png', dpi=CHART_DPI, bbox_inches='tight', 
                    facecolor='#0f1419', edgecolor='none')
        img.seek(0)
        plt.close()
        
        return img
    except Exception as e:
        print(f"Basit grafik oluşturma hatası: {e}")
        plt.close()
        return None

if DEBUG_MODE:
    print("📊 Chart generator utils yüklendi!")
