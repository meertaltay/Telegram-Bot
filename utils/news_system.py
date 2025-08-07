"""
Otomatik Telegram Kanal Haber Sistemi
@primecrypto_tr kanalından otomatik haber çekme ve kullanıcılara gönderme
"""

import requests
import time
import threading
from datetime import datetime
import json
import os
from config import TELEGRAM_TOKEN

# Global değişkenler
CHANNEL_USERNAME = "primecrypto_tr"
CHANNEL_ID = None  # Runtime'da tespit edilecek
active_users = set()  # Aktif kullanıcı ID'leri
last_message_id = None  # Son işlenen mesaj ID'si
news_thread = None  # Haber thread'i
news_system_running = False

# Kullanıcı verilerini dosyada sakla
USER_DATA_FILE = "user_data.json"

def load_user_data():
    """Kullanıcı verilerini yükle"""
    global active_users, last_message_id
    try:
        if os.path.exists(USER_DATA_FILE):
            with open(USER_DATA_FILE, 'r') as f:
                data = json.load(f)
                active_users = set(data.get('active_users', []))
                last_message_id = data.get('last_message_id', None)
                print(f"📚 {len(active_users)} aktif kullanıcı yüklendi")
        else:
            print("📝 Yeni kullanıcı dosyası oluşturulacak")
    except Exception as e:
        print(f"❌ Kullanıcı verisi yükleme hatası: {e}")
        active_users = set()
        last_message_id = None

def save_user_data():
    """Kullanıcı verilerini kaydet"""
    try:
        data = {
            'active_users': list(active_users),
            'last_message_id': last_message_id,
            'updated': datetime.now().isoformat()
        }
        with open(USER_DATA_FILE, 'w') as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        print(f"❌ Kullanıcı verisi kaydetme hatası: {e}")

def add_active_user(user_id):
    """Kullanıcıyı aktif listesine ekle"""
    global active_users
    if user_id not in active_users:
        active_users.add(user_id)
        save_user_data()
        print(f"👤 Yeni kullanıcı eklendi: {user_id} (Toplam: {len(active_users)})")

def get_channel_info():
    """Kanal bilgilerini al"""
    global CHANNEL_ID
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/getChat"
        params = {"chat_id": f"@{CHANNEL_USERNAME}"}
        
        response = requests.get(url, params=params, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data['ok']:
                CHANNEL_ID = data['result']['id']
                channel_title = data['result']['title']
                member_count = data['result'].get('member_count', 'N/A')
                
                print(f"✅ Kanal bulundu: {channel_title}")
                print(f"📊 Kanal ID: {CHANNEL_ID}")
                print(f"👥 Üye sayısı: {member_count}")
                return True
            else:
                print(f"❌ Kanal bilgisi alınamadı: {data}")
                return False
        else:
            print(f"❌ API hatası: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Kanal bilgisi alma hatası: {e}")
        return False

def get_channel_updates():
    """Kanaldan yeni mesajları çek"""
    global last_message_id
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/getUpdates"
        params = {
            "allowed_updates": ["channel_post"],
            "timeout": 5
        }
        
        if last_message_id:
            params["offset"] = last_message_id + 1
        
        response = requests.get(url, params=params, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data['ok']:
                updates = data['result']
                new_messages = []
                
                for update in updates:
                    if 'channel_post' in update:
                        channel_post = update['channel_post']
                        # Sadece bizim kanaldan gelen mesajları işle
                        if channel_post['chat']['id'] == CHANNEL_ID:
                            new_messages.append(channel_post)
                            last_message_id = max(last_message_id or 0, update['update_id'])
                
                if new_messages:
                    save_user_data()  # Son mesaj ID'sini kaydet
                    return new_messages
                return []
            else:
                print(f"❌ Update alma hatası: {data}")
                return []
        else:
            print(f"❌ API hatası: {response.status_code}")
            return []
    except Exception as e:
        print(f"❌ Kanal güncelleme hatası: {e}")
        return []

def format_news_message(channel_post):
    """Haber mesajını formatla"""
    try:
        # Mesaj içeriği
        text = channel_post.get('text', '')
        
        # Eğer mesaj boşsa veya çok kısaysa skip et
        if not text or len(text.strip()) < 10:
            return None
        
        # Tarih formatla
        timestamp = channel_post.get('date', 0)
        dt = datetime.fromtimestamp(timestamp)
        time_str = dt.strftime("%H:%M")
        date_str = dt.strftime("%d.%m.%Y")
        
        # Haber formatı
        formatted_message = f"""🚨 **Prime Crypto Haber**

{text}

📱 **Kaynak:** @{CHANNEL_USERNAME}
⏰ **Zaman:** {time_str} - {date_str}"""
        
        return formatted_message
    except Exception as e:
        print(f"❌ Mesaj formatlama hatası: {e}")
        return None

def send_news_to_users(formatted_message):
    """Formatlanmış haberi tüm kullanıcılara gönder"""
    if not formatted_message or not active_users:
        return
    
    success_count = 0
    error_count = 0
    blocked_users = set()
    
    for user_id in list(active_users):  # Copy to avoid modification during iteration
        try:
            url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
            data = {
                "chat_id": user_id,
                "text": formatted_message,
                "parse_mode": "Markdown",
                "disable_web_page_preview": False
            }
            
            response = requests.post(url, json=data, timeout=10)
            
            if response.status_code == 200:
                result = response.json()
                if result['ok']:
                    success_count += 1
                else:
                    error_description = result.get('description', 'Unknown error')
                    if 'blocked by the user' in error_description or 'user is deactivated' in error_description:
                        blocked_users.add(user_id)
                        print(f"🚫 Kullanıcı bot'u engellemiş: {user_id}")
                    else:
                        error_count += 1
                        print(f"❌ Mesaj gönderme hatası {user_id}: {error_description}")
            else:
                error_count += 1
                print(f"❌ HTTP hatası {user_id}: {response.status_code}")
                
        except Exception as e:
            error_count += 1
            print(f"❌ Kullanıcıya gönderme hatası {user_id}: {e}")
        
        # Rate limiting - Telegram limits
        time.sleep(0.05)  # 50ms delay between messages
    
    # Engellemiş kullanıcıları listeden çıkar
    if blocked_users:
        active_users.difference_update(blocked_users)
        save_user_data()
        print(f"🗑️ {len(blocked_users)} engellemiş kullanıcı listeden çıkarıldı")
    
    # Sonuç raporu
    total_users = len(active_users)
    print(f"📬 Haber gönderildi: ✅ {success_count} başarılı, ❌ {error_count} hata, 👥 {total_users} toplam aktif")

def news_monitoring_loop():
    """Ana haber monitoring döngüsü"""
    global news_system_running
    
    print("🔄 Haber monitoring başlatıldı...")
    
    while news_system_running:
        try:
            # Kanal güncellemelerini kontrol et
            new_messages = get_channel_updates()
            
            if new_messages:
                print(f"📰 {len(new_messages)} yeni mesaj bulundu")
                
                for message in new_messages:
                    # Mesajı formatla
                    formatted_news = format_news_message(message)
                    
                    if formatted_news:
                        print("📤 Haber kullanıcılara gönderiliyor...")
                        send_news_to_users(formatted_news)
                        
                        # Mesajlar arası kısa bekleme
                        time.sleep(2)
            
            # Bir sonraki kontrol için bekle (30 saniye)
            time.sleep(30)
            
        except Exception as e:
            print(f"❌ News monitoring döngü hatası: {e}")
            time.sleep(60)  # Hata durumunda 1 dakika bekle

def start_news_system():
    """Haber sistemini başlat"""
    global news_thread, news_system_running
    
    print("🚀 Otomatik Haber Sistemi başlatılıyor...")
    
    # Kullanıcı verilerini yükle
    load_user_data()
    
    # Kanal bilgilerini al
    if not get_channel_info():
        print("❌ Kanal bilgisi alınamadı, haber sistemi başlatılamıyor!")
        return False
    
    # Monitoring thread'ini başlat
    news_system_running = True
    news_thread = threading.Thread(target=news_monitoring_loop, daemon=True)
    news_thread.start()
    
    print("✅ Otomatik Haber Sistemi başlatıldı!")
    print(f"📡 Kanal: @{CHANNEL_USERNAME}")
    print(f"👥 Aktif kullanıcı: {len(active_users)}")
    print("🔄 Her 30 saniyede kanal kontrol ediliyor...")
    
    return True

def stop_news_system():
    """Haber sistemini durdur"""
    global news_system_running
    news_system_running = False
    save_user_data()
    print("⏹️ Haber sistemi durduruldu")

def get_news_stats():
    """Haber sistemi istatistiklerini al"""
    return {
        'active_users': len(active_users),
        'channel': CHANNEL_USERNAME,
        'last_message_id': last_message_id,
        'system_running': news_system_running
    }

# Test fonksiyonu
def test_news_system():
    """Haber sistemini test et"""
    print("🧪 Haber sistemi test ediliyor...")
    
    # Kanal erişimini test et
    if get_channel_info():
        print("✅ Kanal erişimi başarılı")
        
        # Test mesajı gönder
        test_user_id = 123456789  # Geçersiz ID ile test
        add_active_user(test_user_id)
        
        print(f"📊 Test tamamlandı. Aktif kullanıcı sayısı: {len(active_users)}")
        return True
    else:
        print("❌ Kanal erişimi başarısız")
        return False

if __name__ == "__main__":
    # Direkt çalıştırılırsa test yap
    test_news_system()
