"""
Crypto Telegram Bot - Configuration File
Token'lar ve temel ayarlar
"""

# =============================================================================
# BOT TOKEN'LARI (BURAYA KENDİ TOKEN'LARINIZI YAZIN!)
# =============================================================================
TELEGRAM_TOKEN = "BURAYA_BOT_TOKENINI_YAZ"
OPENAI_API_KEY = "BURAYA_OPENAI_KEYINI_YAZ"  # Opsiyonel

# =============================================================================
# API AYARLARI
# =============================================================================
COINGECKO_BASE_URL = "https://api.coingecko.com/api/v3"
BINANCE_BASE_URL = "https://api.binance.com/api/v3"
YAHOO_FINANCE_BASE_URL = "https://query1.finance.yahoo.com/v8/finance"

# =============================================================================
# BOT AYARLARI
# =============================================================================
# Alarm ayarları
ALARM_CHECK_INTERVAL = 60  # Saniye (60 = 1 dakika)
MAX_ALARMS_PER_USER = 10   # Kullanıcı başına maksimum alarm
PRICE_TOLERANCE = 0.01     # Fiyat toleransı (%1)

# Grafik ayarları
CHART_WIDTH = 18
CHART_HEIGHT = 10
CHART_DPI = 200

# API timeout'ları
API_TIMEOUT = 15  # Saniye
BINANCE_TIMEOUT = 10
COINGECKO_TIMEOUT = 10

# =============================================================================
# DESTEKLENEN COİN LİSTESİ (İLK ETAPTA)
# =============================================================================
POPULAR_COINS = {
    "btc": "bitcoin",
    "eth": "ethereum", 
    "sol": "solana",
    "doge": "dogecoin",
    "ada": "cardano",
    "matic": "matic-network",
    "bnb": "binancecoin",
    "xrp": "ripple",
    "ltc": "litecoin",
    "avax": "avalanche-2",
    "link": "chainlink",
    "uni": "uniswap",
    "shib": "shiba-inu",
    "pepe": "pepe"
}

# =============================================================================
# MESAJ SABITLERI
# =============================================================================
WELCOME_MESSAGE = """
🚀 **Kripto Bot'a Hoş Geldin!**

💎 **Popüler Komutlar:**
- /fiyat btc - Bitcoin fiyatı
- /top10 - En büyük 10 coin
- /analiz eth - Ethereum analizi
- /alarm btc - Fiyat alarmı kur
- /alarmlist - Aktif alarmlarım

🔥 **Hangi analizi merak ediyorsun?**
"""

ERROR_MESSAGES = {
    "coin_not_found": "❌ Coin bulunamadı! Popüler coinler: BTC, ETH, SOL, DOGE",
    "api_error": "❌ API hatası! Biraz sonra tekrar dene.",
    "invalid_price": "❌ Geçerli bir fiyat gir! (Örnek: 50000)",
    "no_data": "❌ Veri alınamadı! Internet bağlantını kontrol et."
}

# =============================================================================
# DEBUGGING (GELİŞTİRME SIRASINDA)
# =============================================================================
DEBUG_MODE = True  # False yap production'da
LOG_LEVEL = "INFO"  # DEBUG, INFO, WARNING, ERROR

print("✅ Config dosyası yüklendi!")
