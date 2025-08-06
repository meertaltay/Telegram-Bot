"""
Binance API Utils
Binance API ile işlemler ve coin sembolleri
"""

import requests
import pandas as pd
from config import *

# Global değişken
BINANCE_SYMBOLS = {}

def load_all_binance_symbols():
    """Binance'dan tüm USDT paritelerini yükle"""
    global BINANCE_SYMBOLS
    try:
        print("🔄 Binance'dan coin listesi yükleniyor...")
        url = f"{BINANCE_BASE_URL}/exchangeInfo"
        response = requests.get(url, timeout=BINANCE_TIMEOUT)
        
        if response.status_code == 200:
            data = response.json()
            for symbol_info in data['symbols']:
                symbol = symbol_info['symbol']
                if symbol.endswith('USDT') and symbol_info['status'] == 'TRADING':
                    base_asset = symbol_info['baseAsset'].lower()
                    BINANCE_SYMBOLS[base_asset] = symbol
            
            print(f"✅ Binance'dan {len(BINANCE_SYMBOLS)} USDT pariti yüklendi!")
            
            # Yaygın coin alias'ları ekle
            aliases = {
                "bitcoin": "btc", "ethereum": "eth", "solana": "sol",
                "dogecoin": "doge", "cardano": "ada", "polygon": "matic",
                "binance": "bnb", "ripple": "xrp", "litecoin": "ltc",
                "avalanche": "avax", "chainlink": "link", "uniswap": "uni",
                "shiba": "shib", "optimism": "op", "arbitrum": "arb",
                "render": "rndr", "polkadot": "dot", "cosmos": "atom"
            }
            
            for alias, symbol in aliases.items():
                if symbol in BINANCE_SYMBOLS:
                    BINANCE_SYMBOLS[alias] = BINANCE_SYMBOLS[symbol]
                    
            return True
        else:
            print(f"❌ Binance API hatası: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Binance yükleme hatası: {e}")
        return False

def find_binance_symbol(coin_input):
    """Coin input'u için Binance sembolü bul"""
    coin_input = coin_input.lower().strip()
    
    # Direkt arama
    if coin_input in BINANCE_SYMBOLS:
        return BINANCE_SYMBOLS[coin_input]
    
    # Kısmi eşleşme ara
    for symbol_key, symbol_value in BINANCE_SYMBOLS.items():
        if coin_input in symbol_key or symbol_key.startswith(coin_input):
            return symbol_value
    
    # USDT ekleyerek dene
    potential_symbol = f"{coin_input.upper()}USDT"
    for symbol_value in BINANCE_SYMBOLS.values():
        if symbol_value == potential_symbol:
            return potential_symbol
    
    return None

def get_binance_ohlc(symbol, interval="1d", limit=100):
    """Binance'dan OHLCV verisi al"""
    try:
        url = f"{BINANCE_BASE_URL}/klines?symbol={symbol.upper()}&interval={interval}&limit={limit}"
        res = requests.get(url, timeout=BINANCE_TIMEOUT)
        if res.status_code != 200:
            return None
        data = res.json()
        
        df = pd.DataFrame(data, columns=[
            "timestamp", "open", "high", "low", "close", "volume",
            "close_time", "quote_asset_volume", "number_of_trades", 
            "taker_buy_base", "taker_buy_quote", "ignore"
        ])
        df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
        df.set_index("timestamp", inplace=True)
        df = df[["open", "high", "low", "close", "volume"]].astype(float)
        return df
    except Exception as e:
        print(f"Binance OHLC hatası: {e}")
        return None

def get_binance_price(symbol):
    """Binance'dan anlık fiyat al"""
    try:
        url = f"{BINANCE_BASE_URL}/ticker/price?symbol={symbol.upper()}"
        response = requests.get(url, timeout=BINANCE_TIMEOUT)
        if response.status_code == 200:
            data = response.json()
            return float(data['price'])
    except Exception as e:
        print(f"Binance fiyat hatası: {e}")
    return None

def get_binance_24h_stats(symbol):
    """Binance'dan 24 saatlik istatistikler al"""
    try:
        url = f"{BINANCE_BASE_URL}/ticker/24hr?symbol={symbol.upper()}"
        response = requests.get(url, timeout=BINANCE_TIMEOUT)
        if response.status_code == 200:
            data = response.json()
            return {
                'price': float(data['lastPrice']),
                'change_24h': float(data['priceChangePercent']),
                'volume_24h': float(data['volume']),
                'high_24h': float(data['highPrice']),
                'low_24h': float(data['lowPrice'])
            }
    except Exception as e:
        print(f"Binance 24h stats hatası: {e}")
    return None

# Bot başlatılırken Binance coinlerini yükle
if DEBUG_MODE:
    print("🔧 Binance API utils yüklendi!")
