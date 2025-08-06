"""
Crypto Telegram Bot - Main File
Ana bot dosyası - tüm komutları buradan yönetir
"""

import telebot
import threading
import time
from config import *

# Komut modüllerini import et
from commands.price_commands import register_price_commands
from commands.alarm_commands import register_alarm_commands

# Bot'u başlat
bot = telebot.TeleBot(TELEGRAM_TOKEN)

# Komutları kaydet
register_price_commands(bot)
register_alarm_commands(bot)

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
# BASIT TEST KOMUTLARI
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
                     f"👤 Kullanıcı: {message.from_user.first_name}",
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

@bot.message_handler(commands=['analiz'])
def analiz_placeholder(message):
    bot.send_message(message.chat.id, 
                     "📈 **Analiz komutu geliştirilme aşamasında!**\n\n"
                     "🎯 Gelecek özellikler:\n"
                     "• RSI, MACD, Bollinger Bands\n"
                     "• Grafik oluşturma\n"
                     "• Destek/Direnç analizi\n\n"
                     "💰 Şimdilik: /fiyat COIN komutunu kullan!")

@bot.message_handler(commands=['makro'])
def makro_placeholder(message):
    bot.send_message(message.chat.id, 
                     "🌐 **Makro analiz geliştirilme aşamasında!**\n\n"
                     "📊 Gelecek özellikler:\n"
                     "• DXY, S&P 500, VIX\n"
                     "• BTC-SPX korelasyonu\n"
                     "• Fed faiz oranları")

@bot.message_handler(commands=['breakout'])
def breakout_placeholder(message):
    bot.send_message(message.chat.id, 
                     "🔥 **Breakout analizi geliştirilme aşamasında!**\n\n"
                     "🎯 Gelecek özellikler:\n"
                     "• Breakout adayı coinler\n"
                     "• Teknik skorlama\n"
                     "• Volume analizi")

@bot.message_handler(commands=['korku'])
def korku_placeholder(message):
    bot.send_message(message.chat.id, 
                     "😱 **Fear & Greed Index geliştirilme aşamasında!**\n\n"
                     "📊 Yakında:\n"
                     "• Günlük korku endeksi\n"
                     "• Piyasa sentiment analizi")

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
                         "⏰ **Alarm için:** /alarm COIN\n"
                         "🏓 **Test için:** /ping")
    
    # Diğer durumlarda
    else:
        bot.send_message(message.chat.id, 
                         "🤔 Henüz öğreniyorum!\n\n"
                         "📝 **Çalışan komutlar:**\n"
                         "• /start - Başlangıç\n"
                         "• /fiyat COIN - Fiyat bilgisi\n"
                         "• /top10 - En büyük 10 coin\n"
                         "• /alarm COIN - Fiyat alarmı\n"
                         "• /test - Bot testi\n"
                         "• /yardim - Tüm komutlar")

# =============================================================================
# BOT BAŞLATMA
# =============================================================================

def main():
    """Ana bot fonksiyonu"""
    print("🚀 Kripto Bot başlatılıyor...")
    print(f"🤖 Bot kullanıcı adı: @{bot_username}")
    print("📱 Telegram'da kullanmaya başlayabilirsin!")
    print("🔧 Geliştirme modu: Temel komutlar aktif")
    print("\n✅ **Çalışan özellikler:**")
    print("• Fiyat sorgulama (/fiyat)")
    print("• Top 10 listesi (/top10)")
    print("• Trend coinler (/trending)")
    print("• Fiyat alarmları (/alarm)")
    print("• Alarm yönetimi (/alarmlist, /alarmstop)")
    print("\n🔄 **Geliştiriliyor:**")
    print("• Teknik analiz grafikleri")
    print("• Makroekonomik analiz")
    print("• Breakout analizleri")
    
    # Bot'u başlat
    while True:
        try:
            print("🟢 Bot çalışıyor...")
            bot.polling(none_stop=True, interval=0, timeout=20)
        except Exception as e:
            print(f"❌ Bot hatası: {e}")
            print("🔄 5 saniye sonra yeniden başlatılıyor...")
            time.sleep(5)
            continue

if __name__ == "__main__":
    main()
