from flask import Flask, request
import qrcode
import io
import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters

import nest_asyncio
nest_asyncio.apply()

TOKEN = "YOUR_TELEGRAM_BOT_TOKEN"  # <- replace this

app = Flask(__name__)

def generate_upi_qr(upi_id, amount):
    upi_url = f"upi://pay?pa={upi_id}&am={amount}&cu=INR"
    qr = qrcode.make(upi_url)
    img_byte_arr = io.BytesIO()
    qr.save(img_byte_arr, format='PNG')
    img_byte_arr.seek(0)
    return img_byte_arr

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    try:
        upi_id, amount = text.split()
        qr_img = generate_upi_qr(upi_id, amount)
        await update.message.reply_photo(photo=qr_img, caption=f"Pay ₹{amount} to {upi_id}")
    except:
        await update.message.reply_text("Send in format: `upi@id amount`")

bot_app = ApplicationBuilder().token(TOKEN).build()
bot_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

@app.route(f'/{TOKEN}', methods=["POST"])
async def webhook():
    update = Update.de_json(request.get_json(force=True), bot_app.bot)
    await bot_app.process_update(update)
    return "ok"

@app.route("/")
def home():
    return "Bot is running!"
