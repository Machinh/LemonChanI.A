import string
import numpy as np
import json

# carregar os dados de treinamento de um arquivo
def carregar_dados_arquivo(nome_arquivo, separador=';'):
    perguntas = []
    respostas = []
    with open(nome_arquivo, 'r') as arquivo:
        for linha in arquivo:
            linha = linha.strip()
            if linha:
                dados = linha.split(separador)
                pergunta = dados[0].strip()
                resposta = dados[1].strip()
                perguntas.append(pergunta)
                respostas.append(resposta)
    return perguntas, respostas

# salvar as perguntas e respostas em formato JSON
def salvar_dados_arquivo(nome_arquivo, perguntas, respostas):
    with open(nome_arquivo, 'w') as arquivo:
        for pergunta, resposta in zip(perguntas, respostas):
            linha = f"{pergunta};{resposta}\n"
            arquivo.write(linha)

#processamento dos dados
def preprocessamento(texto):
    texto = texto.lower()
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

# sair do loop
comando_chave1 = {'sair', 'exit', 'quit'}

# Solicitar nome do usuário
usuario = input('Qual é o seu nome? ')
if usuario == '':
    usuario = 'Usuário'

print(f'Sessão Lemon iniciada usuário {usuario}, O quê temos para hoje?')

# Carregar dados de treinamento de um arquivo
perguntas, respostas = carregar_dados_arquivo('memorias.txt')

# processamento das perguntas
perguntas_preproc = [preprocessamento(pergunta) for pergunta in perguntas]

# Loop infinito para responder a perguntas
while True:
    user_input = input(f'{usuario}: ')

    if user_input.lower() in comando_chave1:
        break

    pergunta_similar_idx = encontrar_pergunta_similar(user_input, perguntas_preproc)
    resposta_bot = respostas[pergunta_similar_idx]
    
    if similaridade_cosseno(preprocessamento(user_input), preprocessamento(resposta_bot)) < 0.4:
        print(f'Lemon: Desculpe usuário {usuario}, eu não sei a resposta para essa pergunta. Você poderia me ensinar?')
        nova_resposta = input('Sua resposta: ')
        perguntas.append(user_input)
        respostas.append(nova_resposta)
        perguntas_preproc.append(preprocessamento(user_input))
        salvar_dados_arquivo('memorias.txt', perguntas, respostas)
        print(f'Lemon: Aprendi algo novo! Obrigado por me ensinar usuário {usuario}.')
    else:
        print('Lemon:', resposta_bot)
