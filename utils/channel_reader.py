"""
Kanal Haber Okuyucu - Bot ile çakışmayan sistem
RSS veya Telegram API ile kanal takibi
"""

import requests
import time
import threading
import json
import os
import hashlib
from datetime import datetime
from config import TELEGRAM_TOKEN

# Kanal bilgileri
CHANNEL_USERNAME = "primecrypto_tr"
CHANNEL_ID = "@primecrypto_tr"

# Dosyalar
USERS_FILE = "news_users.json"
SENT_NEWS_FILE = "sent_news.json"

# Global
news_users = set()
sent_messages = set()  # Gönderilmiş mesajları takip et
news_thread = None
news_running = False

def load_data():
    """Verileri yükle"""
    global news_users, sent_messages
    
    # Kullanıcılar
    try:
        if os.path.exists(USERS_FILE):
            with open(USERS_FILE, 'r') as f:
                data = json.load(f)
                news_users = set(data.get('users', []))
                print(f"📚 {len(news_users)} kullanıcı yüklendi")
    except:
        news_users = set()
    
    # Gönderilmiş haberler
    try:
        if os.path.exists(SENT_NEWS_FILE):
            with open(SENT_NEWS_FILE, 'r') as f:
                data = json.load(f)
                sent_messages = set(data.get('sent', []))
    except:
        sent_messages = set()

def save_data():
    """Verileri kaydet"""
    try:
        # Kullanıcılar
        with open(USERS_FILE, 'w') as f:
            json.dump({'users': list(news_users)}, f)
        
        # Gönderilmiş haberler (son 100 tane)
        recent_sent = list(sent_messages)[-100:]
        with open(SENT_NEWS_FILE, 'w') as f:
            json.dump({'sent': recent_sent}, f)
    except:
        pass

def add_user(user_id):
    """Kullanıcı ekle"""
    if user_id not in news_users:
        news_users.add(user_id)
        save_data()
        return True
    return False

def remove_user(user_id):
    """Kullanıcı çıkar"""
    if user_id in news_users:
        news_users.remove(user_id)
        save_data()
        return True
    return False

def get_message_hash(text):
    """Mesaj hash'i oluştur (tekrar göndermemek için)"""
    return hashlib.md5(text.encode()).hexdigest()

def fetch_channel_messages():
    """Kanaldan mesajları çek - WEB SCRAPING YÖNTEMİ"""
    try:
        # Telegram web preview API kullan
        url = f"https://t.me/s/{CHANNEL_USERNAME}"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            # HTML'den mesajları parse et (basit yöntem)
            # Gerçek implementasyonda BeautifulSoup kullanılabilir
            content = response.text
            
            # Son mesajı bul (basit örnek)
            if "tgme_widget_message_text" in content:
                # Mesaj bulundu
                return ["Kanal güncellendi! Detaylar için kanala bakın."]
        
        return []
        
    except Exception as e:
        print(f"❌ Kanal okuma hatası: {e}")
        return []

def send_to_users(message_text):
    """Mesajı kullanıcılara gönder"""
    if not message_text or not news_users:
        return
    
    # Hash kontrolü - aynı mesajı tekrar gönderme
    msg_hash = get_message_hash(message_text)
    if msg_hash in sent_messages:
        return
    
    sent_messages.add(msg_hash)
    
    # Formatla
    formatted_msg = f"""🚨 **Kripto Haberi**

{message_text}

📱 Kaynak: @{CHANNEL_USERNAME}
⏰ {datetime.now().strftime('%H:%M')}"""
    
    success = 0
    failed = 0
    blocked_users = []
    
    for user_id in list(news_users):
        try:
            url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
            data = {
                "chat_id": user_id,
                "text": formatted_msg,
                "parse_mode": "Markdown",
                "disable_web_page_preview": False
            }
            
            response = requests.post(url, json=data, timeout=5)
            
            if response.status_code == 200:
                result = response.json()
                if result.get('ok'):
                    success += 1
                else:
                    if 'blocked' in str(result).lower():
                        blocked_users.append(user_id)
                    failed += 1
            
            time.sleep(0.05)  # Rate limit
            
        except:
            failed += 1
    
    # Bloklayanları çıkar
    for uid in blocked_users:
        remove_user(uid)
    
    print(f"📬 Haber gönderildi: ✅ {success}, ❌ {failed}")
    save_data()

def alternative_channel_check():
    """Alternatif: Telegram Channel API (Bot API değil)"""
    try:
        # Telegram'ın public channel API'si
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/getChat"
        params = {"chat_id": f"@{CHANNEL_USERNAME}"}
        
        response = requests.get(url, params=params, timeout=5)
        
        if response.status_code == 200:
            # Sadece kanal bilgisini alabiliyoruz, mesajları alamıyoruz
            # Bu yüzden periyodik kontrol mesajı göndereceğiz
            return True
    except:
        pass
    
    return False

def news_monitor_loop():
    """Haber takip döngüsü - ÇAKIŞMASIZ"""
    global news_running
    
    print("📰 Haber takibi başladı (Güvenli mod)")
    
    check_counter = 0
    last_notification_time = time.time()
    
    while news_running:
        try:
            # Her 30 dakikada bir kontrol
            time.sleep(1800)  # 30 dakika
            
            check_counter += 1
            current_time = time.time()
            
            # Her 2 saatte bir bilgilendirme haberi
            if current_time - last_notification_time > 7200:  # 2 saat
                
                info_message = f"""📈 **Piyasa Güncellemesi**

🔹 Bitcoin ve altcoinler takipte
🔹 Önemli gelişmeler için kanalı takip edin
🔹 Detaylar: @{CHANNEL_USERNAME}

💡 Fiyatlar için: /fiyat btc
📊 Analiz için: /analiz eth"""
                
                send_to_users(info_message)
                last_notification_time = current_time
            
            # Kanal kontrolü (opsiyonel)
            messages = fetch_channel_messages()
            for msg in messages[:3]:  # Maksimum 3 mesaj
                send_to_users(msg)
                time.sleep(2)
                
        except Exception as e:
            print(f"❌ Monitor hatası: {e}")
            time.sleep(60)

def start_channel_news():
    """Kanal haber sistemini başlat"""
    global news_thread, news_running
    
    print("📰 Kanal haber sistemi başlatılıyor...")
    
    load_data()
    
    if news_running:
        print("⚠️ Haber sistemi zaten çalışıyor!")
        return False
    
    news_running = True
    news_thread = threading.Thread(target=news_monitor_loop, daemon=True)
    news_thread.start()
    
    print(f"✅ Haber sistemi başladı!")
    print(f"📱 Kanal: @{CHANNEL_USERNAME}")
    print(f"👥 {len(news_users)} aktif kullanıcı")
    
    return True

def stop_channel_news():
    """Haber sistemini durdur"""
    global news_running
    news_running = False
    save_data()
    print("⏹️ Haber sistemi durduruldu")

def get_stats():
    """İstatistikler"""
    return {
        'users': len(news_users),
        'channel': CHANNEL_USERNAME,
        'running': news_running
    }
