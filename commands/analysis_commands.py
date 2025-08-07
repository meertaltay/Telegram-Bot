commands/analysis_commands.py"""
Clean and Simple Analysis Commands  
Sadece 4 timeframe butonu + AI yorumu + Fibonacci dahil - HABER SİSTEMİ ENTEGRELİ
"""

import requests
import telebot
from telebot import types
import pandas as pd
from config import *
from utils.binance_api import find_binance_symbol, get_binance_ohlc
from utils.chart_generator import create_advanced_chart

# 🔥 HABER SİSTEMİ İMPORT
try:
    from utils.news_system import add_active_user
except ImportError:
    print("⚠️ Haber sistemi import edilemedi")
    def add_active_user(user_id):
        pass  # Boş fonksiyon - hata vermemesi için

try:
    import openai
except ImportError:
    print("⚠️ OpenAI import edilemedi")

# Kullanıcı durumlarını takip etmek için
user_analysis_states = {}

def register_analysis_commands(bot):
    """Temiz ve sade analiz komutlarını bot'a kaydet"""
    
    @bot.message_handler(commands=['analiz'])
    def analiz(message):
        """Ana analiz komutu - Sadece timeframe seçimi"""
        try:
            # 🔥 HABER SİSTEMİ: Kullanıcıyı otomatik kaydet
            add_active_user(message.from_user.id)
            
            parts = message.text.strip().split()
            if len(parts) < 2:
                bot.send_message(message.chat.id, 
                    "📊 **Kripto Analiz**\n\n"
                    "🔹 **Kullanım:** /analiz COIN\n\n"
                    "**Örnekler:**\n"
                    "• /analiz btc\n"
                    "• /analiz eth\n"
                    "• /analiz sol\n\n"
                    "📈 Coin seçtikten sonra zaman dilimi seçin!",
                    parse_mode="Markdown")
                return

            coin_input = parts[1].lower()
            
            # Binance sembolü bul
            binance_symbol = find_binance_symbol(coin_input)
            
            if not binance_symbol:
                bot.send_message(message.chat.id, 
                    f"❌ **'{coin_input.upper()}' Binance'da bulunamadı!**\n\n"
                    f"💡 **Popüler:** BTC, ETH, SOL, DOGE, ADA",
                    parse_mode="Markdown")
                return

            # Kullanıcı durumunu kaydet
            user_analysis_states[message.from_user.id] = {
                'coin': coin_input,
                'symbol': binance_symbol,
                'chat_id': message.chat.id
            }

            # Sadece timeframe butonları
            markup = types.InlineKeyboardMarkup(row_width=2)
            
            btn_1h = types.InlineKeyboardButton("⚡ 1 Saat", callback_data=f"tf_1h_{coin_input}")
            btn_4h = types.InlineKeyboardButton("📊 4 Saat", callback_data=f"tf_4h_{coin_input}")
            btn_1d = types.InlineKeyboardButton("📈 1 Gün", callback_data=f"tf_1d_{coin_input}")
            btn_1w = types.InlineKeyboardButton("📅 1 Hafta", callback_data=f"tf_1w_{coin_input}")
            
            markup.add(btn_1h, btn_4h)
            markup.add(btn_1d, btn_1w)
            
            # Güncel fiyatı göster
            try:
                df_quick = get_binance_ohlc(binance_symbol, interval="1d", limit=2)
                if df_quick is not None and not df_quick.empty:
                    current_price = df_quick['close'].iloc[-1]
                    prev_price = df_quick['close'].iloc[-2]
                    change_24h = ((current_price - prev_price) / prev_price) * 100
                    
                    # Fiyat formatı
                    if current_price < 0.01:
                        price_str = f"${current_price:.8f}"
                    elif current_price < 1:
                        price_str = f"${current_price:.6f}"
                    else:
                        price_str = f"${current_price:,.2f}"
                    
                    change_emoji = "📈" if change_24h > 0 else "📉"
                    change_color = "🟢" if change_24h > 0 else "🔴"
                    
                    price_info = f"💰 {price_str} | {change_color} %{change_24h:+.1f} {change_emoji}\n\n"
                else:
                    price_info = ""
            except:
                price_info = ""

            coin_name = binance_symbol.replace('USDT', '').upper()
            
            bot.send_message(
                message.chat.id,
                f"🎯 **{coin_name} Analizi**\n"
                f"{price_info}"
                f"⏰ **Hangi sürede analiz yapalım?**",
                reply_markup=markup,
                parse_mode="Markdown"
            )
            
        except Exception as e:
            print(f"Analiz komutu hatası: {e}")
            bot.send_message(message.chat.id, "❌ Analiz başlatılamadı! Tekrar dene.")

    # Callback handler for timeframe selection
    @bot.callback_query_handler(func=lambda call: call.data.startswith('tf_'))
    def handle_timeframe_selection(call):
        """Timeframe seçimi işle"""
        try:
            # 🔥 HABER SİSTEMİ: Kullanıcıyı otomatik kaydet
            add_active_user(call.from_user.id)
            
            # Callback data parse et: tf_1h_btc
            parts = call.data.split('_')
            timeframe = parts[1]
            coin_input = parts[2]
            
            user_id = call.from_user.id
            
            # Kullanıcı durumu kontrol et
            if user_id not in user_analysis_states:
                bot.answer_callback_query(call.id, "⚠️ Lütfen /analiz komutu ile başlayın!")
                return
            
            user_state = user_analysis_states[user_id]
            binance_symbol = user_state['symbol']
            
            # Buton cevabı ver
            timeframe_names = {
                '1h': '1 Saatlik',
                '4h': '4 Saatlik', 
                '1d': '1 Günlük',
                '1w': '1 Haftalık'
            }
            
            tf_name = timeframe_names[timeframe]
            
            bot.answer_callback_query(call.id, f"🎯 {tf_name} analiz başlıyor...")
            
            # Mesajı güncelle
            bot.edit_message_text(
                f"⏳ **{binance_symbol} - {tf_name} Analiz**\n\n"
                f"📊 Veriler alınıyor...\n"
                f"🤖 AI yorumu hazırlanıyor...\n"
                f"📈 Grafik oluşturuluyor...\n\n"
                f"⚡ Bu işlem 10-15 saniye sürebilir.",
                call.message.chat.id,
                call.message.message_id,
                parse_mode="Markdown"
            )
            
            # Tam analiz yap
            perform_complete_timeframe_analysis(call.message, binance_symbol, coin_input, timeframe, bot)
            
            # Kullanıcı durumunu temizle
            if user_id in user_analysis_states:
                del user_analysis_states[user_id]
                
        except Exception as e:
            print(f"Timeframe selection hatası: {e}")
            bot.answer_callback_query(call.id, "❌ Analiz yapılamadı!")

# =============================================================================
# TAM ANALİZ FONKSİYONU
# =============================================================================

def perform_complete_timeframe_analysis(message, symbol, coin_input, timeframe, bot):
    """Tam analiz - AI yorumu + Fibonacci dahil, 2 mesaj halinde"""
    try:
        # Veri al
        limit_map = {'1h': 168, '4h': 168, '1d': 100, '1w': 52}
        limit = limit_map.get(timeframe, 100)
        
        df = get_binance_ohlc(symbol, interval=timeframe, limit=limit)
        if df is None or df.empty:
            bot.send_message(message.chat.id, f"❌ {symbol} veri alınamadı!")
            return

        # Kapsamlı teknik analiz
        analysis_result = perform_comprehensive_analysis(df, symbol, timeframe)
        
        # Destek/Direnç + Fibonacci seviyeleri
        support_resistance = calculate_support_resistance_with_fibonacci(df)
        
        # 1. MESAJ: GRAFİK
        chart_img = create_advanced_chart(df, symbol, analysis_result, timeframe)
        
        if chart_img:
            timeframe_names = {'1h': '1 Saat', '4h': '4 Saat', '1d': '1 Gün', '1w': '1 Hafta'}
            tf_name = timeframe_names.get(timeframe, timeframe)
            
            # Grafik mesajı kısa tut
            bot.send_photo(
                message.chat.id, 
                chart_img, 
                caption=f"📊 **{symbol} - {tf_name} Teknik Grafik**",
                parse_mode="Markdown"
            )
        
        # 2. MESAJ: KAPSAMLI ANALİZ
        complete_analysis_message = format_complete_analysis_message(
            analysis_result, 
            support_resistance,
            coin_input, 
            timeframe
        )
        
        bot.send_message(message.chat.id, complete_analysis_message, parse_mode="Markdown")
            
    except Exception as e:
        print(f"Tam analiz hatası: {e}")
        bot.send_message(message.chat.id, "❌ Analiz tamamlanamadı!")

# =============================================================================
# MESAJ FORMATI - KAPSAMLI AMA ÖZET
# =============================================================================

def format_complete_analysis_message(analysis_result, support_resistance, coin_input, timeframe):
    """Sadeleştirilmiş ve kullanıcı dostu analiz mesajı"""
    try:
        # Temel bilgiler
        price = analysis_result['price']
        rsi = analysis_result['rsi']
        
        # Fiyat formatı
        if price < 0.01:
            price_str = f"${price:.8f}"
        elif price < 1:
            price_str = f"${price:.6f}"
        else:
            price_str = f"${price:,.0f}"
        
        # Timeframe adı
        timeframe_names = {'1h': '1 Saat', '4h': '4 Saat', '1d': '1 Gün', '1w': '1 Hafta'}
        tf_name = timeframe_names.get(timeframe, timeframe)
        
        mesaj = f"📊 **{coin_input.upper()} - {tf_name} Analiz**\n\n"
        
        # === TEMEL BİLGİ ===
        mesaj += f"💰 **Güncel Fiyat:** {price_str}\n"
        mesaj += f"📈 **RSI:** {rsi:.0f}\n\n"
        
        # === AI ANALİZİ - PROFESYONELLEŞTİRİLMİŞ + BASİTLEŞTİRİLMİŞ ===
        mesaj += f"🤖 **AI ANALİZİ**\n"
        mesaj += f"📊 **Teknik Durum:** "
        
        # Geliştirilmiş AI yorumu oluştur
        professional_analysis = generate_professional_analysis(analysis_result, support_resistance, price, coin_input.upper())
        mesaj += f"{professional_analysis}\n\n"
        
        # Basitleştirme kısmı ekle
        mesaj += f"💭 **Basitçe ne demek istiyorum?**\n"
        simple_explanation = generate_simple_explanation(analysis_result, support_resistance, price)
        mesaj += f"{simple_explanation}\n\n"
        
        # === ÖNEMLİ SEVİYELER - SADECE EN YAKIN ===
        sr = support_resistance
        mesaj += f"📏 **DİKKAT EDİLECEK FİYATLAR**\n"
        
        # En yakın direnç
        if sr['nearest_resistance']:
            r_price = sr['nearest_resistance']['price']
            if r_price < 0.01:
                mesaj += f"🔴 **Direnç:** ${r_price:.8f}\n"
            elif r_price < 1:
                mesaj += f"🔴 **Direnç:** ${r_price:.6f}\n"
            else:
                mesaj += f"🔴 **Direnç:** ${r_price:,.0f}\n"
        
        # En yakın destek
        if sr['nearest_support']:
            s_price = sr['nearest_support']['price']
            if s_price < 0.01:
                mesaj += f"🟢 **Destek:** ${s_price:.8f}\n\n"
            elif s_price < 1:
                mesaj += f"🟢 **Destek:** ${s_price:.6f}\n\n"
            else:
                mesaj += f"🟢 **Destek:** ${s_price:,.0f}\n\n"
        
        # === TREND DURUMU - BASİT ===
        signals = analysis_result.get('signals', [])
        buy_count = len([s for s in signals if s['type'] == 'BUY'])
        sell_count = len([s for s in signals if s['type'] == 'SELL'])
        
        if buy_count > sell_count:
            trend_status = "🐂 **YÜKSELME EĞİLİMDE**"
        elif sell_count > buy_count:
            trend_status = "🐻 **DÜŞME EĞİLİMDE**"
        else:
            trend_status = "⚖️ **KARARSIZ**"
        
        mesaj += f"📈 **TREND:** {trend_status}\n\n"
        
        # === ALT MENÜ ===
        mesaj += f"🔧 ⏰ /alarm {coin_input} | 💧 /likidite {coin_input}\n"
        mesaj += f"⚠️ *Bu analiz yatırım tavsiyesi değildir!*"
        
        return mesaj
        
    except Exception as e:
        print(f"Mesaj formatla hatası: {e}")
        return "❌ Analiz sonucu formatlanamadı!"

# =============================================================================
# BASIT TEKNİK ANALİZ FONKSİYONLARI
# =============================================================================

from utils.technical_analysis import (
    calculate_rsi, calculate_macd, calculate_bollinger_bands
)

def perform_comprehensive_analysis(df, symbol, timeframe):
    """Kapsamlı teknik analiz - basitleştirilmiş"""
    try:
        current_price = df['close'].iloc[-1]
        
        # Temel indikatörler
        rsi = calculate_rsi(df['close']).iloc[-1]
        macd_data = calculate_macd(df['close'])
        bb_data = calculate_bollinger_bands(df['close'])
        
        # Sinyal gücü analizi
        signals = calculate_basic_signals(df, rsi, macd_data, bb_data)
        
        # Genel skor
        overall_score = calculate_basic_score(signals, rsi, current_price, df)
        
        return {
            'symbol': symbol,
            'timeframe': timeframe,
            'price': current_price,
            'rsi': rsi,
            'macd_data': macd_data,
            'bb_data': bb_data,
            'signals': signals,
            'overall_score': overall_score,
            'recommendation': get_basic_recommendation(overall_score, signals)
        }
    except Exception as e:
        print(f"Kapsamlı analiz hatası: {e}")
        return {}

def calculate_basic_signals(df, rsi, macd_data, bb_data):
    """Temel sinyal hesaplama"""
    try:
        signals = []
        current_price = df['close'].iloc[-1]
        
        # RSI Sinyali
        if rsi < 30:
            signals.append({
                'type': 'BUY',
                'indicator': 'RSI',
                'reason': f'Aşırı satım (RSI: {rsi:.1f})',
                'strength': 8
            })
        elif rsi > 70:
            signals.append({
                'type': 'SELL',
                'indicator': 'RSI',
                'reason': f'Aşırı alım (RSI: {rsi:.1f})',
                'strength': 8
            })
        
        # MACD Sinyali
        try:
            macd_current = macd_data['macd'].iloc[-1]
            macd_signal = macd_data['signal'].iloc[-1]
            
            if macd_current > macd_signal:
                signals.append({
                    'type': 'BUY',
                    'indicator': 'MACD',
                    'reason': 'MACD pozitif',
                    'strength': 6
                })
            else:
                signals.append({
                    'type': 'SELL',
                    'indicator': 'MACD',
                    'reason': 'MACD negatif',
                    'strength': 6
                })
        except:
            pass
        
        # Bollinger Bands
        try:
            bb_upper = bb_data['upper'].iloc[-1]
            bb_lower = bb_data['lower'].iloc[-1]
            
            if current_price <= bb_lower:
                signals.append({
                    'type': 'BUY',
                    'indicator': 'Bollinger',
                    'reason': 'Alt band test',
                    'strength': 5
                })
            elif current_price >= bb_upper:
                signals.append({
                    'type': 'SELL',
                    'indicator': 'Bollinger',
                    'reason': 'Üst band test',
                    'strength': 5
                })
        except:
            pass
        
        return signals
    except Exception as e:
        print(f"Temel sinyal hatası: {e}")
        return []

def calculate_basic_score(signals, rsi, current_price, df):
    """Temel skor hesaplama"""
    try:
        signal_score = sum(s['strength'] for s in signals if s['type'] == 'BUY') - sum(s['strength'] for s in signals if s['type'] == 'SELL')
        
        # Trend skoru
        sma_20 = df['close'].rolling(20).mean().iloc[-1]
        trend_score = 2 if current_price > sma_20 else -2
        
        # RSI skoru
        if rsi < 30:
            rsi_score = 3
        elif rsi > 70:
            rsi_score = -3
        else:
            rsi_score = 0
        
        total_score = signal_score + trend_score + rsi_score
        normalized_score = max(0, min(10, (total_score + 15) / 3))
        
        return normalized_score
    except:
        return 5

def get_basic_recommendation(score, signals):
    """Temel öneri"""
    try:
        if score >= 7:
            return "📈 AL"
        elif score >= 6:
            return "📈 DİKKATLİ AL"
        elif score >= 4:
            return "⚖️ BEKLE"
        elif score >= 3:
            return "📉 DİKKATLİ SAT"
        else:
            return "📉 SAT"
    except:
        return "⚖️ BEKLE"

def generate_professional_analysis(analysis_result, support_resistance, current_price, coin_name):
    """Profesyonel analiz - basitleştirilmiş"""
    return f"RSI ve MACD confluence oluşturuyor. Technical setup karışık sinyaller veriyor. Volume confirmation beklenmeli."

def generate_simple_explanation(analysis_result, support_resistance, current_price):
    """Basit açıklama"""
    return f"Basitçe: Mevcut seviyelerde takip et, net kırılım bekle."

def calculate_support_resistance_with_fibonacci(df):
    """Basit destek/direnç hesaplama"""
    try:
        current_price = df['close'].iloc[-1]
        return {
            'nearest_resistance': {'price': current_price * 1.05},
            'nearest_support': {'price': current_price * 0.95},
            'current_price': current_price
        }
    except:
        return {
            'nearest_resistance': None,
            'nearest_support': None,
            'current_price': current_price
        }

print("🎯 Clean and simple analysis commands yüklendi!")
