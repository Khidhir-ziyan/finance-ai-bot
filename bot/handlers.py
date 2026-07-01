import logging
from datetime import datetime, timedelta
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ContextTypes

from services.ai_parser import parse_transaction
from services.database import save_transaction, get_transactions_by_date, get_transactions_by_week

logger = logging.getLogger(__name__)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    chat_id = update.message.chat_id
    
    try:
        parsed = await parse_transaction(text)
        
        if "error" in parsed:
            await context.bot.send_message(
                chat_id=chat_id,
                text=f"Error: {parsed['error']}\n\nContoh format yang benar:\n- 'Jual kaos hitam 3 pcs dapet 250rb'\n- 'Beli bahan baku abis 75000'"
            )
            return
        
        result = save_transaction(
            jenis=parsed["jenis"],
            kategori=parsed["kategori"],
            nominal=parsed["nominal"],
            keterangan=parsed["keterangan"],
            raw_text=text
        )
        
        if result["success"]:
            confirmation = (
                f"Transaksi berhasil dicatat!\n\n"
                f"Jenis: {parsed['jenis']}\n"
                f"Kategori: {parsed['kategori']}\n"
                f"Nominal: Rp {parsed['nominal']:,.0f}\n"
                f"Keterangan: {parsed['keterangan']}"
            )
            await context.bot.send_message(chat_id=chat_id, text=confirmation)
        else:
            await context.bot.send_message(
                chat_id=chat_id,
                text="Terjadi kesalahan saat menyimpan data. Silakan coba lagi."
            )
    except Exception as e:
        logger.error(f"Error handling message: {e}")
        await context.bot.send_message(
            chat_id=chat_id,
            text="Terjadi kesalahan internal. Silakan coba lagi nanti."
        )

async def handle_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = (
        "FinBot-AI - Asisten Keuangan\n\n"
        "Cara menggunakan:\n"
        "- Kirim pesan untuk mencatat transaksi\n"
        "- Contoh: 'Jual kaos hitam 3 pcs dapet 250rb'\n"
        "- Contoh: 'Beli bahan baku abis 75000'\n\n"
        "Perintah:\n"
        "/help - Tampilkan bantuan ini\n"
        "/today - Ringkasan transaksi hari ini\n"
        "/weekly - Ringkasan transaksi minggu ini\n"
        "/summary - Ringkasan semua transaksi"
    )
    await update.message.reply_text(help_text)

async def handle_today(update: Update, context: ContextTypes.DEFAULT_TYPE):
    today = datetime.now().strftime("%Y-%m-%d")
    transactions = get_transactions_by_date(today)
    
    if not transactions:
        await update.message.reply_text("Tidak ada transaksi hari ini.")
        return
    
    total_pemasukan = sum(t["nominal"] for t in transactions if t["jenis"] == "Pemasukan")
    total_pengeluaran = sum(t["nominal"] for t in transactions if t["jenis"] == "Pengeluaran")
    
    summary = f"Ringkasan {today}:\n\n"
    summary += f"Total Pemasukan: Rp {total_pemasukan:,.0f}\n"
    summary += f"Total Pengeluaran: Rp {total_pengeluaran:,.0f}\n"
    summary += f"Selisih: Rp {total_pemasukan - total_pengeluaran:,.0f}\n\n"
    summary += "Transaksi:\n"
    for t in transactions:
        summary += f"- {t['jenis']}: {t['keterangan']} (Rp {t['nominal']:,.0f})\n"
    
    await update.message.reply_text(summary)

async def handle_weekly(update: Update, context: ContextTypes.DEFAULT_TYPE):
    today = datetime.now()
    week_start = today - timedelta(days=today.weekday())
    week_end = week_start + timedelta(days=6)
    
    transactions = get_transactions_by_week(
        week_start.strftime("%Y-%m-%d"),
        week_end.strftime("%Y-%m-%d")
    )
    
    if not transactions:
        await update.message.reply_text("Tidak ada transaksi minggu ini.")
        return
    
    total_pemasukan = sum(t["nominal"] for t in transactions if t["jenis"] == "Pemasukan")
    total_pengeluaran = sum(t["nominal"] for t in transactions if t["jenis"] == "Pengeluaran")
    
    summary = f"Ringkasan Mingguan ({week_start.strftime('%d %b')} - {week_end.strftime('%d %b %Y')}):\n\n"
    summary += f"Total Pemasukan: Rp {total_pemasukan:,.0f}\n"
    summary += f"Total Pengeluaran: Rp {total_pengeluaran:,.0f}\n"
    summary += f"Selisih: Rp {total_pemasukan - total_pengeluaran:,.0f}\n\n"
    summary += f"Jumlah Transaksi: {len(transactions)}"
    
    await update.message.reply_text(summary)

async def handle_summary(update: Update, context: ContextTypes.DEFAULT_TYPE):
    from services.database import get_all_transactions
    transactions = get_all_transactions()
    
    if not transactions:
        await update.message.reply_text("Belum ada transaksi.")
        return
    
    total_pemasukan = sum(t["nominal"] for t in transactions if t["jenis"] == "Pemasukan")
    total_pengeluaran = sum(t["nominal"] for t in transactions if t["jenis"] == "Pengeluaran")
    
    summary = "Ringkasan Semua Transaksi:\n\n"
    summary += f"Total Pemasukan: Rp {total_pemasukan:,.0f}\n"
    summary += f"Total Pengeluaran: Rp {total_pengeluaran:,.0f}\n"
    summary += f"Selisih: Rp {total_pemasukan - total_pengeluaran:,.0f}\n\n"
    summary += f"Jumlah Transaksi: {len(transactions)}"
    
    await update.message.reply_text(summary)