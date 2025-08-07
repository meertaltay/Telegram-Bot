"""
Simplified Analysis Commands - Tek komut sistemi
/analiz - Tüm analiz türlerini içerir
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
    """Basitleştirilmiş analiz komutlarını bot'a kaydet"""
    
    @bot.message_handler(commands=['analiz'])
    def analiz(message):
        """Ana analiz komutu - Tüm analiz türleri"""
        try:
            parts = message.text.strip().split()
            if len(parts) < 2:
                bot.send_message(message.chat.id, 
                    "📊 **Gelişmiş Kripto Analiz**\n\n"
                    "🔹 **Kullanım:** /analiz COIN\n\n"
                    "**Örnekler:**\n"
                    "• /analiz btc\n"
                    "• /analiz eth\n"
                    "• /analiz sol\n\n"
                    "📈 Coin seçtikten sonra analiz türü seçebilirsiniz!",
                    parse_mode="Markdown")
                return

            coin_input = parts[1].lower()
            
            # Binance sembolü bul
            binance_symbol = find_binance_symbol(coin_input)
            
            if not binance_symbol:
                bot.send_message(message.chat.id, 
                    f"❌ **'{coin_input.upper()}' Binance'da bulunamadı!**\n\n"
                    f"💡 **Popüler:** BTC, ETH, SOL, DOGE, ADA\n\n"
                    f"💰 *Fiyat için:* /fiyat {coin_input}",
                    parse_mode="Markdown")
                return

            # Kullanıcı durumunu kaydet
            user_analysis_states[message.from_user.id] = {
                'coin': coin_input,
                'symbol': binance_symbol,
                'chat_id': message.chat.id
            }

            # Ana analiz menüsü oluştur
            markup = types.InlineKeyboardMarkup(row_width=2)
            
            # Timeframe butonları
            btn_1h = types.InlineKeyboardButton("📊 1 Saat", callback_data=f"tf_1h_{coin_input}")
            btn_4h = types.InlineKeyboardButton("📈 4 Saat", callback_data=f"tf_4h_{coin_input}")
            btn_1d = types.InlineKeyboardButton("📉 1 Gün", callback_data=f"tf_1d_{coin_input}")
            btn_1w = types.InlineKeyboardButton("📅 1 Hafta", callback_data=f"tf_1w_{coin_input}")
            
            # Özel analiz butonları
            btn_multi = types.InlineKeyboardButton("🔥 Çoklu TF", callback_data=f"multi_{coin_input}")
            btn_ai = types.InlineKeyboardButton("🤖 AI Tahmin", callback_data=f"ai_{coin_input}")
            btn_signals = types.InlineKeyboardButton("🎯 Sinyaller", callback_data=f"signals_{coin_input}")
            btn_fib = types.InlineKeyboardButton("📐 Fibonacci", callback_data=f"fib_{coin_input}")
            
            # Buton dizilimi
            markup.add(btn_1h, btn_4h)
            markup.add(btn_1d, btn_1w)
            markup.add(btn_multi, btn_ai)
            markup.add(btn_signals, btn_fib)
            
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
                        price_str = f"${current_price:,.4f}"
                    
                    change_emoji = "📈" if change_24h > 0 else "📉"
                    change_color = "🟢" if change_24h > 0 else "🔴"
                    
                    price_info = f"\n💰 **Güncel:** {price_str} | {change_color} %{change_24h:+.2f} {change_emoji}\n"
                else:
                    price_info = ""
            except:
                price_info = ""

            coin_name = binance_symbol.replace('USDT', '').upper()
            
            bot.send_message(
                message.chat.id,
                f"🎯 **{coin_name} - Gelişmiş Analiz**{price_info}\n"
                f"📊 **Hangi analizi istiyorsunuz?**\n\n"
                f"**⏰ Timeframe Analizi:**\n"
                f"🔹 1 Saat - Scalping & Kısa vadeli\n"
                f"🔹 4 Saat - Günlük pozisyonlar\n" 
                f"🔹 1 Gün - Swing trading\n"
                f"🔹 1 Hafta - Uzun vadeli yatırım\n\n"
                f"**🚀 Özel Analizler:**\n"
                f"🔹 Çoklu TF - Tüm timeframe'ler\n"
                f"🔹 AI Tahmin - Fiyat tahmini\n"
                f"🔹 Sinyaller - Trading sinyalleri\n"
                f"🔹 Fibonacci - Retracement seviyeleri\n\n"
                f"👇 **Bir seçenek tıklayın:**",
                reply_markup=markup,
                parse_mode="Markdown"
            )
            
        except Exception as e:
            print(f"Analiz komutu hatası: {e}")
            bot.send_message(message.chat.id, "❌ Analiz başlatılamadı! Tekrar dene.")

    # Callback handler for all analysis types
    @bot.callback_query_handler(func=lambda call: call.data.startswith(('tf_', 'multi_', 'ai_', 'signals_', 'fib_')))
    def handle_analysis_selection(call):
        """Analiz seçimi işle"""
        try:
            # Callback data parse et
            if call.data.startswith('tf_'):
                # Timeframe analizi: tf_1h_btc
                parts = call.data.split('_')
                timeframe = parts[1]
                coin_input = parts[2]
                analysis_type = "timeframe"
            else:
                # Özel analizler: multi_btc, ai_btc, etc.
                parts = call.data.split('_')
                analysis_type = parts[0]
                coin_input = parts[1]
                timeframe = "1d"  # Default
            
            user_id = call.from_user.id
            
            # Kullanıcı durumu kontrol et
            if user_id not in user_analysis_states:
                bot.answer_callback_query(call.id, "⚠️ Lütfen /analiz komutu ile başlayın!")
                return
            
            user_state = user_analysis_states[user_id]
            binance_symbol = user_state['symbol']
            
            # Buton cevabı ver
            analysis_names = {
                'tf_1h': '1 Saatlik Teknik Analiz',
                'tf_4h': '4 Saatlik Teknik Analiz', 
                'tf_1d': '1 Günlük Teknik Analiz',
                'tf_1w': '1 Haftalık Teknik Analiz',
                'multi': 'Çoklu Timeframe Analizi',
                'ai': 'AI Fiyat Tahmini',
                'signals': 'Trading Sinyalleri',
                'fib': 'Fibonacci Analizi'
            }
            
            analysis_key = f"{analysis_type}_{timeframe}" if analysis_type == "timeframe" else analysis_type
            analysis_name = analysis_names.get(analysis_key, 'Analiz')
            
            bot.answer_callback_query(call.id, f"🎯 {analysis_name} başlıyor...")
            
            # Mesajı güncelle
            bot.edit_message_text(
                f"⏳ **{binance_symbol} - {analysis_name}**\n\n"
                f"📊 Veriler alınıyor...\n"
                f"🤖 AI yorumu hazırlanıyor...\n"
                f"📈 Grafik oluşturuluyor...\n\n"
                f"⚡ Bu işlem 10-15 saniye sürebilir.",
                call.message.chat.id,
                call.message.message_id,
                parse_mode="Markdown"
            )
            
            # Analiz tipine göre işlem yap
            if analysis_type == "timeframe":
                perform_timeframe_analysis(call.message, binance_symbol, coin_input, timeframe, bot)
            elif analysis_type == "multi":
                perform_multi_timeframe_analysis(call.message, binance_symbol, coin_input, bot)
            elif analysis_type == "ai":
                perform_ai_prediction(call.message, binance_symbol, coin_input, bot)
            elif analysis_type == "signals":
                perform_signals_analysis(call.message, binance_symbol, coin_input, bot)
            elif analysis_type == "fib":
                perform_fibonacci_analysis(call.message, binance_symbol, coin_input, bot)
            
            # Kullanıcı durumunu temizle
            if user_id in user_analysis_states:
                del user_analysis_states[user_id]
                
        except Exception as e:
            print(f"Analysis selection hatası: {e}")
            bot.answer_callback_query(call.id, "❌ Analiz yapılamadı!")

# =============================================================================
# ANALİZ FONKSİYONLARI
# =============================================================================

def perform_timeframe_analysis(message, symbol, coin_input, timeframe, bot):
    """Timeframe analizi - 2 mesaj halinde"""
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
        
        # Destek/Direnç seviyeleri
        support_resistance = calculate_support_resistance_levels(df)
        
        # 1. MESAJ: GRAFİK
        chart_img = create_advanced_chart(df, symbol, analysis_result, timeframe)
        
        if chart_img:
            timeframe_names = {'1h': '1 Saat', '4h': '4 Saat', '1d': '1 Gün', '1w': '1 Hafta'}
            tf_name = timeframe_names.get(timeframe, timeframe)
            
            bot.send_photo(
                message.chat.id, 
                chart_img, 
                caption=f"📊 **{symbol} - {tf_name} Teknik Analiz Grafiği**",
                parse_mode="Markdown"
            )
        
        # 2. MESAJ: DETAYLI ANALİZ
        analysis_message = format_detailed_analysis_message(
            analysis_result, 
            ai_commentary, 
            trading_recommendation,
            support_resistance,
            coin_input, 
            timeframe
        )
        
        bot.send_message(message.chat.id, analysis_message, parse_mode="Markdown")
            
    except Exception as e:
        print(f"Timeframe analiz hatası: {e}")
        bot.send_message(message.chat.id, "❌ Analiz tamamlanamadı!")

def perform_multi_timeframe_analysis(message, symbol, coin_input, bot):
    """Çoklu timeframe analizi"""
    try:
        bot.send_message(message.chat.id, f"📊 {symbol} çoklu timeframe analizi başlıyor...")
        
        # Çoklu timeframe analizi
        timeframe_results = analyze_multiple_timeframes(symbol)
        
        if not timeframe_results:
            bot.send_message(message.chat.id, "❌ Çoklu timeframe analizi yapılamadı!")
            return
        
        # Sonuçları formatla
        multi_tf_message = format_multi_timeframe_message(timeframe_results, coin_input)
        bot.send_message(message.chat.id, multi_tf_message, parse_mode="Markdown")
        
    except Exception as e:
        print(f"Multi timeframe hatası: {e}")
        bot.send_message(message.chat.id, "❌ Çoklu timeframe analizi yapılamadı!")

def perform_ai_prediction(message, symbol, coin_input, bot):
    """AI fiyat tahmini"""
    try:
        bot.send_message(message.chat.id, f"🤖 {symbol} AI tahmini oluşturuluyor...")
        
        # AI tahmini
        prediction = generate_ai_prediction(symbol, coin_input, 7)
        
        if prediction:
            bot.send_message(message.chat.id, prediction, parse_mode="Markdown")
        else:
            bot.send_message(message.chat.id, "❌ AI tahmini oluşturulamadı!")
            
    except Exception as e:
        print(f"AI tahmin hatası: {e}")
        bot.send_message(message.chat.id, "❌ AI tahmini yapılamadı!")

def perform_signals_analysis(message, symbol, coin_input, bot):
    """Trading sinyalleri analizi"""
    try:
        bot.send_message(message.chat.id, f"🎯 {symbol} sinyalleri analiz ediliyor...")
        
        # Multi-timeframe sinyal analizi
        signals_analysis = generate_comprehensive_signals(symbol)
        
        if signals_analysis:
            signals_message = format_signals_message(signals_analysis, coin_input)
            bot.send_message(message.chat.id, signals_message, parse_mode="Markdown")
        else:
            bot.send_message(message.chat.id, "❌ Sinyal analizi yapılamadı!")
            
    except Exception as e:
        print(f"Sinyal analizi hatası: {e}")
        bot.send_message(message.chat.id, "❌ Sinyal analizi yapılamadı!")

def perform_fibonacci_analysis(message, symbol, coin_input, bot):
    """Fibonacci analizi"""
    try:
        bot.send_message(message.chat.id, f"📐 {symbol} Fibonacci analizi...")
        
        df = get_binance_ohlc(symbol, interval="1d", limit=100)
        if df is None or df.empty:
            bot.send_message(message.chat.id, "❌ Veri alınamadı!")
            return

        # Fibonacci seviyeleri
        fib_levels = calculate_fibonacci_levels(df)
        current_price = df['close'].iloc[-1]
        
        # Fibonacci mesajı
        fib_message = format_fibonacci_message(fib_levels, current_price, coin_input)
        bot.send_message(message.chat.id, fib_message, parse_mode="Markdown")
        
    except Exception as e:
        print(f"Fibonacci analiz hatası: {e}")
        bot.send_message(message.chat.id, "❌ Fibonacci analizi yapılamadı!")

# =============================================================================
# MESAJ FORMATLAMA FONKSİYONLARI
# =============================================================================

def format_detailed_analysis_message(analysis_result, ai_commentary, trading_rec, support_resistance, coin_input, timeframe):
    """Detaylı analiz mesajı - 2. mesaj için"""
    try:
        # Temel bilgiler
        price = analysis_result['price']
        rsi = analysis_result['rsi']
        overall_score = analysis_result['overall_score']
        
        # Fiyat formatı
        if price < 0.01:
            price_str = f"${price:.8f}"
        elif price < 1:
            price_str = f"${price:.6f}"
        else:
            price_str = f"${price:,.4f}"
        
        # Timeframe adı
        timeframe_names = {'1h': '1 Saat', '4h': '4 Saat', '1d': '1 Gün', '1w': '1 Hafta'}
        tf_name = timeframe_names.get(timeframe, timeframe)
        
        mesaj = f"📊 **{coin_input.upper()} - {tf_name} Detay Analiz**\n\n"
        
        # === TEMel VERİLER ===
        mesaj += f"💰 **Güncel Fiyat:** {price_str}\n"
        mesaj += f"📈 **RSI:** {rsi:.1f} | **Teknik Skor:** {overall_score:.1f}/10\n\n"
        
        # === AI YORUMU ===
        mesaj += f"🤖 **AI ANALİZİ**\n"
        ai_clean = ai_commentary.replace("**", "").replace("📊", "").replace("💭", "").replace("🎯", "").replace("⚠️", "")
        mesaj += f"{ai_clean[:200]}...\n\n"
        
        # === TRADİNG ÖNERİSİ ===
        tr = trading_rec
        mesaj += f"💼 **TRADİNG ÖNERİSİ**\n"
        mesaj += f"{tr['emoji']} **Ben olsam:** {tr['action']}\n"
        mesaj += f"📝 **Sebep:** {tr['reason']}\n"
        mesaj += f"🎯 **Güven:** {tr['confidence']}\n\n"
        
        if tr['stop_loss'] and tr['take_profit']:
            mesaj += f"**💡 Pozisyon Detayları:**\n"
            mesaj += f"🟢 Entry: ${tr['entry_price']:.4f}\n"
            mesaj += f"🔴 Stop: ${tr['stop_loss']:.4f}\n"
            mesaj += f"🎯 Target: ${tr['take_profit']:.4f}\n"
            mesaj += f"⚖️ R/R: {tr['risk_reward']:.1f}\n\n"
        
        # === DESTEK & DİRENÇ ===
        sr = support_resistance
        mesaj += f"📏 **DESTEK & DİRENÇ SEVİYELERİ**\n"
        
        if sr['resistance_levels']:
            r1 = sr['resistance_levels'][0]
            r_dist = ((r1 - price) / price) * 100
            mesaj += f"🔴 **En yakın direnç:** ${r1:.4f} (+%{r_dist:.1f})\n"
        
        if sr['support_levels']:
            s1 = sr['support_levels'][0]
            s_dist = ((price - s1) / price) * 100
            mesaj += f"🟢 **En yakın destek:** ${s1:.4f} (-%{s_dist:.1f})\n\n"
        
        # === TREND DURUMU ===
        signals = analysis_result.get('signals', [])
        buy_count = len([s for s in signals if s['type'] == 'BUY'])
        sell_count = len([s for s in signals if s['type'] == 'SELL'])
        
        if buy_count > sell_count:
            trend_status = "🐂 **BULLISH TREND**"
            trend_desc = "Alıcılar kontrolde"
        elif sell_count > buy_count:
            trend_status = "🐻 **BEARISH TREND**"
            trend_desc = "Satıcılar kontrolde"
        else:
            trend_status = "⚖️ **NEUTRAL TREND**"
            trend_desc = "Belirsizlik hakim"
        
        mesaj += f"📈 **TREND ANALİZİ**\n"
        mesaj += f"{trend_status}\n"
        mesaj += f"📊 {trend_desc}\n"
        mesaj += f"🎯 Alım: {buy_count} | Satım: {sell_count}\n\n"
        
        # === DİĞER KOMUTLAR ===
        mesaj += f"🔧 **DİĞER ANALİZLER**\n"
        mesaj += f"⏰ Alarm: /alarm {coin_input}\n"
        mesaj += f"📊 Yeni analiz: /analiz {coin_input}\n\n"
        
        mesaj += f"⚠️ *Bu analiz yatırım tavsiyesi değildir!*"
        
        return mesaj
        
    except Exception as e:
        print(f"Detaylı mesaj formatla hatası: {e}")
        return "❌ Analiz sonucu formatlanamadı!"

def format_multi_timeframe_message(timeframe_results, coin_input):
    """Çoklu timeframe mesajını formatla"""
    try:
        mesaj = f"📊 **{coin_input.upper()} - Çoklu Timeframe Analizi**\n\n"
        
        timeframes = ['1h', '4h', '1d', '1w']
        timeframe_names = {'1h': '1 Saat', '4h': '4 Saat', '1d': '1 Gün', '1w': '1 Hafta'}
        
        for tf in timeframes:
            if tf in timeframe_results:
                result = timeframe_results[tf]
                score = result.get('overall_score', 5)
                trend = result.get('trend', 'NEUTRAL')
                
                # Emoji seçimi
                if score >= 7:
                    emoji = "🚀"
                elif score >= 6:
                    emoji = "📈"
                elif score >= 4:
                    emoji = "⚖️"
                elif score >= 3:
                    emoji = "📉"
                else:
                    emoji = "🔻"
                
                tf_name = timeframe_names.get(tf, tf)
                mesaj += f"**{tf_name}:** {emoji} {score:.1f}/10 - {trend}\n"
        
        # Genel değerlendirme
        scores = [r.get('overall_score', 5) for r in timeframe_results.values()]
        avg_score = sum(scores) / len(scores) if scores else 5
        
        if avg_score >= 7:
            overall = "🚀 **Güçlü Boğa Trendi**"
        elif avg_score >= 6:
            overall = "📈 **Boğa Trendi**"
        elif avg_score >= 4:
            overall = "⚖️ **Nötr/Kararsız**"
        elif avg_score >= 3:
            overall = "📉 **Ayı Trendi**"
        else:
            overall = "🔻 **Güçlü Ayı Trendi**"
        
        mesaj += f"\n📊 **Genel Değerlendirme**\n"
        mesaj += f"{overall}\n"
        mesaj += f"🎯 **Ortalama Skor:** {avg_score:.1f}/10\n\n"
        
        mesaj += f"💡 **Detay analiz:** /analiz {coin_input}\n"
        mesaj += f"⚠️ *Yatırım tavsiyesi değildir!*"
        
        return mesaj
    except Exception as e:
        print(f"Multi TF mesaj hatası: {e}")
        return "❌ Çoklu timeframe sonucu formatlanamadı!"

def format_fibonacci_message(fib_levels, current_price, coin_input):
    """Fibonacci mesajını formatla"""
    try:
        mesaj = f"📐 **{coin_input.upper()} - Fibonacci Retracement**\n\n"
        
        # Mevcut fiyat formatı
        if current_price < 0.01:
            current_str = f"${current_price:.8f}"
        elif current_price < 1:
            current_str = f"${current_price:.6f}"
        else:
            current_str = f"${current_price:,.4f}"
        
        mesaj += f"💰 **Güncel Fiyat:** {current_str}\n\n"
        
        # Fibonacci seviyeleri
        mesaj += f"📏 **Fibonacci Seviyeleri:**\n"
        
        for level, price in fib_levels.items():
            if current_price > price:
                emoji = "🟢"  # Destek
                role = "Destek"
            else:
                emoji = "🔴"  # Direnç
                role = "Direnç"
            
            distance = abs((current_price - price) / current_price * 100)
            
            if price < 0.01:
                price_str = f"${price:.8f}"
            elif price < 1:
                price_str = f"${price:.6f}"
            else:
                price_str = f"${price:,.4f}"
            
            mesaj += f"{emoji} **{level}:** {price_str} ({role}, %{distance:.1f})\n"
        
        mesaj += f"\n💡 **Nasıl Kullanılır:**\n"
        mesaj += f"🟢 Yeşil seviyeler potansiyel destek\n"
        mesaj += f"🔴 Kırmızı seviyeler potansiyel direnç\n"
        mesaj += f"📊 %23.6, %38.2, %61.8 güçlü seviyeler\n\n"
        
        mesaj += f"⏰ **Alarm kur:** /alarm {coin_input}\n"
        mesaj += f"⚠️ *Yatırım tavsiyesi değildir!*"
        
        return mesaj
    except Exception as e:
        print(f"Fibonacci mesaj hatası: {e}")
        return "❌ Fibonacci analizi formatlanamadı!"

# =============================================================================
# TEKNİK ANALİZ FONKSİYONLARI - İMPORT EDİLMİŞ
# =============================================================================

# Diğer gerekli import edilmiş fonksiyonlar
from utils.technical_analysis import (
    calculate_rsi, calculate_macd, calculate_bollinger_bands
)

# Eksik fonksiyonları burada tanımla (önceki koddaki gibi)
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

def calculate_fibonacci_levels(df, lookback=50):
    """Fibonacci Retracement Levels hesapla"""
    try:
        recent_data = df.tail(lookback)
        high_price = recent_data['high'].max()
        low_price = recent_data['low'].min()
        
        diff = high_price - low_price
        
        fib_levels = {
            '0%': high_price,
            '23.6%': high_price - (diff * 0.236),
            '38.2%': high_price - (diff * 0.382),
            '50%': high_price - (diff * 0.5),
            '61.8%': high_price - (diff * 0.618),
            '78.6%': high_price - (diff * 0.786),
            '100%': low_price
        }
        
        return fib_levels
    except Exception as e:
        print(f"Fibonacci hesaplama hatası: {e}")
        return {}

def calculate_ichimoku(df):
    """Ichimoku Cloud hesapla"""
    try:
        # Conversion Line (Tenkan-sen)
        high_9 = df['high'].rolling(window=9).max()
        low_9 = df['low'].rolling(window=9).min()
        conversion_line = (high_9 + low_9) / 2
        
        # Base Line (Kijun-sen)
        high_26 = df['high'].rolling(window=26).max()
        low_26 = df['low'].rolling(window=26).min()
        base_line = (high_26 + low_26) / 2
        
        return {
            'conversion_line': conversion_line,
            'base_line': base_line
        }
    except Exception as e:
        print(f"Ichimoku hesaplama hatası: {e}")
        return {}

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
            
            # MACD crossover
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
        
        # Gelişmiş indikatörler
        ichimoku_data = calculate_ichimoku(df)
        fib_levels = calculate_fibonacci_levels(df)
        
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
            'ichimoku_data': ichimoku_data,
            'fib_levels': fib_levels,
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
    """AI ile trading yorumu oluştur"""
    try:
        if not OPENAI_API_KEY or OPENAI_API_KEY == "BURAYA_OPENAI_KEYINI_YAZ":
            return "🤖 AI yorumu için OpenAI API key gerekli!"
        
        current_price = df['close'].iloc[-1]
        rsi = analysis_result.get('rsi', 50)
        overall_score = analysis_result.get('overall_score', 5)
        
        prompt = f"""
Sen profesyonel kripto trading analisti sin. {symbol} için {timeframe} analizi:

Veriler:
- Fiyat: ${current_price:,.4f}
- RSI: {rsi:.1f}
- Skor: {overall_score:.1f}/10

Kısa yorumuyla:
📊 Teknik Durum: (Bullish/Bearish/Nötr)
💭 Yorum: (2 cümle analiz)
🎯 Beklenti: (kısa vadeli)
⚠️ Risk: (ana risk)

Kısa ve net ol, max 150 kelime.
"""

        client = openai.OpenAI(api_key=OPENAI_API_KEY)
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Sen uzman kripto analisti sin. Kısa ve pratik yorumlar yaparsın."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=200,
            temperature=0.7
        )
        
        return response.choices[0].message.content
        
    except Exception as e:
        print(f"AI yorum hatası: {e}")
        score = analysis_result.get('overall_score', 5)
        if score >= 7:
            return "📊 Teknik Durum: Bullish\n💭 Güçlü alım sinyalleri görülüyor\n🎯 Beklenti: Yükselişe devam\n⚠️ Risk: Aşırı alım riski"
        elif score <= 3:
            return "📊 Teknik Durum: Bearish\n💭 Satış baskısı ağır basıyor\n🎯 Beklenti: Düşüş beklenebilir\n⚠️ Risk: Momentum kaybı"
        else:
            return "📊 Teknik Durum: Nötr\n💭 Kararsızlık hakim durumda\n🎯 Beklenti: Beklemede kalın\n⚠️ Risk: Yön belirsizliği"

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

def calculate_support_resistance_levels(df):
    """Destek ve direnç seviyelerini hesapla"""
    try:
        current_price = df['close'].iloc[-1]
        
        highs = []
        lows = []
        window = 5
        
        for i in range(window, len(df) - window):
            if all(df['high'].iloc[i] >= df['high'].iloc[i-j] for j in range(1, window+1)) and \
               all(df['high'].iloc[i] >= df['high'].iloc[i+j] for j in range(1, window+1)):
                highs.append(df['high'].iloc[i])
            
            if all(df['low'].iloc[i] <= df['low'].iloc[i-j] for j in range(1, window+1)) and \
               all(df['low'].iloc[i] <= df['low'].iloc[i+j] for j in range(1, window+1)):
                lows.append(df['low'].iloc[i])
        
        resistance_levels = [r for r in highs if r > current_price]
        support_levels = [s for s in lows if s < current_price]
        
        resistance_levels = sorted(resistance_levels)[:3]
        support_levels = sorted(support_levels, reverse=True)[:3]
        
        return {
            'support_levels': support_levels,
            'resistance_levels': resistance_levels,
            'current_price': current_price
        }
        
    except Exception as e:
        print(f"Destek/Direnç hesaplama hatası: {e}")
        return {
            'support_levels': [],
            'resistance_levels': [],
            'current_price': df['close'].iloc[-1]
        }

def analyze_multiple_timeframes(symbol, timeframes=['1h', '4h', '1d', '1w']):
    """Çoklu timeframe analizi"""
    try:
        timeframe_results = {}
        
        for tf in timeframes:
            if tf == '1h':
                limit = 168
            elif tf == '4h':
                limit = 168
            elif tf == '1d':
                limit = 100
            else:
                limit = 52
            
            df = get_binance_ohlc(symbol, interval=tf, limit=limit)
            if df is not None and not df.empty:
                analysis = perform_single_timeframe_analysis(df)
                timeframe_results[tf] = analysis
        
        return timeframe_results
    except Exception as e:
        print(f"Çoklu timeframe analiz hatası: {e}")
        return {}

def perform_single_timeframe_analysis(df):
    """Tek timeframe için basit analiz"""
    try:
        current_price = df['close'].iloc[-1]
        rsi = calculate_rsi(df['close']).iloc[-1]
        sma_20 = df['close'].rolling(20).mean().iloc[-1]
        
        trend = 'BULLISH' if current_price > sma_20 else 'BEARISH'
        score = 7 if trend == 'BULLISH' and rsi < 70 else 3 if trend == 'BEARISH' and rsi > 30 else 5
        
        return {
            'price': current_price,
            'rsi': rsi,
            'trend': trend,
            'overall_score': score
        }
    except:
        return {'price': 0, 'rsi': 50, 'trend': 'NEUTRAL', 'overall_score': 5}

def generate_comprehensive_signals(symbol):
    """Basit sinyal analizi"""
    try:
        df = get_binance_ohlc(symbol, interval="1d", limit=30)
        if df is None or df.empty:
            return None
        
        rsi = calculate_rsi(df['close']).iloc[-1]
        signals = []
        
        if rsi < 30:
            signals.append({
                'type': 'BUY',
                'indicator': 'RSI',
                'reason': f'Aşırı satım (RSI: {rsi:.1f})',
                'strength': 7,
                'confidence': 'Yüksek'
            })
        elif rsi > 70:
            signals.append({
                'type': 'SELL',
                'indicator': 'RSI',
                'reason': f'Aşırı alım (RSI: {rsi:.1f})',
                'strength': 7,
                'confidence': 'Yüksek'
            })
        
        return {
            'symbol': symbol,
            'signals': signals,
            'signal_count': len(signals),
            'bullish_strength': sum(s['strength'] for s in signals if s['type'] == 'BUY'),
            'bearish_strength': sum(s['strength'] for s in signals if s['type'] == 'SELL')
        }
    except:
        return None

def format_signals_message(signals_analysis, coin_input):
    """Sinyal mesajını formatla"""
    try:
        if not signals_analysis:
            return "❌ Sinyal analizi yapılamadı!"
        
        signals = signals_analysis['signals']
        bullish_strength = signals_analysis['bullish_strength']
        bearish_strength = signals_analysis['bearish_strength']
        
        mesaj = f"🎯 **{coin_input.upper()} - Trading Sinyalleri**\n\n"
        
        if bullish_strength > bearish_strength:
            overall = "🟢 BULLISH"
            strength_diff = bullish_strength - bearish_strength
        elif bearish_strength > bullish_strength:
            overall = "🔴 BEARISH"
            strength_diff = bearish_strength - bullish_strength
        else:
            overall = "🟡 NEUTRAL"
            strength_diff = 0
        
        mesaj += f"📊 **Genel Durum:** {overall}\n"
        mesaj += f"💪 **Sinyal Gücü:** {strength_diff:.1f}\n\n"
        
        if signals:
            mesaj += f"⚡ **Aktif Sinyaller:**\n"
            for signal in signals[:3]:
                mesaj += f"• **{signal['type']}** - {signal['indicator']}\n"
                mesaj += f"   📝 {signal['reason']}\n"
                mesaj += f"   💪 Güç: {signal.get('strength', 0):.0f}/10\n\n"
        else:
            mesaj += f"📊 Şu anda güçlü sinyal yok\n\n"
        
        mesaj += f"⚠️ *Yatırım tavsiyesi değildir!*"
        
        return mesaj
    except:
        return "❌ Sinyal mesajı formatlanamadı!"

def generate_ai_prediction(symbol, coin_input, days):
    """AI ile fiyat tahmini"""
    try:
        if not OPENAI_API_KEY or OPENAI_API_KEY == "BURAYA_OPENAI_KEYINI_YAZ":
            return "🤖 **AI tahmini için OpenAI API key gerekli!**\n\nconfig.py'de OPENAI_API_KEY'i ayarlayın."
        
        df = get_binance_ohlc(symbol, interval="1d", limit=30)
        if df is None or df.empty:
            return None
        
        current_price = df['close'].iloc[-1]
        rsi = calculate_rsi(df['close']).iloc[-1]
        
        prompt = f"{symbol} için {days} günlük fiyat tahmini yap. Güncel fiyat: ${current_price:.4f}, RSI: {rsi:.1f}. Kısa ve net tahmin ver (max 200 kelime)."
        
        client = openai.OpenAI(api_key=OPENAI_API_KEY)
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=250
        )
        
        return f"🤖 **{symbol} - {days} Günlük AI Tahmini**\n\n{response.choices[0].message.content}\n\n⚠️ *Yatırım tavsiyesi değildir!*"
        
    except Exception as e:
        print(f"AI tahmin hatası: {e}")
        return f"❌ AI tahmini oluşturulamadı!"

print("🎯 Simplified analysis commands yüklendi!")
