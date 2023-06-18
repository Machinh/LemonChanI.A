import string
import numpy as np
import time

# Dados de treinamento
perguntas = ['Qual é o seu nome?', 'Qual é a cor do céu?', 'Quanto é 2 + 2?']
respostas = ['Meu nome é Chatbot', 'A cor do céu é azul', '2 + 2 é igual a 4']

# Pré-processamento dos dados
def preprocessamento(texto):
    texto = texto.lower()
    texto = texto.translate(str.maketrans('', '', string.punctuation))
    return texto

perguntas_preproc = [preprocessamento(pergunta) for pergunta in perguntas]

# Função para calcular a similaridade cosseno entre duas strings
def similaridade_cosseno(str1, str2):
    palavras_str1 = set(str1.split())
    palavras_str2 = set(str2.split())
    
    intersecao = palavras_str1.intersection(palavras_str2)
    similaridade = len(intersecao) / (np.sqrt(len(palavras_str1)) * np.sqrt(len(palavras_str2)))
    
    return similaridade

# Função para encontrar a pergunta mais similar
def encontrar_pergunta_similar(pergunta):
    perguntas_similares = []
    pergunta_preproc = preprocessamento(pergunta)
    for i, pergunta_treino in enumerate(perguntas_preproc):
        similaridade = similaridade_cosseno(pergunta_preproc, pergunta_treino)
        perguntas_similares.append((i, similaridade))
    perguntas_similares.sort(key=lambda x: x[1], reverse=True)
    pergunta_similar_idx = perguntas_similares[0][0]
    return pergunta_similar_idx

# Comandos para sair do loop
comando_chave1 = {'sair', 'exit', 'quit'}

# Solicitar nome do usuário
usuario = input('Qual é o seu nome? ')
if usuario == '':
    usuario = 'Usuário'

print(f'Olá {usuario}! O que temos para hoje?')

# Loop infinito para responder a perguntas
while True:
    user_input = input(f'{usuario}: ')
    
    if user_input.lower() in comando_chave1:
        break
    
    pergunta_similar_idx = encontrar_pergunta_similar(user_input)
    resposta_bot = respostas[pergunta_similar_idx]
    
    print('Lemon: ', resposta_bot)
    
    time.sleep(1)
