import ccxt
import telebot
from flask import Flask, request

# Replace these placeholders with your actual API keys and secrets
exchange_api_keys = {
    'mexc': {'apiKey': 'mx0vglsktbvhwLYb5D', 'secret': '07f99b1cafec47368b85c24290d969cb'},
    'bingx': {'apiKey': '2BwZQAGVZ00Qhx5QUZmjld7pw0bae2mvrZwgodAUfdhHW4CWAQ5bMnbi50ym62n1GHxsKjFmjs00uhpqZkjWg', 'secret': 'nhBQ752uv9ksQf5q4H0GrBOidExUWLSR4nymxisBL0tw1QjPDmLnsHonxQ3olof4JlH4jAoib8OBCAhCkQ'},
    'coinex': {'apiKey': '6E036A0906624D368A7D5AF59451D442', 'secret': '15D96BC28DD052F8A94E19CDFA312F784596688CFA85F220'}
}

async def fetch_ticker(exchange, symbol):
    try:
        ticker = await exchange.fetch_ticker(symbol)
        return ticker
    except ccxt.NetworkError as e:
        print(f"Network error: {e}")
    except ccxt.ExchangeError as e:
        print(f"Exchange error: {e}")
    return None

async def find_arbitrage_opportunities():
    # Initialize exchange objects
    exchanges = {}
    for exchange_name, api_keys in exchange_api_keys.items():
        exchanges[exchange_name] = getattr(ccxt, exchange_name)({**api_keys})

    # Fetch all trading pairs available on each exchange
    exchange_markets = {}
    for exchange_name, exchange in exchanges.items():
        exchange_markets[exchange_name] = await exchange.load_markets()

    # Fetch ticker data concurrently for all trading pairs on each exchange
    tasks = []
    for symbol in set.intersection(*[set(markets.keys()) for markets in exchange_markets.values()]):
        for exchange_name, exchange in exchanges.items():
            tasks.append(fetch_ticker(exchange, symbol))

    ticker_results = await asyncio.gather(*tasks, return_exceptions=True)

    # Iterate over ticker results and find arbitrage opportunities
    arbitrage_opportunities = []
    for i in range(0, len(ticker_results), len(exchanges)):
        symbol = ticker_results[i]['symbol']
        prices = {ticker_results[j]['exchange']: ticker_results[j]['last'] for j in range(i, i+len(exchanges))}
        max_price = max(prices.values())
        min_price = min(prices.values())
        price_difference = abs(max_price - min_price)
        percentage_difference = (price_difference / min_price) * 100

        if percentage_difference >= 1:
            max_exchange = max(prices, key=prices.get)
            min_exchange = min(prices, key=prices.get)
            arbitrage_opportunity = f'Trading Pair: {symbol}, {min_exchange} Price: {min_price}, {max_exchange} Price: {max_price}, Difference: {price_difference:.8f} ({percentage_difference:.2f}%)'
            arbitrage_opportunities.append(arbitrage_opportunity)

    return arbitrage_opportunities

app = Flask(__name__)
bot = telebot.TeleBot("7077125494:AAEfbQ6xjGvyz44aAy2fPVAS_yQFGgmwS44")

@app.route("/", methods=["POST"])
def webhook():
    update = telebot.types.Update.de_json(request.stream.read().decode("utf-8"))
    bot.process_new_updates([update])
    return "!", 200

@bot.message_handler(commands=['start'])
def start(message):
    # Find arbitrage opportunities
    arbitrage_opportunities = find_arbitrage_opportunities()

    # Send arbitrage opportunities to the user
    if arbitrage_opportunities:
        for opportunity in arbitrage_opportunities:
            bot.send_message(message.chat.id, opportunity)
    else:
        bot.send_message(message.chat.id, "No arbitrage opportunities found.")

# Start the bot
bot.polling()
