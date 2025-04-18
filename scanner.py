from flask import Flask, request
import qrcode
import io
import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters
import threading
import nest_asyncio

nest_asyncio.apply()

TOKEN = "your-token-here"

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

# Start bot polling setup (required for webhooks to function correctly)
threading.Thread(target=bot_app.run_polling, daemon=True).start()

@app.route(f'/{TOKEN}', methods=["POST"])
async def webhook():
    try:
        data = request.get_json(force=True)
        update = Update(**data)
        await bot_app.process_update(update)
    except Exception as e:
        print("Error processing update:", e)
    return "ok"

@app.route("/")
def home():
    return "Bot is running!"
