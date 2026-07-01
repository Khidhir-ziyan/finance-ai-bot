import logging
from fastapi import FastAPI, Request, Response
from telegram import Update, Bot
from telegram.ext import Application, MessageHandler, filters, CommandHandler
import uvicorn

from config import TELEGRAM_TOKEN, AUTHORIZED_SENDER_ID
from bot.handlers import handle_message, handle_help, handle_summary, handle_today, handle_weekly

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

app = FastAPI(title="FinBot-AI")

bot = Bot(token=TELEGRAM_TOKEN)
application = Application.builder().token(TELEGRAM_TOKEN).build()

application.add_handler(CommandHandler("help", handle_help))
application.add_handler(CommandHandler("summary", handle_summary))
application.add_handler(CommandHandler("today", handle_today))
application.add_handler(CommandHandler("weekly", handle_weekly))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

@app.on_event("startup")
async def startup():
    await application.initialize()
    logger.info("Bot application initialized")

@app.post("/webhook")
async def webhook(request: Request):
    try:
        data = await request.json()
        update = Update.de_json(data, bot)
        
        if update.message:
            sender_id = update.message.from_user.id
            if sender_id != AUTHORIZED_SENDER_ID:
                logger.warning(f"Unauthorized access attempt from sender_id: {sender_id}")
                await bot.send_message(
                    chat_id=update.message.chat_id,
                    text="Akses ditolak. Anda tidak memiliki izin menggunakan bot ini."
                )
                return Response(status_code=200)
        
        await application.process_update(update)
        return Response(status_code=200)
    except Exception as e:
        logger.error(f"Webhook error: {e}")
        return Response(status_code=500)

@app.get("/health")
async def health():
    return {"status": "healthy", "service": "FinBot-AI"}

@app.get("/")
async def root():
    return {"message": "FinBot-AI is running", "docs": "/docs"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)