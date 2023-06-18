from perguntas_respostas import ler_perguntas_respostas, preprocessar_dados, criar_modelo, chat

# Leitura das perguntas e respostas
perguntas, respostas = ler_perguntas_respostas("perguntas_respostas.txt")

# Pré-processamento dos dados
tokenizer, train_questions_padded, train_answers_padded = preprocessar_dados(perguntas, respostas)

# Criação do modelo
model = criar_modelo(train_questions_padded, train_answers_padded)

# Lista de comandos-chave
comando_chave1 = {'sair', 'exit', 'quit'}

# Exemplo de conversação
while True:
    user_input = input("Usuário: ")
    if user_input.lower() in comando_chave1:
        break
    response = chat(user_input, tokenizer, model)
    print("Lemon:", response)
