"""
Crypto Telegram Bot - Clean Main File
Temizlenmiş ve sadeleştirilmiş ana bot dosyası
"""

import telebot
import threading
import time
from config import *

# Utils modüllerini import et
from utils.binance_api import load_all_binance_symbols, find_binance_symbol
from utils.technical_analysis import *
from utils.chart_generator import create_advanced_chart

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
# TEMEL KOMUTLAR - TEMİZLENMİŞ
# =============================================================================

@bot.message_handler(commands=['start'])
def start(message):
    if not should_respond_in_group(message):
        return
        
    # Basitleştirilmiş klavye menüsü
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row("/analiz", "/fiyat")
    markup.row("/alarm", "/top10")
    markup.row("/yardim", "/ping")
    
    start_message = """🚀 **Kripto Bot'a Hoş Geldin!**

💡 **En Popüler Komutlar:**
📊 /analiz COIN - Teknik analiz + AI yorumu
💰 /fiyat COIN - Güncel fiyat bilgisi
⏰ /alarm COIN - Fiyat alarmı kur

🎯 **Örnek kullanım:**
• /analiz btc (sonra timeframe seç)
• /fiyat eth
• /alarm sol

📋 Tüm komutlar için: /yardim"""
    
    bot.send_message(message.chat.id, start_message, 
                     reply_markup=markup, parse_mode="Markdown")

@bot.message_handler(commands=['yardim', 'help'])
def yardim(message):
    if not should_respond_in_group(message):
        return
        
    help_text = """📊 **Kripto Bot Komutları**

💰 **Temel Komutlar:**
• /fiyat COIN - Fiyat bilgisi
• /top10 - En büyük 10 cryptocurrency
• /analiz COIN - Teknik analiz (timeframe seçimi)

⏰ **Alarm Sistemi:**
• /alarm COIN - Fiyat alarmı kur
• /alarmlist - Aktif alarmları göster
• /alarmstop COIN - Alarm sil

🔧 **Diğer:**
• /ping - Bot çalışıyor mu test et
• /yardim - Bu yardım menüsü

💡 **Örnek Kullanım:**
• /analiz btc → Timeframe butonları çıkar → Seç
• /fiyat eth → Ethereum fiyat bilgisi
• /alarm sol → Solana için alarm kur

🚀 **Yeni Özellikler:**
✅ AI yorumu her analizde otomatik
✅ Fibonacci seviyeleri dahil
✅ Trading önerileri
✅ Destek/Direnç seviyeleri

⚠️ Bu bot yatırım tavsiyesi vermez!"""
    
    bot.send_message(message.chat.id, help_text, parse_mode="Markdown")

# =============================================================================
# TEST KOMUTLARI - SADECE GEREKLİLER
# =============================================================================

@bot.message_handler(commands=['test'])
def test_bot(message):
    """Bot çalışıyor mu test et"""
    if not should_respond_in_group(message):
        return
    
    bot.send_message(message.chat.id, 
                     "✅ **Bot Çalışıyor!**\n\n"
                     f"🤖 Bot: @{bot_username}\n"
                     f"💬 Chat ID: {message.chat.id}\n"
                     f"👤 Kullanıcı: {message.from_user.first_name}\n\n"
                     f"🚀 **Ana komut:** /analiz btc",
                     parse_mode="Markdown")

@bot.message_handler(commands=['ping'])
def ping(message):
    """Ping-Pong testi"""
    if not should_respond_in_group(message):
        return
    
    bot.send_message(message.chat.id, "🏓 **PONG!** Bot aktif! 🚀")

@bot.message_handler(commands=['status'])
def bot_status(message):
    """Bot durumu ve istatistikleri"""
    if not should_respond_in_group(message):
        return
    
    try:
        from utils.binance_api import BINANCE_SYMBOLS
        
        status_text = f"📊 **Bot Durumu:**\n\n"
        status_text += f"🤖 **Bot:** @{bot_username}\n"
        status_text += f"📈 **Desteklenen coinler:** {len(BINANCE_SYMBOLS)} adet\n"
        status_text += f"🎯 **AI Analiz:** {'✅ Aktif' if OPENAI_API_KEY and OPENAI_API_KEY != 'BURAYA_OPENAI_KEYINI_YAZ' else '❌ API key gerekli'}\n"
        status_text += f"⏰ **Alarm sistemi:** ✅ Aktif\n\n"
        
        status_text += f"🔥 **Aktif Özellikler:**\n"
        status_text += f"• Teknik analiz + AI yorumu\n"
        status_text += f"• Fibonacci seviyeleri dahil\n"
        status_text += f"• Trading önerileri\n"
        status_text += f"• Fiyat alarm sistemi\n\n"
        
        status_text += f"🎯 **En popüler:** /analiz btc"
        
        bot.send_message(message.chat.id, status_text, parse_mode="Markdown")
        
    except Exception as e:
        print(f"Status komutu hatası: {e}")
        bot.send_message(message.chat.id, "✅ Bot çalışıyor!")

# =============================================================================
# HIZLI KOMUTLAR - SADELEŞTİRİLMİŞ
# =============================================================================

@bot.message_handler(commands=['btc', 'bitcoin'])
def quick_btc(message):
    """Hızlı Bitcoin menüsü"""
    if not should_respond_in_group(message):
        return
    
    bot.send_message(message.chat.id, 
                     "⚡ **Bitcoin Hızlı Menü:**\n\n"
                     "📊 /analiz btc - Teknik analiz\n"
                     "💰 /fiyat btc - Fiyat bilgisi\n"
                     "⏰ /alarm btc - Fiyat alarmı")

@bot.message_handler(commands=['eth', 'ethereum'])
def quick_eth(message):
    """Hızlı Ethereum menüsü"""
    if not should_respond_in_group(message):
        return
    
    bot.send_message(message.chat.id, 
                     "⚡ **Ethereum Hızlı Menü:**\n\n"
                     "📊 /analiz eth - Teknik analiz\n"
                     "💰 /fiyat eth - Fiyat bilgisi\n"
                     "⏰ /alarm eth - Fiyat alarmı")

# =============================================================================
# GENEL MESAJ HANDLERİ - SADELEŞTİRİLMİŞ
# =============================================================================

@bot.message_handler(func=lambda message: True)
def echo_all(message):
    """Sadeleştirilmiş genel mesaj handler"""
    if not should_respond_in_group(message):
        return
    
    text = message.text.lower() if message.text else ""
    
    # Selamlaşma
    if any(word in text for word in ['merhaba', 'selam', 'hello', 'hi', 'hey']):
        greetings = [
            "🚀 Selam! /analiz btc ile Bitcoin analizi yap!",
            "👋 Hey! Hangi coin'i analiz edelim? /analiz COIN",
            "😄 Merhaba! Yeni AI analiz sistemi için /analiz dene!",
            "🤖 Selam! /yardim ile tüm komutları gör!"
        ]
        response = greetings[hash(text) % len(greetings)]
        bot.send_message(message.chat.id, response)
    
    # Yardım isteği
    elif any(word in text for word in ['yardım', 'help', 'komut', 'nasıl']):
        bot.send_message(message.chat.id, 
                         "🆘 **Hızlı Yardım:**\n\n"
                         "📊 **Ana komut:** /analiz COIN\n"
                         "💰 **Fiyat:** /fiyat COIN\n"
                         "⏰ **Alarm:** /alarm COIN\n"
                         "📋 **Tümü:** /yardim\n\n"
                         "💡 **Örnek:** /analiz btc")
    
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
                             f"📊 /analiz {coin_mentioned} - Teknik analiz\n"
                             f"💰 /fiyat {coin_mentioned} - Fiyat bilgisi\n"
                             f"⏰ /alarm {coin_mentioned} - Fiyat alarmı\n\n"
                             f"Hangisini istiyorsun?")
        else:
            bot.send_message(message.chat.id, 
                             "🎯 **Coin analizi için:**\n\n"
                             "📊 /analiz btc (Bitcoin analizi)\n"
                             "📊 /analiz eth (Ethereum analizi)\n"
                             "💰 /fiyat COIN (fiyat bilgisi)")
    
    # Trading soruları
    elif any(word in text for word in ['al', 'sat', 'buy', 'sell', 'trade', 'analiz']):
        bot.send_message(message.chat.id, 
                         "🎯 **Analiz için:**\n\n"
                         "📊 /analiz btc - Bitcoin analizi\n"
                         "📊 /analiz eth - Ethereum analizi\n"
                         "💡 Her analizde AI yorumu + trading önerisi\n\n"
                         "⚠️ Yatırım tavsiyesi değildir!")
    
    # Diğer durumlarda
    else:
        bot.send_message(message.chat.id, 
                         "🤔 **Ne yapmak istiyorsun?**\n\n"
                         "🔥 **Popüler:**\n"
                         "📊 /analiz btc - Bitcoin analizi\n"
                         "💰 /fiyat eth - Ethereum fiyatı\n"
                         "⏰ /alarm sol - Solana alarmı\n\n"
                         "📋 **Tüm komutlar:** /yardim")

# =============================================================================
# BOT BAŞLATMA - TEMİZLENMİŞ
# =============================================================================

def main():
    """Ana bot fonksiyonu - temizlenmiş versiyon"""
    
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
    
    print("🚀 Temizlenmiş Kripto Bot başlatılıyor...")
    print(f"🤖 Bot kullanıcı adı: @{bot_username}")
    print("📱 Telegram'da kullanmaya başlayabilirsin!")
    print("🎯 CLEAN VERSION - Sadece gerekli özellikler!")
    
    print(f"\n✅ **AKTİF ÖZELLİKLER:**")
    print("• Fiyat sorgulama (/fiyat)")
    print("• Top 10 listesi (/top10)")
    print("• Teknik analiz + AI yorumu (/analiz)")
    print("• Fiyat alarmları (/alarm, /alarmlist, /alarmstop)")
    print("• Destek/Direnç + Fibonacci dahil")
    print("• Trading önerileri")
    print("• Grup chat desteği")
    print("• Temiz ve sade arayüz")
    
    print(f"\n🤖 **AI Durumu:** {ai_status}")
    
    print(f"\n🎯 **ÖRNEK KOMUTLAR:**")
    print("• /analiz btc → Timeframe seç → Analiz al")
    print("• /fiyat eth → Ethereum fiyatı")
    print("• /alarm sol → Solana alarmı kur")
    print("• /top10 → En büyük 10 coin")
    
    # Bot'u başlat
    while True:
        try:
            print(f"\n🟢 Temizlenmiş bot çalışıyor ve komutları bekliyor...")
            print("📊 Sadeleştirilmiş ve kullanıcı dostu sistem hazır!")
            print("🎯 Ana komut: /analiz COIN")
            bot.polling(none_stop=True, interval=0, timeout=20)
        except Exception as e:
            print(f"❌ Bot hatası: {e}")
            print("🔄 5 saniye sonra yeniden başlatılıyor...")
            time.sleep(5)
            continue

if __name__ == "__main__":
    main()
