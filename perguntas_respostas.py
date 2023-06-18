import csv
import numpy as np
import tensorflow as tf

# Função para ler perguntas e respostas de um arquivo CSV
def ler_perguntas_respostas(nome_arquivo):
    perguntas = []
    respostas = []

    with open(nome_arquivo, 'r', newline='') as file:
        reader = csv.reader(file)
        next(reader)  # Pula a linha de cabeçalho do arquivo CSV
        for row in reader:
            perguntas.append(row[0])
            respostas.append(row[1])

    return perguntas, respostas

# Função para pré-processar os dados de treinamento
def preprocessar_dados(perguntas, respostas):
    tokenizer = tf.keras.preprocessing.text.Tokenizer()
    tokenizer.fit_on_texts(perguntas + respostas)

    train_questions_encoded = tokenizer.texts_to_sequences(perguntas)
    train_answers_encoded = tokenizer.texts_to_sequences(respostas)

    train_questions_padded = tf.keras.preprocessing.sequence.pad_sequences(train_questions_encoded)
    train_answers_padded = tf.keras.preprocessing.sequence.pad_sequences(train_answers_encoded)

    return tokenizer, train_questions_padded, train_answers_padded

# Função para criar o modelo
def criar_modelo(train_questions_padded, train_answers_padded):
    input_dim = np.max([np.max(train_questions_padded), np.max(train_answers_padded)]) + 1
    hidden_size = 128

    encoder_inputs = tf.keras.layers.Input(shape=(None,))
    encoder_embedding = tf.keras.layers.Embedding(input_dim, hidden_size)(encoder_inputs)
    encoder_outputs, state_h, state_c = tf.keras.layers.LSTM(hidden_size, return_state=True)(encoder_embedding)
    encoder_states = [state_h, state_c]

    decoder_inputs = tf.keras.layers.Input(shape=(None,))
    decoder_embedding = tf.keras.layers.Embedding(input_dim, hidden_size)(decoder_inputs)
    decoder_lstm = tf.keras.layers.LSTM(hidden_size, return_sequences=True, return_state=True)
    decoder_outputs, _, _ = decoder_lstm(decoder_embedding, initial_state=encoder_states)
    decoder_dense = tf.keras.layers.Dense(input_dim, activation='softmax')
    decoder_outputs = decoder_dense(decoder_outputs)

    model = tf.keras.models.Model([encoder_inputs, decoder_inputs], decoder_outputs)
    model.compile(optimizer='rmsprop', loss='categorical_crossentropy')

    return model

# Função para responder perguntas do usuário
def chat(input_text, tokenizer, model):
    input_seq = tokenizer.texts_to_sequences([input_text])
    input_padded = tf.keras.preprocessing.sequence.pad_sequences(input_seq, maxlen=model.input_shape[1])
    input_padded = np.tile(input_padded, (model.input_shape[0], 1))  # Replica a entrada para ter o mesmo número de amostras
    predicted = model.predict([input_padded, np.zeros((input_padded.shape[0], model.input_shape[1]))])
    predicted_word_indices = np.argmax(predicted, axis=2)
    response = ' '.join([tokenizer.index_word.get(idx, '') for idx in predicted_word_indices[0]])
    return response

# Lista de comandos-chave
comando_chave1 = {'sair', 'exit', 'quit'}
