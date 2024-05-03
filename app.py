import ccxt
import requests
from flask import Flask, request

# Replace 'YOUR_TELEGRAM_BOT_TOKEN' with your actual bot token
TOKEN = "7077125494:AAEfbQ6xjGvyz44aAy2fPVAS_yQFGgmwS44"
# Replace 'YOUR_CHAT_ID' with your actual chat ID
chat_id = "6189017266"

# Initialize exchange objects
exchange_api_keys = {
    'mexc': {'apiKey': 'mx0vglsktbvhwLYb5D', 'secret': '07f99b1cafec47368b85c24290d969cb'},
    'bingx': {'apiKey': '2BwZQAGVZ00Qhx5QUZmjld7pw0bae2mvrZwgodAUfdhHW4CWAQ5bMnbi50ym62n1GHxsKjFmjs00uhpqZkjWg', 'secret': 'nhBQ752uv9ksQf5q4H0GrBOidExUWLSR4nymxisBL0tw1QjPDmLnsHonxQ3olof4JlH4jAoib8OBCAhCkQ'},
    'coinex': {'apiKey': '6E036A0906624D368A7D5AF59451D442', 'secret': '15D96BC28DD052F8A94E19CDFA312F784596688CFA85F220'}
}

# Initialize exchange objects
exchanges = {}
for exchange_name, api_keys in exchange_api_keys.items():
    exchanges[exchange_name] = getattr(ccxt, exchange_name)({**api_keys})

app = Flask(__name__)

@app.route('/')
def hello():
    return 'Hello, World!'

@app.route('/start', methods=['POST'])
def start():
    send_opportunities()
    return 'OK'

def send_opportunities():
    # Fetch all trading pairs available on each exchange
    exchange_markets = {}
    for exchange_name, exchange in exchanges.items():
        exchange_markets[exchange_name] = exchange.load_markets()

    # Iterate over trading pairs on each exchange
    for symbol in set.intersection(*[set(markets.keys()) for markets in exchange_markets.values()]):
        # Fetch ticker data for the trading pair on each exchange
        tickers = {exchange_name: exchange.fetch_ticker(symbol) for exchange_name, exchange in exchanges.items()}
        
        # Extract last prices from the ticker data for each exchange
        last_prices = {exchange_name: ticker['last'] if ticker is not None else None for exchange_name, ticker in tickers.items()}
        
        # Calculate the price differences and percentage differences between each pair of exchanges
        max_percentage_difference = 0
        max_difference_pair = None
        for i, (exchange_name1, last_price1) in enumerate(last_prices.items()):
            for exchange_name2, last_price2 in list(last_prices.items())[i+1:]:
                # Check if both last prices are not None
                if last_price1 is not None and last_price2 is not None:
                    price_difference = abs(last_price1 - last_price2)
                    percentage_difference = (price_difference / last_price1) * 100
                    
                    # Check if the percentage difference is greater than or equal to 1%
                    if percentage_difference >= 1:
                        if percentage_difference > max_percentage_difference:
                            max_percentage_difference = percentage_difference
                            max_difference_pair = (exchange_name1, exchange_name2)
                        
        # Send the trading pair with the highest percentage difference to Telegram
        if max_difference_pair is not None:
            exchange_name1, exchange_name2 = max_difference_pair
            last_price1 = last_prices[exchange_name1]
            last_price2 = last_prices[exchange_name2]
            price_difference = abs(last_price1 - last_price2)
            message = f'Trading Pair: {symbol}, {exchange_name1} Price: {last_price1}, {exchange_name2} Price: {last_price2}, Difference: {price_difference:.8f} ({max_percentage_difference:.2f}%)'
            url = f"https://api.telegram.org/bot{TOKEN}/sendMessage?chat_id={chat_id}&text={message}"
            requests.get(url)

# Set up webhook URL
if __name__ == '__main__':
    # Replace 'YOUR_TELEGRAM_BOT_TOKEN' with your actual bot token
    bot_token = "7077125494:AAEfbQ6xjGvyz44aAy2fPVAS_yQFGgmwS44"
    # Replace 'YOUR_WEBHOOK_URL' with the webhook URL provided by Render
    webhook_url = "https://arbitrage-2smi.onrender.com/start"
    
    # Set the webhook URL for your bot
    response = requests.post(f"https://api.telegram.org/bot{bot_token}/setWebhook?url={webhook_url}")

    # Check the response from the Telegram Bot API
    if response.ok:
        print("Webhook URL has been set successfully.")
    else:
        print("Failed to set webhook URL:", response.text)
    
    app.run(debug=True)
