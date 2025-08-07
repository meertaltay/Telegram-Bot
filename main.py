"""
Crypto Telegram Bot - Main File (FINAL VERSION)
Ana bot dosyası - gelişmiş analiz sistemi ile
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
    markup.row("/breakout", "/signals")
    markup.row("/korku", "/predict")
    markup.row("/alarm", "/alarmlist")
    markup.row("/yardim")
    
    bot.send_message(message.chat.id, WELCOME_MESSAGE, 
                     reply_markup=markup, parse_mode="Markdown")

@bot.message_handler(commands=['yardim', 'help'])
def yardim(message):
    if not should_respond_in_group(message):
        return
        
    help_text = """🤖 **Gelişmiş Kripto Bot Komutları:**

📊 **Ana Komutlar:**
- /fiyat COIN - Coin fiyatı + detaylar
- /top10 - En büyük 10 cryptocurrency
- /trending - Trend olan coinler

📈 **Gelişmiş Analiz:**
- /analiz COIN - Temel analiz (1d)
- /analiz COIN 4h - Timeframe analizi
- /analiz COIN multi - Çoklu timeframe
- /analiz COIN ai - AI ile analiz
- /analiz COIN fib - Fibonacci seviyeleri

🎯 **Trading Sinyalleri:**
- /signals COIN - Güçlü trading sinyalleri
- /breakout - Breakout adayları (gelişmiş)
- /predict COIN - AI fiyat tahmini

⚡ **Alarm Sistemi:**
- /alarm COIN - Fiyat alarmı kur
- /alarmlist - Aktif alarmları göster
- /alarmstop COIN - Alarm kaldır

🌐 **Piyasa Analizi:**
- /korku - Fear & Greed Index

💡 **Örnek Kullanım:**
- /analiz btc 4h
- /signals eth
- /predict sol 7
- /alarm ada

🚀 **400+ coin + AI analiz sistemi!**"""
    
    bot.send_message(message.chat.id, help_text, parse_mode="Markdown")

# =============================================================================
# GELIŞMIŞ TEST KOMUTLARI
# =============================================================================

@bot.message_handler(commands=['test'])
def test_bot(message):
    """Bot çalışıyor mu test et"""
    if not should_respond_in_group(message):
        return
    
    bot.send_message(message.chat.id, 
                     "✅ **Gelişmiş Bot Çalışıyor!**\n\n"
                     f"🤖 Bot adı: @{bot_username}\n"
                     f"💬 Chat ID: {message.chat.id}\n"
                     f"👤 Kullanıcı: {message.from_user.first_name}\n\n"
                     f"🚀 **Yeni Özellikler:**\n"
                     f"• Çoklu timeframe analizi ✅\n"
                     f"• AI fiyat tahmini ✅\n"
                     f"• Gelişmiş indikatörler ✅\n"
                     f"• Sinyal gücü sistemi ✅\n"
                     f"• Entry/Exit noktaları ✅\n"
                     f"• Risk analizi ✅\n\n"
                     f"🎯 **Test komutları:**\n"
                     f"• /analiz btc multi\n"
                     f"• /signals eth\n"
                     f"• /predict sol",
                     parse_mode="Markdown")

@bot.message_handler(commands=['ping'])
def ping(message):
    """Ping-Pong testi"""
    if not should_respond_in_group(message):
        return
    
    bot.send_message(message.chat.id, "🏓 **PONG!** Gelişmiş bot aktif! 🚀⚡")

@bot.message_handler(commands=['status'])
def bot_status(message):
    """Bot durumu ve istatistikleri"""
    if not should_respond_in_group(message):
        return
    
    try:
        # Basit istatistikler
        from utils.binance_api import BINANCE_SYMBOLS
        
        status_text = f"📊 **Bot Durumu:**\n\n"
        status_text += f"🤖 **Bot:** @{bot_username}\n"
        status_text += f"📈 **Desteklenen coinler:** {len(BINANCE_SYMBOLS)} adet\n"
        status_text += f"🎯 **AI Analiz:** {'✅ Aktif' if OPENAI_API_KEY and OPENAI_API_KEY != 'BURAYA_OPENAI_KEYINI_YAZ' else '❌ API key gerekli'}\n"
        status_text += f"⏰ **Alarm sistemi:** ✅ Aktif\n"
        status_text += f"📊 **Gelişmiş analiz:** ✅ Aktif\n\n"
        
        status_text += f"🔥 **Son güncellemeler:**\n"
        status_text += f"• Çoklu timeframe analizi\n"
        status_text += f"• AI ile fiyat tahmini\n"
        status_text += f"• Fibonacci retracement\n"
        status_text += f"• Gelişmiş sinyal sistemi\n"
        status_text += f"• Risk yönetimi araçları\n\n"
        
        status_text += f"🎯 **En popüler komutlar:**\n"
        status_text += f"• /analiz btc multi\n"
        status_text += f"• /signals eth\n"
        status_text += f"• /predict sol 7"
        
        bot.send_message(message.chat.id, status_text, parse_mode="Markdown")
        
    except Exception as e:
        print(f"Status komutu hatası: {e}")
        bot.send_message(message.chat.id, "✅ Bot çalışıyor ama istatistik alınamadı!")

# =============================================================================
# HİZLI KOMUTLAR (SHORTCUTS)
# =============================================================================

@bot.message_handler(commands=['btc', 'bitcoin'])
def quick_btc(message):
    """Hızlı Bitcoin analizi"""
    if not should_respond_in_group(message):
        return
    
    bot.send_message(message.chat.id, 
                     "⚡ **Hızlı Bitcoin Menüsü:**\n\n"
                     "📊 /fiyat btc - Fiyat bilgisi\n"
                     "📈 /analiz btc - Teknik analiz\n"
                     "🎯 /signals btc - Trading sinyalleri\n"
                     "🤖 /predict btc - AI tahmini\n"
                     "⏰ /alarm btc - Fiyat alarmı\n\n"
                     "🚀 Hangisini istiyorsun?")

@bot.message_handler(commands=['eth', 'ethereum'])
def quick_eth(message):
    """Hızlı Ethereum analizi"""
    if not should_respond_in_group(message):
        return
    
    bot.send_message(message.chat.id, 
                     "⚡ **Hızlı Ethereum Menüsü:**\n\n"
                     "📊 /fiyat eth - Fiyat bilgisi\n"
                     "📈 /analiz eth multi - Çoklu timeframe\n"
                     "🎯 /signals eth - Trading sinyalleri\n"
                     "🤖 /predict eth 7 - 7 günlük tahmin\n"
                     "⏰ /alarm eth - Fiyat alarmı\n\n"
                     "🔥 Hangisini seçiyorsun?")

# =============================================================================
# PLACEHOLDER KOMUTLAR (GELECEKTEKİ ÖZELLİKLER)
# =============================================================================

@bot.message_handler(commands=['makro'])
def makro_placeholder(message):
    bot.send_message(message.chat.id, 
                     "🌐 **Makro analiz sonraki güncellemede!**\n\n"
                     "📊 Gelecek özellikler:\n"
                     "• DXY, S&P 500, VIX analizi\n"
                     "• BTC-SPX korelasyonu\n"
                     "• Fed faiz oranları etkisi\n"
                     "• Makro sentiment analizi\n\n"
                     "💡 Şimdilik: /analiz COIN multi komutunu kullan!\n"
                     "🤖 AI analiz: /analiz COIN ai")

@bot.message_handler(commands=['portfolio'])
def portfolio_placeholder(message):
    bot.send_message(message.chat.id, 
                     "💼 **Portfolio takibi geliştiriliyor!**\n\n"
                     "🎯 Gelecek özellikler:\n"
                     "• Kişisel portfolio girişi\n"
                     "• Kar/zarar takibi\n"
                     "• Portfolio alarmları\n"
                     "• Risk analizi\n"
                     "• Performans raporları\n\n"
                     "⏰ Şimdilik: /alarm sistemi ile takip yap!")

@bot.message_handler(commands=['news'])
def news_placeholder(message):
    bot.send_message(message.chat.id, 
                     "📰 **Kripto haberleri yakında!**\n\n"
                     "🔥 Gelecek özellikler:\n"
                     "• Güncel kripto haberleri\n"
                     "• Sentiment analizi\n"
                     "• Önemli duyurular\n"
                     "• Fiyat etkisi analizi\n\n"
                     "💡 Şimdilik: /korku komutu ile sentiment'i takip et!")

# =============================================================================
# GENEL MESAJ HANDLERİ
# =============================================================================

@bot.message_handler(func=lambda message: True)
def echo_all(message):
    """Tüm diğer mesajlar için gelişmiş handler"""
    if not should_respond_in_group(message):
        return
    
    text = message.text.lower() if message.text else ""
    
    # Selamlaşma
    if any(word in text for word in ['merhaba', 'selam', 'hello', 'hi', 'hey']):
        greetings = [
            "🚀 Selam! Hangi coin'i analiz edelim? (/analiz COIN)",
            "👋 Hey! Yeni AI tahmin özelliğini denedin mi? (/predict COIN)",
            "😄 Merhaba! Çoklu timeframe analizi için /analiz COIN multi yaz!",
            "🤖 Selam! Gelişmiş sinyal sistemi için /signals COIN dene!"
        ]
        response = greetings[hash(text) % len(greetings)]
        bot.send_message(message.chat.id, response)
    
    # Yardım isteği
    elif any(word in text for word in ['yardım', 'help', 'komut', 'nasıl']):
        bot.send_message(message.chat.id, 
                         "🆘 **Yardım Menüsü:**\n\n"
                         "📋 **Tüm komutlar:** /yardim\n"
                         "📊 **Fiyat:** /fiyat COIN\n"
                         "📈 **Analiz:** /analiz COIN\n"
                         "🎯 **Sinyaller:** /signals COIN\n"
                         "🤖 **AI tahmin:** /predict COIN\n"
                         "⏰ **Alarm:** /alarm COIN\n"
                         "🏓 **Test:** /ping\n\n"
                         "💡 **Yeni:** Çoklu timeframe için /analiz COIN multi!")
    
    # Coin soruları (gelişmiş AI)
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
                             f"🎯 **{coin_mentioned.upper()} Analiz Menüsü:**\n\n"
                             f"📊 **Temel:** /fiyat {coin_mentioned}\n"
                             f"📈 **Analiz:** /analiz {coin_mentioned}\n"
                             f"🔥 **Çoklu TF:** /analiz {coin_mentioned} multi\n"
                             f"🤖 **AI tahmin:** /predict {coin_mentioned}\n"
                             f"🎯 **Sinyaller:** /signals {coin_mentioned}\n"
                             f"⏰ **Alarm:** /alarm {coin_mentioned}\n\n"
                             f"💡 Hangi analizi istiyorsun?")
    
    # Trading soruları
    elif any(word in text for word in ['al', 'sat', 'buy', 'sell', 'trade', 'sinyal']):
        bot.send_message(message.chat.id, 
                         "🎯 **Trading Araçları:**\n\n"
                         "📊 **Güçlü sinyaller:** /signals COIN\n"
                         "📈 **Detaylı analiz:** /analiz COIN multi\n"
                         "🔥 **Breakout adayları:** /breakout\n"
                         "🤖 **AI tahmini:** /predict COIN\n"
                         "😱 **Piyasa sentiment:** /korku\n\n"
                         "⚠️ **Risk uyarısı:** Bu analizler yatırım tavsiyesi değildir!")
    
    # AI ve tahmin soruları
    elif any(word in text for word in ['ai', 'tahmin', 'predict', 'gelecek', 'nolur']):
        bot.send_message(message.chat.id, 
                         "🤖 **AI Tahmin Sistemi:**\n\n"
                         "🎯 **Kullanım:** /predict COIN [GÜN]\n\n"
                         "**Örnekler:**\n"
                         "• /predict btc - 7 günlük tahmin\n"
                         "• /predict eth 14 - 14 günlük tahmin\n"
                         "• /predict sol 30 - Maksimum 30 gün\n\n"
                         "🔥 **Özellikler:**\n"
                         "• GPT-4 ile analiz\n"
                         "• Teknik indikatör bazlı\n"
                         "• Risk/ödül hesaplaması\n\n"
                         "⚠️ Yatırım tavsiyesi değildir!")
    
    # Diğer durumlarda
    else:
        bot.send_message(message.chat.id, 
                         "🤔 **Ne yapmak istiyorsun?**\n\n"
                         "🔥 **Popüler komutlar:**\n"
                         "• /analiz btc multi - Çoklu timeframe\n"
                         "• /signals eth - Trading sinyalleri\n"
                         "• /predict sol - AI tahmini\n"
                         "• /breakout - Breakout adayları\n"
                         "• /top10 - En büyük coinler\n\n"
                         "📋 **Tüm komutlar:** /yardim\n"
                         "🏓 **Bot testi:** /ping")

# =============================================================================
# BOT BAŞLATMA (GELİŞMİŞ)
# =============================================================================

def main():
    """Ana bot fonksiyonu - gelişmiş versiyon"""
    
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
    
    print("🚀 Gelişmiş Kripto Bot başlatılıyor...")
    print(f"🤖 Bot kullanıcı adı: @{bot_username}")
    print("📱 Telegram'da kullanmaya başlayabilirsin!")
    print("🎯 FULL ADVANCED VERSION - Tüm özellikler aktif!")
    
    print(f"\n🌟 **YENİ ÖZELLİKLER:**")
    print("🔥 Çoklu timeframe analizi (1h, 4h, 1d, 1w)")
    print(f"🤖 AI fiyat tahmini ({ai_status})")
    print("📐 Fibonacci retracement seviyeleri")
    print("📊 Gelişmiş teknik indikatörler")
    print("🎯 Sinyal gücü sistemi (1-10)")
    print("💼 Entry/Exit noktaları + Stop-loss")
    print("⚖️ Risk analizi ve yönetimi")
    print("🔥 Gelişmiş breakout analizi")
    
    print(f"\n✅ **AKTİF ÖZELLİKLER:**")
    print("• Fiyat sorgulama (/fiyat)")
    print("• Top 10 listesi (/top10)")
    print("• Trend coinler (/trending)")
    print("• Gelişmiş teknik analiz (/analiz)")
    print("• Çoklu timeframe (/analiz COIN multi)")
    print("• AI tahmin (/predict)")
    print("• Trading sinyalleri (/signals)")
    print("• Gelişmiş breakout (/breakout)")
    print("• Fear & Greed Index (/korku)")
    print("• Fiyat alarmları (/alarm)")
    print("• Alarm yönetimi (/alarmlist, /alarmstop)")
    print("• Gelişmiş grafikler")
    print("• Grup chat desteği")
    print("• Hızlı komutlar (/btc, /eth)")
    
    print(f"\n🔄 **GELECEKTEKİ ÖZELLİKLER:**")
    print("• Makroekonomik analiz (/makro)")
    print("• Portfolio takibi (/portfolio)")
    print("• Kripto haberleri (/news)")
    print("• Social sentiment analizi")
    print("• DeFi protokol entegrasyonu")
    
    print(f"\n🎯 **ÖRNEK KOMUTLAR:**")
    print("• /analiz btc multi")
    print("• /signals eth")
    print("• /predict sol 7")
    print("• /breakout")
    print("• /alarm ada")
    
    # Bot'u başlat
    while True:
        try:
            print(f"\n🟢 Gelişmiş bot çalışıyor ve komutları bekliyor...")
            print("📊 400+ coin + AI analiz sistemi hazır!")
            print("🎯 Yeni özellikleri test etmeyi unutma!")
            bot.polling(none_stop=True, interval=0, timeout=20)
        except Exception as e:
            print(f"❌ Bot hatası: {e}")
            print("🔄 5 saniye sonra yeniden başlatılıyor...")
            time.sleep(5)
            continue

if __name__ == "__main__":
    main()
