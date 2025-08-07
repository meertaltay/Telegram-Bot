"""
Crypto Telegram Bot - Main File (SIMPLIFIED VERSION)
Ana bot dosyası - sadeleştirilmiş ve temiz versiyon
"""

import telebot
import threading
import time
from config import *

# Utils modüllerini import et
from utils.binance_api import load_all_binance_symbols, find_binance_symbol
from utils.technical_analysis import *
from utils.chart_generator import create_advanced_chart, create_simple_price_chart

# Komut modüllerini import et
from commands.price_commands import register_price_commands
from commands.alarm_commands import register_alarm_commands
from commands.analysis_commands import register_analysis_commands

# Likidite haritası modülü
from utils.liquidity_heatmap import add_liquidity_command_to_bot

# Bot'u başlat
bot = telebot.TeleBot(TELEGRAM_TOKEN)

# Komutları kaydet
register_price_commands(bot)
register_alarm_commands(bot)
register_analysis_commands(bot)

# Likidite komutlarını kaydet
add_liquidity_command_to_bot(bot)

# Global değişkenler
bot_info = bot.get_me()
bot_username = bot_info.username
print(f"🤖 Bot adı: @{bot_username}")

# =============================================================================
# YARDIMCI FONKSİYONLAR
# =============================================================================

def is_group_chat(message):
    """Mesajın grup sohbetinden gelip gelmediğini kontrol et"""
    return message.chat.type in ['group', 'supergroup']

def should_respond_in_group(message):
    """Grupta cevap verilip verilmeyeceğini kontrol et"""
    if not is_group_chat(message):
        return True  # Özel sohbetlerde her zaman cevap ver
    
    # Bot komutları her zaman çalışır
    if message.text and message.text.startswith('/'):
        return True
    
    # Bot taglenmiş mi kontrol et
    if message.text and f"@{bot_username}" in message.text:
        return True
    
    # Reply yapılmış mı kontrol et
    if message.reply_to_message and message.reply_to_message.from_user.id == bot.get_me().id:
        return True
    
    return False

# =============================================================================
# TEMEL KOMUTLAR - SADELEŞTİRİLMİŞ
# =============================================================================

@bot.message_handler(commands=['start'])
def start(message):
    if not should_respond_in_group(message):
        return
        
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row("/fiyat", "/analiz")
    markup.row("/likidite", "/alarm") 
    markup.row("/top10", "/trending")
    markup.row("/korku", "/yardim")
    
    bot.send_message(message.chat.id, WELCOME_MESSAGE, 
                     reply_markup=markup, parse_mode="Markdown")

@bot.message_handler(commands=['yardim', 'help'])
def yardim(message):
    if not should_respond_in_group(message):
        return
        
    help_text = """🤖 **Kripto Bot Komutları:**

📊 **Temel Komutlar:**
- /fiyat COIN - Coin fiyatı (örn: /fiyat btc)
- /top10 - En büyük 10 coin
- /trending - Trend coinler

📈 **Analiz:**
- /analiz COIN - Teknik analiz (örn: /analiz eth)
- /likidite COIN - Likidite haritası

⏰ **Alarm Sistemi:**
- /alarm COIN - Fiyat alarmı kur
- /alarmlist - Aktif alarmlarım
- /alarmstop COIN - Alarm kaldır

🌐 **Piyasa:**
- /korku - Fear & Greed Index

🔧 **Diğer:**
- /test - Bot durumu
- /ping - Bağlantı testi

💡 **Örnekler:**
- /fiyat btc
- /analiz eth
- /likidite sol
- /alarm doge

🚀 **500+ coin destekleniyor!**"""
    
    bot.send_message(message.chat.id, help_text, parse_mode="Markdown")

# =============================================================================
# TEST KOMUTLARI - BASİTLEŞTİRİLMİŞ
# =============================================================================

@bot.message_handler(commands=['test'])
def test_bot(message):
    """Bot çalışıyor mu test et"""
    if not should_respond_in_group(message):
        return
    
    bot.send_message(message.chat.id, 
                     "✅ **Bot Çalışıyor!**\n\n"
                     f"🤖 Bot adı: @{bot_username}\n"
                     f"💬 Chat ID: {message.chat.id}\n"
                     f"👤 Kullanıcı: {message.from_user.first_name}\n\n"
                     f"🚀 **Aktif Özellikler:**\n"
                     f"• Fiyat sorgulama ✅\n"
                     f"• Teknik analiz ✅\n"
                     f"• Likidite haritası ✅\n"
                     f"• Alarm sistemi ✅\n\n"
                     f"🎯 **Test komutları:**\n"
                     f"• /fiyat btc\n"
                     f"• /analiz eth\n"
                     f"• /likidite sol",
                     parse_mode="Markdown")

@bot.message_handler(commands=['ping'])
def ping(message):
    """Ping-Pong testi"""
    if not should_respond_in_group(message):
        return
    
    bot.send_message(message.chat.id, "🏓 **PONG!** Bot aktif! ✅")

# =============================================================================
# KORKU İNDEKSİ KOMUTU
# =============================================================================

@bot.message_handler(commands=['korku'])
def fear_greed_index(message):
    """Fear & Greed Index göster"""
    if not should_respond_in_group(message):
        return
    
    try:
        import requests
        
        bot.send_message(message.chat.id, "📊 Fear & Greed Index yükleniyor...")
        
        url = "https://api.alternative.me/fng/"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data['data']:
                fng_data = data['data'][0]
                value = int(fng_data['value'])
                classification = fng_data['value_classification']
                
                # Emoji ve renk belirle
                if value <= 20:
                    emoji = "😱"
                    color = "🔴"
                elif value <= 40:
                    emoji = "😰"
                    color = "🟠"
                elif value <= 60:
                    emoji = "😐"
                    color = "🟡"
                elif value <= 80:
                    emoji = "🤑"
                    color = "🟢"
                else:
                    emoji = "🚀"
                    color = "🟢"
                
                # Piyasa yorumu
                if value <= 25:
                    market_comment = "**Aşırı Korku** - Alım fırsatı olabilir"
                elif value <= 45:
                    market_comment = "**Korku** - Temkinli yaklaşım"
                elif value <= 55:
                    market_comment = "**Nötr** - Dengeli piyasa"
                elif value <= 75:
                    market_comment = "**Açgözlülük** - Dikkatli olun"
                else:
                    market_comment = "**Aşırı Açgözlülük** - Risk yüksek"
                
                result_text = f"📊 **Fear & Greed Index**\n\n"
                result_text += f"{color} **{value}/100** {emoji}\n"
                result_text += f"📈 **Durum:** {classification.title()}\n\n"
                result_text += f"💡 **Yorum:** {market_comment}\n\n"
                result_text += f"🔄 *Son güncelleme: {fng_data['timestamp'][:10]}*"
                
                bot.send_message(message.chat.id, result_text, parse_mode="Markdown")
            else:
                bot.send_message(message.chat.id, "❌ Fear & Greed verisi alınamadı!")
        else:
            bot.send_message(message.chat.id, ERROR_MESSAGES["api_error"])
            
    except Exception as e:
        print(f"Fear & Greed hatası: {e}")
        bot.send_message(message.chat.id, ERROR_MESSAGES["api_error"])

# =============================================================================
# GENEL MESAJ HANDLERİ - BASİTLEŞTİRİLMİŞ
# =============================================================================

@bot.message_handler(func=lambda message: True)
def echo_all(message):
    """Basitleştirilmiş genel mesaj handler"""
    if not should_respond_in_group(message):
        return
    
    text = message.text.lower() if message.text else ""
    
    # Selamlaşma
    if any(word in text for word in ['merhaba', 'selam', 'hello', 'hi', 'hey']):
        greetings = [
            "👋 Selam! Hangi coin'i analiz edelim?",
            "🚀 Hey! /fiyat btc ile başla!",
            "😄 Merhaba! /analiz eth dene!",
            "🎯 Selam! /likidite sol ile likidite haritası gör!"
        ]
        response = greetings[hash(text) % len(greetings)]
        bot.send_message(message.chat.id, response)
    
    # Yardım isteği
    elif any(word in text for word in ['yardım', 'help', 'komut', 'nasıl']):
        bot.send_message(message.chat.id, 
                         "🆘 **Komutlar için:** /yardim\n\n"
                         "🔥 **Popüler:**\n"
                         "• /fiyat btc - Bitcoin fiyatı\n"
                         "• /analiz eth - Ethereum analizi\n"  
                         "• /likidite sol - Solana likidite\n"
                         "• /alarm doge - Dogecoin alarmı")
    
    # Coin soruları 
    elif any(word in text for word in ['btc', 'bitcoin', 'eth', 'ethereum', 'sol', 'solana']):
        coin_mentioned = None
        if any(word in text for word in ['btc', 'bitcoin']):
            coin_mentioned = 'btc'
        elif any(word in text for word in ['eth', 'ethereum']):
            coin_mentioned = 'eth'
        elif any(word in text for word in ['sol', 'solana']):
            coin_mentioned = 'sol'
        
        if coin_mentioned:
            bot.send_message(message.chat.id, 
                             f"🎯 **{coin_mentioned.upper()} için:**\n\n"
                             f"📊 /fiyat {coin_mentioned} - Fiyat bilgisi\n"
                             f"📈 /analiz {coin_mentioned} - Teknik analiz\n"
                             f"💧 /likidite {coin_mentioned} - Likidite haritası\n"
                             f"⏰ /alarm {coin_mentioned} - Fiyat alarmı\n\n"
                             f"💡 Hangisini istiyorsun?")
    
    # Trading soruları
    elif any(word in text for word in ['al', 'sat', 'buy', 'sell', 'trade', 'sinyal', 'likidite']):
        bot.send_message(message.chat.id, 
                         "🎯 **Trading Araçları:**\n\n"
                         "💧 **Likidite haritası:** /likidite COIN\n"
                         "📈 **Teknik analiz:** /analiz COIN\n"
                         "📊 **Piyasa durumu:** /korku\n"
                         "📋 **En büyük coinler:** /top10\n\n"
                         "⚠️ **Risk uyarısı:** Bu analizler yatırım tavsiyesi değildir!")
    
    # Diğer durumlarda
    else:
        bot.send_message(message.chat.id, 
                         "🤔 **Ne yapmak istiyorsun?**\n\n"
                         "📊 /fiyat COIN - Fiyat bilgisi\n"
                         "📈 /analiz COIN - Teknik analiz\n"
                         "💧 /likidite COIN - Likidite haritası\n"
                         "⏰ /alarm COIN - Fiyat alarmı\n"
                         "📋 /yardim - Tüm komutlar\n\n"
                         "🏓 /ping - Bot testi")

# =============================================================================
# BOT BAŞLATMA - SADELEŞTİRİLMİŞ
# =============================================================================

def main():
    """Ana bot fonksiyonu - sadeleştirilmiş versiyon"""
    
    print("🔄 Sistem hazırlıkları...")
    
    # Binance coin listesini yükle
    print("📊 Binance coin listesi yükleniyor...")
    binance_success = load_all_binance_symbols()
    
    if binance_success:
        print("✅ Binance entegrasyonu başarılı!")
    else:
        print("⚠️ Binance yüklemede sorun var, temel coinler kullanılacak")
    
    # OpenAI kontrolü
    ai_status = "✅ Aktif" if OPENAI_API_KEY and OPENAI_API_KEY != "BURAYA_OPENAI_KEYINI_YAZ" else "❌ API key gerekli"
    
    print("🚀 Sadeleştirilmiş Kripto Bot başlatılıyor...")
    print(f"🤖 Bot kullanıcı adı: @{bot_username}")
    print("📱 Telegram'da kullanmaya başlayabilirsin!")
    
    print(f"\n✅ **AKTİF ÖZELLİKLER:**")
    print("• Fiyat sorgulama (/fiyat)")
    print("• Top 10 listesi (/top10)")
    print("• Trend coinler (/trending)")
    print("• Teknik analiz (/analiz)")
    print("• Likidite haritası (/likidite)")
    print("• Fear & Greed Index (/korku)")
    print("• Fiyat alarmları (/alarm)")
    print("• Alarm yönetimi (/alarmlist, /alarmstop)")
    print("• Grup chat desteği")
    
    print(f"\n🤖 **AI DESTEĞİ:** {ai_status}")
    
    print(f"\n🎯 **ÖRNEK KOMUTLAR:**")
    print("• /fiyat btc")
    print("• /analiz eth")
    print("• /likidite sol")
    print("• /alarm doge")
    print("• /top10")
    print("• /korku")
    
    # Bot'u başlat
    while True:
        try:
            print(f"\n🟢 Sadeleştirilmiş Kripto Bot çalışıyor ve komutları bekliyor...")
            print("📊 500+ coin + Professional likidite haritası aktif!")
            print("🎯 Sade ve kullanıcı dostu komut yapısı!")
            bot.polling(none_stop=True, interval=0, timeout=20)
        except Exception as e:
            print(f"❌ Bot hatası: {e}")
            print("🔄 5 saniye sonra yeniden başlatılıyor...")
            time.sleep(5)
            continue

if __name__ == "__main__":
    main()
