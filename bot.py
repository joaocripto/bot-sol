import os
import logging
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

# ══════════════════════════════════════
# CONFIGURAÇÕES
# ══════════════════════════════════════
TOKEN = os.environ.get("TELEGRAM_TOKEN") or os.environ.get("TOKEN")
GRUPO = os.environ.get("TELEGRAM_CHAT_ID") or os.environ.get("GRUPO")

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("AchadinhosBot")

# ══════════════════════════════════════
# COMANDO /start
# ══════════════════════════════════════
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🛍️ *Bot Achadinhos da Sol ativo!*\n\n"
        "📌 *Como usar:*\n\n"
        "1️⃣ /achadinho nome - preço - link\n"
        "_(posta produto formatado no grupo)_\n\n"
        "2️⃣ Cole um link da Shopee aqui\n"
        "_(eu formato e posto no grupo)_\n\n"
        "3️⃣ /buscar palavra\n"
        "_(busca no Mercado Livre e posta)_\n\n"
        "🤖 A cada 3h posto ofertas automáticas do ML!",
        parse_mode="Markdown"
    )

# ══════════════════════════════════════
# COMANDO /achadinho — formato manual
# ══════════════════════════════════════
async def achadinho(update: Update, context: ContextTypes.DEFAULT_TYPE):
    texto = " ".join(context.args)
    if not texto:
        await update.message.reply_text(
            "⚠️ Use assim:\n`/achadinho Nome - R$XX,XX - link`",
            parse_mode="Markdown"
        )
        return

    partes = texto.split(" - ")
    if len(partes) >= 3:
        nome  = partes[0].strip()
        preco = partes[1].strip()
        link  = partes[2].strip()
        msg = formatar_produto(nome, preco, link, "Manual")
    else:
        msg = f"🔥 *ACHADINHO DA SOL* 🔥\n\n{texto}"

    # Posta no grupo
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
# COMANDO /buscar — busca no ML
# ══════════════════════════════════════
async def buscar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    termo = " ".join(context.args)
    if not termo:
        await update.message.reply_text("⚠️ Use: `/buscar tênis nike`", parse_mode="Markdown")
        return

    await update.message.reply_text(f"🔍 Buscando *{termo}* no Mercado Livre...", parse_mode="Markdown")
    produtos = buscar_ml(termo, limite=3)

    if not produtos:
        await update.message.reply_text("❌ Nenhum produto encontrado.")
        return

    for p in produtos:
        msg = formatar_produto(p["nome"], p["preco"], p["link"], "Mercado Livre")
        try:
            await context.bot.send_message(
                chat_id=GRUPO,
                text=msg,
                parse_mode="Markdown",
                disable_web_page_preview=False
            )
        except Exception as e:
            log.error(f"Erro ao postar produto: {e}")

    await update.message.reply_text(f"✅ {len(produtos)} produtos postados no grupo!")

# ══════════════════════════════════════
# LINK AUTOMÁTICO — detecta Shopee/ML
# ══════════════════════════════════════
async def link_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    texto = update.message.text or ""

    if "shopee.com.br" in texto or "shope.ee" in texto:
        await update.message.reply_text("🛍️ Link da Shopee detectado! Formatando...")
        msg = (
            f"🔥 *ACHADINHO DA SOL* 🔥\n\n"
            f"🛍️ *Produto Shopee*\n"
            f"💰 *Veja o preço no link!*\n"
            f"🔗 {texto.strip()}\n\n"
            f"⚡ Corre que pode acabar!\n"
            f"👆 Clique no link e aproveite!"
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

    elif "mercadolivre.com.br" in texto or "mercadolibre.com" in texto:
        await update.message.reply_text("🛒 Link do ML detectado! Formatando...")
        msg = (
            f"🔥 *ACHADINHO DA SOL* 🔥\n\n"
            f"🛒 *Produto Mercado Livre*\n"
            f"💰 *Veja o preço no link!*\n"
            f"🔗 {texto.strip()}\n\n"
            f"⚡ Corre que pode acabar!\n"
            f"👆 Clique no link e aproveite!"
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
# AUTO POST — Mercado Livre a cada 3h
# ══════════════════════════════════════
async def auto_ofertas(context: ContextTypes.DEFAULT_TYPE):
    log.info("Buscando ofertas automáticas do ML...")
    categorias = [
        ("eletronicos oferta", "⚡"),
        ("moda feminina", "👗"),
        ("casa decoracao", "🏠"),
        ("calcados tenis", "👟"),
        ("beleza skincare", "💄"),
        ("smartphone barato", "📱"),
        ("fone ouvido", "🎧"),
    ]

    import random
    termo, emoji = random.choice(categorias)
    produtos = buscar_ml(termo, limite=2)

    if not produtos:
        log.warning("Sem produtos ML")
        return

    for p in produtos:
        msg = formatar_produto(p["nome"], p["preco"], p["link"], "Mercado Livre", emoji)
        try:
            await context.bot.send_message(
                chat_id=GRUPO,
                text=msg,
                parse_mode="Markdown",
                disable_web_page_preview=False
            )
            log.info(f"Produto postado: {p['nome'][:50]}")
        except Exception as e:
            log.error(f"Erro auto post: {e}")

# ══════════════════════════════════════
# HELPERS
# ══════════════════════════════════════
def buscar_ml(termo, limite=3):
    """Busca ofertas no Promobit via RSS — funciona em qualquer servidor"""
    import re
    feeds = [
        "https://www.promobit.com.br/feed/ofertas/rss.xml",
        "https://www.pelando.com.br/feed",
    ]
    produtos = []
    vistos = set()
    for feed_url in feeds:
        try:
            r = requests.get(feed_url, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
            r.raise_for_status()
            items = re.findall(r'<item>(.*?)</item>', r.text, re.DOTALL)
            for item in items:
                titulo_m = re.search(r'<title>(?:<![CDATA[)?(.*?)(?:]]>)?</title>', item)
                link_m   = re.search(r'<link>(.*?)</link>', item) or re.search(r'<guid>(.*?)</guid>', item)
                desc_m   = re.search(r'<description>(?:<![CDATA[)?(.*?)(?:]]>)?</description>', item, re.DOTALL)
                if titulo_m:
                    nome = re.sub(r'<[^>]+>', '', titulo_m.group(1)).strip()
                    if nome and nome not in vistos and len(nome) > 5:
                        vistos.add(nome)
                        desc = re.sub(r'<[^>]+>', '', desc_m.group(1) if desc_m else '')[:200].strip()
                        # Tenta extrair preço da descrição
                        preco_m = re.search(r'R\$\s*([\d.,]+)', desc)
                        preco = f"R$ {preco_m.group(1)}" if preco_m else "Veja o preço no link!"
                        produtos.append({
                            "nome": nome,
                            "preco": preco,
                            "link": link_m.group(1).strip() if link_m else feed_url,
                        })
                        if len(produtos) >= limite:
                            return produtos
        except Exception as e:
            log.error(f"Erro feed {feed_url}: {e}")
    return produtos

def formatar_produto(nome, preco, link, fonte="", emoji="🔥"):
    return (
        f"{emoji} *ACHADINHO DA SOL* {emoji}\n\n"
        f"🛍️ *{nome}*\n"
        f"💰 *{preco}*\n"
        f"🔗 {link}\n\n"
        f"⚡ Corre que pode acabar!\n"
        f"👆 Clique no link e aproveite!\n\n"
        f"_via {fonte}_"
    )

# ══════════════════════════════════════
# MAIN
# ══════════════════════════════════════
def main():
    log.info("Achadinhos da Sol Bot iniciando...")
    app = ApplicationBuilder().token(TOKEN).build()

    # Handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("achadinho", achadinho))
    app.add_handler(CommandHandler("buscar", buscar))
    app.add_handler(MessageHandler(
        filters.TEXT & filters.Regex(r'(shopee|mercadolivre|shope\.ee|mercadolibre)'),
        link_handler
    ))

    # Auto post a cada 3h
    app.job_queue.run_repeating(auto_ofertas, interval=10800, first=30)

    log.info("Bot rodando!")
    app.run_polling(drop_pending_updates=True, allowed_updates=["message"])

if __name__ == "__main__":
    main()
