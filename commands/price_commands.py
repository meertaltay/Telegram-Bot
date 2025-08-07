"""
Price Commands - Fiyat ile ilgili komutlar
/fiyat, /top10, /trending komutları - HABER SİSTEMİ ENTEGRELİ
"""

import requests
import telebot
from config import *

# 🔥 HABER SİSTEMİ İMPORT
try:
    from utils.news_system import add_active_user
except ImportError:
    print("⚠️ Haber sistemi import edilemedi")
    def add_active_user(user_id):
        pass  # Boş fonksiyon - hata vermemesi için

def register_price_commands(bot):
    """Fiyat komutlarını bot'a kaydet"""
    
    @bot.message_handler(commands=['fiyat'])
    def fiyat(message):
        """Coin fiyatı getir"""
        try:
            # 🔥 HABER SİSTEMİ: Kullanıcıyı otomatik kaydet
            add_active_user(message.from_user.id)
            
            parts = message.text.strip().split()
            if len(parts) < 2:
                bot.send_message(message.chat.id, 
                    "💡 **Kullanım:** /fiyat COIN\n\n"
                    "🔥 **Örnekler:**\n"
                    "• /fiyat btc\n"
                    "• /fiyat ethereum\n"
                    "• /fiyat sol",
                    parse_mode="Markdown")
                return

            coin_input = parts[1].lower()
            
            # Config'den coin ID'sini al
            if coin_input in POPULAR_COINS:
                coin_id = POPULAR_COINS[coin_input]
            else:
                # CoinGecko'da ara
                coin_id = search_coin_id(coin_input)
                if not coin_id:
                    bot.send_message(message.chat.id, 
                        f"❌ '{coin_input.upper()}' bulunamadı!\n\n"
                        "🔍 **Popüler coinler:** BTC, ETH, SOL, DOGE, ADA",
                        parse_mode="Markdown")
                    return

            # Fiyat bilgilerini al
            price_data = get_coin_price(coin_id)
            if not price_data:
                bot.send_message(message.chat.id, ERROR_MESSAGES["api_error"])
                return

            # Mesajı formatla
            formatted_message = format_price_message(coin_id, price_data, coin_input)
            bot.send_message(message.chat.id, formatted_message, parse_mode="Markdown")
            
        except Exception as e:
            print(f"Fiyat komutu hatası: {e}")
            bot.send_message(message.chat.id, ERROR_MESSAGES["api_error"])

    @bot.message_handler(commands=['top10'])
    def top10_coins(message):
        """En büyük 10 cryptocurrency"""
        try:
            # 🔥 HABER SİSTEMİ: Kullanıcıyı otomatik kaydet
            add_active_user(message.from_user.id)
            
            bot.send_message(message.chat.id, "🔄 Top 10 yükleniyor...")
            
            url = f"{COINGECKO_BASE_URL}/coins/markets?vs_currency=usd&order=market_cap_desc&per_page=10&page=1"
            response = requests.get(url, timeout=COINGECKO_TIMEOUT)
            
            if response.status_code != 200:
                bot.send_message(message.chat.id, ERROR_MESSAGES["api_error"])
                return
                
            coins = response.json()
            result_text = "🏆 **Top 10 Cryptocurrency:**\n\n"
            
            for i, coin in enumerate(coins, 1):
                name = coin['name']
                symbol = coin['symbol'].upper()
                price = coin['current_price']
                change_24h = coin.get('price_change_percentage_24h', 0)
                
                # Fiyat formatı
                if price < 0.01:
                    price_str = f"${price:.8f}"
                elif price < 1:
                    price_str = f"${price:.6f}"
                else:
                    price_str = f"${price:,.2f}"
                
                change_emoji = "📈" if change_24h > 0 else "📉"
                change_color = "🟢" if change_24h > 0 else "🔴"
                
                result_text += f"**{i}. {name}** ({symbol})\n"
                result_text += f"   💰 {price_str}\n"
                result_text += f"   📊 {change_color} %{change_24h:.2f} {change_emoji}\n\n"
                
            result_text += "💡 **Detay için:** /fiyat SYMBOL"
            bot.send_message(message.chat.id, result_text, parse_mode="Markdown")
            
        except Exception as e:
            print(f"Top 10 hatası: {e}")
            bot.send_message(message.chat.id, ERROR_MESSAGES["api_error"])

    @bot.message_handler(commands=['trending'])
    def trending_coins(message):
        """Trend olan coinler"""
        try:
            # 🔥 HABER SİSTEMİ: Kullanıcıyı otomatik kaydet
            add_active_user(message.from_user.id)
            
            bot.send_message(message.chat.id, "🔥 Trend coinler yükleniyor...")
            
            url = f"{COINGECKO_BASE_URL}/search/trending"
            response = requests.get(url, timeout=COINGECKO_TIMEOUT)
            
            if response.status_code != 200:
                bot.send_message(message.chat.id, ERROR_MESSAGES["api_error"])
                return
                
            data = response.json()
            trending = data.get('coins', [])[:7]
            
            if not trending:
                bot.send_message(message.chat.id, "❌ Trend verisi alınamadı!")
                return
                
            result_text = "🔥 **Trend Coinler:**\n\n"
            for i, item in enumerate(trending, 1):
                coin = item['item']
                name = coin['name']
                symbol = coin['symbol'].upper()
                rank = coin.get('market_cap_rank', 'N/A')
                
                result_text += f"**{i}. {name}** ({symbol})\n"
                result_text += f"   📊 Rank: #{rank}\n\n"
                
            result_text += "💡 **Fiyat için:** /fiyat SYMBOL"
            bot.send_message(message.chat.id, result_text, parse_mode="Markdown")
            
        except Exception as e:
            print(f"Trending hatası: {e}")
            bot.send_message(message.chat.id, ERROR_MESSAGES["api_error"])

# =============================================================================
# YARDIMCI FONKSİYONLAR
# =============================================================================

def search_coin_id(query):
    """CoinGecko'da coin ara"""
    try:
        search_url = f"{COINGECKO_BASE_URL}/search?query={query}"
        response = requests.get(search_url, timeout=COINGECKO_TIMEOUT)
        if response.status_code == 200:
            search_data = response.json()
            if search_data.get('coins'):
                return search_data['coins'][0]['id']
    except:
        pass
    return None

def get_coin_price(coin_id):
    """Coin fiyat bilgilerini al"""
    try:
        url = f"{COINGECKO_BASE_URL}/simple/price?ids={coin_id}&vs_currencies=usd&include_24hr_change=true&include_24hr_vol=true&include_market_cap=true"
        response = requests.get(url, timeout=COINGECKO_TIMEOUT)
        
        if response.status_code == 200:
            data = response.json()
            if coin_id in data:
                return data[coin_id]
    except:
        pass
    return None

def format_price_message(coin_id, price_data, coin_input):
    """Fiyat mesajını formatla"""
    price = price_data['usd']
    change_24h = price_data.get('usd_24h_change', 0)
    volume_24h = price_data.get('usd_24h_vol', 0)
    market_cap = price_data.get('usd_market_cap', 0)
    
    change_emoji = "📈" if change_24h > 0 else "📉"
    change_color = "🟢" if change_24h > 0 else "🔴"
    
    # Fiyat formatı
    if price < 0.01:
        price_str = f"${price:.8f}"
    elif price < 1:
        price_str = f"${price:.6f}"
    else:
        price_str = f"${price:,.2f}"
        
    volume_str = f"${volume_24h:,.0f}" if volume_24h > 0 else "N/A"
    mcap_str = f"${market_cap:,.0f}" if market_cap > 0 else "N/A"
    
    coin_name = coin_id.replace('-', ' ').title()
    
    mesaj = f"{change_emoji} **{coin_name}**\n\n"
    mesaj += f"💰 **Fiyat:** {price_str}\n"
    mesaj += f"📊 **24s Değişim:** {change_color} %{change_24h:.2f}\n"
    mesaj += f"📈 **24s Hacim:** {volume_str}\n"
    mesaj += f"🏦 **Market Cap:** {mcap_str}\n\n"
    mesaj += "🚀 Sence nasıl ilerler?\n\n"
    mesaj += f"⏰ *Fiyat alarmı için:* /alarm {coin_input}"
    
    return mesaj

print("💰 Price commands yüklendi!")
