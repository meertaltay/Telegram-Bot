"""
Crypto Telegram Bot - Main File
Ana bot dosyası - tüm komutları buradan yönetir
"""

import telebot
import threading
import time
from config import *

# Bot'u başlat
bot = telebot.TeleBot(TELEGRAM_TOKEN)

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
# BASIT TEST KOMUTLARI (ÇALIŞIYOR MU DİYE)
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
# PLACEHOLDER KOMUTLAR (SONRA GELİŞTİRECEĞİZ)
# =============================================================================

@bot.message_handler(commands=['fiyat'])
def fiyat_placeholder(message):
    bot.send_message(message.chat.id, 
                     "📊 **Fiyat komutu geliştirilme aşamasında!**\n\n"
                     "🔄 Yakında hazır olacak!\n"
                     "📝 Şimdilik: /test komutu ile bot'u test edebilirsin!")

@bot.message_handler(commands=['analiz'])
def analiz_placeholder(message):
    bot.send_message(message.chat.id, 
                     "📈 **Analiz komutu geliştirilme aşamasında!**\n\n"
                     "🎯 Gelecek özellikler:\n"
                     "• RSI, MACD, Bollinger Bands\n"
                     "• Grafik oluşturma\n"
                     "• Destek/Direnç analizi")

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
                         "📊 **Test için:** /test\n"
                         "🏓 **Ping için:** /ping")
    
    # Diğer durumlarda
    else:
        bot.send_message(message.chat.id, 
                         "🤔 Henüz geliştirilme aşamasındayım!\n\n"
                         "📝 **Çalışan komutlar:**\n"
                         "• /start - Başlangıç\n"
                         "• /test - Bot testi\n"
                         "• /ping - Ping testi\n"
                         "• /yardim - Komut listesi")

# =============================================================================
# BOT BAŞLATMA
# =============================================================================

def main():
    """Ana bot fonksiyonu"""
    print("🚀 Kripto Bot başlatılıyor...")
    print(f"🤖 Bot kullanıcı adı: @{bot_username}")
    print("📱 Telegram'da kullanmaya başlayabilirsin!")
    print("🔧 Geliştirme modu: Temel komutlar aktif")
    
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
