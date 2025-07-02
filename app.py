import json
import asyncio
from datetime import datetime
from pytz import timezone
from apscheduler.schedulers.background import BackgroundScheduler
from telegram import Bot

# CONFIGURAÇÕES
TOKEN = '7719517808:AAGEINbjIMMH_yiBYuFZWPW5u8R-Mzk-JQc'
CHAT_ID = '7714785907'
TIMEZONE = timezone('America/Sao_Paulo')
OPERATIONS_FILE = 'operations.json'

bot = Bot(token=TOKEN)

def carregar_operacoes():
    with open(OPERATIONS_FILE, 'r') as f:
        return json.load(f)

def dias_restantes(data_str):
    hoje = datetime.now(TIMEZONE).date()
    data_op = datetime.strptime(data_str, '%Y-%m-%d').date()
    return (data_op - hoje).days

def gerar_relatorio():
    operacoes = carregar_operacoes()
    hoje = datetime.now(TIMEZONE).date()
    relatorio = f"📊 *Relatório de Operações* ({hoje.strftime('%d/%m/%Y')})\n\n"
    aviso_especial = ""

    for op in operacoes:
        dias = dias_restantes(op["data"])
        status = f"{dias} dias restantes" if dias > 1 else \
                 "⚠️ Último dia!" if dias == 1 else \
                 "❌ Vencido!"

        relatorio += f"• {op['nome']} - 💰 R${op['valor']:.2f} - 📅 {op['data']} - {status}\n"

        if dias == 1:
            aviso_especial += f"\n🔔 *Atenção!* A operação *{op['nome']}* vence *amanhã!*"

    if aviso_especial:
        relatorio += "\n" + aviso_especial

    return relatorio

async def enviar_relatorio():
    texto = gerar_relatorio()
    await bot.send_message(chat_id=CHAT_ID, text=texto, parse_mode='Markdown')

def agendar():
    scheduler = BackgroundScheduler(timezone=TIMEZONE)

    # ✅ Envia todos os dias às 12h00 e às 23h00
    scheduler.add_job(lambda: asyncio.run(enviar_relatorio()), 'cron', hour=12, minute=0)
    scheduler.add_job(lambda: asyncio.run(enviar_relatorio()), 'cron', hour=23, minute=0)

    scheduler.start()

if __name__ == '__main__':
    asyncio.run(enviar_relatorio())  # Envia ao iniciar uma vez
    agendar()

    print("Bot está rodando. Pressione Ctrl+C para sair.")
    import time
    try:
        while True:
            time.sleep(10)
    except (KeyboardInterrupt, SystemExit):
        print("Bot finalizado.")
