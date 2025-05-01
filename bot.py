import telebot as tb
import random
import os
from dotenv import load_dotenv
import pandas as pd
import datetime
import schedule as sc
import time
import random


planilha = 'aniversarios.ods'

# Carregamento do token do bot e inicialização do bot
load_dotenv()
bot = tb.TeleBot(os.getenv("BOT_TOKEN"), parse_mode = "none")

# Envia diariamente mensagens dando feliz aniversario pros aniversariantes do dia
def niver_diario():
    print("[LOG] Função niver_diario foi chamada")
    hoje = datetime.date.today()
    dia, mes = hoje.day, hoje.month

    try: 
        df = pd.read_excel(planilha, engine="odf", sheet_name="aniversarios")
        df['aniversario'] = pd.to_datetime(df['aniversario'])

        aniversariantes = df[
            (df['aniversario'].dt.day == dia) & (df['aniversario'].dt.month == mes)
        ]
        print(aniversariantes)

        for _, row, in aniversariantes.iterrows():
            username = row['username']
            mensagem = f"Feliz aniversário, @{username}! Aproveite seu dia!"
            bot.send_message(chat_id=-4677092344, text=mensagem)

    except Exception as e:
        print(f"Erro ao verificar aniversários: {e}")

@bot.message_handler(commands=['start', 'help'])
def start(message:tb.types.Message):
    bot.reply_to(message, "Olá, eu sou o bot do Da Roca! (ou o Da Roca é meu bot? Veremos. =)\n *Funcionalidades*\n\n- _/sorteio <min> <max>_ - sorteia um inteiro no intervalo inserido;\n- _/engracado_ - coisas funny\n- _/aniversariantes_ - mostra uma lista de aniversariantes\n- _/presente_ - Gerador de ideias de presente Ultra Hiper Mega Blaster bão dimais da conta\n- _/amigosecreto_ - em construção\n- _/about_ - em construção\n- _/spotify_ - em construção\n")

@bot.message_handler(['engracado'])
def engracado(message:tb.types.Message):
    bot.reply_to(message, 'https://www.youtube.com/watch?v=dQw4w9WgXcQ')

@bot.message_handler(['sorteio'])
def sorteio(message:tb.types.Message):
    try:
        partes = message.text.split()
        if len(partes) < 3:
            bot.reply_to(message, "Use assim: /sorteio <mínimo> <máximo>")
        
        menor = min(int(partes[1]), int(partes[2]))
        maior = max(int(partes[1]), int(partes[2]))

        numero = random.randint(menor, maior)

        bot.reply_to(message, f"Número escolhido: {numero}")
    
    except ValueError:
        bot.reply_to(message, "Algum erro ocorreu. Verifique se os números dados são inteiros.")

@bot.message_handler(['aniversariantes'])
def aniversariantes(message:tb.types.Message):
    df = pd.read_excel(planilha, engine="odf", sheet_name="aniversarios")
    df['aniversario'] = pd.to_datetime(df['aniversario'])

    lista = []

    for _, row in df.iterrows():
        nome = row['nome']
        data = row['aniversario'].strftime('%d/%m')
        lista.append(f"- {nome} - {data}")

    reply = "Lista de aniversários: \n" + "\n".join(lista)

    bot.reply_to(message, reply)
    
@bot.message_handler(['presente'])
def presente(message:tb.types.Message):
    df = pd.read_excel(planilha, engine="odf", sheet_name="presentes")
    lista = []

    for _, row in df.iterrows():
        presente = row['presentes']
        lista.append(f"{presente}")

    escolha = random.choice(lista)

    bot.reply_to(message, f"Gerador de ideias de presentes 2k25 Ultra Mega Blaster by Darroca Bot \nIdeia de presente: {escolha}")

sc.every().day.at("08:00").do(niver_diario)

bot.infinity_polling()

while True:
    sc.run_pending()
    time.sleep(1)
