import telebot
import requests
import logging
import time
import pandas as pd
from database import Database
from telebot import types
import threading
import csv
import random
import html

api_token = '6930072072:AAGJN46yEyiqTBXZVcvARrN7fHlwjfy3ZMc'
bot = telebot.TeleBot(api_token)
MARKET_STATUS_API_KEY = 'H3U4QWAAE7GI2Y8W'
df = pd.read_csv('stonk.csv')
database = Database()
database.create_table_if_not_exists()
ticker_id_file = 'ticker_ids.csv'
# Configure logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

def read_ticker_ids():
  ticker_ids = {}
  with open(ticker_id_file, 'r') as file:
      reader = csv.reader(file)
      for row in reader:
          ticker_ids[row[0]] = row[1]
  return ticker_ids

# Function to fetch cryptocurrency info by ID
def fetch_crypto_info_by_id(id):
  try:
      response = requests.get(f'https://api.coinlore.net/api/ticker/?id={id}')
      data = response.json()
      return data
  except Exception as e:
      logger.error("Error fetching crypto info by ID: %s", e)
      return None


# Command handlers
@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.chat.id
    if not database.is_user_registered(user_id):
        confirm_registration_message(user_id)
    else:
        welcome_back_message(user_id, message.from_user.username)

@bot.message_handler(commands=['me'])
def display_user_info(message):
    user_id = message.chat.id
    user_info_message(user_id, message.from_user)

# Callback query handlers
@bot.callback_query_handler(func=lambda call: call.data == 'confirm_registration')
def confirm_registration(call):
    user_id = call.from_user.id
    handle_confirm_registration(user_id, call.message.message_id)

@bot.callback_query_handler(func=lambda call: call.data == 'menu_cmd')
def menu_callback(call):
    user_id = call.from_user.id
    handle_menu_callback(user_id, call.message.message_id)

@bot.callback_query_handler(func=lambda call: call.data == 'free_cmd')
def free_callback(call):
    user_id = call.from_user.id
    handle_free_callback(user_id)

@bot.callback_query_handler(func=lambda call: call.data == 'back_cmd_free')
def back_callback_free(call):
    menu_callback(call)

@bot.callback_query_handler(func=lambda call: call.data == 'other_tool_cmd')
def other_tool_callback(call):
    user_id = call.from_user.id
    handle_other_tool_callback(user_id, call.message.message_id)

@bot.callback_query_handler(func=lambda call: call.data == 'back_cmd_other_tool')
def back_callback_other_tool(call):
    menu_callback(call)

@bot.callback_query_handler(func=lambda call: call.data == 'usa_market_cmd')
def usa_market_callback(call):
    user_id = call.from_user.id
    usa_market_commands_message(user_id, call.message.message_id, bot)

@bot.callback_query_handler(func=lambda call: call.data == 'crypto_cmd')
def crypto_callback(call):
    user_id = call.from_user.id
    crypto_commands_message(user_id, call.message.message_id, bot)

@bot.callback_query_handler(func=lambda call: call.data == 'back_cmd_usa_market')
def back_callback_usa_market(call):
    handle_menu_callback(call.from_user.id, call.message.message_id)

@bot.callback_query_handler(func=lambda call: call.data == 'back_cmd_crypto')
def back_callback_crypto(call):
    handle_menu_callback(call.from_user.id, call.message.message_id)

def confirm_registration_message(user_id):
  gif_url = "https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExZnQxNjd2cG1pNjZyc2p0cGZqOXJiYjZlM2VxOGw0bGlmZnZubnNmbCZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/GRPy8MKag9U1U88hzY/giphy.gif"
  welcome_message = "Welcome! A new user registration has been detected. " \
                    "Please click the 'Confirm' button below to complete your registration."

  keyboard = types.InlineKeyboardMarkup()
  confirm_button = types.InlineKeyboardButton("Confirm", callback_data='confirm_registration')
  keyboard.add(confirm_button)

  bot.send_animation(user_id, gif_url, caption=welcome_message, parse_mode='html', reply_markup=keyboard)
  threading.Timer(5.0, delete_gif_message, args=[user_id, gif_message.message_id]).start()


def delete_gif_message(user_id, message_id):
 time.sleep(5)
 bot.delete_message(user_id, message_id)

def welcome_back_message(user_id, username):
  gif_url ="https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExZTU0cGZxdmJlbnZ5MzY1OGtqd2YweXdxMjB5emhlNXF3YW91dmZ6dyZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/ASd0Ukj0y3qMM/giphy.gif"
  welcome_message = f"Welcome Back @{username}.\nUse the 'Menu' button to interact with the bot."

  keyboard = types.InlineKeyboardMarkup()
  menu_button = types.InlineKeyboardButton("Menu", callback_data='menu_cmd')
  keyboard.add(menu_button)

  bot.send_animation(user_id, gif_url, caption=welcome_message, parse_mode='html', reply_markup=keyboard)


def user_info_message(user_id, user):
    if not database.is_user_registered(user_id):
        bot.send_message(user_id, "Please register first using /register.")
        return

    user_info = database.get_user_info(user_id)
    if user_info:
        formatted_registration_time = user_info['registration_time'].strftime('%d %b %Y')
        response = (
            f"🌟 *User Information* 🌟\n"
            f"𝗡𝗮𝗺𝗲 : {user.first_name} {user.last_name if user.last_name else ''}\n"
            f"𝗨𝘀𝗲𝗿 : @{user.username if user.username else 'N/A'}\n"
            f"𝗜𝗗 : `{user_info['user_id']}`\n"
            f"𝗧𝘆𝗽𝗲 : {user_info['user_type']}\n"
            f"𝗥𝗲𝗴𝗶𝘀𝘁𝗿𝗮𝘁𝗶𝗼𝗻 𝗧𝗶𝗺𝗲 : {formatted_registration_time}"
        )
        bot.send_message(user_id, response, parse_mode='MarkdownV2')
    else:
        bot.send_message(user_id, "Failed to retrieve user information.")

def handle_confirm_registration(user_id, message_id):
    if not database.is_user_registered(user_id):
        generated_user_id = database.register_user(user_id)
        user_info = database.get_user_info(user_id)

        if user_info and user_info.get('unique_id'):
            escaped_unique_id = user_info['unique_id'].replace('!', r'\!')
            success_message = f"𝗥𝗲𝗴𝗶𝘀𝘁𝗿𝗮𝘁𝗶𝗼𝗻 𝗦𝘂𝗰𝗰𝗲𝘀𝘀𝘂𝗹 ✅️ \n𝗬𝗼𝘂𝗿 𝗧𝗿𝗮𝗱𝗲 𝗜𝗗: {escaped_unique_id}"
            bot.send_message(user_id, success_message)
            bot.delete_message(user_id, message_id)
        else:
            bot.send_message(user_id, "An error occurred while processing your request. Please try again.")
    else:
        bot.send_message(user_id, "You are already registered! Welcome back.")

def handle_menu_callback(user_id, message_id):
    if not database.is_user_registered(user_id):
        bot.send_message(user_id, "Please register first using /register.")
        return

    user_info = database.get_user_info(user_id)
    if user_info:
        user_info_text = (
            f"𝗧𝗿𝗮𝗱𝗲 𝗜𝗗 : `{user_info['unique_id']}`\n"
            f"𝗨𝘀𝗲𝗿 : {user_info['user_type']}"
        )
        sent_message = bot.send_message(user_id, user_info_text, parse_mode='MarkdownV2')
        free_button = types.InlineKeyboardButton("Menu", callback_data='free_cmd')
        other_tool_button = types.InlineKeyboardButton("Market", callback_data='other_tool_cmd')
        menu_markup = types.InlineKeyboardMarkup().row(free_button, other_tool_button)
        bot.edit_message_reply_markup(chat_id=user_id, message_id=sent_message.message_id, reply_markup=menu_markup)
        bot.delete_message(user_id, message_id)
    else:
        bot.send_message(user_id, "Failed to retrieve user information.")

def handle_free_callback(user_id):
  if not database.is_user_registered(user_id):
      bot.send_message(user_id, "Please register first using /register.")
      return

  gif_url ="https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExZTU0cGZxdmJlbnZ5MzY1OGtqd2YweXdxMjB5emhlNXF3YW91dmZ6dyZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/ASd0Ukj0y3qMM/giphy.gif"
  available_commands = "Available Commands:\n/predict - 30 Days Prediction\n/chart - Visual Appreance of Stock for Diffrent Time-Frames"

  keyboard = types.InlineKeyboardMarkup()
  back_button = types.InlineKeyboardButton("Back", callback_data='back_cmd_free')
  keyboard.add(back_button)

  bot.send_animation(user_id, gif_url, caption=available_commands, parse_mode='html', reply_markup=keyboard)


def handle_other_tool_callback(user_id, message_id):
    usa_market_button = types.InlineKeyboardButton("US Market", callback_data='usa_market_cmd')
    crypto_button = types.InlineKeyboardButton("Crypto", callback_data='crypto_cmd')
    back_button = types.InlineKeyboardButton("Back", callback_data='back_cmd_other_tool')
    other_tool_markup = types.InlineKeyboardMarkup().row(usa_market_button, crypto_button, back_button)
    bot.edit_message_reply_markup(chat_id=user_id, message_id=message_id, reply_markup=other_tool_markup)

def usa_market_commands_message(user_id, message_id=None, bot=None):
  if bot is None:
      raise ValueError("Bot object is required.")

  gif_url = "https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExYXVzazBrM3JubXZyZnU0MTBqaXlua2JsOGszZWxkaWd1NWFuc3lncCZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/ic96TVwf0fx3C07df1/giphy.gif"
  commands_message = """
  🇺🇸 **USA Market Commands** 🇺🇸

  Select a command:

  • /marketnow - *Current market status.*
  • /exchange FROMCURRENCY TOCURRENCY - *Exchange rate.*
  • /topgain - *Top gainers.*
  """

  keyboard = types.InlineKeyboardMarkup()
  back_button = types.InlineKeyboardButton("Back to Menu", callback_data='back_cmd_usa_market')
  keyboard.add(back_button)

  if message_id:
      bot.send_animation(user_id, gif_url, caption=commands_message, parse_mode='Markdown', reply_markup=keyboard)
  else:
      bot.send_animation(user_id, gif_url, caption=commands_message, parse_mode='Markdown')


def crypto_commands_message(user_id, message_id=None, bot=None):
  gif_url = "https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExbnRubmE2azd1dHRyNHB3bnRhOGYxaGRoeWtmYjl3cThwZHlzenhiciZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/3ohs7HdhQA4ffttvrO/giphy.gif"  # GIF URL for animation

  commands_message = """
  🪙 **Crypto Commands** 🪙

  Select a command:

  • /cryptmarket - Get Info on Specific Token.
  • /globalcrypto - Global Status Of Cryptos.
  """

  keyboard = types.InlineKeyboardMarkup()  # Create inline keyboard markup
  back_button = types.InlineKeyboardButton("Back to Menu", callback_data='back_cmd_crypto')
  keyboard.add(back_button)

  if message_id:
      bot.send_animation(user_id, gif_url, caption=commands_message, parse_mode='Markdown', reply_markup=keyboard)
      bot.edit_message_text(chat_id=user_id, message_id=message_id, text=commands_message, reply_markup=keyboard, parse_mode='Markdown')
  else:
      bot.send_animation(user_id, gif_url, caption=commands_message, parse_mode='Markdown', reply_markup=keyboard)


def fetch_market_data():
    try:
        response = requests.get(f'https://www.alphavantage.co/query?function=MARKET_STATUS&apikey={MARKET_STATUS_API_KEY}')
        data = response.json()
        return data
    except Exception as e:
        logger.error("Error fetching market data: %s", e)
        return None

def fetch_exchange_rate(from_currency, to_currency):
    try:
        response = requests.get(f'https://www.alphavantage.co/query?function=CURRENCY_EXCHANGE_RATE&from_currency={from_currency.upper()}&to_currency={to_currency.upper()}&apikey={MARKET_STATUS_API_KEY}')
        data = response.json()
        return data
    except Exception as e:
        logger.error("Error fetching exchange rate data: %s", e)
        return None

@bot.message_handler(commands=['marketnow'])
def send_market_status(message):
    market_data = fetch_market_data()
    if market_data:
        formatted_message = "📊 *Market Status* 📊\n\n"
        for market in market_data['markets']:
            formatted_message += f"🌐 *Region:* {market['region']}\n"
            formatted_message += f"📈 *Market Type:* {market['market_type']}\n"
            formatted_message += f"🕒 *Local Open:* {market['local_open']}\n"
            formatted_message += f"🕓 *Local Close:* {market['local_close']}\n"
            formatted_message += f"📊 *Primary Exchanges:* {market['primary_exchanges']}\n"
            formatted_message += f"📊 *Status:* {market['current_status'].capitalize()}\n"
            formatted_message += "--------------------------------\n"
        bot.reply_to(message, formatted_message, parse_mode='Markdown')
    else:
        bot.reply_to(message, "Failed to fetch market status or empty data received.")

def fetch_global_crypto_data():
    try:
        response = requests.get(f'https://api.coinlore.net/api/global/')
        data = response.json()
        return data
    except Exception as e:
        logger.error("Error fetching global crypto data: %s", e)
        return None

@bot.message_handler(commands=['globalcrypto'])
def send_global_crypto_info(message):
    global_crypto_data = fetch_global_crypto_data()
    if global_crypto_data:
        formatted_message = "🌐 *Global Crypto Market Info* 🌐\n\n"
        formatted_message += f"📊 *Total Coins Count:* {global_crypto_data[0]['coins_count']}\n"
        formatted_message += f"📈 *Active Markets:* {global_crypto_data[0]['active_markets']}\n"
        formatted_message += f"💰 *Total Market Cap (USD):* {global_crypto_data[0]['total_mcap']}\n"
        formatted_message += f"💹 *Total 24h Volume (USD):* {global_crypto_data[0]['total_volume']}\n"
        formatted_message += f"📊 *Bitcoin Dominance (%):* {global_crypto_data[0]['btc_d']}\n"
        formatted_message += f"📊 *Ethereum Dominance (%):* {global_crypto_data[0]['eth_d']}\n"
        formatted_message += f"📈 *Market Cap Change (%):* {global_crypto_data[0]['mcap_change']}\n"
        formatted_message += f"📉 *Volume Change (%):* {global_crypto_data[0]['volume_change']}\n"
        formatted_message += f"📈 *Average Change Percent (%):* {global_crypto_data[0]['avg_change_percent']}\n"
        formatted_message += f"💹 *Volume All Time High (USD):* {global_crypto_data[0]['volume_ath']}\n"
        formatted_message += f"💰 *Market Cap All Time High (USD):* {global_crypto_data[0]['mcap_ath']}\n"
        bot.reply_to(message, formatted_message, parse_mode='Markdown')
    else:
        bot.reply_to(message, "Failed to fetch global crypto market data or empty data received.")

def loading_bar(current_step, total_steps):
    bar = "▓" * current_step + "░" * (total_steps - current_step)
    return f"[{bar}] {current_step}/{total_steps}"

@bot.message_handler(commands=['predict'])
def handle_predict(message):
    msg = message.text.split()

    if len(msg) != 3:
        bot.reply_to(message, "Invalid command format. Use /predict Stock TimeFrame")
        return

    _, stock_short, time_period = msg

    stock_info = df[df['Stock_short'] == stock_short.upper()]

    if stock_info.empty:
        bot.reply_to(message, f"Stock {stock_short} not found!")
        return

    if time_period == '30d':
        avg_close_price = stock_info['Avg_30_days_close_price'].values[0]
    elif time_period == '6m':
        avg_close_price = stock_info['Avg_6_months_close_price'].values[0]
    elif time_period == '1y':
        avg_close_price = stock_info['Avg_1_year_close_price'].values[0]
    else:
        bot.reply_to(message, "Invalid time period. Use 30d, 6m, or 1y.")
        return

    # Simulate bot typing
    bot.send_chat_action(message.chat.id, 'typing')
    time.sleep(2)

    sent_message = bot.send_message(chat_id=message.chat.id, text=f"Fetching {loading_bar(0, 3)}")

    time.sleep(2)
    bot.edit_message_text(chat_id=message.chat.id, message_id=sent_message.message_id, text=f" {loading_bar(1, 3)}")

    time.sleep(2)
    bot.edit_message_text(chat_id=message.chat.id, message_id=sent_message.message_id, text=f" {loading_bar(2, 3)}")

    final_response = (
        f"--------\n"
        f"**Average {time_period.capitalize()} Close Price**\n"
        f"📈 **Stock:** {stock_info['Stock_name'].values[0]} ({stock_short})\n"
        f"💵 **Price:** ${avg_close_price:.2f}"
    )

    bot.edit_message_text(chat_id=message.chat.id, message_id=sent_message.message_id, text=final_response, parse_mode='Markdown')

def fetch_top_gainers():
    try:
        response = requests.get(f'https://www.alphavantage.co/query?function=TOP_GAINERS_LOSERS&apikey={MARKET_STATUS_API_KEY}')
        data = response.json()
        return data
    except Exception as e:
        logger.error("Error fetching top gainers data: %s", e)
        return None

@bot.message_handler(commands=['topgain'])
def send_top_gainers(message):
    top_gainers_data = fetch_top_gainers()
    if top_gainers_data and 'top_gainers' in top_gainers_data:
        formatted_message = "📈 *Top Gainers* 📈\n\n"
        for gainer in top_gainers_data['top_gainers']:
            formatted_message += f"🔹 *Ticker:* {gainer['ticker']}\n"
            formatted_message += f"💲 *Price:* {gainer['price']}\n"
            formatted_message += f"📈 *Change Amount:* {gainer['change_amount']}\n"
            formatted_message += f"📈 *Change Percentage:* {gainer['change_percentage']}\n"
            formatted_message += f"📊 *Volume:* {gainer['volume']}\n"
            formatted_message += "--------------------------------\n"
        bot.reply_to(message, formatted_message, parse_mode='Markdown')
    else:
        bot.reply_to(message, "Failed to fetch top gainers or empty data received.")

@bot.message_handler(commands=['exchange'])
def send_exchange_rate(message):
    text = message.text.split()
    if len(text) == 3:
        from_currency = text[1].upper()
        to_currency = text[2].upper()
        exchange_data = fetch_exchange_rate(from_currency, to_currency)
        if exchange_data and 'Realtime Currency Exchange Rate' in exchange_data:
            exchange_rate = exchange_data['Realtime Currency Exchange Rate']['5. Exchange Rate']
            bot.reply_to(message, f"💱 Exchange Rate 💱\n\n🔄 From: {from_currency}\n➡️ To: {to_currency}\n💰 Rate: {exchange_rate}")
        else:
            bot.reply_to(message, "Failed to fetch exchange rate or invalid currency.")
    else:
        bot.reply_to(message, "Invalid command format. Use /exchange FROMCURRENCY TOCURRENCY")

@bot.message_handler(commands=['chart'])
def chart(message):
    duration = message.text.split()[1] if len(message.text.split()) > 1 else None
    if duration:
        if duration == '30d':
            send_progress_chart(message, 'images/30d_chart.png', "Here's the chart for the last 30 days:")
        elif duration == '6m':
            send_progress_chart(message, 'images/6m_chart.png', "Here's the chart for the last 6 months:")
        elif duration == '1y':
            send_progress_chart(message, 'images/1y_chart.png', "Here's the chart for the last 1 year:")
        else:
            bot.reply_to(message, "Invalid duration. Please specify a valid duration ('30d', '6m', or '1y').")
    else:
        bot.reply_to(message, "Please specify a duration (e.g., /chart 30d)")

def send_progress_chart(message, chart_name, caption, progress=0, sent_message=None):
  visual_bar = generate_progress_bar(progress)

  if sent_message:
      # Edit the existing message to update the visual bar and display "Generating Chart..."
      bot.edit_message_text(chat_id=message.chat.id, message_id=sent_message.message_id, text=f"Generating Chart...\n{visual_bar}", parse_mode=None)
  else:
      # Send a new message with the visual bar and display "Generating Chart..."
      sent_message = bot.send_message(message.chat.id, f"Generating Chart...\n{visual_bar}", parse_mode=None)

  if progress < 100:
      # Increment progress and continue generating chart
      progress += random.randint(6, 14)  # Increment progress by random amount
      time.sleep(2)  # Adjust delay as needed
      send_progress_chart(message, chart_name, caption, progress, sent_message)
  else:
      # Send the chart when progress reaches 100%
      send_chart(message, chart_name, caption)


def generate_progress_bar(progress):
  bar_length = 20
  filled_blocks = int(progress / (100 / bar_length))
  empty_blocks = bar_length - filled_blocks

  # Define colors for filled and empty blocks
  filled_color = '🟩'  # Green
  empty_color = '⬜'    # White

  # Construct the progress bar
  progress_bar = filled_color * filled_blocks + empty_color * empty_blocks

  return f"`{progress_bar} {progress}%`"

def send_chart(message, chart_name, caption):
    with open(chart_name, 'rb') as chart_image:
        bot.send_photo(message.chat.id, chart_image, caption=caption)



# Handler for /cryptomarket command
@bot.message_handler(commands=['cryptomarket'])
def send_crypto_market_info(message):
  bot.send_message(message.chat.id, "Sure! What cryptocurrency are you interested in?")

  @bot.message_handler(func=lambda inner_message: True, content_types=['text'])
  def handle_crypto_ticker(inner_message):
      ticker_symbol = inner_message.text.upper()
      ticker_ids = read_ticker_ids()
      if ticker_symbol in ticker_ids:
          crypto_id = ticker_ids[ticker_symbol]
          crypto_info = fetch_crypto_info_by_id(crypto_id)
          if crypto_info:
              formatted_message = f"📊 *Crypto Market Info for {ticker_symbol}* 📊\n\n"
              formatted_message += f"📈 *Name:* {crypto_info[0]['name']}\n"
              formatted_message += f"💰 *Price (USD):* {crypto_info[0]['price_usd']}\n"
              formatted_message += f"📉 *Change (24h):* {crypto_info[0]['percent_change_24h']}%\n"
              formatted_message += f"📈 *Change (1h):* {crypto_info[0]['percent_change_1h']}%\n"
              formatted_message += f"📉 *Change (7d):* {crypto_info[0]['percent_change_7d']}%\n"
              formatted_message += f"💹 *Market Cap (USD):* {crypto_info[0]['market_cap_usd']}\n"
              formatted_message += f"📊 *24h Volume (USD):* {crypto_info[0]['volume24']}\n"
              formatted_message += f"💲 *Circulating Supply:* {crypto_info[0]['csupply']}\n"
              bot.reply_to(inner_message, formatted_message, parse_mode='Markdown')
          else:
              bot.reply_to(inner_message, "Failed to fetch crypto market info or empty data received.")
      else:
          bot.reply_to(inner_message, "Invalid ticker symbol. Please provide a valid cryptocurrency ticker symbol.")

bot.polling(none_stop=True)
