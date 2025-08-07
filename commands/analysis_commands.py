"""
Advanced Analysis Commands - Gelişmiş teknik analiz komutları
/analiz, /breakout, /makro komutları + AI tahmin + Çoklu timeframe
"""

import requests
import telebot
from config import *
from utils.binance_api import find_binance_symbol, get_binance_ohlc
from utils.technical_analysis import *
from utils.chart_generator import create_advanced_chart
import openai

def register_analysis_commands(bot):
    """Gelişmiş analiz komutlarını bot'a kaydet"""
    
    @bot.message_handler(commands=['analiz'])
    def analiz(message):
        """Gelişmiş teknik analiz yap"""
        try:
            parts = message.text.strip().split()
            if len(parts) < 2:
                bot.send_message(message.chat.id, 
                    "📊 **Gelişmiş Teknik Analiz:**\n\n"
                    "🔹 **Temel:** /analiz COIN\n"
                    "🔹 **Timeframe:** /analiz COIN 4h\n"
                    "🔹 **AI Tahmin:** /analiz COIN ai\n"
                    "🔹 **Çoklu TF:** /analiz COIN multi\n"
                    "🔹 **Fibonacci:** /analiz COIN fib\n\n"
                    "**Örnekler:**\n"
                    "• /analiz btc 1h\n"
                    "• /analiz eth ai\n"
                    "• /analiz sol multi\n"
                    "• /analiz ada fib\n\n"
                    "📈 **Timeframeler:** 1h, 4h, 1d, 1w",
                    parse_mode="Markdown")
                return

            coin_input = parts[1].lower()
            analysis_type = parts[2].lower() if len(parts) > 2 else "1d"
            
            # Binance sembolü bul
            binance_symbol = find_binance_symbol(coin_input)
            
            if not binance_symbol:
                bot.send_message(message.chat.id, 
                    f"❌ **'{coin_input.upper()}' Binance'da bulunamadı!**\n\n"
                    f"💡 **Popüler:** BTC, ETH, SOL, DOGE, ADA\n\n"
                    f"💰 *Fiyat için:* /fiyat {coin_input}",
                    parse_mode="Markdown")
                return

            # Analiz tipine göre farklı işlemler
            if analysis_type == "ai":
                await analyze_with_ai(message, binance_symbol, coin_input)
            elif analysis_type == "multi":
                await analyze_multiple_timeframes_command(message, binance_symbol, coin_input)
            elif analysis_type == "fib":
                await analyze_with_fibonacci(message, binance_symbol, coin_input)
            elif analysis_type in ["1h", "4h", "1d", "1w"]:
                await analyze_single_timeframe(message, binance_symbol, coin_input, analysis_type)
            else:
                # Default 1d analizi
                await analyze_single_timeframe(message, binance_symbol, coin_input, "1d")
            
        except Exception as e:
            print(f"Analiz hatası: {e}")
            bot.send_message(message.chat.id, "❌ Analiz yapılamadı! Biraz sonra tekrar dene.")

    @bot.message_handler(commands=['signals'])
    def trading_signals(message):
        """Güçlü trading sinyalleri"""
        try:
            parts = message.text.strip().split()
            if len(parts) < 2:
                bot.send_message(message.chat.id, 
                    "🎯 **Trading Sinyalleri:**\n\n"
                    "/signals COIN\n\n"
                    "**Özellikler:**\n"
                    "• Sinyal gücü skoru (1-10)\n"
                    "• Entry/Exit noktaları\n"
                    "• Stop-loss önerileri\n"
                    "• Risk/Reward oranı\n\n"
                    "**Örnek:** /signals btc",
                    parse_mode="Markdown")
                return

            coin_input = parts[1].lower()
            binance_symbol = find_binance_symbol(coin_input)
            
            if not binance_symbol:
                bot.send_message(message.chat.id, f"❌ '{coin_input.upper()}' bulunamadı!")
                return

            bot.send_message(message.chat.id, f"🎯 {binance_symbol} sinyalleri analiz ediliyor...")
            
            # Multi-timeframe sinyal analizi
            signals_analysis = generate_comprehensive_signals(binance_symbol)
            
            if signals_analysis:
                signals_message = format_signals_message(signals_analysis, coin_input)
                bot.send_message(message.chat.id, signals_message, parse_mode="Markdown")
            else:
                bot.send_message(message.chat.id, "❌ Sinyal analizi yapılamadı!")
                
        except Exception as e:
            print(f"Sinyal analizi hatası: {e}")
            bot.send_message(message.chat.id, "❌ Sinyal analizi yapılamadı!")

    @bot.message_handler(commands=['breakout'])
    def breakout_analiz(message):
        """Gelişmiş breakout adayları analiz et"""
        try:
            bot.send_message(message.chat.id, "🔥 Gelişmiş breakout analizi başlıyor...")
            
            # Gelişmiş breakout analizi
            breakout_results = analyze_breakout_candidates_advanced()
            
            if not breakout_results:
                bot.send_message(message.chat.id, 
                    "❌ Şu anda güçlü breakout adayı bulunamadı!")
                return
            
            # Sonuç mesajı
            breakout_message = format_advanced_breakout_message(breakout_results)
            bot.send_message(message.chat.id, breakout_message, parse_mode="Markdown")
            
        except Exception as e:
            print(f"Breakout analiz hatası: {e}")
            bot.send_message(message.chat.id, "❌ Breakout analizi yapılamadı!")

    @bot.message_handler(commands=['korku'])
    def korku_index(message):
        """Gelişmiş Fear & Greed Index"""
        try:
            # Fear & Greed Index
            fng_data = get_fear_greed_index()
            
            # Bitcoin korelasyon analizi
            btc_correlation = analyze_fng_btc_correlation()
            
            # Mesaj formatı
            fear_message = format_fear_greed_message(fng_data, btc_correlation)
            bot.send_message(message.chat.id, fear_message, parse_mode="Markdown")
                
        except Exception as e:
            print(f"Korku endeksi hatası: {e}")
            bot.send_message(message.chat.id, "❌ Korku endeksi alınamadı!")

    @bot.message_handler(commands=['predict'])
    def ai_prediction(message):
        """AI ile fiyat tahmini"""
        try:
            parts = message.text.strip().split()
            if len(parts) < 2:
                bot.send_message(message.chat.id, 
                    "🤖 **AI Fiyat Tahmini:**\n\n"
                    "/predict COIN [DAYS]\n\n"
                    "**Örnekler:**\n"
                    "• /predict btc\n"
                    "• /predict eth 7\n"
                    "• /predict sol 30\n\n"
                    "⚠️ **Bu tahmini yatırım tavsiyesi değil!**",
                    parse_mode="Markdown")
                return

            coin_input = parts[1].lower()
            days = int(parts[2]) if len(parts) > 2 else 7
            days = min(days, 30)  # Maksimum 30 gün
            
            binance_symbol = find_binance_symbol(coin_input)
            if not binance_symbol:
                bot.send_message(message.chat.id, f"❌ '{coin_input.upper()}' bulunamadı!")
                return

            bot.send_message(message.chat.id, f"🤖 {binance_symbol} için AI tahmini oluşturuluyor...")
            
            # AI tahmini
            prediction = generate_ai_prediction(binance_symbol, coin_input, days)
            
            if prediction:
                bot.send_message(message.chat.id, prediction, parse_mode="Markdown")
            else:
                bot.send_message(message.chat.id, "❌ AI tahmini oluşturulamadı!")
                
        except Exception as e:
            print(f"AI tahmin hatası: {e}")
            bot.send_message(message.chat.id, "❌ AI tahmini yapılamadı!")

# =============================================================================
# ANALİZ FONKSİYONLARI
# =============================================================================

async def analyze_single_timeframe(message, symbol, coin_input, timeframe):
    """Tek timeframe analizi"""
    try:
        bot.send_message(message.chat.id, f"📊 {symbol} {timeframe} analiz ediliyor...")
        
        # Timeframe'e göre limit ayarla
        limit_map = {'1h': 168, '4h': 168, '1d': 100, '1w': 52}
        limit = limit_map.get(timeframe, 100)
        
        df = get_binance_ohlc(symbol, interval=timeframe, limit=limit)
        if df is None or df.empty:
            bot.send_message(message.chat.id, f"❌ {symbol} veri alınamadı!")
            return

        # Kapsamlı analiz
        analysis_result = perform_comprehensive_analysis(df, symbol, timeframe)
        
        # Grafik oluştur
        chart_img = create_advanced_chart(df, symbol, analysis_result, timeframe)
        
        # Analiz mesajı
        analysis_message = format_comprehensive_analysis_message(analysis_result, coin_input, timeframe)
        
        if chart_img:
            bot.send_photo(message.chat.id, chart_img, caption=analysis_message, parse_mode="Markdown")
        else:
            bot.send_message(message.chat.id, analysis_message, parse_mode="Markdown")
            
    except Exception as e:
        print(f"Timeframe analiz hatası: {e}")
        bot.send_message(message.chat.id, "❌ Analiz yapılamadı!")

async def analyze_multiple_timeframes_command(message, symbol, coin_input):
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
        
        # En güçlü timeframe'i ayrıca göster
        strongest_tf = find_strongest_timeframe(timeframe_results)
        if strongest_tf:
            bot.send_message(message.chat.id, 
                f"🎯 **En güçlü sinyal {strongest_tf['timeframe']} timeframe'inde!**\n"
                f"Skor: {strongest_tf['score']}/10")
            
    except Exception as e:
        print(f"Multi timeframe hatası: {e}")

async def analyze_with_fibonacci(message, symbol, coin_input):
    """Fibonacci analizi"""
    try:
        bot.send_message(message.chat.id, f"📐 {symbol} Fibonacci analizi...")
        
        df = get_binance_ohlc(symbol, interval="1d", limit=100)
        if df is None or df.empty:
            return

        # Fibonacci seviyeleri
        fib_levels = calculate_fibonacci_levels(df)
        current_price = df['close'].iloc[-1]
        
        # Fibonacci mesajı
        fib_message = format_fibonacci_message(fib_levels, current_price, coin_input)
        bot.send_message(message.chat.id, fib_message, parse_mode="Markdown")
        
    except Exception as e:
        print(f"Fibonacci analiz hatası: {e}")

async def analyze_with_ai(message, symbol, coin_input):
    """AI ile analiz"""
    try:
        bot.send_message(message.chat.id, f"🤖 {symbol} AI analizi başlıyor...")
        
        # Teknik veri al
        df = get_binance_ohlc(symbol, interval="1d", limit=100)
        if df is None or df.empty:
            return

        # AI analizi
        ai_analysis = generate_ai_analysis(df, symbol, coin_input)
        
        if ai_analysis:
            bot.send_message(message.chat.id, ai_analysis, parse_mode="Markdown")
        else:
            bot.send_message(message.chat.id, "❌ AI analizi yapılamadı!")
            
    except Exception as e:
        print(f"AI analiz hatası: {e}")

# =============================================================================
# KAPSAMLI ANALİZ FONKSİYONU
# =============================================================================

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

# =============================================================================
# AI TAHMİN FONKSİYONLARI
# =============================================================================

def generate_ai_prediction(symbol, coin_input, days):
    """OpenAI ile fiyat tahmini"""
    try:
        if not OPENAI_API_KEY or OPENAI_API_KEY == "BURAYA_OPENAI_KEYINI_YAZ":
            return "🤖 **AI tahmini için OpenAI API key gerekli!**\n\nconfig.py'de OPENAI_API_KEY'i ayarlayın."
        
        # Veri topla
        df = get_binance_ohlc(symbol, interval="1d", limit=60)
        if df is None or df.empty:
            return None
        
        # Teknik indikatörleri hesapla
        current_price = df['close'].iloc[-1]
        rsi = calculate_rsi(df['close']).iloc[-1]
        macd_data = calculate_macd(df['close'])
        
        # AI için prompt hazırla
        prompt = create_ai_prediction_prompt(df, symbol, current_price, rsi, macd_data, days)
        
        # OpenAI API çağrısı
        client = openai.OpenAI(api_key=OPENAI_API_KEY)
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Sen profesyonel bir kripto analisti ve trader'sın. Teknik analiz ve piyasa verilerine dayanarak objektif tahminler yaparsın."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=500,
            temperature=0.7
        )
        
        ai_response = response.choices[0].message.content
        
        # AI cevabını formatla
        formatted_response = f"🤖 **AI Fiyat Tahmini - {symbol}**\n\n"
        formatted_response += f"📊 **Güncel Fiyat:** ${current_price:,.4f}\n"
        formatted_response += f"📅 **Tahmin Süresi:** {days} gün\n\n"
        formatted_response += ai_response
        formatted_response += f"\n\n⚠️ **Uyarı:** Bu tahmin yatırım tavsiyesi değildir!"
        
        return formatted_response
        
    except Exception as e:
        print(f"AI tahmin hatası: {e}")
        return None

def create_ai_prediction_prompt(df, symbol, current_price, rsi, macd_data, days):
    """AI için prompt oluştur"""
    try:
        # Son 7 günlük değişim
        price_change_7d = ((current_price - df['close'].iloc[-8]) / df['close'].iloc[-8]) * 100
        
        # Volume trendi
        avg_volume = df['volume'].tail(20).mean()
        recent_volume = df['volume'].tail(3).mean()
        volume_trend = "Artış" if recent_volume > avg_volume else "Azalış"
        
        # MACD durumu
        macd_signal = "Bullish" if macd_data['macd'].iloc[-1] > macd_data['signal'].iloc[-1] else "Bearish"
        
        prompt = f"""
{symbol} için {days} günlük fiyat tahmini yap.

Mevcut Veriler:
- Güncel Fiyat: ${current_price:,.4f}
- 7 Günlük Değişim: %{price_change_7d:.2f}
- RSI: {rsi:.1f}
- MACD: {macd_signal}
- Volume Trendi: {volume_trend}

Aşağıdaki formatta tahmin ver:
1. Fiyat hedefi (min-max aralığı)
2. Olasılık yüzdesi
3. Ana gerekçeler (3 madde)
4. Risk faktörleri
5. Önemli seviyeler

Objektif ve açıklayıcı ol. Kesin tahmin vermek yerine olasılık aralıkları kullan.
"""
        return prompt
    except:
        return f"{symbol} için {days} günlük teknik analiz bazlı fiyat tahmini yap."

def generate_ai_analysis(df, symbol, coin_input):
    """AI ile genel analiz"""
    try:
        if not OPENAI_API_KEY or OPENAI_API_KEY == "BURAYA_OPENAI_KEYINI_YAZ":
            return "🤖 **AI analizi için OpenAI API key gerekli!**"
        
        # Teknik veriler
        current_price = df['close'].iloc[-1]
        rsi = calculate_rsi(df['close']).iloc[-1]
        
        # Basit AI analizi
        prompt = f"Kripto para {symbol} için teknik analiz yap. Güncel fiyat: ${current_price:.4f}, RSI: {rsi:.1f}. Kısa ve net analiz ver."
        
        client = openai.OpenAI(api_key=OPENAI_API_KEY)
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=300
        )
        
        return f"🤖 **AI Analizi - {symbol}**\n\n{response.choices[0].message.content}"
        
    except Exception as e:
        print(f"AI genel analiz hatası: {e}")
        return None

# =============================================================================
# MESAJ FORMATLAMA FONKSİYONLARI
# =============================================================================

def format_comprehensive_analysis_message(analysis, coin_input, timeframe):
    """Kapsamlı analiz mesajını formatla"""
    try:
        price = analysis['price']
        rsi = analysis['rsi']
        signals = analysis['signals']
        entry_exit = analysis['entry_exit']
        overall_score = analysis['overall_score']
        recommendation = analysis['recommendation']
        
        # Fiyat formatı
        if price < 0.01:
            price_str = f"${price:.8f}"
        elif price < 1:
            price_str = f"${price:.6f}"
        else:
            price_str = f"${price:,.4f}"
        
        mesaj = f"📊 **Gelişmiş Analiz - {timeframe.upper()}**\n\n"
        mesaj += f"💰 **Fiyat:** {price_str}\n"
        mesaj += f"🎯 **RSI:** {rsi:.1f}\n"
        mesaj += f"⭐ **Genel Skor:** {overall_score:.1f}/10\n"
        mesaj += f"💡 **Öneri:** {recommendation}\n\n"
        
        # En güçlü sinyaller
        if signals:
            strong_signals = [s for s in signals if s['strength'] >= 6]
            if strong_signals:
                mesaj += f"🎯 **Güçlü Sinyaller:**\n"
                for signal in strong_signals[:3]:
                    mesaj += f"• {signal['type']}: {signal['reason']} (Güç: {signal['strength']}/10)\n"
                mesaj += "\n"
        
        # Entry/Exit noktaları
        if entry_exit and entry_exit.get('action') != 'HOLD':
            action = entry_exit['action']
            confidence = entry_exit['confidence']
            
            mesaj += f"🎯 **Trading Önerisi:** {action}\n"
            mesaj += f"📊 **Güven:** {confidence:.1f}/10\n"
            
            if action == 'BUY' and entry_exit.get('entry_points'):
                mesaj += f"🟢 **Entry:** ${entry_exit['entry_points'][0]['price']:.4f}\n"
                mesaj += f"🔴 **Stop Loss:** ${entry_exit['stop_loss']:.4f}\n"
                mesaj += f"🎯 **Take Profit:** ${entry_exit['take_profit']:.4f}\n"
            
            mesaj += "\n"
        
        mesaj += f"⏰ **Alarm:** /alarm {coin_input}\n"
        mesaj += f"🤖 **AI Tahmin:** /predict {coin_input}\n"
        mesaj += f"📊 **Çoklu TF:** /analiz {coin_input} multi"
        
        return mesaj
    except Exception as e:
        print(f"Mesaj formatla hatası: {e}")
        return "❌ Analiz sonucu formatlanamadı!"

def format_multi_timeframe_message(timeframe_results, coin_input):
    """Çoklu timeframe mesajını formatla"""
    try:
        mesaj = f"📊 **Çoklu Timeframe Analizi**\n\n"
        
        timeframes = ['1h', '4h', '1d', '1w']
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
                
                mesaj += f"**{tf.upper()}:** {emoji} {score:.1f}/10 - {trend}\n"
        
        # Genel değerlendirme
        avg_score = sum(r.get('overall_score', 5) for r in timeframe_results.values()) / len(timeframe_results)
        
        if avg_score >= 7:
            overall = "🚀 Güçlü Boğa"
        elif avg_score >= 6:
            overall = "📈 Boğa"
        elif avg_score >= 4:
            overall = "⚖️ Nötr"
        elif avg_score >= 3:
            overall = "📉 Ayı"
        else:
            overall = "🔻 Güçlü Ayı"
        
        mesaj += f"\n📊 **Genel Durum:** {overall} ({avg_score:.1f}/10)\n\n"
        mesaj += f"🎯 **Detay analiz:** /analiz {coin_input} 4h\n"
        mesaj += f"🤖 **AI görüşü:** /analiz {coin_input} ai"
        
        return mesaj
    except Exception as e:
        print(f"Multi TF mesaj hatası: {e}")
        return "❌ Çoklu timeframe sonucu formatlanamadı!"

def format_fibonacci_message(fib_levels, current_price, coin_input):
    """Fibonacci mesajını formatla"""
    try:
        mesaj = f"📐 **Fibonacci Retracement Seviyeleri**\n\n"
        
        # Mevcut fiyatın hangi seviyede olduğunu bul
        current_level = None
        for level, price in fib_levels.items():
            if abs(current_price - price) / current_price < 0.02:  # %2 tolerans
                current_level = level
                break
        
        mesaj += f"💰 **Güncel Fiyat:** ${current_price:.4f}"
        if current_level:
            mesaj += f" *({current_level} yakınında)*"
        mesaj += "\n\n"
        
        for level, price in fib_levels.items():
            if current_price > price:
                emoji = "🟢"  # Destek
                role = "Destek"
            else:
                emoji = "🔴"  # Direnç
                role = "Direnç"
            
            distance = abs((current_price - price) / current_price * 100)
            mesaj += f"{emoji} **{level}:** ${price:.4f} ({role}, %{distance:.1f})\n"
        
        mesaj += f"\n💡 **Kullanım:**\n"
        mesaj += f"• Yeşil seviyeler: Potansiyel destek\n"
        mesaj += f"• Kırmızı seviyeler: Potansiyel direnç\n\n"
        mesaj += f"⏰ **Alarm kur:** /alarm {coin_input}"
        
        return mesaj
    except Exception as e:
        print(f"Fibonacci mesaj hatası: {e}")
        return "❌ Fibonacci analizi formatlanamadı!"

# =============================================================================
# YARDIMCI FONKSİYONLAR
# =============================================================================

def calculate_comprehensive_score(signals, trend_strength, risk_analysis):
    """Kapsamlı skor hesapla"""
    try:
        # Sinyal skorları
        signal_score = sum(s['strength'] for s in signals if s['type'] == 'BUY') - sum(s['strength'] for s in signals if s['type'] == 'SELL')
        signal_score = max(-10, min(10, signal_score))
        
        # Trend skoru
        trend_score = trend_strength.get('score', 0)
        
        # Risk skoru (düşük risk = yüksek skor)
        risk_score = 10 - risk_analysis.get('risk_level', 5)
        
        # Ağırlıklı ortalama
        weighted_score = (signal_score * 0.4 + trend_score * 0.4 + risk_score * 0.2)
        
        # 0-10 arasına normalize et
        normalized_score = (weighted_score + 10) / 2
        
        return max(0, min(10, normalized_score))
    except:
        return 5

def get_comprehensive_recommendation(score, signals):
    """Kapsamlı öneri ver"""
    try:
        # Sinyal sayıları
        buy_signals = len([s for s in signals if s['type'] == 'BUY'])
        sell_signals = len([s for s in signals if s['type'] == 'SELL'])
        
        if score >= 8:
            return "🚀 GÜÇLÜ AL"
        elif score >= 7:
            return "📈 AL"
        elif score >= 6:
            if buy_signals > sell_signals:
                return "📈 ZAYIF AL"
            else:
                return "⚖️ BEKLE"
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
        
        # Çoklu SMA
        sma_5 = df['close'].rolling(5).mean().iloc[-1]
        sma_10 = df['close'].rolling(10).mean().iloc[-1]
        sma_20 = df['close'].rolling(20).mean().iloc[-1]
        sma_50 = df['close'].rolling(50).mean().iloc[-1]
        
        # Trend puanı
        trend_score = 0
        if current_price > sma_5: trend_score += 2
        if current_price > sma_10: trend_score += 2
        if current_price > sma_20: trend_score += 2
        if current_price > sma_50: trend_score += 2
        if sma_5 > sma_10: trend_score += 1
        if sma_10 > sma_20: trend_score += 1
        
        # Momentum
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
        # Volatilite
        returns = df['close'].pct_change().dropna()
        volatility = returns.std() * 100
        
        # Maksimum düşüş
        rolling_max = df['close'].expanding().max()
        drawdown = (df['close'] - rolling_max) / rolling_max * 100
        max_drawdown = abs(drawdown.min())
        
        # Sinyal tutarlılığı
        signal_consistency = len([s for s in signals if s['confidence'] == 'Yüksek']) / max(len(signals), 1)
        
        # Risk seviyesi
        if volatility > 8 or max_drawdown > 20:
            risk_level = 8  # Yüksek risk
        elif volatility > 5 or max_drawdown > 10:
            risk_level = 6  # Orta risk
        else:
            risk_level = 3  # Düşük risk
        
        return {
            'volatility': volatility,
            'max_drawdown': max_drawdown,
            'risk_level': risk_level,
            'signal_consistency': signal_consistency,
            'risk_description': 'Yüksek' if risk_level >= 7 else 'Orta' if risk_level >= 4 else 'Düşük'
        }
    except:
        return {'volatility': 5, 'max_drawdown': 10, 'risk_level': 5, 'signal_consistency': 0.5, 'risk_description': 'Orta'}

def generate_comprehensive_signals(symbol):
    """Kapsamlı sinyal analizi"""
    try:
        # Çoklu timeframe sinyalleri
        timeframes = ['1h', '4h', '1d']
        all_signals = []
        
        for tf in timeframes:
            df = get_binance_ohlc(symbol, interval=tf, limit=100)
            if df is not None and not df.empty:
                analysis = perform_single_timeframe_analysis(df)
                if analysis and analysis.get('signals'):
                    for signal in analysis['signals']:
                        signal['timeframe'] = tf
                        all_signals.append(signal)
        
        # Sinyalleri grupla ve güçlendir
        consolidated_signals = consolidate_signals(all_signals)
        
        return {
            'symbol': symbol,
            'signals': consolidated_signals,
            'signal_count': len(consolidated_signals),
            'bullish_strength': sum(s['strength'] for s in consolidated_signals if s['type'] == 'BUY'),
            'bearish_strength': sum(s['strength'] for s in consolidated_signals if s['type'] == 'SELL')
        }
    except Exception as e:
        print(f"Kapsamlı sinyal hatası: {e}")
        return None

def consolidate_signals(signals):
    """Sinyalleri birleştir ve güçlendir"""
    try:
        # Aynı tip sinyalleri grupla
        signal_groups = {}
        
        for signal in signals:
            key = f"{signal['type']}_{signal['indicator']}"
            if key not in signal_groups:
                signal_groups[key] = []
            signal_groups[key].append(signal)
        
        # Her grup için en güçlü sinyali al
        consolidated = []
        for group_signals in signal_groups.values():
            if len(group_signals) > 1:
                # Çoklu timeframe destekli sinyal - güçlendir
                strongest = max(group_signals, key=lambda x: x['strength'])
                strongest['strength'] = min(10, strongest['strength'] + len(group_signals) - 1)
                strongest['reason'] += f" (Multi-TF)"
                consolidated.append(strongest)
            else:
                consolidated.append(group_signals[0])
        
        return sorted(consolidated, key=lambda x: x['strength'], reverse=True)
    except:
        return signals

def analyze_breakout_candidates_advanced():
    """Gelişmiş breakout analizi"""
    try:
        candidates = ["btc", "eth", "sol", "ada", "matic", "dot", "avax", "link", "uni", "atom"]
        results = []
        
        for coin in candidates:
            binance_symbol = find_binance_symbol(coin)
            if not binance_symbol:
                continue
            
            df = get_binance_ohlc(binance_symbol, interval="1d", limit=100)
            if df is None or df.empty:
                continue
            
            # Gelişmiş breakout skoru
            breakout_analysis = calculate_advanced_breakout_score(df, binance_symbol)
            
            if breakout_analysis['score'] >= 6:
                results.append({
                    'symbol': binance_symbol,
                    'coin': coin.upper(),
                    'score': breakout_analysis['score'],
                    'reasons': breakout_analysis['reasons'],
                    'probability': breakout_analysis['probability'],
                    'target': breakout_analysis['target'],
                    'risk_reward': breakout_analysis['risk_reward']
                })
        
        return sorted(results, key=lambda x: x['score'], reverse=True)[:6]
    except Exception as e:
        print(f"Gelişmiş breakout hatası: {e}")
        return []

def calculate_advanced_breakout_score(df, symbol):
    """Gelişmiş breakout skoru"""
    try:
        current_price = df['close'].iloc[-1]
        
        # Temel skorlama
        analysis = perform_single_timeframe_analysis(df)
        base_score = analysis.get('overall_score', 5)
        
        # Breakout faktörleri
        breakout_factors = []
        additional_score = 0
        
        # Volume artışı
        avg_volume = df['volume'].tail(20).mean()
        recent_volume = df['volume'].tail(3).mean()
        volume_ratio = recent_volume / avg_volume
        
        if volume_ratio > 1.5:
            additional_score += 2
            breakout_factors.append(f"Hacim artışı ({volume_ratio:.1f}x)")
        
        # Bollinger sıkışması
        bb_data = calculate_bollinger_bands(df['close'])
        bb_width = (bb_data['upper'].iloc[-1] - bb_data['lower'].iloc[-1]) / bb_data['middle'].iloc[-1]
        bb_avg_width = ((bb_data['upper'] - bb_data['lower']) / bb_data['middle']).tail(20).mean()
        
        if bb_width < bb_avg_width * 0.8:
            additional_score += 1.5
            breakout_factors.append("Bollinger sıkışması")
        
        # Direnç testi
        resistance_levels = find_resistance_levels(df, current_price)
        if resistance_levels:
            distance_to_resistance = (resistance_levels[0] - current_price) / current_price * 100
            if 0 < distance_to_resistance < 3:
                additional_score += 2
                breakout_factors.append("Direnç testinde")
        
        # RSI momentum
        rsi = calculate_rsi(df['close']).iloc[-1]
        if 50 < rsi < 65:
            additional_score += 1
            breakout_factors.append("RSI momentum")
        
        total_score = min(10, base_score + additional_score)
        
        # Hedef ve olasılık hesapla
        target_percentage = min(total_score * 2, 15)
        probability = min(total_score * 8, 80)
        
        # Risk/Reward
        support_levels = find_support_levels(df, current_price)
        stop_loss = support_levels[0] if support_levels else current_price * 0.95
        target_price = current_price * (1 + target_percentage / 100)
        
        risk = (current_price - stop_loss) / current_price * 100
        reward = target_percentage
        risk_reward = reward / max(risk, 1)
        
        return {
            'score': round(total_score, 1),
            'reasons': breakout_factors[:3],
            'probability': round(probability),
            'target': round(target_percentage, 1),
            'risk_reward': round(risk_reward, 1)
        }
    except:
        return {'score': 0, 'reasons': [], 'probability': 0, 'target': 0, 'risk_reward': 0}

def format_advanced_breakout_message(results):
    """Gelişmiş breakout mesajını formatla"""
    try:
        mesaj = f"🔥 **Gelişmiş Breakout Analizi**\n\n"
        
        for i, result in enumerate(results, 1):
            score_emoji = "🚀" if result['score'] >= 8.5 else "⚡" if result['score'] >= 7 else "🎯"
            
            mesaj += f"**{i}. {result['coin']}** {score_emoji}\n"
            mesaj += f"   📊 Skor: {result['score']}/10\n"
            mesaj += f"   🎯 Hedef: +%{result['target']}\n"
            mesaj += f"   📈 Olasılık: %{result['probability']}\n"
            mesaj += f"   ⚖️ R/R: {result['risk_reward']}\n"
            mesaj += f"   🔥 Sebepler: {', '.join(result['reasons'])}\n\n"
        
        mesaj += f"💡 **En yüksek skor:** {results[0]['coin']} ({results[0]['score']}/10)\n"
        mesaj += f"🎯 **Detay analiz:** /analiz {results[0]['coin'].lower()}\n"
        mesaj += f"⏰ **Alarm kur:** /alarm {results[0]['coin'].lower()}"
        
        return mesaj
    except:
        return "❌ Breakout mesajı formatlanamadı!"

def get_fear_greed_index():
    """Fear & Greed Index al"""
    try:
        url = "https://api.alternative.me/fng/?limit=7&format=json"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            return data['data']
    except:
        pass
    return None

def analyze_fng_btc_correlation():
    """Fear & Greed ile BTC korelasyonu"""
    try:
        # Basit korelasyon analizi
        df = get_binance_ohlc("BTCUSDT", interval="1d", limit=30)
        if df is None:
            return None
        
        btc_returns = df['close'].pct_change().tail(7).mean() * 100
        
        return {
            'btc_7d_return': btc_returns,
            'correlation_strength': 'Güçlü' if abs(btc_returns) > 5 else 'Orta'
        }
    except:
        return None

def format_fear_greed_message(fng_data, btc_correlation):
    """Fear & Greed mesajını formatla"""
    try:
        if not fng_data:
            return "❌ Fear & Greed Index alınamadı!"
        
        current = fng_data[0]
        value = int(current['value'])
        classification = current['value_classification']
        
        # Emoji ve yorum
        if value >= 75:
            emoji = "🤑"
            yorum = "Aşırı açgözlülük! Dikkatli ol!"
            action = "Kar realizasyonu zamanı olabilir"
        elif value >= 55:
            emoji = "😊"
            yorum = "Açgözlülük hakim!"
            action = "Pozisyon büyüklüğüne dikkat et"
        elif value >= 45:
            emoji = "😐"
            yorum = "Nötr durum"
            action = "Bekle ve gözle"
        elif value >= 25:
            emoji = "😰"
            yorum = "Korku var"
            action = "Kademeli alım fırsatı"
        else:
            emoji = "😱"
            yorum = "Aşırı korku! Fırsat olabilir!"
            action = "Güçlü alım fırsatı (risk sermayesiyle)"
        
        mesaj = f"📊 **Fear & Greed Index** {emoji}\n\n"
        mesaj += f"**Değer:** {value}/100\n"
        mesaj += f"**Durum:** {classification}\n"
        mesaj += f"💭 **Yorum:** {yorum}\n"
        mesaj += f"💡 **Strateji:** {action}\n\n"
        
        # Haftalık trend
        if len(fng_data) >= 7:
            week_ago_value = int(fng_data[6]['value'])
            change = value - week_ago_value
            trend = "↗️" if change > 0 else "↘️" if change < 0 else "➡️"
            mesaj += f"📈 **7 günlük değişim:** {trend} {change:+d} puan\n"
        
        # BTC korelasyonu
        if btc_correlation:
            btc_return = btc_correlation['btc_7d_return']
            mesaj += f"₿ **BTC 7g performans:** %{btc_return:+.1f}\n"
        
        return mesaj
    except:
        return "❌ Fear & Greed analizi formatlanamadı!"

def format_signals_message(signals_analysis, coin_input):
    """Sinyal mesajını formatla"""
    try:
        if not signals_analysis:
            return "❌ Sinyal analizi yapılamadı!"
        
        signals = signals_analysis['signals']
        bullish_strength = signals_analysis['bullish_strength']
        bearish_strength = signals_analysis['bearish_strength']
        
        mesaj = f"🎯 **Trading Sinyalleri**\n\n"
        
        # Genel durum
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
        
        # En güçlü sinyaller
        strong_signals = [s for s in signals if s['strength'] >= 6]
        if strong_signals:
            mesaj += f"⚡ **Güçlü Sinyaller:**\n"
            for signal in strong_signals[:4]:
                confidence_emoji = "🔥" if signal['confidence'] == 'Yüksek' else "⚡" if signal['confidence'] == 'Orta' else "💫"
                mesaj += f"{confidence_emoji} **{signal['type']}** - {signal['indicator']}\n"
                mesaj += f"   📝 {signal['reason']}\n"
                mesaj += f"   💪 Güç: {signal['strength']}/10\n"
                if 'timeframe' in signal:
                    mesaj += f"   ⏰ TF: {signal['timeframe']}\n"
                mesaj += "\n"
        
        # Özet öneri
        if strength_diff >= 10:
            recommendation = "🚀 Güçlü pozisyon al"
        elif strength_diff >= 5:
            recommendation = "📈 Pozisyon al"
        elif strength_diff >= -5:
            recommendation = "⚖️ Bekle"
        elif strength_diff >= -10:
            recommendation = "📉 Pozisyon azalt"
        else:
            recommendation = "🔻 Pozisyondan çık"
        
        mesaj += f"💡 **Öneri:** {recommendation}\n\n"
        mesaj += f"📊 **Detay analiz:** /analiz {coin_input}\n"
        mesaj += f"⏰ **Alarm kur:** /alarm {coin_input}"
        
        return mesaj
    except:
        return "❌ Sinyal mesajı formatlanamadı!"

def find_strongest_timeframe(timeframe_results):
    """En güçlü timeframe'i bul"""
    try:
        strongest = None
        max_score = 0
        
        for tf, result in timeframe_results.items():
            score = result.get('overall_score', 0)
            if score > max_score:
                max_score = score
                strongest = {'timeframe': tf, 'score': score}
        
        return strongest
    except:
        return None

print("📈 Advanced analysis commands yüklendi!")
