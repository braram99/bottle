from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackContext, ConversationHandler, MessageHandler, Filters
from telegram_bot_config import TELEGRAM_TOKEN
from risk_logic import evaluar_trade, mostrar_resumen

# Estados de la conversación
SYMBOL, SESSION, BALANCE, SL_PIPS, PIP_VALUE, QUALITY, CONFLUENCIAS, PSYCHOLOGY, RISK_RESULT = range(9)

# Variables temporales del usuario
user_data = {}

# /start command
def start(update: Update, context: CallbackContext):
    update.message.reply_text(
        "👋 Hello! I'm your Trading Risk Assistant.\n\nUse /risk to evaluate if you should trade today."
    )

# /risk conversation start
def start_risk(update: Update, context: CallbackContext):
    update.message.reply_text("📊 Let's evaluate your trade.\n\nWhat symbol are you analyzing? (e.g. EURUSD)")
    return SYMBOL

def get_symbol(update: Update, context: CallbackContext):
    user_data['symbol'] = update.message.text
    update.message.reply_text("Which session is it? (NYO, LON, ASIA, etc.)")
    return SESSION

def get_session(update: Update, context: CallbackContext):
    user_data['session'] = update.message.text
    update.message.reply_text("What's your account balance? (in USD)")
    return BALANCE

def get_balance(update: Update, context: CallbackContext):
    user_data['balance'] = float(update.message.text)
    update.message.reply_text("What's your Stop Loss in pips?")
    return SL_PIPS

def get_sl_pips(update: Update, context: CallbackContext):
    user_data['sl_pips'] = float(update.message.text)
    update.message.reply_text("What's the pip value for 1.0 lot? (e.g. 10)")
    return PIP_VALUE

def get_pip_value(update: Update, context: CallbackContext):
    user_data['pip_value'] = float(update.message.text)
    update.message.reply_text("Quality of setup? (A+, A, B, C)")
    return QUALITY

def get_quality(update: Update, context: CallbackContext):
    user_data['quality'] = update.message.text.upper()
    update.message.reply_text("Now list your confluences (comma separated):\n- estructura_clara\n- eu_gu_correlacion\n- trending_correcto\n- rompe_highs_lows\n- fvg_poi\n- rr_ok\n- direccion_1h\n- direccion_4h\n- noticias_ausentes")
    return CONFLUENCIAS

def get_confluencias(update: Update, context: CallbackContext):
    raw = update.message.text.replace(" ", "").split(",")
    keys = ["estructura_clara", "eu_gu_correlacion", "trending_correcto", "rompe_highs_lows",
            "fvg_poi", "rr_ok", "direccion_1h", "direccion_4h", "noticias_ausentes"]
    user_data['confluencias'] = {key: (key in raw) for key in keys}
    update.message.reply_text("Is your psychology OK? (y/n)")
    return PSYCHOLOGY

def get_psychology(update: Update, context: CallbackContext):
    user_data['psychology_ok'] = update.message.text.lower() == 'y'
    user_data['racha_perdedora'] = False  # You can ask this too if you want
    user_data['volatilidad_normal'] = True  # Optional
    user_data['rr'] = 2.0  # RR expected — puede pedirlo luego también

    # Run evaluation
    resultado = evaluar_trade(
        symbol=user_data['symbol'],
        session=user_data['session'],
        balance=user_data['balance'],
        sl_pips=user_data['sl_pips'],
        pip_value=user_data['pip_value'],
        quality=user_data['quality'],
        confluencias=user_data['confluencias'],
        psicologia_ok=user_data['psychology_ok'],
        racha_perdedora=user_data['racha_perdedora'],
        volatilidad_normal=user_data['volatilidad_normal'],
        rr=user_data['rr']
    )

    resumen = mostrar_resumen(resultado)
    update.message.reply_text(f"✅ Risk Evaluation Completed:\n\n{resumen}")
    return ConversationHandler.END

def cancel(update: Update, context: CallbackContext):
    update.message.reply_text("❌ Risk evaluation cancelled.")
    return ConversationHandler.END

# Main bot runner
def main():
    updater = Updater(TELEGRAM_TOKEN)
    dp = updater.dispatcher

    # Conversation
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('risk', start_risk)],
        states={
            SYMBOL: [MessageHandler(Filters.text & ~Filters.command, get_symbol)],
            SESSION: [MessageHandler(Filters.text & ~Filters.command, get_session)],
            BALANCE: [MessageHandler(Filters.text & ~Filters.command, get_balance)],
            SL_PIPS: [MessageHandler(Filters.text & ~Filters.command, get_sl_pips)],
            PIP_VALUE: [MessageHandler(Filters.text & ~Filters.command, get_pip_value)],
            QUALITY: [MessageHandler(Filters.text & ~Filters.command, get_quality)],
            CONFLUENCIAS: [MessageHandler(Filters.text & ~Filters.command, get_confluencias)],
            PSYCHOLOGY: [MessageHandler(Filters.text & ~Filters.command, get_psychology)],
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )

    dp.add_handler(CommandHandler('start', start))
    dp.add_handler(conv_handler)

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
