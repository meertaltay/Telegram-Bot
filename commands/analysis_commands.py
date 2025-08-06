"""
Analysis Commands - Teknik analiz komutları
/analiz, /breakout, /makro komutları
"""

import requests
import telebot
from config import *
from utils.binance_api import find_binance_symbol, get_binance_ohlc
from utils.technical_analysis import *
from utils.chart_generator import create_price_chart

def register_analysis_commands(bot):
    """Analiz komutlarını bot'a kaydet"""
    
    @bot.message_handler(commands=['analiz'])
    def analiz(message):
        """Teknik analiz yap"""
        try:
            parts = message.text.strip().split()
            if len(parts) < 2:
                bot.send_message(message.chat.id, 
                    "📊 **Teknik Analiz Nasıl Yapılır:**\n\n"
                    "🔹 /analiz COIN - Teknik analiz + grafik\n\n"
                    "**Örnekler:**\n"
                    "• /analiz btc\n"
                    "• /analiz ethereum\n"
                    "• /analiz sol\n\n"
                    "📈 RSI, MACD, Bollinger Bands analizi yapılır!",
                    parse_mode="Markdown")
                return

            coin_input = parts[1].lower()
            
            # Binance sembolü bul
            binance_symbol = find_binance_symbol(coin_input)
            
            if not binance_symbol:
                # Benzer coinleri öner
                similar_coins = []
                from utils.binance_api import BINANCE_SYMBOLS
                for symbol_key in list(BINANCE_SYMBOLS.keys())[:20]:
                    if coin_input in symbol_key:
                        similar_coins.append(symbol_key.upper())
                
                suggestion_text = f"\n\n🔍 **Benzer:** {', '.join(similar_coins[:5])}" if similar_coins else ""
                
                bot.send_message(message.chat.id, 
                    f"❌ **'{coin_input.upper()}' Binance'da bulunamadı!**\n\n"
                    f"💡 **Popüler:** BTC, ETH, SOL, DOGE, ADA{suggestion_text}\n\n"
                    f"💰 *Fiyat için:* /fiyat {coin_input}",
                    parse_mode="Markdown")
                return

            bot.send_message(message.chat.id, f"📊 {binance_symbol} analiz ediliyor...")
            
            # OHLCV verisi al
            df = get_binance_ohlc(binance_symbol, interval="1d", limit=200)
            if df is None or df.empty:
                bot.send_message(message.chat.id, f"❌ {binance_symbol} veri alınamadı!")
                return

            # Teknik analiz yap
            analysis_result = perform_technical_analysis(df, binance_symbol, coin_input)
            
            # Grafik oluştur
            chart_img = create_price_chart(df, binance_symbol, analysis_result['chart_data'])
            
            if chart_img:
                # Analiz mesajı
                analysis_message = format_analysis_message(analysis_result, coin_input)
                
                # Grafik + açıklama gönder
                bot.send_photo(message.chat.id, chart_img, caption=analysis_message, parse_mode="Markdown")
            else:
                # Sadece metin analizi gönder
                analysis_message = format_analysis_message(analysis_result, coin_input)
                bot.send_message(message.chat.id, analysis_message, parse_mode="Markdown")
            
        except Exception as e:
            print(f"Analiz hatası: {e}")
            bot.send_message(message.chat.id, "❌ Analiz yapılamadı! Biraz sonra tekrar dene.")

    @bot.message_handler(commands=['breakout'])
    def breakout_analiz(message):
        """Breakout adayları analiz et"""
        try:
            bot.send_message(message.chat.id, "🔥 Breakout adayları analiz ediliyor...")
            
            # Analiz edilecek coinler
            breakout_candidates = [
                "btc", "eth", "sol", "ada", "matic", "dot", "avax", 
                "link", "uni", "atom", "near", "op", "arb"
            ]
            
            breakout_results = []
            
            for coin in breakout_candidates[:8]:  # İlk 8 coin
                try:
                    binance_symbol = find_binance_symbol(coin)
                    if not binance_symbol:
                        continue
                    
                    df = get_binance_ohlc(binance_symbol, interval="1d", limit=100)
                    if df is None or df.empty:
                        continue
                    
                    # Breakout analizi
                    breakout_score = calculate_breakout_score(df)
                    
                    if breakout_score['score'] >= 5:  # Minimum skor
                        breakout_results.append({
                            'symbol': binance_symbol,
                            'coin': coin.upper(),
                            'score': breakout_score['score'],
                            'reasons': breakout_score['reasons'],
                            'potential': breakout_score['potential'],
                            'price': df['close'].iloc[-1]
                        })
                        
                except Exception as coin_error:
                    print(f"Breakout analiz hatası ({coin}): {coin_error}")
                    continue
            
            # Sonuçları sırala
            breakout_results.sort(key=lambda x: x['score'], reverse=True)
            
            if not breakout_results:
                bot.send_message(message.chat.id, 
                    "❌ Şu anda güçlü breakout adayı bulunamadı!\n\n"
                    "🔍 Piyasa konsolidasyon döneminde olabilir.")
                return
            
            # Sonuç mesajı
            mesaj = f"🔥 **Breakout Adayları** (Top {len(breakout_results)}):\n\n"
            
            for i, result in enumerate(breakout_results[:6], 1):
                # Score emoji
                if result['score'] >= 8:
                    score_emoji = "🚀"
                elif result['score'] >= 7:
                    score_emoji = "⚡"
                elif result['score'] >= 6:
                    score_emoji = "🎯"
                else:
                    score_emoji = "📈"
                
                mesaj += f"**{i}. {result['coin']}** {score_emoji}\n"
                mesaj += f"   💰 Fiyat: ${result['price']:.6f}\n"
                mesaj += f"   📊 Skor: {result['score']}/10\n"
                mesaj += f"   🔥 Sebepler: {', '.join(result['reasons'][:2])}\n\n"
            
            mesaj += f"💡 **Detay analiz:** /analiz COIN\n"
            mesaj += f"⚠️ **Risk:** Stop-loss kullanmayı unutma!"
            
            bot.send_message(message.chat.id, mesaj, parse_mode="Markdown")
            
        except Exception as e:
            print(f"Breakout analiz hatası: {e}")
            bot.send_message(message.chat.id, "❌ Breakout analizi yapılamadı!")

    @bot.message_handler(commands=['korku'])
    def korku_index(message):
        """Fear & Greed Index"""
        try:
            url = "https://api.alternative.me/fng/?limit=1&format=json"
            res = requests.get(url, timeout=API_TIMEOUT)
            
            if res.status_code != 200:
                bot.send_message(message.chat.id, "❌ Fear & Greed alınamadı!")
                return
                
            data = res.json()
            value = int(data['data'][0]['value'])
            classification = data['data'][0]['value_classification']
            
            if value >= 75:
                emoji = "🤑"
                yorum = "Aşırı açgözlülük! Dikkatli ol!"
            elif value >= 55:
                emoji = "😊" 
                yorum = "Açgözlülük hakim!"
            elif value >= 45:
                emoji = "😐"
                yorum = "Nötr durum"
            elif value >= 25:
                emoji = "😰"
                yorum = "Korku var"
            else:
                emoji = "😱"
                yorum = "Aşırı korku! Fırsat olabilir!"
            
            bot.send_message(message.chat.id,
                f"📊 **Fear & Greed Index** {emoji}\n\n"
                f"**Değer:** {value}/100\n"
                f"**Durum:** {classification}\n\n"
                f"💭 **Yorum:** {yorum}",
                parse_mode="Markdown")
                
        except Exception as e:
            print(f"Korku hatası: {e}")
            bot.send_message(message.chat.id, "❌ Korku endeksi alınamadı!")

# =============================================================================
# YARDIMCI FONKSİYONLAR
# =============================================================================

def perform_technical_analysis(df, symbol, coin_input):
    """Kapsamlı teknik analiz yap"""
    try:
        latest = df.iloc[-1]
        price = latest['close']
        
        # Teknik indikatörler
        rsi_values = calculate_rsi(df['close'])
        current_rsi = rsi_values.iloc[-1]
        
        macd_data = calculate_macd(df['close'])
        bb_data = calculate_bollinger_bands(df['close'])
        
        # Trend analizi
        trend_data = calculate_trend_strength(df)
        
        # Volume analizi
        volume_data = calculate_volume_analysis(df)
        
        # Destek/Direnç
        support_resistance = find_support_resistance(df)
        
        # Trading sinyalleri
        signals = generate_trading_signals(df)
        
        # Genel skor hesapla
        overall_score = calculate_overall_score(current_rsi, macd_data, trend_data, volume_data)
        
        return {
            'price': price,
            'rsi': current_rsi,
            'trend': trend_data,
            'volume': volume_data,
            'support_resistance': support_resistance,
            'signals': signals,
            'overall_score': overall_score,
            'chart_data': {
                'rsi': current_rsi,
                'macd_signal': 'Bullish' if macd_data['macd'].iloc[-1] > macd_data['signal'].iloc[-1] else 'Bearish',
                'trend': trend_data['trend_direction'],
                'support': support_resistance['support_levels'][0] if support_resistance['support_levels'] else price * 0.95,
                'resistance': support_resistance['resistance_levels'][0] if support_resistance['resistance_levels'] else price * 1.05,
                'volume_ratio': volume_data['volume_ratio'],
                'volume_analysis': volume_data['volume_analysis'],
                'recommendation': get_recommendation(overall_score)
            }
        }
    except Exception as e:
        print(f"Teknik analiz hatası: {e}")
        return {
            'price': 0,
            'rsi': 50,
            'trend': {'trend_direction': 'Belirsiz'},
            'volume': {'volume_analysis': 'Belirsiz'},
            'support_resistance': {'support_levels': [], 'resistance_levels': []},
            'signals': [],
            'overall_score': 5,
            'chart_data': {}
        }

def calculate_breakout_score(df):
    """Breakout skorunu hesapla"""
    try:
        price = df['close'].iloc[-1]
        
        # Trend
        trend_data = calculate_trend_strength(df)
        score = trend_data['trend_score']
        reasons = []
        
        # RSI
        rsi = calculate_rsi(df['close']).iloc[-1]
        if 40 < rsi < 70:
            score += 2
            reasons.append("RSI optimal")
        elif rsi > 70:
            score -= 1
            reasons.append("RSI yüksek")
        
        # Volume
        volume_data = calculate_volume_analysis(df)
        if volume_data['volume_ratio'] > 1.3:
            score += 2
            reasons.append("Hacim artışı")
        
        # Volatilite
        volatility = df['close'].tail(20).pct_change().std() * 100
        if volatility < 3:
            score += 1
            reasons.append("Düşük volatilite")
        
        # Potansiyel hesapla
        potential = min(score * 2, 15)
        
        return {
            'score': min(score, 10),
            'reasons': reasons,
            'potential': potential
        }
    except Exception as e:
        print(f"Breakout skor hatası: {e}")
        return {'score': 0, 'reasons': [], 'potential': 0}

def calculate_overall_score(rsi, macd_data, trend_data, volume_data):
    """Genel analiz skoru hesapla"""
    try:
        score = 5  # Başlangıç
        
        # RSI katkısı
        if 30 < rsi < 70:
            score += 1
        elif rsi < 30:
            score += 2  # Oversold
        elif rsi > 70:
            score -= 1  # Overbought
        
        # Trend katkısı
        score += (trend_data['trend_score'] - 2.5) * 0.8
        
        # Volume katkısı
        if volume_data['volume_ratio'] > 1.2:
            score += 0.5
        
        # MACD katkısı
        if macd_data['macd'].iloc[-1] > macd_data['signal'].iloc[-1]:
            score += 0.5
        
        return max(0, min(10, score))
    except:
        return 5

def get_recommendation(score):
    """Skora göre öneri ver"""
    if score >= 7:
        return "🚀 GÜÇLÜ AL"
    elif score >= 6:
        return "📈 AL"
    elif score >= 4:
        return "⚖️ BEKLE"
    elif score >= 3:
        return "📉 SAT"
    else:
        return "🔻 GÜÇLÜ SAT"

def format_analysis_message(analysis, coin_input):
    """Analiz mesajını formatla"""
    try:
        price = analysis['price']
        rsi = analysis['rsi']
        trend = analysis['trend']['trend_direction']
        volume = analysis['volume']['volume_analysis']
        score = analysis['overall_score']
        
        # Fiyat formatı
        if price < 0.01:
            price_str = f"${price:.8f}"
        elif price < 1:
            price_str = f"${price:.6f}"
        else:
            price_str = f"${price:,.4f}"
        
        recommendation = get_recommendation(score)
        
        mesaj = f"📊 **Teknik Analiz Sonucu**\n\n"
        mesaj += f"💰 **Fiyat:** {price_str}\n"
        mesaj += f"🎯 **RSI:** {rsi:.1f}\n"
        mesaj += f"📈 **Trend:** {trend}\n"
        mesaj += f"🔊 **Hacim:** {volume}\n\n"
        mesaj += f"⭐ **Genel Skor:** {score:.1f}/10\n"
        mesaj += f"💡 **Öneri:** {recommendation}\n\n"
        
        # Sinyaller
        if analysis['signals']:
            mesaj += f"🎯 **Sinyaller:**\n"
            for signal in analysis['signals'][:2]:
                mesaj += f"• {signal['type']}: {signal['reason']}\n"
            mesaj += "\n"
        
        mesaj += f"⏰ **Alarm kurmak için:** /alarm {coin_input}\n"
        mesaj += f"🔍 **Breakout analizi:** /breakout"
        
        return mesaj
    except Exception as e:
        print(f"Mesaj formatla hatası: {e}")
        return "❌ Analiz sonucu formatlanamadı!"

print("📈 Analysis commands yüklendi!")
