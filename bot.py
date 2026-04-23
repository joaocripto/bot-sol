import os
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

TOKEN = os.environ.get("TOKEN")
GRUPO = os.environ.get("GRUPO")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🛍️ Bot de Achadinhos da Sol ativo!\n\nUse: /achadinho nome - preço - link")

async def achadinho(update: Update, context: ContextTypes.DEFAULT_TYPE):
    texto = " ".join(context.args)
    if texto:
        partes = texto.split(" - ")
        if len(partes) == 3:
            nome, preco, link = partes
            mensagem = (
                f"🔥 *ACHADINHO DA SOL* 🔥\n\n"
                f"🛍️ *{nome}*\n"
                f"💰 *{preco}*\n"
                f"🔗 {link}\n\n"
                f"👆 Clique no link e aproveite!"
            )
        else:
            mensagem = f"🔥 *ACHADINHO DA SOL* 🔥\n\n{texto}"
        await update.message.reply_text(mensagem, parse_mode="Markdown")
    else:
        await update.message.reply_text("⚠️ Use assim:\n/achadinho Nome - R$XX,XX - link")

async def buscar_ofertas(context: ContextTypes.DEFAULT_TYPE):
    try:
        url = "https://api.mercadolibre.com/sites/MLB/search?q=oferta+do+dia&sort=price_asc&limit=1&condition=new"
        r = requests.get(url, timeout=10)
        data = r.json()
        items = data.get("results", [])
        if not items:
            return
        item = items[0]
        nome = item["title"]
        preco = f"R${item['price']:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        link = item["permalink"]
        mensagem = (
            f"🔥 *ACHADINHO DA SOL* 🔥\n\n"
            f"🛍️ *{nome}*\n"
            f"💰 *{preco}*\n"
            f"🔗 {link}\n\n"
            f"👆 Clique no link e aproveite!"
        )
        await context.bot.send_message(chat_id=GRUPO, text=mensagem, parse_mode="Markdown")
    except Exception as e:
        print(f"Erro: {e}")

app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("achadinho", achadinho))
app.job_queue.run_repeating(buscar_ofertas, interval=3600, first=15)
app.run_polling(drop_pending_updates=True)
