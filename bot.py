import telebot as tb
import random
import os
from dotenv import load_dotenv
import pandas as pd
import datetime
import schedule as sc
import time
import random
import json
from spotify_helper import create_playlist, add_track, remove_track

PLANILHA = 'aniversarios.ods'
SORTEIOS = 'sorteios.json'
PLAYLIST = 'playlist.json'
playlists = {}

# Carregamento do token do bot e inicialização do bot
load_dotenv()
bot = tb.TeleBot(os.getenv("BOT_TOKEN"), parse_mode = "none")

def niver_diario():
    """
    Função que verifica se há aniversários no dia e envia uma simples mensagem de parabéns."""
    print("[LOG] Função niver_diario foi chamada")
    hoje = datetime.date.today()
    dia, mes = hoje.day, hoje.month

    try: 
        df = pd.read_excel(PLANILHA, engine="odf", sheet_name="aniversarios")
        df['aniversario'] = pd.to_datetime(df['aniversario'])

        aniversariantes = df[
            (df['aniversario'].dt.day == dia) & (df['aniversario'].dt.month == mes)
        ]
        print(aniversariantes)

        for _, row, in aniversariantes.iterrows():
            name = row['name']
            mensagem = f"Feliz aniversário, @{name}! Aproveite seu dia!"
            bot.send_message(chat_id=-4677092344, text=mensagem)

    except Exception as e:
        print(f"Erro ao verificar aniversários: {e}")

def save_json(data, filename):
    """
    Função auxiliar que salva um dicionário em um arquivo JSON.
    """
    with open(filename, 'w') as f:
        json.dump(data,f)

def load_json(filename):
    """
    Função auxiliar que carrega um dicionário de um arquivo JSON.
    """
    if os.path.exists(filename):
        with open(filename, 'r') as f:
            return json.load(f)
    return {}
        
def get_username(user_id):
    """
    Função auxiliar que retorna o nome de usuário do usuário.
    """
    return f"user_{user_id}"

@bot.message_handler(commands=['start', 'help'])
def start(message:tb.types.Message):
    """
    Comando inicial do bot. Envia uma mensagem de boas-vindas e lista as funcionalidades disponíveis.
    """
    bot.reply_to(message, "Olá, eu sou o bot do Da Roca! (ou o Da Roca é meu bot? Veremos. =)\n Funcionalidades\n\n- /sorteio <min> <max> - sorteia um inteiro no intervalo inserido;\n- /engracado - coisas funny\n- /aniversariantes - mostra uma lista de aniversariantes\n- /presente - Gerador de ideias de presente Ultra Hiper Mega Blaster bão dimais da conta\n- /amigosecreto <iniciar/participar/sortear> - Cria um novo sorteio de amigo secreto! Extremamente útil para grupos que gostam de se presentear.\n- /about - em construção\n- /spotify <iniciar/adicionar/playlist> - Acesse a playlist do grupo! Compartilhe suas músicas favoritas com o grupo e faça parte de uma salada musical!\n")

@bot.message_handler(['engracado'])
def engracado(message:tb.types.Message):
    """"
    Comando que envia coisas supostamente engraçadas. (O humor do bot é quebrado.)
    """
    bot.reply_to(message, 'https://www.youtube.com/watch?v=dQw4w9WgXcQ')

@bot.message_handler(['sorteio'])
def sorteio(message:tb.types.Message):
    """
    Comando que sorteia um número inteiro entre dois números dados pelo usuário.
    """
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
    """
    Comando que busca na planilha de aniversários e retorna uma lista de aniversariantes.
    """
    df = pd.read_excel(PLANILHA, engine="odf", sheet_name="aniversarios")
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
    """
    Comando que gera uma ideia de presente aleatória a partir de uma lista de presentes.
    """
    df = pd.read_excel(PLANILHA, engine="odf", sheet_name="presentes")
    lista = []

    for _, row in df.iterrows():
        presente = row['presentes']
        lista.append(f"{presente}")

    escolha = random.choice(lista)

    bot.reply_to(message, f"Gerador de ideias de presentes 2k25 Ultra Mega Blaster by Darroca Bot \nIdeia de presente: {escolha}")

def is_admin(chat_id, user_id):
    try: 
        member = bot.get_chat_member(chat_id, user_id)
        return member.status in ['administrator', 'creator']
    except Exception as e:
        print(f"Erro ao verificar admin: {e}")
        return False

@bot.message_handler('amigosecreto')
def amigosecreto(message:tb.types.Message):
    """
    Comando que inicia um sorteio de amigo secreto. Utiliza três subcomandos: iniciar, participar e sortear.
    - iniciar: inicia um novo sorteio. 
    - participar: adiciona o usuário ao sorteio.
    - sortear: realiza o sorteio e envia as mensagens para os participantes.
    """
    parts = message.text.split()
    if len(parts) < 2:
        bot.reply_to(message, "Use assim: /amigosecreto <iniciar/participar/sortear> <nome>")
        return

    comando = parts[1]
    handlers = {
        "iniciar": iniciar,
        "participar": participar,
        "sortear": sortear
    }
    handler = handlers.get(comando)
    if handler:
        handler(message, parts)
    else:
        bot.reply_to(message, "Comando inválido. Use /amigosecreto <iniciar/participar/sortear>.")
        
def iniciar(message:tb.types.Message):
    """
    Função que inicia um novo sorteio de amigo secreto. Cria um novo ID de sorteio e salva no arquivo JSON.
    """

    if message.chat.type not in ['group', 'supergroup']:
        bot.reply_to(message, "Você deve enviar isso em um grupo.")
        return
    
    if not is_admin(message.chat.id, message.from_user.id):
        bot.reply_to(message, "Apenas administradores podem iniciar um sorteio.")
        return

    _id_sorteio = str(int(time.time()))
    sorteios = load_json(SORTEIOS)
    sorteios[_id_sorteio] = {
        "participantes": []
    }
    save_json(sorteios, SORTEIOS)
    bot.reply_to(message, f"Sorteio iniciado. Para participar, envie na DM do bot: /amigosecreto participar {_id_sorteio}.")

def participar(message:tb.types.Message, parts):
    """
    Função que adiciona o usuário ao sorteio. Verifica se o sorteio existe e se o usuário já está participando.
    """
    _id_sorteio = parts[2]
    sorteios = load_json(SORTEIOS)
    if _id_sorteio not in sorteios:
        bot.reply_to(message, "Sorteio não encontrado.")
        return
    
    if message.chat.type != 'private':
        bot.reply_to(message, "Você deve enviar isso na DM do bot.")
        return

    user = {
        "user_id": message.from_user.id,
        "username": message.from_user.username
    }

    participando = any(p['user_id'] == user["user_id"] for p in sorteios[_id_sorteio]['participantes'])

    if participando:
        bot.reply_to(message, "Você já está participando desse sorteio.")
    else:
        sorteios[_id_sorteio]["participantes"].append(user)
        save_json(sorteios, SORTEIOS)
        bot.reply_to(message, "Você foi adicionado ao sorteio.")

def sortear(message:tb.types.Message, parts):
    """
    Função que realiza o sorteio. Verifica se o sorteio existe e se há participantes suficientes, então realiza o sorteio e informa os resultados aos participantes.
    """
    _id_sorteio = parts[2]
    sorteios = load_json(SORTEIOS)

    if message.chat.type not in ['group', 'supergroup']:
        bot.reply_to(message, "Você deve enviar isso em um grupo.")
        return

    if not is_admin(message.chat.id, message.from_user.id):
        bot.reply_to(message, "Apenas administradores podem realizar o sorteio.")
        return

    if _id_sorteio not in sorteios:
        bot.reply_to(message, "Sorteio não encontrado.")
        return
    
    participantes = sorteios[_id_sorteio]['participantes']
    if len(participantes) <= 2:
        bot.reply_to(message, "Não há participantes suficientes.")
        return

    p2 = participantes.copy()
    tries = 0
    max_tries = 100 # limita a quantidade de tentativas a 100 (evita possiveis loops infinitos)

    while True:
        random.shuffle(p2)
        if all(p1['user_id'] != p2[i]['user_id'] for i, p1 in enumerate(participantes)):
            break
        tries += 1
        if tries > max_tries:
            bot.reply_to(message, "Não foi possível sortear. Tente novamente.")
            return
        
    for i in range(len(participantes)):
        user_id = participantes[i]['user_id']
        am_username = p2[i]['username']
        bot.send_message(user_id, f"Você tirou @{am_username} como amigo secreto! Não conte para ninguém!")

    bot.reply_to("Sorteio realizado com sucesso.")
    
    del sorteios[_id_sorteio]
    if not sorteios:
        os.remove(SORTEIOS)
    else:
        save_json(sorteios, SORTEIOS)

@bot.message_handler(commands=['spotify'])
def spotify_handler(message:tb.types.Message):
    """
    Handler para o comando /spotify. Faz a lógica de tratamento do comando e chama as respectivas funções.
    """
    global playlists
    parts = message.text.split(maxsplit=2)
    chat_id = str(message.chat.id)
    playlists = load_json(PLAYLIST)

    if len(parts) < 2:
        bot.reply_to(message, "Comandos:\n- /spotify iniciar <nome da playlist>\n- /spotify adicionar <nome da música>\n- /spotify playlist")
        return

    comando = parts[1]
    handlers = {
        "iniciar": spotify_iniciar,
        "adicionar": spotify_adicionar,
        "playlist": spotify_playlist
    }

    handler = handlers.get(comando)
    if handler:
        handler(message, parts, chat_id)
    else:
        bot.reply_to(message, "Comando inválido. Use /spotify para ver os comandos disponíveis.")

def spotify_iniciar(message:tb.types.Message, parts, chat_id):
    """
    Função que inicia uma nova playlist. Verifica se o chat/grupo já tem uma playlist criada e, se não, cria uma nova.
    """
    global playlists
    if len(parts) < 3:
        bot.reply_to(message, "Forneça um nome para a playlist: /spotify iniciar <nome>")
        return
    if chat_id in playlists:
        bot.reply_to(message, "Você já tem uma playlist criada. Use /spotify playlist para ver.")
        return
    if not is_admin(message.chat.id, message.from_user.id):
        bot.reply_to(message, "Apenas administradores podem iniciar um sorteio.")
        return
    nome = parts[2]
    playlist_id, url = create_playlist(nome)
    playlists[chat_id] = {"id": playlist_id, "url": url}
    save_json(playlists, PLAYLIST)
    bot.reply_to(message, f"Playlist criada com sucesso: {url}")

def spotify_adicionar(message:tb.types.Message, parts, chat_id):
    """
    Função que adiciona uma música à playlist. Verifica se o chat/grupo tem uma playlist e, se sim, busca a música por link ou nome, adicionando-a à playlist.
    """
    global playlists
    if chat_id not in playlists:
        bot.reply_to(message, "Crie primeiro uma playlist com /spotify iniciar.")
        return
    if len(parts) < 3:
        bot.reply_to(message, "Use: /spotify adicionar <nome da música>")
        return
    sucesso, nome = add_track(playlists[chat_id]['id'], parts[2])
    if sucesso:
        bot.reply_to(message, f"Música '{nome}' adicionada!")
    else:
        bot.reply_to(message, "Não consegui encontrar essa música.")

def spotify_remover(message:tb.types.Message, parts, chat_id):
    """
    Função que remove uma música da playlist. Verifica se o chat/grupo tem uma playlist e, se sim, busca a música por link ou nome, removendo-a da playlist.
    """
    global playlists
    if chat_id not in playlists:
        bot.reply_to(message, "Crie primeiro uma playlist com /spotify iniciar.")
        return
    if len(parts) < 3:
        bot.reply_to(message, "Use: /spotify remover <nome da música>")
        return
    if not is_admin(message.chat.id, message.from_user.id):
        bot.reply_to(message, "Apenas administradores podem remover músicas.")
        return
    sucesso, nome = remove_track(playlists[chat_id]['id'], parts[2])
    if sucesso:
        bot.reply_to(message, f"Música '{nome}' removida!")
    else:
        bot.reply_to(message, "Não consegui encontrar essa música.")

def spotify_playlist(message:tb.types.Message, parts, chat_id):
    """
    Função que retorna o link da playlist criada. Se não houver playlist, informa ao usuário.
    """
    global playlists
    if chat_id in playlists:
        bot.reply_to(message, f"Link da playlist: {playlists[chat_id]['url']}")
    else:
        bot.reply_to(message, "Nenhuma playlist criada ainda. Use /spotify iniciar.")


# Scheduler para verificar aniversários diariamente
sc.every().day.at("08:00").do(niver_diario)

# Inicia o bot
bot.infinity_polling()

# Inicia o scheduler em um loop separado
while True:
    sc.run_pending()
    time.sleep(1)
