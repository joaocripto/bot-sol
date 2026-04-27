import os
import logging
import re
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

# ══════════════════════════════════════
# CONFIGURAÇÕES
# ══════════════════════════════════════
TOKEN = os.environ.get("TOKEN")
GRUPO = os.environ.get("GRUPO")

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("AchadinhosBot")

# ══════════════════════════════════════
# COMANDO /start
# ══════════════════════════════════════
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🛍️ *Bot Achadinhos da Sol ativo!*\n\n"
        "📌 *Como usar:*\n\n"
        "1️⃣ /produto Nome | Preço | Link\n"
        "_(ex: /produto Tênis Nike | R$199,90 | shopee.com/xxx)_\n\n"
        "2️⃣ Cole qualquer link aqui\n"
        "_(Shopee, ML, Amazon — eu formato e posto!)_\n\n"
        "3️⃣ /promo texto livre\n"
        "_(posta uma promoção personalizada)_",
        parse_mode="Markdown"
    )

# ══════════════════════════════════════
# COMANDO /produto — formato completo
# ══════════════════════════════════════
async def produto(update: Update, context: ContextTypes.DEFAULT_TYPE):
    texto = " ".join(context.args)
    if not texto or "|" not in texto:
        await update.message.reply_text(
            "⚠️ Use assim:\n`/produto Nome | Preço | Link`\n\n"
            "Exemplo:\n`/produto Tênis Nike Air | R$199,90 | https://shopee.com.br/xxx`",
            parse_mode="Markdown"
        )
        return

    partes = [p.strip() for p in texto.split("|")]
    nome  = partes[0] if len(partes) > 0 else ""
    preco = partes[1] if len(partes) > 1 else ""
    link  = partes[2] if len(partes) > 2 else ""
    extra = partes[3] if len(partes) > 3 else ""  # info adicional opcional

    msg = formatar_produto(nome, preco, link, extra)

    try:
        await context.bot.send_message(
            chat_id=GRUPO,
            text=msg,
            parse_mode="Markdown",
            disable_web_page_preview=False
        )
        await update.message.reply_text("✅ Postado no grupo!")
    except Exception as e:
        log.error(f"Erro ao postar: {e}")
        await update.message.reply_text(f"❌ Erro: {e}")

# ══════════════════════════════════════
# COMANDO /promo — texto livre
# ══════════════════════════════════════
async def promo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    texto = " ".join(context.args)
    if not texto:
        await update.message.reply_text("⚠️ Use: `/promo seu texto aqui`", parse_mode="Markdown")
        return

    msg = (
        f"🔥 *ACHADINHO DA SOL* 🔥\n\n"
        f"{texto}\n\n"
        f"⚡ _Corre que pode acabar!_"
    )

    try:
        await context.bot.send_message(
            chat_id=GRUPO,
            text=msg,
            parse_mode="Markdown"
        )
        await update.message.reply_text("✅ Postado no grupo!")
    except Exception as e:
        await update.message.reply_text(f"❌ Erro: {e}")

# ══════════════════════════════════════
# LINK AUTOMÁTICO — detecta loja pelo link
# ══════════════════════════════════════
async def link_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    texto = update.message.text or ""
    link  = extrair_link(texto)
    if not link:
        return

    loja = detectar_loja(link)
    emoji_loja = {
        "Shopee": "🛍️",
        "Mercado Livre": "🛒",
        "Amazon": "📦",
        "Americanas": "🛍️",
        "Magazine Luiza": "🏪",
        "Casas Bahia": "🏠",
    }.get(loja, "🔗")

    msg = (
        f"🔥 *ACHADINHO DA SOL* 🔥\n\n"
        f"{emoji_loja} *Produto {loja}*\n\n"
        f"💰 *Veja o preço no link abaixo!*\n"
        f"🔗 {link}\n\n"
        f"⚡ _Corre que pode acabar!_\n"
        f"👆 _Clique no link e aproveite!_"
    )

    try:
        await context.bot.send_message(
            chat_id=GRUPO,
            text=msg,
            parse_mode="Markdown",
            disable_web_page_preview=False
        )
        await update.message.reply_text(f"✅ Link da {loja} postado no grupo!")
    except Exception as e:
        log.error(f"Erro link: {e}")
        await update.message.reply_text(f"❌ Erro: {e}")

# ══════════════════════════════════════
# HELPERS
# ══════════════════════════════════════
def formatar_produto(nome, preco, link, extra=""):
    # Detecta se tem desconto no preço (ex: "R$199 de R$399")
    desconto = ""
    if "de r$" in preco.lower() or "por r$" in preco.lower():
        partes = re.split(r'(?i)(de r\$|por r\$)', preco)
        preco_atual = partes[0].strip()
        preco_orig  = partes[-1].strip() if len(partes) > 1 else ""
        if preco_orig:
            desconto = f"\n~~{preco_orig}~~"
        preco = preco_atual

    extra_txt = f"\n\nℹ️ _{extra}_" if extra else ""

    return (
        f"🔥 *ACHADINHO DA SOL* 🔥\n\n"
        f"🛍️ *{nome}*\n\n"
        f"💰 *{preco}*{desconto}\n"
        f"🔗 {link}"
        f"{extra_txt}\n\n"
        f"⚡ _Corre que pode acabar!_\n"
        f"👆 _Clique no link e aproveite!_"
    )

def extrair_link(texto):
    match = re.search(r'https?://\S+', texto)
    return match.group(0) if match else None

def detectar_loja(link):
    lojas = {
        "shopee": "Shopee",
        "shope.ee": "Shopee",
        "mercadolivre": "Mercado Livre",
        "mercadolibre": "Mercado Livre",
        "amazon": "Amazon",
        "amzn": "Amazon",
        "americanas": "Americanas",
        "magazineluiza": "Magazine Luiza",
        "magalu": "Magazine Luiza",
        "casasbahia": "Casas Bahia",
    }
    link_lower = link.lower()
    for chave, nome in lojas.items():
        if chave in link_lower:
            return nome
    return "Loja"

# ══════════════════════════════════════
# MAIN
# ══════════════════════════════════════
def main():
    log.info("Achadinhos da Sol Bot iniciando...")
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("produto", produto))
    app.add_handler(CommandHandler("promo", promo))
    app.add_handler(MessageHandler(
        filters.TEXT & filters.Regex(r'https?://'),
        link_handler
    ))

    log.info("Bot rodando!")
    app.run_polling(drop_pending_updates=True, allowed_updates=["message"])

if __name__ == "__main__":
    main()
