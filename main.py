"""
Crypto Telegram Bot - Main File
Ana bot dosyası - tüm komutları buradan yönetir
"""

import telebot
import threading
import time
from config import *

# Utils modüllerini import et
from utils.binance_api import load_all_binance_symbols, find_binance_symbol
from utils.technical_analysis import *
from utils.chart_generator import create_price_chart, create_simple_price_chart

# Komut modüllerini import et
from commands.price_commands import register_price_commands
from commands.alarm_commands import register_alarm_commands
from commands.analysis_commands import register_analysis_commands

# Bot'u başlat
bot = telebot.TeleBot(TELEGRAM_TOKEN)

# Komutları kaydet
register_price_commands(bot)
register_alarm_commands(bot)
register_analysis_commands(bot)

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
# TEMEL KOMUTLAR
# =============================================================================

@bot.message_handler(commands=['start'])
def start(message):
    if not should_respond_in_group(message):
        return
        
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row("/fiyat", "/top10")
    markup.row("/analiz", "/trending") 
    markup.row("/makro", "/breakout")
    markup.row("/korku", "/yardim")
    markup.row("/alarm", "/alarmlist")
    
    bot.send_message(message.chat.id, WELCOME_MESSAGE, 
                     reply_markup=markup, parse_mode="Markdown")

@bot.message_handler(commands=['yardim', 'help'])
def yardim(message):
    if not should_respond_in_group(message):
        return
        
    help_text = """🤖 **Kripto Bot Komutları:**

📊 **Ana Komutlar:**
- /fiyat COIN - Coin fiyatı + detaylar
- /top10 - En büyük 10 cryptocurrency
- /trending - Trend olan coinler
- /analiz COIN - Teknik analiz + grafik

🔍 **Arama:**
- /coinara COIN - Coin arama

🌐 **Makro & Piyasa:**
- /makro - Makroekonomik analiz
- /breakout - Breakout adayı coinler

⚡ **Alarm Sistemi:**
- /alarm COIN - Fiyat alarmı kur
- /alarmlist - Aktif alarmları göster
- /alarmstop COIN - Alarm kaldır

⚡ **Diğer:**
- /korku - Fear & Greed Index

💡 **Örnek Kullanım:**
- /fiyat btc
- /analiz ethereum
- /alarm sol

🚀 **400+ coin destekleniyor!**"""
    
    bot.send_message(message.chat.id, help_text, parse_mode="Markdown")

# =============================================================================
# TEST KOMUTLARI
# =============================================================================

@bot.message_handler(commands=['test'])
def test_bot(message):
    """Bot çalışıyor mu test et"""
    if not should_respond_in_group(message):
        return
    
    bot.send_message(message.chat.id, 
                     "✅ **Bot çalışıyor!**\n\n"
                     f"🤖 Bot adı: @{bot_username}\n"
                     f"💬 Chat ID: {message.chat.id}\n"
                     f"👤 Kullanıcı: {message.from_user.first_name}\n\n"
                     f"📊 **Çalışan özellikler:**\n"
                     f"• Fiyat sorgulama ✅\n"
                     f"• Teknik analiz ✅\n"
                     f"• Fiyat alarmları ✅\n"
                     f"• Grafik oluşturma ✅",
                     parse_mode="Markdown")

@bot.message_handler(commands=['ping'])
def ping(message):
    """Ping-Pong testi"""
    if not should_respond_in_group(message):
        return
    
    bot.send_message(message.chat.id, "🏓 **PONG!** Bot aktif! 🚀")

# =============================================================================
# PLACEHOLDER KOMUTLAR (HENÜZ GELİŞTİRİLMEDİ)
# =============================================================================

@bot.message_handler(commands=['makro'])
def makro_placeholder(message):
    bot.send_message(message.chat.id, 
                     "🌐 **Makro analiz geliştirilme aşamasında!**\n\n"
                     "📊 Gelecek özellikler:\n"
                     "• DXY, S&P 500, VIX\n"
                     "• BTC-SPX korelasyonu\n"
                     "• Fed faiz oranları\n\n"
                     "💡 Şimdilik: /analiz COIN komutunu kullan!")

@bot.message_handler(commands=['coinara'])
def coinara_placeholder(message):
    bot.send_message(message.chat.id, 
                     "🔍 **Coin arama geliştirilme aşamasında!**\n\n"
                     "💡 Şimdilik: /fiyat COIN komutunu dene!")

# =============================================================================
# GENEL MESAJ HANDLERİ
# =============================================================================

@bot.message_handler(func=lambda message: True)
def echo_all(message):
    """Tüm diğer mesajlar için genel handler"""
    if not should_respond_in_group(message):
        return
    
    text = message.text.lower() if message.text else ""
    
    # Selamlaşma
    if any(word in text for word in ['merhaba', 'selam', 'hello', 'hi']):
        greetings = [
            "🚀 Selam! Hangi coin analiz edelim?",
            "👋 Hey! Crypto dünyasında neler var?",
            "😄 Merhaba! Ben senin kripto asistanın! 🤖"
        ]
        response = greetings[hash(text) % len(greetings)]
        bot.send_message(message.chat.id, response)
    
    # Yardım isteği
    elif any(word in text for word in ['yardım', 'help', 'komut']):
        bot.send_message(message.chat.id, 
                         "🆘 **Yardım için:** /yardim\n"
                         "📊 **Fiyat için:** /fiyat COIN\n"
                         "📈 **Analiz için:** /analiz COIN\n"
                         "⏰ **Alarm için:** /alarm COIN\n"
                         "🏓 **Test için:** /ping")
    
    # Coin soruları (basit AI)
    elif any(word in text for word in ['btc', 'bitcoin', 'eth', 'ethereum']):
        coin_mentioned = None
        if 'btc' in text or 'bitcoin' in text:
            coin_mentioned = 'btc'
        elif 'eth' in text or 'ethereum' in text:
            coin_mentioned = 'eth'
        
        if coin_mentioned:
            bot.send_message(message.chat.id, 
                             f"🎯 **{coin_mentioned.upper()}** hakkında konuşuyoruz!\n\n"
                             f"📊 **Fiyat:** /fiyat {coin_mentioned}\n"
                             f"📈 **Analiz:** /analiz {coin_mentioned}\n"
                             f"⏰ **Alarm:** /alarm {coin_mentioned}")
    
    # Diğer durumlarda
    else:
        bot.send_message(message.chat.id, 
                         "🤔 Ne yapmak istiyorsun?\n\n"
                         "📝 **Popüler komutlar:**\n"
                         "• /fiyat btc - Bitcoin fiyatı\n"
                         "• /analiz eth - Ethereum analizi\n"
                         "• /alarm sol - Solana alarmı\n"
                         "• /top10 - En büyük coinler\n"
                         "• /yardim - Tüm komutlar")

# =============================================================================
# BOT BAŞLATMA
# =============================================================================

def main():
    """Ana bot fonksiyonu"""
    # Binance coin listesini yükle
    print("🔄 Binance coin listesi yükleniyor...")
    load_all_binance_symbols()
    
    print("🚀 Kripto Bot başlatılıyor...")
    print(f"🤖 Bot kullanıcı adı: @{bot_username}")
    print("📱 Telegram'da kullanmaya başlayabilirsin!")
    print("🎯 Tam özellikli versiyon - Tüm komutlar aktif!")
    
    print("\n✅ **Aktif özellikler:**")
    print("• Fiyat sorgulama (/fiyat)")
    print("• Top 10 listesi (/top10)")
    print("• Trend coinler (/trending)")
    print("• Teknik analiz (/analiz)")
    print("• Breakout analizi (/breakout)")
    print("• Fear & Greed Index (/korku)")
    print("• Fiyat alarmları (/alarm)")
    print("• Alarm yönetimi (/alarmlist, /alarmstop)")
    print("• Grafik oluşturma")
    print("• Grup chat desteği")
    
    print("\n🔄 **Geliştiriliyor:**")
    print("• Makroekonomik analiz (/makro)")
    print("• Coin arama (/coinara)")
    print("• Portfolio takibi")
    
    # Bot'u başlat
    while True:
        try:
            print("\n🟢 Bot çalışıyor ve komutları bekliyor...")
            bot.polling(none_stop=True, interval=0, timeout=20)
        except Exception as e:
            print(f"❌ Bot hatası: {e}")
            print("🔄 5 saniye sonra yeniden başlatılıyor...")
            time.sleep(5)
            continue

if __name__ == "__main__":
    main()
