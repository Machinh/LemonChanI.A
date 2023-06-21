import string
import numpy as np
import json
from unidecode import unidecode
import subprocess

# Dados de treinamento de um arquivo
def carregar_dados_arquivo(nome_arquivo):
    with open(nome_arquivo, 'r') as arquivo:
        dados = json.load(arquivo)
    return dados

# Salvar as perguntas e respostas em formato JSON
def salvar_dados_arquivo(nome_arquivo, dados):
    with open(nome_arquivo, 'w') as arquivo:
        json.dump(dados, arquivo, indent=4, ensure_ascii=False)

# Processamento dos dados
def preprocessamento(texto):
    texto = texto.lower()
    texto = unidecode(texto)  # Remove os acentos
    texto = texto.translate(str.maketrans('', '', string.punctuation))
    return texto

# Calcular a similaridade cosseno entre duas strings
def similaridade_cosseno(str1, str2):
    palavras_str1 = set(str1.split())
    palavras_str2 = set(str2.split())

    intersecao = palavras_str1.intersection(palavras_str2)
    similaridade = len(intersecao) / (np.sqrt(len(palavras_str1)) * np.sqrt(len(palavras_str2)))

    return similaridade

# Encontrar a pergunta mais similar
def encontrar_pergunta_similar(pergunta, perguntas_preproc):
    perguntas_similares = []
    pergunta_preproc = preprocessamento(pergunta)
    for i, pergunta_treino in enumerate(perguntas_preproc):
        similaridade = similaridade_cosseno(pergunta_preproc, pergunta_treino)
        perguntas_similares.append((i, similaridade))
    perguntas_similares.sort(key=lambda x: x[1], reverse=True)
    pergunta_similar_idx = perguntas_similares[0][0]
    return pergunta_similar_idx

# Algoritmo de aprendizado por reforço Q-Learning
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
            q_values[pergunta_idx][pergunta_similar_idx] += taxa_aprendizado * (
                        recompensas[pergunta_similar_idx] + fator_desconto * np.max(
                    q_values[pergunta_similar_idx]) - q_values[pergunta_idx][pergunta_similar_idx])
        else:
            q_values[pergunta_idx][pergunta_similar_idx] += taxa_aprendizado * (
                        recompensas[pergunta_similar_idx] - q_values[pergunta_idx][pergunta_similar_idx])

    return q_values

# Sair do loop
comando_chave1 = {'sair', 'exit', 'quit'}
#comandos
comandos_disponiveis = ['help | Lista de comandos', 'ip | Mostra o IP atual', 'scan [endereço IP | Varredura de rede]', 'exit, sair | Fechar o prompt da IA']
# Nome do usuário
usuario = input('Qual é o seu nome? ')
if usuario == '':
    usuario = 'Usuário'

print(f'Sessão Lemon iniciando usuário {usuario}, O que temos para hoje?')

# Dados de treinamento do arquivo
dados = carregar_dados_arquivo('memorias.json')
perguntas = [item['pergunta'] for item in dados]
respostas = [item['resposta'] for item in dados]
comportamentos_inadequados = ["vadia", "xingamento2", "xingamento3"]

# Processamento das perguntas
perguntas_preproc = [preprocessamento(pergunta) for pergunta in perguntas]

# Definir recompensas
recompensas = np.zeros(len(perguntas))

# Função para obter o endereço IP
def obter_endereco_ip():
    resultado = subprocess.check_output(['curl', 'ifconfig.me'])
    resultado_str = resultado.decode('utf-8').strip()
    return resultado_str

# Algoritmo de Q-Learning
q_values = q_learning(perguntas, respostas, perguntas_preproc, recompensas)

# Loop infinito para responder perguntas
while True:
    user_input = input(f'{usuario}: ')

    if user_input.lower() in comando_chave1:
        break

    if any(inadequado in user_input.lower() for inadequado in comportamentos_inadequados):
        print("Lemon: Desculpe, mas meu criador me incentivou a não responder a comportamentos inadequados.")
        continue

    if user_input.lower() == 'qual é o meu ip?' or user_input.lower() == 'mostre meu ip' or user_input.lower()== 'ip' or user_input.lower() == 'meu ip?':
        ip = obter_endereco_ip()
        print(f'Lemon: Seu endereço IP é: {ip}')

        #nmap scan
    elif user_input.lower().startswith('scan'):
        try:
            ip = user_input.split('scan ')[1]
            resultado = subprocess.check_output(['nmap', ip])
            resultado_str = resultado.decode('utf-8')
            print(f'Lemon: Aqui está o resultado da varredura da rede:\n{resultado_str}')
        except IndexError:
            print("Lemon: Você precisa fornecer um endereço IP antes do 'scan' para o comando Nmap. exemplo: scan [endereço IP]")

    elif user_input.lower() == 'help' or user_input.lower() == 'Help':
        print('Lemon: COMANDOS DISPONÌVEIS DA WATSON V-1:')
        for i, comando in enumerate(comandos_disponiveis, 1):
            print(f'{i}. {comando}')

    else:
        pergunta_similar_idx = encontrar_pergunta_similar(user_input, perguntas_preproc)
        if similaridade_cosseno(preprocessamento(user_input), preprocessamento(perguntas[pergunta_similar_idx])) < 0.2:
            print(f'Lemon: Desculpe usuário {usuario}, eu não sei a resposta para essa pergunta. '
                  f'Você poderia me ensinar detalhadamente?')
            nova_resposta = input('Sua resposta: ')
            if nova_resposta.strip() != '':
                perguntas.append(user_input)
                respostas.append(nova_resposta)
                perguntas_preproc.append(preprocessamento(user_input))
                recompensas = np.append(recompensas, 1.0)  # Recompensa positiva para a nova resposta
                q_values = q_learning(perguntas, respostas, perguntas_preproc, recompensas)
                dados = [{'pergunta': pergunta, 'resposta': resposta} for pergunta, resposta in zip(perguntas, respostas)]
                salvar_dados_arquivo('memorias.json', dados)
                print(f'Lemon: Aprendi algo novo! Obrigado por me ensinar, usuário {usuario}.')
        else:
            print('Lemon:', respostas[pergunta_similar_idx])
            recompensas[pergunta_similar_idx] = 1.0  # Recompensa positiva para resposta correta
