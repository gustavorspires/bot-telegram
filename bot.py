import telebot as tb
import random

bot = tb.TeleBot("7595047242:AAHIpE81azO9focgvhnrb0jFHvdDD1G0_8U", parse_mode = "none")

@bot.message_handler(commands=['start', 'help'])
def start(message:tb.types.Message):
    bot.reply_to(message, "Olá, eu sou o bot do Da Roca! (ou o Da Roca é meu bot? Veremos. =)")

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



bot.infinity_polling()