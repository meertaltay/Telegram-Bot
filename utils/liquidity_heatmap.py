"""
Professional Volume-Based Liquidity Heatmap Generator
CoinGlass tarzı profesyonel likidite haritası
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.colors as mcolors
import numpy as np
import pandas as pd
from io import BytesIO
from utils.binance_api import get_binance_ohlc
import seaborn as sns

def create_professional_liquidity_heatmap(symbol, timeframe='1h', lookback_hours=48):
    """
    CoinGlass tarzı profesyonel likidite haritası oluştur
    """
    try:
        # Veri al
        df = get_binance_ohlc(symbol, interval=timeframe, limit=lookback_hours)
        if df is None or df.empty:
            return None

        # Likidite seviyelerini hesapla
        liquidity_data = calculate_liquidity_levels(df)
        
        # Grafik oluştur
        fig, ax = plt.subplots(1, 1, figsize=(20, 12), facecolor='#0a0a0f')
        ax.set_facecolor('#0a0a0f')
        
        # Likidite haritasını çiz
        create_heatmap_background(ax, liquidity_data)
        
        # Fiyat çizgisini ekle
        add_price_line(ax, df)
        
        # Likidite barlarını ekle
        add_liquidity_bars(ax, liquidity_data)
        
        # Fiyat etiketlerini ekle
        add_price_labels(ax, liquidity_data)
        
        # Başlık ve stil
        setup_professional_style(ax, symbol)
        
        # Grafik kaydet
        img = BytesIO()
        plt.savefig(img, format='png', dpi=300, bbox_inches='tight', 
                    facecolor='#0a0a0f', edgecolor='none')
        img.seek(0)
        plt.close()
        
        return img
        
    except Exception as e:
        print(f"Likidite haritası oluşturma hatası: {e}")
        plt.close()
        return None

def calculate_liquidity_levels(df, num_levels=50):
    """
    Fiyat seviyelerinde likidite hesapla
    """
    try:
        current_price = df['close'].iloc[-1]
        high_price = df['high'].max()
        low_price = df['low'].min()
        
        # Fiyat aralığını genişlet (%10)
        price_range = high_price - low_price
        extended_high = high_price + (price_range * 0.05)
        extended_low = low_price - (price_range * 0.05)
        
        # Fiyat seviyelerini oluştur
        price_levels = np.linspace(extended_low, extended_high, num_levels)
        
        liquidity_levels = []
        
        for price_level in price_levels:
            # Bu seviyeye yakın işlem gören volume'u hesapla
            proximity_threshold = (extended_high - extended_low) / num_levels
            
            # Yakın fiyat seviyelerindeki volume'u topla
            level_volume = 0
            level_touches = 0
            
            for i, row in df.iterrows():
                # High/Low bu seviyeyi test ettiyse
                if row['low'] <= price_level <= row['high']:
                    # Fiyata olan yakınlığa göre ağırlıklandır
                    distance = min(
                        abs(row['high'] - price_level),
                        abs(row['low'] - price_level),
                        abs(row['close'] - price_level)
                    )
                    
                    if distance <= proximity_threshold:
                        weight = 1 - (distance / proximity_threshold)
                        level_volume += row['volume'] * weight
                        level_touches += 1
            
            # Likidite gücü hesapla
            liquidity_strength = level_volume * (1 + level_touches * 0.1)
            
            liquidity_levels.append({
                'price': price_level,
                'volume': level_volume,
                'touches': level_touches,
                'strength': liquidity_strength,
                'type': 'support' if price_level < current_price else 'resistance'
            })
        
        # Güce göre sırala ve normalize et
        liquidity_levels.sort(key=lambda x: x['strength'], reverse=True)
        max_strength = max(level['strength'] for level in liquidity_levels) if liquidity_levels else 1
        
        for level in liquidity_levels:
            level['normalized_strength'] = level['strength'] / max_strength
            
        return {
            'levels': liquidity_levels,
            'current_price': current_price,
            'price_range': (extended_low, extended_high)
        }
        
    except Exception as e:
        print(f"Likidite hesaplama hatası: {e}")
        return None

def create_heatmap_background(ax, liquidity_data):
    """
    Mor gradient arkaplan oluştur
    """
    try:
        levels = liquidity_data['levels']
        price_range = liquidity_data['price_range']
        
        # Gradient renkleri (mor tonları)
        colors = ['#0a0a0f', '#1a0a2e', '#16213e', '#0f3460', '#533483']
        n_bins = 100
        cmap = mcolors.LinearSegmentedColormap.from_list('liquidity', colors, N=n_bins)
        
        # Her fiyat seviyesi için gradient intensity
        y_positions = [level['price'] for level in levels]
        intensities = [level['normalized_strength'] for level in levels]
        
        # Arkaplan gradienti
        for i, level in enumerate(levels):
            y_pos = level['price']
            intensity = level['normalized_strength']
            
            # Bar yüksekliği
            bar_height = (price_range[1] - price_range[0]) / len(levels)
            
            # Renk intensity'sine göre
            color = cmap(intensity)
            
            # Arkaplan dikdörtgeni
            rect = patches.Rectangle(
                (0, y_pos - bar_height/2), 1, bar_height,
                facecolor=color, alpha=0.6, edgecolor='none'
            )
            ax.add_patch(rect)
            
    except Exception as e:
        print(f"Arkaplan oluşturma hatası: {e}")

def add_price_line(ax, df):
    """
    Fiyat çizgisini ekle (mini candlestick benzeri)
    """
    try:
        # Son 100 veriyi al
        recent_df = df.tail(100)
        
        # X ekseni için normalize edilmiş pozisyonlar
        x_positions = np.linspace(0.2, 0.8, len(recent_df))
        
        # Candlestick benzeri çizim
        for i, (idx, row) in enumerate(recent_df.iterrows()):
            x_pos = x_positions[i]
            
            # Renk belirle
            color = '#00ff88' if row['close'] >= row['open'] else '#ff4757'
            
            # High-Low çizgisi
            ax.plot([x_pos, x_pos], [row['low'], row['high']], 
                   color=color, linewidth=0.5, alpha=0.8)
            
            # Open-Close dikdörtgeni
            body_height = abs(row['close'] - row['open'])
            body_bottom = min(row['close'], row['open'])
            
            rect = patches.Rectangle(
                (x_pos - 0.002, body_bottom), 0.004, body_height,
                facecolor=color, alpha=0.9, edgecolor=color
            )
            ax.add_patch(rect)
            
    except Exception as e:
        print(f"Fiyat çizgisi hatası: {e}")

def add_liquidity_bars(ax, liquidity_data):
    """
    Horizontal likidite barları ekle
    """
    try:
        levels = liquidity_data['levels']
        
        # En güçlü seviyeleri al
        strong_levels = [level for level in levels if level['normalized_strength'] > 0.3][:20]
        
        for level in strong_levels:
            y_pos = level['price']
            strength = level['normalized_strength']
            level_type = level['type']
            
            # Bar uzunluğu
            bar_length = strength * 0.15
            
            # Renk (destek: yeşil tonları, direnç: kırmızı tonları)
            if level_type == 'support':
                color = '#00ff88' if strength > 0.7 else '#26de81' if strength > 0.5 else '#2ed573'
            else:
                color = '#ff4757' if strength > 0.7 else '#ff6348' if strength > 0.5 else '#ff7675'
            
            # Sol tarafta bar (support/resistance)
            if level_type == 'support':
                ax.barh(y_pos, bar_length, height=(liquidity_data['price_range'][1] - liquidity_data['price_range'][0]) / 100,
                       left=0.85, color=color, alpha=0.8, edgecolor='none')
            else:
                ax.barh(y_pos, bar_length, height=(liquidity_data['price_range'][1] - liquidity_data['price_range'][0]) / 100,
                       left=0.85, color=color, alpha=0.8, edgecolor='none')
            
            # Volume yazısı
            if strength > 0.6:
                volume_text = format_volume(level['volume'])
                ax.text(0.82, y_pos, volume_text, fontsize=8, color='white', 
                       ha='right', va='center', alpha=0.9)
                
    except Exception as e:
        print(f"Likidite bar hatası: {e}")

def add_price_labels(ax, liquidity_data):
    """
    Sağ tarafta fiyat etiketleri ekle
    """
    try:
        current_price = liquidity_data['current_price']
        price_range = liquidity_data['price_range']
        
        # Fiyat seviyelerini belirle
        num_labels = 15
        price_labels = np.linspace(price_range[0], price_range[1], num_labels)
        
        for price in price_labels:
            # Güncel fiyata yakınsa vurgula
            if abs(price - current_price) / current_price < 0.005:
                color = '#ffff00'
                fontweight = 'bold'
                fontsize = 10
            else:
                color = '#ffffff'
                fontweight = 'normal'
                fontsize = 9
            
            # Fiyat formatla
            if price < 1:
                price_text = f"${price:.6f}"
            elif price < 100:
                price_text = f"${price:.2f}"
            else:
                price_text = f"${price:,.0f}"
            
            # Sağ tarafta göster
            ax.text(1.02, price, price_text, fontsize=fontsize, color=color,
                   ha='left', va='center', fontweight=fontweight,
                   transform=ax.get_yaxis_transform())
                   
    except Exception as e:
        print(f"Fiyat etiketi hatası: {e}")

def setup_professional_style(ax, symbol):
    """
    Profesyonel stil ayarları
    """
    try:
        # Eksen ayarları
        ax.set_xlim(0, 1)
        ax.set_facecolor('#0a0a0f')
        
        # Grid kaldır
        ax.grid(False)
        
        # X eksenini gizle
        ax.set_xticks([])
        ax.spines['bottom'].set_visible(False)
        ax.spines['top'].set_visible(False)
        ax.spines['left'].set_visible(False)
        ax.spines['right'].set_visible(False)
        
        # Y ekseni ayarları
        ax.tick_params(colors='white', labelsize=9)
        ax.yaxis.set_label_position('right')
        ax.yaxis.tick_right()
        
        # Başlık
        ax.text(0.02, 0.98, f'📊 {symbol} - Liquidity Heatmap', 
                transform=ax.transAxes, fontsize=16, color='white',
                fontweight='bold', va='top')
        
        # Legend
        ax.text(0.02, 0.94, '🟢 Support Levels    🔴 Resistance Levels', 
                transform=ax.transAxes, fontsize=10, color='white',
                va='top', alpha=0.8)
        
        # Volume scale açıklaması
        ax.text(0.02, 0.06, '📈 Bar Length = Liquidity Strength\n💰 Volume shown for strong levels', 
                transform=ax.transAxes, fontsize=9, color='white',
                va='bottom', alpha=0.7)
                
    except Exception as e:
        print(f"Stil ayarlama hatası: {e}")

def format_volume(volume):
    """
    Volume'u okunabilir formatta göster
    """
    if volume >= 1e9:
        return f"{volume/1e9:.1f}B"
    elif volume >= 1e6:
        return f"{volume/1e6:.1f}M"
    elif volume >= 1e3:
        return f"{volume/1e3:.1f}K"
    else:
        return f"{volume:.0f}"

# Komut entegrasyonu için fonksiyon
def add_liquidity_command_to_bot(bot):
    """
    Likidite haritası komutunu bot'a ekle
    """
    
    @bot.message_handler(commands=['liquidity', 'likidite'])
    def liquidity_heatmap_command(message):
        """Likidite haritası komutu"""
        try:
            parts = message.text.strip().split()
            if len(parts) < 2:
                bot.send_message(message.chat.id, 
                    "💧 **Likidite Haritası:**\n\n"
                    "/liquidity COIN [TIMEFRAME]\n\n"
                    "**Örnekler:**\n"
                    "• /liquidity btc\n"
                    "• /liquidity eth 1h\n"
                    "• /liquidity sol 4h\n\n"
                    "📊 **Özellikler:**\n"
                    "• Volume bazlı destek/direnç\n"
                    "• Profesyonel görselleştirme\n"
                    "• Likidite gücü analizi",
                    parse_mode="Markdown")
                return

            coin_input = parts[1].lower()
            timeframe = parts[2] if len(parts) > 2 else '1h'
            
            # Binance sembolü bul
            from utils.binance_api import find_binance_symbol
            binance_symbol = find_binance_symbol(coin_input)
            
            if not binance_symbol:
                bot.send_message(message.chat.id, 
                    f"❌ '{coin_input.upper()}' bulunamadı!")
                return

            bot.send_message(message.chat.id, 
                f"💧 {binance_symbol} likidite haritası oluşturuluyor...")
            
            # Likidite haritası oluştur
            heatmap_img = create_professional_liquidity_heatmap(binance_symbol, timeframe)
            
            if heatmap_img:
                caption = (f"💧 **{binance_symbol} Likidite Haritası**\n\n"
                          f"⏰ Timeframe: {timeframe}\n"
                          f"🟢 **Yeşil barlar:** Destek seviyeleri\n"
                          f"🔴 **Kırmızı barlar:** Direnç seviyeleri\n"
                          f"📊 **Bar uzunluğu:** Likidite gücü\n\n"
                          f"💡 Güçlü seviyeler potansiyel dönüş noktalarıdır!")
                
                bot.send_photo(message.chat.id, heatmap_img, 
                             caption=caption, parse_mode="Markdown")
            else:
                bot.send_message(message.chat.id, 
                    "❌ Likidite haritası oluşturulamadı!")
                
        except Exception as e:
            print(f"Likidite komutu hatası: {e}")
            bot.send_message(message.chat.id, 
                "❌ Likidite analizi yapılamadı!")

# Test fonksiyonu
def test_liquidity_heatmap():
    """Test için likidite haritası oluştur"""
    try:
        img = create_professional_liquidity_heatmap("BTCUSDT", "1h")
        if img:
            print("✅ Likidite haritası başarıyla oluşturuldu!")
            # Test için dosyaya kaydet
            with open("test_liquidity.png", "wb") as f:
                f.write(img.getvalue())
        else:
            print("❌ Likidite haritası oluşturulamadı!")
    except Exception as e:
        print(f"Test hatası: {e}")

if __name__ == "__main__":
    print("💧 Professional Liquidity Heatmap Generator yüklendi!")
    print("🧪 Test çalıştırmak için test_liquidity_heatmap() fonksiyonunu çağır")
