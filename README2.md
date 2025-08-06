markdown# 🚀 Crypto Telegram Bot

Advanced cryptocurrency analysis and price alert Telegram bot with technical analysis, real-time price tracking, and smart notifications.

## ✨ Features

### 📊 Price Tracking
- Real-time price data for 400+ cryptocurrencies
- 24h price changes and volume
- Market cap information
- Top 10 cryptocurrencies
- Trending coins

### 📈 Technical Analysis
- RSI (Relative Strength Index)
- MACD (Moving Average Convergence Divergence)
- Bollinger Bands
- Support/Resistance levels
- Volume analysis
- Interactive charts with matplotlib

### ⏰ Price Alerts
- Custom price alerts for any supported coin
- Multiple alerts per user
- Automatic notifications when target price is reached
- Easy alert management

### 🔥 Market Analysis
- Breakout candidate analysis
- Fear & Greed Index
- Market sentiment analysis
- Trading signals

## 🛠️ Installation

### Prerequisites
- Python 3.8+
- Telegram Bot Token
- OpenAI API Key (optional)

### Setup
1. Clone the repository:
```bash
git clone https://github.com/yourusername/crypto-telegram-bot.git
cd crypto-telegram-bot

Install dependencies:

bashpip install -r requirements.txt

Configure your tokens in config.py:

pythonTELEGRAM_TOKEN = "your_telegram_bot_token"
OPENAI_API_KEY = "your_openai_key"  # Optional

Run the bot:

bashpython main.py
📱 Commands
Basic Commands

/start - Initialize the bot
/help - Show all commands
/test - Test bot functionality

Price Commands

/fiyat COIN - Get current price (e.g., /fiyat btc)
/top10 - Top 10 cryptocurrencies
/trending - Trending coins

Analysis Commands

/analiz COIN - Technical analysis with chart
/breakout - Breakout candidate analysis
/korku - Fear & Greed Index

Alert Commands

/alarm COIN - Set price alert
/alarmlist - View active alerts
/alarmstop COIN - Remove alert
/cancel - Cancel alert setup

🏗️ Project Structure
crypto-telegram-bot/
├── main.py                 # Main bot file
├── config.py              # Configuration settings
├── requirements.txt       # Python dependencies
├── commands/              # Command modules
│   ├── __init__.py
│   ├── price_commands.py  # Price-related commands
│   ├── alarm_commands.py  # Alert system
│   └── analysis_commands.py # Technical analysis
├── utils/                 # Utility modules
│   ├── __init__.py
│   ├── binance_api.py     # Binance API integration
│   ├── technical_analysis.py # Technical indicators
│   └── chart_generator.py # Chart creation
└── README.md
🔧 Configuration
Bot Settings

ALARM_CHECK_INTERVAL: Alarm check frequency (seconds)
MAX_ALARMS_PER_USER: Maximum alerts per user
PRICE_TOLERANCE: Price tolerance for alerts (%)

Chart Settings

CHART_WIDTH: Chart width
CHART_HEIGHT: Chart height
CHART_DPI: Chart resolution

🎯 Supported Coins
The bot supports 400+ cryptocurrencies through Binance and CoinGecko APIs:
Popular coins include:

Bitcoin (BTC)
Ethereum (ETH)
Solana (SOL)
Dogecoin (DOGE)
Cardano (ADA)
Polygon (MATIC)
And many more...

🚨 Alerts System
Features

Set custom price targets
Multiple alerts per coin
Automatic notifications
Easy management commands

Usage Example
/alarm btc
> Enter target price: 50000
> Confirm: yes
✅ Alert set for Bitcoin at $50,000
📊 Technical Analysis
Indicators

RSI: Relative Strength Index for momentum
MACD: Trend following momentum indicator
Bollinger Bands: Volatility indicator
Support/Resistance: Key price levels
Volume Analysis: Trading volume patterns

Chart Features

Dark theme for better readability
Multiple timeframes
Interactive legends
Professional styling

🤝 Contributing

Fork the repository
Create a feature branch
Make your changes
Test thoroughly
Submit a pull request

📄 License
This project is licensed under the MIT License - see the LICENSE file for details.
⚠️ Disclaimer
This bot is for educational and informational purposes only. It does not provide financial advice. Always do your own research before making investment decisions.
🆘 Support
For support and questions:

Create an issue on GitHub
Check the documentation
Review the configuration guide


Made with ❤️ for the crypto community
