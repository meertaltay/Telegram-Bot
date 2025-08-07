"""
Alarm Commands - Fiyat alarm sistemi
/alarm, /alarmlist, /alarmstop komutları - HABER SİSTEMİ ENTEGRELİ
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

# Global alarm değişkenleri
price_alarms = {}  # {user_id: [{'coin': 'eth', 'target_price': 3500, 'coin_id': 'ethereum'}]}
user_states = {}   # {user_id: {'state': 'waiting_price', 'coin': 'eth'}}

def register_alarm_commands(bot):
    """Alarm komutlarını bot'a kaydet"""
    
    @bot.message_handler(commands=['alarm'])
    def alarm_komut(message):
        """Fiyat alarmı kur"""
        user_id = message.from_user.id
        
        try:
            # 🔥 HABER SİSTEMİ: Kullanıcıyı otomatik kaydet
            add_active_user(user_id)
            
            parts = message.text.strip().split()
            if len(parts) < 2:
                bot.send_message(message.chat.id, 
                    "⏰ **Fiyat Alarmı Nasıl Kurulur:**\n\n"
                    "🔹 /alarm COIN - Fiyat alarmı kur\n\n"
                    "**Örnekler:**\n"
                    "• /alarm btc\n"
                    "• /alarm eth\n"
                    "• /alarm sol\n\n"
                    "📋 *Aktif alarmlar:* /alarmlist\n"
                    "🗑️ *Alarm sil:* /alarmstop COIN",
                    parse_mode="Markdown")
                return

            coin_input = parts[1].lower()
            
            # Coin ID'sini bul
            if coin_input in POPULAR_COINS:
                coin_id = POPULAR_COINS[coin_input]
            else:
                coin_id = search_coin_for_alarm(coin_input)
                if not coin_id:
                    bot.send_message(message.chat.id, 
                        f"❌ **'{coin_input.upper()}' bulunamadı!**\n\n"
                        "🔍 **Popüler:** BTC, ETH, SOL, DOGE, ADA",
                        parse_mode="Markdown")
                    return

            # Mevcut fiyatı al
            current_price = get_current_price_for_alarm(coin_id)
            if not current_price:
                bot.send_message(message.chat.id, "❌ Fiyat bilgisi alınamadı!")
                return

            # Kullanıcı durumunu ayarla
            user_states[user_id] = {
                'state': 'waiting_price',
                'coin': coin_input,
                'coin_id': coin_id,
                'current_price': current_price
            }

            # Fiyat formatı
            if current_price < 0.01:
                price_str = f"${current_price:.8f}"
            elif current_price < 1:
                price_str = f"${current_price:.6f}"
            else:
                price_str = f"${current_price:,.2f}"

            coin_name = coin_id.replace('-', ' ').title()
            bot.send_message(message.chat.id, 
                f"⏰ **{coin_name} Fiyat Alarmı**\n\n"
                f"💰 **Şu anki fiyat:** {price_str}\n\n"
                f"🎯 **Hangi fiyatta bildirim almak istiyorsun?**\n"
                f"Sadece sayıyı yaz (örn: 50000)",
                parse_mode="Markdown")
                
        except Exception as e:
            print(f"Alarm komut hatası: {e}")
            bot.send_message(message.chat.id, "❌ Alarm kurulamadı!")

    @bot.message_handler(commands=['alarmlist'])
    def alarm_listesi(message):
        """Aktif alarmları listele"""
        user_id = message.from_user.id
        
        # 🔥 HABER SİSTEMİ: Kullanıcıyı otomatik kaydet
        add_active_user(user_id)
        
        user_alarms = get_user_alarms(user_id)
        
        if not user_alarms:
            bot.send_message(message.chat.id, 
                "📭 **Aktif alarmın yok!**\n\n"
                "⏰ Alarm kurmak için: /alarm COIN\n"
                "💡 Örnek: /alarm btc",
                parse_mode="Markdown")
            return
        
        alarm_text = "⏰ **Aktif Fiyat Alarmların:**\n\n"
        
        for i, alarm in enumerate(user_alarms, 1):
            coin_name = alarm['coin_id'].replace('-', ' ').title()
            target = alarm['target_price']
            
            # Mevcut fiyatı al
            current_price = get_current_price_for_alarm(alarm['coin_id'])
            if current_price:
                if target < 0.01:
                    target_str = f"${target:.8f}"
                elif target < 1:
                    target_str = f"${target:.6f}"
                else:
                    target_str = f"${target:,.2f}"
                    
                if current_price < 0.01:
                    current_str = f"${current_price:.8f}"
                elif current_price < 1:
                    current_str = f"${current_price:.6f}"
                else:
                    current_str = f"${current_price:,.2f}"
                
                # Mesafe hesapla
                distance = ((target - current_price) / current_price) * 100
                distance_emoji = "📈" if distance > 0 else "📉"
                
                alarm_text += f"**{i}. {coin_name}** ({alarm['coin']})\n"
                alarm_text += f"   🎯 Hedef: {target_str}\n"
                alarm_text += f"   💰 Şu an: {current_str}\n"
                alarm_text += f"   📊 Mesafe: {distance_emoji} %{abs(distance):.1f}\n\n"
            else:
                alarm_text += f"**{i}. {coin_name}** ({alarm['coin']})\n"
                alarm_text += f"   🎯 Hedef: ${target:,.2f}\n"
                alarm_text += f"   ❌ Fiyat alınamadı\n\n"
        
        alarm_text += "🗑️ **Alarm silmek için:** /alarmstop COIN"
        
        bot.send_message(message.chat.id, alarm_text, parse_mode="Markdown")

    @bot.message_handler(commands=['alarmstop'])
    def alarm_durdur(message):
        """Alarmı durdur"""
        user_id = message.from_user.id
        
        try:
            # 🔥 HABER SİSTEMİ: Kullanıcıyı otomatik kaydet
            add_active_user(user_id)
            
            parts = message.text.strip().split()
            if len(parts) < 2:
                bot.send_message(message.chat.id, 
                    "🗑️ **Alarm Silmek İçin:**\n\n"
                    "/alarmstop COIN\n\n"
                    "**Örnek:** /alarmstop btc\n\n"
                    "📋 *Alarmlarını görmek için:* /alarmlist",
                    parse_mode="Markdown")
                return

            coin_input = parts[1].lower()
            
            # Coin ID'sini bul
            if coin_input in POPULAR_COINS:
                coin_id = POPULAR_COINS[coin_input]
            else:
                coin_id = search_coin_for_alarm(coin_input)
                if not coin_id:
                    bot.send_message(message.chat.id, 
                        f"❌ '{coin_input.upper()}' bulunamadı!",
                        parse_mode="Markdown")
                    return

            # Alarmı kaldır
            user_alarms = get_user_alarms(user_id)
            found_alarm = None
            
            for alarm in user_alarms:
                if alarm['coin_id'] == coin_id:
                    found_alarm = alarm
                    break
            
            if found_alarm:
                remove_price_alarm(user_id, coin_id)
                coin_name = coin_id.replace('-', ' ').title()
                bot.send_message(message.chat.id, 
                    f"✅ **{coin_name} alarmı silindi!**\n\n"
                    "📋 *Kalan alarmlar:* /alarmlist",
                    parse_mode="Markdown")
            else:
                coin_name = coin_id.replace('-', ' ').title()
                bot.send_message(message.chat.id, 
                    f"❌ **{coin_name} için aktif alarm yok!**\n\n"
                    "📋 *Alarmlarını görmek için:* /alarmlist",
                    parse_mode="Markdown")
                
        except Exception as e:
            print(f"Alarm durdur hatası: {e}")
            bot.send_message(message.chat.id, "❌ Alarm silinemedi!")

    @bot.message_handler(commands=['cancel'])
    def cancel_alarm(message):
        """Alarm kurulumunu iptal et"""
        user_id = message.from_user.id
        
        # 🔥 HABER SİSTEMİ: Kullanıcıyı otomatik kaydet
        add_active_user(user_id)
        
        if user_id in user_states:
            del user_states[user_id]
            bot.send_message(message.chat.id, "❌ **Alarm kurulum iptal edildi!**")
        else:
            bot.send_message(message.chat.id, "ℹ️ İptal edilecek işlem yok.")

    # Fiyat girişi için handler
    @bot.message_handler(func=lambda message: message.from_user.id in user_states and user_states[message.from_user.id]['state'] == 'waiting_price')
    def handle_price_input(message):
        """Kullanıcının girdiği fiyatı işle"""
        user_id = message.from_user.id
        user_state = user_states[user_id]
        
        # 🔥 HABER SİSTEMİ: Kullanıcıyı otomatik kaydet
        add_active_user(user_id)
        
        try:
            # Fiyatı parse et
            price_text = message.text.strip().replace(',', '').replace('$', '')
            target_price = float(price_text)
            
            if target_price <= 0:
                bot.send_message(message.chat.id, "❌ Geçerli bir fiyat gir! (0'dan büyük olmalı)")
                return
            
            coin = user_state['coin']
            coin_id = user_state['coin_id']
            current_price = user_state['current_price']
            
            # Kullanıcı durumunu güncelle
            user_states[user_id] = {
                'state': 'waiting_confirmation',
                'coin': coin,
                'coin_id': coin_id,
                'target_price': target_price,
                'current_price': current_price
            }
            
            # Fiyat formatları
            if target_price < 0.01:
                target_str = f"${target_price:.8f}"
            elif target_price < 1:
                target_str = f"${target_price:.6f}"
            else:
                target_str = f"${target_price:,.2f}"
                
            if current_price < 0.01:
                current_str = f"${current_price:.8f}"
            elif current_price < 1:
                current_str = f"${current_price:.6f}"
            else:
                current_str = f"${current_price:,.2f}"
            
            # Yüzde hesapla
            percentage = ((target_price - current_price) / current_price) * 100
            direction = "yukarı" if percentage > 0 else "aşağı"
            percentage_str = f"%{abs(percentage):.1f}"
            
            coin_name = coin_id.replace('-', ' ').title()
            
            bot.send_message(message.chat.id, 
                f"⏰ **Alarm Onayı**\n\n"
                f"🪙 **Coin:** {coin_name} ({coin.upper()})\n"
                f"💰 **Şu anki fiyat:** {current_str}\n"
                f"🎯 **Hedef fiyat:** {target_str}\n"
                f"📊 **Değişim:** {percentage_str} {direction}\n\n"
                f"✅ **Onaylıyor musun?**\n"
                f"'evet' yaz onaylamak için\n"
                f"'hayır' yaz iptal etmek için",
                parse_mode="Markdown")
                
        except ValueError:
            bot.send_message(message.chat.id, 
                "❌ **Geçersiz fiyat!**\n\n"
                "Sadece sayı gir (örnek: 50000 veya 0.50)\n"
                "İptal etmek için: /cancel")
        except Exception as e:
            print(f"Fiyat input hatası: {e}")
            bot.send_message(message.chat.id, "❌ Bir hata oluştu! Tekrar dene.")
            if user_id in user_states:
                del user_states[user_id]

    # Onay için handler
    @bot.message_handler(func=lambda message: message.from_user.id in user_states and user_states[message.from_user.id]['state'] == 'waiting_confirmation')
    def handle_confirmation(message):
        """Kullanıcının onayını işle"""
        user_id = message.from_user.id
        user_state = user_states[user_id]
        text = message.text.lower().strip()
        
        # 🔥 HABER SİSTEMİ: Kullanıcıyı otomatik kaydet
        add_active_user(user_id)
        
        if text in ['evet', 'yes', 'y', 'e', 'tamam', 'ok']:
            # Alarmı kaydet
            coin = user_state['coin']
            coin_id = user_state['coin_id']
            target_price = user_state['target_price']
            
            add_price_alarm(user_id, coin, coin_id, target_price)
            
            # Fiyat formatı
            if target_price < 0.01:
                target_str = f"${target_price:.8f}"
            elif target_price < 1:
                target_str = f"${target_price:.6f}"
            else:
                target_str = f"${target_price:,.2f}"
            
            coin_name = coin_id.replace('-', ' ').title()
            
            bot.send_message(message.chat.id, 
                f"✅ **Alarm Kuruldu!**\n\n"
                f"🎯 {coin_name} {target_str} seviyesine ulaştığında bildirim alacaksın!\n\n"
                f"📋 *Alarmlarını görmek için:* /alarmlist\n"
                f"🗑️ *Alarm silmek için:* /alarmstop {coin}",
                parse_mode="Markdown")
                
            # Kullanıcı durumunu temizle
            del user_states[user_id]
            
        elif text in ['hayır', 'no', 'n', 'h', 'iptal', 'cancel']:
            coin_name = user_state['coin_id'].replace('-', ' ').title()
            bot.send_message(message.chat.id, 
                f"❌ **{coin_name} alarmı iptal edildi!**\n\n"
                "⏰ Tekrar kurmak için: /alarm COIN",
                parse_mode="Markdown")
                
            # Kullanıcı durumunu temizle
            del user_states[user_id]
            
        else:
            bot.send_message(message.chat.id, 
                "❓ **Lütfen net cevap ver:**\n\n"
                "✅ 'evet' - Alarmı kur\n"
                "❌ 'hayır' - İptal et")

# =============================================================================
# YARDIMCI FONKSİYONLAR
# =============================================================================

def search_coin_for_alarm(query):
    """Alarm için coin ara"""
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

def get_current_price_for_alarm(coin_id):
    """Alarm için güncel fiyat al"""
    try:
        url = f"{COINGECKO_BASE_URL}/simple/price?ids={coin_id}&vs_currencies=usd"
        response = requests.get(url, timeout=COINGECKO_TIMEOUT)
        if response.status_code == 200:
            data = response.json()
            if coin_id in data:
                return data[coin_id]['usd']
    except:
        pass
    return None

def add_price_alarm(user_id, coin, coin_id, target_price):
    """Kullanıcı için fiyat alarmı ekle"""
    if user_id not in price_alarms:
        price_alarms[user_id] = []
    
    # Aynı coin için mevcut alarm var mı kontrol et
    for i, alarm in enumerate(price_alarms[user_id]):
        if alarm['coin_id'] == coin_id:
            # Mevcut alarmı güncelle
            price_alarms[user_id][i] = {
                'coin': coin.upper(),
                'coin_id': coin_id,
                'target_price': target_price
            }
            return True
    
    # Maksimum alarm kontrolü
    if len(price_alarms[user_id]) >= MAX_ALARMS_PER_USER:
        return False
    
    # Yeni alarm ekle
    price_alarms[user_id].append({
        'coin': coin.upper(),
        'coin_id': coin_id,
        'target_price': target_price
    })
    return True

def remove_price_alarm(user_id, coin_id):
    """Kullanıcının belirli coin alarmını kaldır"""
    if user_id in price_alarms:
        price_alarms[user_id] = [alarm for alarm in price_alarms[user_id] if alarm['coin_id'] != coin_id]
        if not price_alarms[user_id]:
            del price_alarms[user_id]

def get_user_alarms(user_id):
    """Kullanıcının aktif alarmlarını getir"""
    return price_alarms.get(user_id, [])

print("⏰ Alarm commands yüklendi!")
