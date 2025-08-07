"""
Clean and Simple Analysis Commands
Sadece 4 timeframe butonu + AI yorumu + Fibonacci dahil
"""

import requests
import telebot
from telebot import types
import pandas as pd
from config import *
from utils.binance_api import find_binance_symbol, get_binance_ohlc
from utils.chart_generator import create_advanced_chart
import openai

# Kullanıcı durumlarını takip etmek için
user_analysis_states = {}

def register_analysis_commands(bot):
    """Temiz ve sade analiz komutlarını bot'a kaydet"""
    
    @bot.message_handler(commands=['analiz'])
    def analiz(message):
        """Ana analiz komutu - Sadece timeframe seçimi"""
        try:
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
            
            # Tam analiz yap (AI + Fibonacci dahil)
            perform_complete_timeframe_analysis(call.message, binance_symbol, coin_input, timeframe, bot)
            
            # Kullanıcı durumunu temizle
            if user_id in user_analysis_states:
                del user_analysis_states[user_id]
                
        except Exception as e:
            print(f"Timeframe selection hatası: {e}")
            bot.answer_callback_query(call.id, "❌ Analiz yapılamadı!")

# =============================================================================
# TAM ANALİZ FONKSİYONU - AI + FİBONACCİ DAHİL
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
        
        # AI yorumu oluştur
        ai_commentary = generate_ai_trading_commentary(df, analysis_result, symbol, timeframe)
        
        # Trading önerileri
        trading_recommendation = generate_trading_recommendation(analysis_result, df, symbol)
        
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
            ai_commentary, 
            trading_recommendation,
            support_resistance,
            coin_input, 
            timeframe
        )
        
        bot.send_message(message.chat.id, complete_analysis_message, parse_mode="Markdown")
            
    except Exception as e:
        print(f"Tam analiz hatası: {e}")
        bot.send_message(message.chat.id, "❌ Analiz tamamlanamadı!")

# =============================================================================
# YENİ MESAJ FORMATI - KAPSAMLI AMA ÖZET
# =============================================================================

def format_complete_analysis_message(analysis_result, ai_commentary, trading_rec, support_resistance, coin_input, timeframe):
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
        mesaj += f"💭 **Ne demek istiyorum?**\n"
        simple_explanation = generate_simple_explanation(analysis_result, support_resistance, price)
        mesaj += f"{simple_explanation}\n\n"
        
        # === ÖNEMLİ SEVİYELER - SADECE EN YAKIN ===
        sr = support_resistance
        mesaj += f"📏 **DİKKAT EDİLECEK FİYATLAR**\n"
        
        # En yakın direnç
        if sr['nearest_resistance']:
            r_price = sr['nearest_resistance']['price']
            mesaj += f"🔴 **Direnç:** ${r_price:,.0f}\n"
        
        # En yakın destek
        if sr['nearest_support']:
            s_price = sr['nearest_support']['price']
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
        mesaj += f"🔧 ⏰ /alarm {coin_input} | 🔄 /analiz {coin_input}\n"
        mesaj += f"⚠️ *Bu tahmin yatırım tavsiyesi değildir!*"
        
        return mesaj
        
    except Exception as e:
        print(f"Mesaj formatla hatası: {e}")
        return "❌ Analiz sonucu formatlanamadı!"

def generate_professional_analysis(analysis_result, support_resistance, current_price, coin_name):
    """Profesyonel ve ikna edici AI analizi"""
    try:
        rsi = analysis_result.get('rsi', 50)
        overall_score = analysis_result.get('overall_score', 5)
        signals = analysis_result.get('signals', [])
        
        # MACD durumu
        macd_data = analysis_result.get('macd_data', {})
        if macd_data and 'macd' in macd_data and len(macd_data['macd']) > 0:
            macd_current = macd_data['macd'].iloc[-1]
            macd_signal = macd_data['signal'].iloc[-1]
            macd_bullish = macd_current > macd_signal
        else:
            macd_bullish = overall_score > 5
        
        # Destek/Direnç seviyeleri
        resistance = None
        support = None
        
        if support_resistance.get('nearest_resistance'):
            resistance = support_resistance['nearest_resistance']['price']
        if support_resistance.get('nearest_support'):
            support = support_resistance['nearest_support']['price']
        
        # Profesyonel analiz oluştur
        analysis = ""
        
        # RSI bazlı durum tespiti
        if rsi > 70:
            # Aşırı alım bölgesi
            analysis += f"RSI {rsi:.0f} seviyesiyle aşırı alım bölgesinde. MACD "
            if macd_bullish:
                analysis += f"hala pozitif momentumu koruyor ancak divergence riski artıyor. "
            else:
                analysis += f"negatif sinyal vererek düzeltme ihtimalini güçlendiriyor. "
            
            if resistance:
                analysis += f"${resistance:,.0f} direnci kritik seviye olarak öne çıkıyor. Bu seviyeden rejection alması halinde "
                target_down = resistance * 0.92
                analysis += f"${target_down:,.0f} seviyelerine kadar teknik düzeltme beklenebilir.\n\n"
            else:
                analysis += f"Kısa vadede %8-12 arası profit-taking baskısı normal karşılanmalı.\n\n"
                
            analysis += f"💡 **Volume patternı** ve **momentum oscillatorları** yakından takip edilmeli. "
            analysis += f"Breaking point yaklaşıyor."
                
        elif rsi < 30:
            # Aşırı satım bölgesi
            analysis += f"RSI {rsi:.0f} ile oversold bölgesinde güçlü reversal sinyali. MACD "
            if macd_bullish:
                analysis += f"bullish crossover ile toparlanma başlangıcını işaret ediyor. "
            else:
                analysis += f"henüz pozitif momentum vermese de RSI ile **positive divergence** oluşabilir. "
            
            if resistance:
                analysis += f"İlk hedef ${resistance:,.0f} direnci. Bu seviye kırılırsa **breakout senaryosu** devreye girebilir ve "
                target_up = resistance * 1.08
                analysis += f"${target_up:,.0f} seviyelerine momentum ile yükseliş olabilir.\n\n"
            else:
                analysis += f"Bu seviyelerden %15-20 **rebound** hareketi teknik olarak beklenir.\n\n"
                
            analysis += f"💡 **Accumulation zone**'dayız. **Smart money** girişleri artabilir."
                
        else:
            # Normal bölge (30-70 arası)
            if overall_score >= 7:
                # Güçlü boğa senaryosu
                analysis += f"RSI {rsi:.0f} ile sağlıklı momentum alanında. MACD "
                if macd_bullish:
                    analysis += f"**golden cross** formasyonu tamamlayarak trend güçlenmesini doğruluyor. "
                else:
                    analysis += f"henüz net sinyal vermese de **higher lows** pattern'ı korunuyor. "
                
                if resistance:
                    analysis += f"${resistance:,.0f} seviyesi **key resistance** olarak öne çıkıyor. Kırılım durumunda **impulse wave** başlayabilir ve "
                    target_up = resistance * 1.12
                    analysis += f"${target_up:,.0f} hedefine **extension** hareketi beklenebilir.\n\n"
                else:
                    analysis += f"Trend devamı senaryosu ağırlık kazanıyor. **Bullish continuation** pattern'ı aktif.\n\n"
                    
                analysis += f"💡 **Volume expansion** ve **institutional flow** takip edilmeli. Momentum güçleniyor."
                    
            elif overall_score <= 3:
                # Zayıf/ayı senaryosu  
                analysis += f"RSI {rsi:.0f} seviyesinde ancak **bearish pressure** hissediliyor. MACD "
                if not macd_bullish:
                    analysis += f"**death cross** formasyonuyla satış baskısını doğruluyor. "
                else:
                    analysis += f"pozitif olsa da **weakening momentum** dikkat çekiyor. "
                
                if support:
                    analysis += f"${support:,.0f} **critical support** seviyesi. Bu seviye kaybedilirse **breakdown** senaryosu aktif hale gelir ve "
                    target_down = support * 0.88
                    analysis += f"${target_down:,.0f} seviyelerine **capitulation** hareketi olabilir.\n\n"
                else:
                    analysis += f"**Bear flag** pattern'ı tamamlanma aşamasında. Aşağı yönlü baskı artıyor.\n\n"
                    
                analysis += f"💡 **Stop-loss** seviyeleri ve **risk management** kritik önemde."
            else:
                # Nötr/belirsiz durum
                analysis += f"RSI {rsi:.0f} ile **consolidation zone**'da. MACD **sideways** hareket ederek belirsizlik yaratıyor. "
                
                if resistance and support:
                    range_percentage = ((resistance - support) / support) * 100
                    analysis += f"${support:,.0f} - ${resistance:,.0f} **trading range**'ı (%{range_percentage:.1f}) içinde **range-bound** hareket. "
                    analysis += f"**Breakout direction** henüz net değil.\n\n"
                else:
                    analysis += f"**Neutral zone**'dayız. **Directional bias** oluşması bekleniyor.\n\n"
                    
                analysis += f"💡 **Volume spike** ve **catalyst event** beklenebilir. **Coiling** formasyonu var."
        
        # Momentum ve sinyal yorumu
        if len(signals) > 0:
            strong_signals = [s for s in signals if s.get('strength', 0) >= 7]
            if strong_signals:
                signal_type = strong_signals[0]['type']
                if signal_type == 'BUY':
                    analysis += f" **Multiple timeframe confluence** bulluş sinyali veriyor."
                else:
                    analysis += f" **Technical indicators** bearish alignment gösteriyor."
            else:
                analysis += f" **Mixed signals** mevcut, **wait-and-see** yaklaşımı mantıklı."
        else:
            analysis += f" **Teknik indikatörler** henüz net pozisyon almamış."
        
        return analysis
        
    except Exception as e:
        print(f"Profesyonel analiz hatası: {e}")
        # Fallback profesyonel yorum
        if resistance:
            return f"Teknik momentum pozitif görünüyor. ${resistance:,.0f} **key resistance** seviyesini kırması durumunda **bullish breakout** senaryosu aktif hale gelebilir. MACD ve RSI **confluence** oluşturuyor.\n\n💡 **Volume confirmation** beklenmeli."
        else:
            return f"**Technical setup** karışık sinyaller veriyor. RSI ve MACD **neutral zone**'da. **Breakout direction** için **catalyst** bekleniyor.\n\n💡 **Risk management** öncelikli."

def generate_simple_explanation(analysis_result, support_resistance, current_price):
    """Profesyonel analizin basit açıklaması - Yani şu demek kısmı"""
    try:
        rsi = analysis_result.get('rsi', 50)
        overall_score = analysis_result.get('overall_score', 5)
        signals = analysis_result.get('signals', [])
        
        # Destek/Direnç seviyeleri
        resistance = None
        support = None
        
        if support_resistance.get('nearest_resistance'):
            resistance = support_resistance['nearest_resistance']['price']
        if support_resistance.get('nearest_support'):
            support = support_resistance['nearest_support']['price']
        
        explanation = ""
        
        # RSI durumuna göre basit açıklama
        if rsi > 70:
            # Aşırı alım
            explanation += f"Fiyat çok yükseldi, biraz dinlenme zamanı. "
            if resistance:
                explanation += f"${resistance:,.0f} seviyesinden geri dönüp "
                if support:
                    explanation += f"${support:,.0f} civarına düzelebilir."
                else:
                    explanation += f"%5-8 kadar düzelebilir."
            else:
                explanation += "Kar satışları artabilir."
                
        elif rsi < 30:
            # Aşırı satım
            explanation += f"Fiyat çok düştü, yükseliş vakti gelebilir. "
            if resistance:
                explanation += f"${resistance:,.0f} seviyesini test eder, kırılırsa güzel yükseliş başlar."
            else:
                explanation += "Bu seviyelerden %10-15 toparlanma olabilir."
                
        else:
            # Normal bölge
            if overall_score >= 7:
                # Pozitif durum
                explanation += f"Teknik görünüm iyi. "
                if resistance:
                    explanation += f"${resistance:,.0f} seviyesini geçerse "
                    next_target = resistance * 1.06
                    explanation += f"${next_target:,.0f} civarına çıkabilir."
                else:
                    explanation += "Yükseliş devam edebilir."
                    
            elif overall_score <= 3:
                # Negatif durum
                explanation += f"Teknik görünüm zayıf. "
                if support:
                    explanation += f"${support:,.0f} desteği kırılırsa "
                    next_down = support * 0.94
                    explanation += f"${next_down:,.0f} seviyesine düşebilir."
                else:
                    explanation += "Düşüş devam edebilir."
            else:
                # Belirsiz durum
                if resistance and support:
                    explanation += f"${support:,.0f} ile ${resistance:,.0f} arasında gidip geliyor. Hangi tarafı kırarsa o tarafa gider."
                else:
                    explanation += "Belirsizlik var. Hangi yöne kırılacak belli değil."
        
        # Sinyal durumu açıklaması
        if len(signals) > 0:
            strong_signals = [s for s in signals if s.get('strength', 0) >= 7]
            if strong_signals:
                signal_type = strong_signals[0]['type']
                if signal_type == 'BUY':
                    explanation += f" Alım sinyalleri güçlü, momentum artabilir."
                else:
                    explanation += f" Satış sinyalleri var, dikkatli ol."
            else:
                explanation += f" Sinyaller karışık, sabır gerekli."
        else:
            explanation += f" Net sinyal yok, beklemek mantıklı."
        
        return explanation
        
    except Exception as e:
        print(f"Basit açıklama hatası: {e}")
        # Fallback açıklama
        if resistance:
            return f"Basitçe: ${resistance:,.0f} seviyesi önemli. Kırarsa yükselir, kıramazsa düzeltme yapar. Takip et."
        else:
            return f"Basitçe: Karışık durum var. Kırılım bekle, sonra hareket et."

# =============================================================================
# DESTEK/DİRENÇ + FİBONACCİ BİRLEŞİK FONKSİYON
# =============================================================================

def calculate_support_resistance_with_fibonacci(df):
    """Destek/Direnç + Fibonacci seviyelerini birleştir ve en yakınları bul"""
    try:
        current_price = df['close'].iloc[-1]
        
        # === TEKNIK DESTEK/DİRENÇ SEVİYELERİ ===
        highs = []
        lows = []
        window = 5
        
        for i in range(window, len(df) - window):
            # Direnç (yerel maksimum)
            if all(df['high'].iloc[i] >= df['high'].iloc[i-j] for j in range(1, window+1)) and \
               all(df['high'].iloc[i] >= df['high'].iloc[i+j] for j in range(1, window+1)):
                highs.append(df['high'].iloc[i])
            
            # Destek (yerel minimum)
            if all(df['low'].iloc[i] <= df['low'].iloc[i-j] for j in range(1, window+1)) and \
               all(df['low'].iloc[i] <= df['low'].iloc[i+j] for j in range(1, window+1)):
                lows.append(df['low'].iloc[i])
        
        # === FİBONACCİ SEVİYELERİ ===
        recent_data = df.tail(50)
        high_price = recent_data['high'].max()
        low_price = recent_data['low'].min()
        diff = high_price - low_price
        
        fib_levels = {
            'Fib 23.6%': high_price - (diff * 0.236),
            'Fib 38.2%': high_price - (diff * 0.382),
            'Fib 50%': high_price - (diff * 0.5),
            'Fib 61.8%': high_price - (diff * 0.618),
        }
        
        # === TÜM SEVİYELERİ BİRLEŞTİR ===
        all_levels = []
        
        # Teknik dirençler
        for level in highs:
            if level > current_price:
                distance = ((level - current_price) / current_price) * 100
                all_levels.append({
                    'price': level,
                    'type': 'Teknik Direnç',
                    'distance': distance,
                    'direction': 'resistance'
                })
        
        # Teknik destekler
        for level in lows:
            if level < current_price:
                distance = ((current_price - level) / current_price) * 100
                all_levels.append({
                    'price': level,
                    'type': 'Teknik Destek',
                    'distance': distance,
                    'direction': 'support'
                })
        
        # Fibonacci seviyeleri
        for fib_name, fib_price in fib_levels.items():
            if fib_price > current_price:
                distance = ((fib_price - current_price) / current_price) * 100
                all_levels.append({
                    'price': fib_price,
                    'type': fib_name,
                    'distance': distance,
                    'direction': 'resistance'
                })
            else:
                distance = ((current_price - fib_price) / current_price) * 100
                all_levels.append({
                    'price': fib_price,
                    'type': fib_name,
                    'distance': distance,
                    'direction': 'support'
                })
        
        # === EN YAKIN SEVİYELERİ BUL ===
        resistance_levels = [l for l in all_levels if l['direction'] == 'resistance']
        support_levels = [l for l in all_levels if l['direction'] == 'support']
        
        # Mesafeye göre sırala
        resistance_levels.sort(key=lambda x: x['distance'])
        support_levels.sort(key=lambda x: x['distance'])
        
        return {
            'nearest_resistance': resistance_levels[0] if resistance_levels else None,
            'nearest_support': support_levels[0] if support_levels else None,
            'current_price': current_price
        }
        
    except Exception as e:
        print(f"Destek/Direnç+Fib hesaplama hatası: {e}")
        return {
            'nearest_resistance': None,
            'nearest_support': None,
            'current_price': df['close'].iloc[-1]
        }

# =============================================================================
# TEKNİK ANALİZ FONKSİYONLARI (ÖNCEKİ KODDAN)
# =============================================================================

# Diğer gerekli import edilmiş fonksiyonlar
from utils.technical_analysis import (
    calculate_rsi, calculate_macd, calculate_bollinger_bands
)

def calculate_stochastic(df, k_period=14, d_period=3):
    """Stochastic Oscillator hesapla"""
    try:
        high_max = df['high'].rolling(window=k_period).max()
        low_min = df['low'].rolling(window=k_period).min()
        
        k_percent = ((df['close'] - low_min) / (high_max - low_min)) * 100
        d_percent = k_percent.rolling(window=d_period).mean()
        
        return {
            'k_percent': k_percent,
            'd_percent': d_percent
        }
    except Exception as e:
        print(f"Stochastic hesaplama hatası: {e}")
        return {
            'k_percent': pd.Series(index=df.index, dtype=float),
            'd_percent': pd.Series(index=df.index, dtype=float)
        }

def calculate_signal_strength(df, rsi, macd_data, bb_data, stoch_data):
    """Her sinyal için güç skoru (1-10) hesapla"""
    try:
        signals = []
        current_price = df['close'].iloc[-1]
        
        # RSI Sinyali
        if rsi < 30:
            strength = min(10, (30 - rsi) / 3)
            signals.append({
                'type': 'BUY',
                'indicator': 'RSI',
                'reason': f'Aşırı satım (RSI: {rsi:.1f})',
                'strength': round(strength),
                'confidence': 'Yüksek' if strength >= 7 else 'Orta' if strength >= 5 else 'Düşük'
            })
        elif rsi > 70:
            strength = min(10, (rsi - 70) / 3)
            signals.append({
                'type': 'SELL',
                'indicator': 'RSI',
                'reason': f'Aşırı alım (RSI: {rsi:.1f})',
                'strength': round(strength),
                'confidence': 'Yüksek' if strength >= 7 else 'Orta' if strength >= 5 else 'Düşük'
            })
        
        # MACD Sinyali
        try:
            macd_current = macd_data['macd'].iloc[-1]
            macd_signal = macd_data['signal'].iloc[-1]
            macd_prev = macd_data['macd'].iloc[-2]
            signal_prev = macd_data['signal'].iloc[-2]
            
            if macd_current > macd_signal and macd_prev <= signal_prev:
                signals.append({
                    'type': 'BUY',
                    'indicator': 'MACD',
                    'reason': 'MACD pozitif kesişim',
                    'strength': 7,
                    'confidence': 'Yüksek'
                })
            elif macd_current < macd_signal and macd_prev >= signal_prev:
                signals.append({
                    'type': 'SELL',
                    'indicator': 'MACD',
                    'reason': 'MACD negatif kesişim',
                    'strength': 7,
                    'confidence': 'Yüksek'
                })
        except:
            pass
        
        # Bollinger Bands Sinyali
        try:
            bb_upper = bb_data['upper'].iloc[-1]
            bb_lower = bb_data['lower'].iloc[-1]
            
            if current_price <= bb_lower:
                signals.append({
                    'type': 'BUY',
                    'indicator': 'Bollinger',
                    'reason': 'Alt band test',
                    'strength': 6,
                    'confidence': 'Orta'
                })
            elif current_price >= bb_upper:
                signals.append({
                    'type': 'SELL',
                    'indicator': 'Bollinger',
                    'reason': 'Üst band test',
                    'strength': 6,
                    'confidence': 'Orta'
                })
        except:
            pass
        
        return signals
    except Exception as e:
        print(f"Sinyal gücü hesaplama hatası: {e}")
        return []

def perform_comprehensive_analysis(df, symbol, timeframe):
    """Kapsamlı teknik analiz"""
    try:
        current_price = df['close'].iloc[-1]
        
        # Temel indikatörler
        rsi = calculate_rsi(df['close']).iloc[-1]
        macd_data = calculate_macd(df['close'])
        bb_data = calculate_bollinger_bands(df['close'])
        stoch_data = calculate_stochastic(df)
        
        # Sinyal gücü analizi
        signals = calculate_signal_strength(df, rsi, macd_data, bb_data, stoch_data)
        
        # Entry/Exit noktaları
        entry_exit = calculate_entry_exit_points(df, current_price, bb_data, signals)
        
        # Trend gücü
        trend_strength = calculate_trend_strength_advanced(df)
        
        # Risk analizi
        risk_analysis = calculate_risk_metrics(df, signals)
        
        # Genel skor
        overall_score = calculate_comprehensive_score(signals, trend_strength, risk_analysis)
        
        return {
            'symbol': symbol,
            'timeframe': timeframe,
            'price': current_price,
            'rsi': rsi,
            'macd_data': macd_data,
            'bb_data': bb_data,
            'stoch_data': stoch_data,
            'signals': signals,
            'entry_exit': entry_exit,
            'trend_strength': trend_strength,
            'risk_analysis': risk_analysis,
            'overall_score': overall_score,
            'recommendation': get_comprehensive_recommendation(overall_score, signals)
        }
    except Exception as e:
        print(f"Kapsamlı analiz hatası: {e}")
        return {}

# Diğer yardımcı fonksiyonlar (önceki koddan kopyala)
def calculate_entry_exit_points(df, current_price, bb_data, signals):
    """Net entry/exit noktaları hesapla"""
    try:
        buy_signals = [s for s in signals if s['type'] == 'BUY']
        sell_signals = [s for s in signals if s['type'] == 'SELL']
        
        buy_strength = sum(s['strength'] for s in buy_signals)
        sell_strength = sum(s['strength'] for s in sell_signals)
        
        entry_exit_points = {
            'current_price': current_price,
            'action': 'BUY' if buy_strength > sell_strength else 'SELL' if sell_strength > buy_strength else 'HOLD',
            'confidence': abs(buy_strength - sell_strength),
            'entry_points': [],
            'stop_loss': current_price * 0.95,
            'take_profit': current_price * 1.05
        }
        
        return entry_exit_points
    except Exception as e:
        print(f"Entry/Exit hesaplama hatası: {e}")
        return {}

def calculate_comprehensive_score(signals, trend_strength, risk_analysis):
    """Kapsamlı skor hesapla"""
    try:
        signal_score = sum(s['strength'] for s in signals if s['type'] == 'BUY') - sum(s['strength'] for s in signals if s['type'] == 'SELL')
        signal_score = max(-10, min(10, signal_score))
        
        trend_score = trend_strength.get('score', 0)
        risk_score = 10 - risk_analysis.get('risk_level', 5)
        
        weighted_score = (signal_score * 0.4 + trend_score * 0.4 + risk_score * 0.2)
        normalized_score = (weighted_score + 10) / 2
        
        return max(0, min(10, normalized_score))
    except:
        return 5

def get_comprehensive_recommendation(score, signals):
    """Kapsamlı öneri ver"""
    try:
        buy_signals = len([s for s in signals if s['type'] == 'BUY'])
        sell_signals = len([s for s in signals if s['type'] == 'SELL'])
        
        if score >= 8:
            return "🚀 GÜÇLÜ AL"
        elif score >= 7:
            return "📈 AL"
        elif score >= 6:
            return "📈 ZAYIF AL" if buy_signals > sell_signals else "⚖️ BEKLE"
        elif score >= 4:
            return "⚖️ BEKLE"
        elif score >= 3:
            return "📉 ZAYIF SAT"
        elif score >= 2:
            return "📉 SAT"
        else:
            return "🔻 GÜÇLÜ SAT"
    except:
        return "⚖️ BEKLE"

def calculate_trend_strength_advanced(df):
    """Gelişmiş trend gücü hesapla"""
    try:
        current_price = df['close'].iloc[-1]
        
        sma_5 = df['close'].rolling(5).mean().iloc[-1]
        sma_10 = df['close'].rolling(10).mean().iloc[-1]
        sma_20 = df['close'].rolling(20).mean().iloc[-1]
        sma_50 = df['close'].rolling(50).mean().iloc[-1]
        
        trend_score = 0
        if current_price > sma_5: trend_score += 2
        if current_price > sma_10: trend_score += 2
        if current_price > sma_20: trend_score += 2
        if current_price > sma_50: trend_score += 2
        if sma_5 > sma_10: trend_score += 1
        if sma_10 > sma_20: trend_score += 1
        
        momentum = ((current_price - df['close'].iloc[-10]) / df['close'].iloc[-10]) * 100
        
        return {
            'score': min(10, trend_score),
            'direction': 'BULLISH' if trend_score >= 6 else 'BEARISH' if trend_score <= 3 else 'NEUTRAL',
            'momentum': momentum,
            'strength': 'Güçlü' if trend_score >= 8 else 'Orta' if trend_score >= 5 else 'Zayıf'
        }
    except:
        return {'score': 5, 'direction': 'NEUTRAL', 'momentum': 0, 'strength': 'Orta'}

def calculate_risk_metrics(df, signals):
    """Risk metriklerini hesapla"""
    try:
        returns = df['close'].pct_change().dropna()
        volatility = returns.std() * 100
        
        rolling_max = df['close'].expanding().max()
        drawdown = (df['close'] - rolling_max) / rolling_max * 100
        max_drawdown = abs(drawdown.min())
        
        signal_consistency = len([s for s in signals if s['confidence'] == 'Yüksek']) / max(len(signals), 1)
        
        if volatility > 8 or max_drawdown > 20:
            risk_level = 8
        elif volatility > 5 or max_drawdown > 10:
            risk_level = 6
        else:
            risk_level = 3
        
        return {
            'volatility': volatility,
            'max_drawdown': max_drawdown,
            'risk_level': risk_level,
            'signal_consistency': signal_consistency,
            'risk_description': 'Yüksek' if risk_level >= 7 else 'Orta' if risk_level >= 4 else 'Düşük'
        }
    except:
        return {'volatility': 5, 'max_drawdown': 10, 'risk_level': 5, 'signal_consistency': 0.5, 'risk_description': 'Orta'}

def generate_ai_trading_commentary(df, analysis_result, symbol, timeframe):
    """AI ile trading yorumu oluştur - UZUN VERSİYON"""
    try:
        if not OPENAI_API_KEY or OPENAI_API_KEY == "BURAYA_OPENAI_KEYINI_YAZ":
            return "🤖 AI yorumu için OpenAI API key gerekli!"
        
        current_price = df['close'].iloc[-1]
        rsi = analysis_result.get('rsi', 50)
        overall_score = analysis_result.get('overall_score', 5)
        
        # MACD durumu
        macd_data = analysis_result.get('macd_data', {})
        if macd_data and 'macd' in macd_data and len(macd_data['macd']) > 0:
            macd_current = macd_data['macd'].iloc[-1]
            macd_signal = macd_data['signal'].iloc[-1]
            macd_status = "Bullish" if macd_current > macd_signal else "Bearish"
        else:
            macd_status = "Neutral"
        
        # Volume analizi
        avg_volume = df['volume'].tail(20).mean()
        recent_volume = df['volume'].tail(3).mean()
        volume_trend = "Yüksek" if recent_volume > avg_volume * 1.2 else "Normal" if recent_volume > avg_volume * 0.8 else "Düşük"
        
        # Trend yönü
        sma20 = df['close'].rolling(20).mean().iloc[-1]
        trend_direction = "Yükseliş" if current_price > sma20 else "Düşüş"
        
        prompt = f"""
Sen profesyonel kripto trading analisti ve uzmanısın. {symbol} için {timeframe} timeframe'inde detaylı analiz yapıyorsun.

Mevcut Durum:
- Fiyat: ${current_price:,.2f}
- RSI: {rsi:.1f}
- MACD: {macd_status}
- Volume: {volume_trend}
- Trend: {trend_direction}
- Teknik Skor: {overall_score:.1f}/10

DETAYLI yorum yap (300-400 kelime):

📊 Teknik Durum: (Bullish/Bearish/Nötr ve detayı)
💭 Piyasa Analizi: (Mevcut durumun detaylı açıklaması, neden böyle olduğu, hangi faktörler etkili)
🎯 Kısa Vadeli Beklenti: (Bu timeframe'de ne beklenebilir, hangi seviyelere odaklanmalı)
📈 Orta Vadeli Görünüm: (Genel trend nasıl gelişebilir)
⚠️ Risk Faktörleri: (Dikkat edilmesi gereken noktalar)
💡 Trading Stratejisi: (Bu durumda nasıl yaklaşılmalı)

Trading dili kullan, detaylı ve profesyonel ol ama anlaşılır yaz. Teknik indikatörlerin neden bu sonuçları verdiğini açıkla.
"""

        client = openai.OpenAI(api_key=OPENAI_API_KEY)
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Sen uzman kripto trader ve analisti sin. Detaylı, kapsamlı ve profesyonel analizler yaparsın."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=600,
            temperature=0.7
        )
        
        return response.choices[0].message.content
        
    except Exception as e:
        print(f"AI yorum hatası: {e}")
        # Fallback detaylı yorum
        score = analysis_result.get('overall_score', 5)
        rsi = analysis_result.get('rsi', 50)
        
        if score >= 7:
            return f"""📊 Teknik Durum: Güçlü Bullish
💭 Piyasa Analizi: RSI {rsi:.1f} seviyesinde ve teknik indikatörler güçlü alım sinyalleri veriyor. Volume artışı momentum destekliyor. Fiyat önemli direnç seviyelerini test ediyor ve yukarı yönlü hareket potansiyeli yüksek.
🎯 Kısa Vadeli: Yükseliş trendinin devam etmesi bekleniyor. Üst direnç seviyelerinin kırılması durumunda güçlü ralliler görülebilir.
📈 Orta Vadeli: Boğa trendinin sürdürülebilirliği yüksek. Ancak aşırı alım riski yakın takipte.
⚠️ Risk: Aşırı alım bölgesine yaklaşılıyor. Kar realizasyonu için dikkatli olunmalı.
💡 Strateji: Kademeli alım, sıkı stop-loss ile pozisyon büyütme."""
        elif score <= 3:
            return f"""📊 Teknik Durum: Güçlü Bearish
💭 Piyasa Analizi: RSI {rsi:.1f} ile düşük seviyelerde ve satış baskısı ağır basıyor. Teknik indikatörler düşüş sinyali veriyor. Volume ile desteklenen satışlar trend değişimine işaret ediyor.
🎯 Kısa Vadeli: Düşüş trendinin devam etmesi muhtemel. Alt destek seviyelerinin kırılması durumunda hızlı düşüşler beklenebilir.
📈 Orta Vadeli: Ayı trendi hakimiyetini sürdürüyor. Toparlanma sinyalleri için alt seviyelerde beklemek mantıklı.
⚠️ Risk: Momentumun kaybolması durumunda daha derin düşüşler görülebilir.
💡 Strateji: Nakit beklemede, güçlü destek seviyelerinde dikkatli pozisyon alma."""
        else:
            return f"""📊 Teknik Durum: Nötr/Kararsız
💭 Piyasa Analizi: RSI {rsi:.1f} ile orta seviyelerde ve piyasada belirsizlik hakim. Alıcı ve satıcılar arasında denge mevcut. Volume düşük ve yön tespiti zorlaşıyor.
🎯 Kısa Vadeli: Dar bantta hareket bekleniyor. Önemli seviyelerden kırılım yönü takip edilmeli.
📈 Orta Vadeli: Trend belirlenmesi için katalizer beklenirken yan yana hareket sürebilir.
⚠️ Risk: Sahte kırılımlar olabilir. Stop-loss mesafeleri geniş tutulmalı.
💡 Strateji: Beklemede kalın, net sinyal gelene kadar pozisyon almayın."""

def generate_trading_recommendation(analysis_result, df, symbol):
    """Trading önerisi oluştur"""
    try:
        current_price = df['close'].iloc[-1]
        signals = analysis_result.get('signals', [])
        overall_score = analysis_result.get('overall_score', 5)
        
        strong_buy_signals = len([s for s in signals if s['type'] == 'BUY' and s['strength'] >= 7])
        strong_sell_signals = len([s for s in signals if s['type'] == 'SELL' and s['strength'] >= 7])
        
        if overall_score >= 8 and strong_buy_signals > 0:
            action = "LONG AÇ"
            reason = f"{strong_buy_signals} güçlü alım sinyali"
            confidence = "Yüksek"
            emoji = "🚀"
        elif overall_score >= 6.5:
            action = "DİKKATLİ LONG"
            reason = "Orta güçlü sinyaller"
            confidence = "Orta"
            emoji = "📈"
        elif overall_score <= 2 and strong_sell_signals > 0:
            action = "SHORT AÇ"
            reason = f"{strong_sell_signals} güçlü satış sinyali"
            confidence = "Yüksek"
            emoji = "📉"
        elif overall_score <= 3.5:
            action = "DİKKATLİ SHORT"
            reason = "Zayıflık sinyalleri"
            confidence = "Orta"
            emoji = "🔻"
        else:
            action = "BEKLE"
            reason = "Karışık sinyaller"
            confidence = "Düşük"
            emoji = "⚖️"
        
        if "LONG" in action:
            entry_price = current_price
            stop_loss = current_price * 0.97
            take_profit = current_price * 1.06
            risk_reward = (take_profit - entry_price) / (entry_price - stop_loss)
        elif "SHORT" in action:
            entry_price = current_price
            stop_loss = current_price * 1.03
            take_profit = current_price * 0.94
            risk_reward = (entry_price - take_profit) / (stop_loss - entry_price)
        else:
            entry_price = current_price
            stop_loss = None
            take_profit = None
            risk_reward = 0
        
        return {
            'action': action,
            'emoji': emoji,
            'reason': reason,
            'confidence': confidence,
            'entry_price': entry_price,
            'stop_loss': stop_loss,
            'take_profit': take_profit,
            'risk_reward': risk_reward
        }
        
    except Exception as e:
        print(f"Trading öneri hatası: {e}")
        return {
            'action': 'BEKLE',
            'emoji': '⚖️',
            'reason': 'Analiz tamamlanamadı',
            'confidence': 'Düşük',
            'entry_price': df['close'].iloc[-1],
            'stop_loss': None,
            'take_profit': None,
            'risk_reward': 0
        }

print("🎯 Clean and simple analysis commands yüklendi!")
