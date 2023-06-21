import string
import numpy as np
import json
from unidecode import unidecode
import subprocess

# dados de treinamento de um arquivo
def carregar_dados_arquivo(nome_arquivo):
    with open(nome_arquivo, 'r') as arquivo:
        dados = json.load(arquivo)
    return dados

# salvar as perguntas e respostas em formato JSON
def salvar_dados_arquivo(nome_arquivo, dados):
    with open(nome_arquivo, 'w') as arquivo:
        json.dump(dados, arquivo, indent=4, ensure_ascii=False)

# processamento dos dados
def preprocessamento(texto):
    texto = texto.lower()
    texto = unidecode(texto)  # remove os acentos
    texto = texto.translate(str.maketrans('', '', string.punctuation))
    return texto

# calcular a similaridade cosseno entre duas strings
def similaridade_cosseno(str1, str2):
    palavras_str1 = set(str1.split())
    palavras_str2 = set(str2.split())

    intersecao = palavras_str1.intersection(palavras_str2)
    similaridade = len(intersecao) / (np.sqrt(len(palavras_str1)) * np.sqrt(len(palavras_str2)))

    return similaridade

# encontrar a pergunta mais similar
def encontrar_pergunta_similar(pergunta, perguntas_preproc):
    perguntas_similares = []
    pergunta_preproc = preprocessamento(pergunta)
    for i, pergunta_treino in enumerate(perguntas_preproc):
        similaridade = similaridade_cosseno(pergunta_preproc, pergunta_treino)
        perguntas_similares.append((i, similaridade))
    perguntas_similares.sort(key=lambda x: x[1], reverse=True)
    pergunta_similar_idx = perguntas_similares[0][0]
    return pergunta_similar_idx

# algoritmo de aprendizado por reforço Q-Learning
def q_learning(perguntas, respostas, perguntas_preproc, recompensas, taxa_aprendizado=0.1, fator_desconto=0.9, num_iteracoes=1000):
    num_perguntas = len(perguntas)
    q_values = np.zeros((num_perguntas, num_perguntas))

    for _ in range(num_iteracoes):
        pergunta_idx = np.random.randint(num_perguntas)
        pergunta = perguntas[pergunta_idx]

        pergunta_preproc = preprocessamento(pergunta)
        pergunta_similar_idx = encontrar_pergunta_similar(pergunta, perguntas_preproc)
        resposta_bot = respostas[pergunta_similar_idx]

        if similaridade_cosseno(pergunta_preproc, preprocessamento(resposta_bot)) < 0.4:
            q_values[pergunta_idx][pergunta_similar_idx] += taxa_aprendizado * (recompensas[pergunta_similar_idx] + fator_desconto * np.max(q_values[pergunta_similar_idx]) - q_values[pergunta_idx][pergunta_similar_idx])
        else:
            q_values[pergunta_idx][pergunta_similar_idx] += taxa_aprendizado * (recompensas[pergunta_similar_idx] - q_values[pergunta_idx][pergunta_similar_idx])

    return q_values

# sair do loop
comando_chave1 = {'sair', 'exit', 'quit'}

# nome do usuário
usuario = input('Qual é o seu nome? ')
if usuario == '':
    usuario = 'Usuário'

print(f'Sessão Lemon iniciando usuário {usuario}, O quê temos para hoje?')

# dados de treinamento do arquivo
dados = carregar_dados_arquivo('memorias.json')
perguntas = [item['pergunta'] for item in dados]
respostas = [item['resposta'] for item in dados]

# processamento das perguntas
perguntas_preproc = [preprocessamento(pergunta) for pergunta in perguntas]

# Definir recompensas
recompensas = np.zeros(len(perguntas))

# algoritmo de Q-Learning
q_values = q_learning(perguntas, respostas, perguntas_preproc, recompensas)

# Loop infinito para responder a perguntas
while True:
    user_input = input(f'{usuario}: ')

    if user_input.lower() in comando_chave1:
        break

    if user_input.lower() == 'qual é o meu ip?':
        # comando para obter o endereço IP
        resultado = subprocess.check_output(['curl', 'ifconfig.me'])

        # resultado em uma string legível
        resultado_str = resultado.decode('utf-8').strip()

        # resultado para o usuário
        print(f'Lemon: Seu endereço IP é: {resultado_str}')

    elif user_input.lower().startswith('use o nmap'):
        # endereço IP da pergunta do usuário
        ip = user_input.split('use o nmap para escanear ')[1]

        # comando Nmap usando o endereço IP
        resultado = subprocess.check_output(['nmap', ip])

        # resultado em uma string legível
        resultado_str = resultado.decode('utf-8')

        # resultado para o usuário
        print(f'Lemon: Aqui está o resultado da varredura da rede:\n{resultado_str}')
    else:
        pergunta_similar_idx = encontrar_pergunta_similar(user_input, perguntas_preproc)
        resposta_bot = respostas[pergunta_similar_idx]

        if similaridade_cosseno(preprocessamento(user_input), preprocessamento(resposta_bot)) < 0.2:
            print(f'Lemon: Desculpe usuário {usuario}, eu não sei a resposta para essa pergunta. Você poderia me ensinar detalhadamente?')
            nova_resposta = input('Sua resposta: ')
            perguntas.append(user_input)
            respostas.append(nova_resposta)
            perguntas_preproc.append(preprocessamento(user_input))
            recompensas = np.append(recompensas, 1.0)  # recompensa positiva para a nova resposta
            q_values = q_learning(perguntas, respostas, perguntas_preproc, recompensas)
            dados = [{'pergunta': pergunta, 'resposta': resposta} for pergunta, resposta in zip(perguntas, respostas)]
            salvar_dados_arquivo('memorias.json', dados)
            print(f'Lemon: Aprendi algo novo! Obrigado por me ensinar usuário {usuario}.')
        else:
            print('Lemon:', resposta_bot)
            recompensas[pergunta_similar_idx] = 1.0  # recompensa positiva para resposta correta
