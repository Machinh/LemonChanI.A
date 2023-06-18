import numpy as np
import tensorflow as tf

# Exemplo básico de dados de treinamento
train_questions = ["Qual é o seu nome?", "Qual é a sua cor favorita?"]
train_answers = ["Meu nome é Chatbot", "Minha cor favorita é azul"]

# Pré-processamento dos dados de treinamento
tokenizer = tf.keras.preprocessing.text.Tokenizer()
tokenizer.fit_on_texts(train_questions + train_answers)
train_questions_encoded = tokenizer.texts_to_sequences(train_questions)
train_answers_encoded = tokenizer.texts_to_sequences(train_answers)

# Padding das sequências para o mesmo comprimento
train_questions_padded = tf.keras.preprocessing.sequence.pad_sequences(train_questions_encoded)
train_answers_padded = tf.keras.preprocessing.sequence.pad_sequences(train_answers_encoded)

# Definição da arquitetura do modelo
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

# Definição do modelo
model = tf.keras.models.Model([encoder_inputs, decoder_inputs], decoder_outputs)
model.compile(optimizer='rmsprop', loss='categorical_crossentropy')

# Treinamento do modelo
model.fit([train_questions_padded, train_answers_padded[:, :-1]], 
          tf.keras.utils.to_categorical(train_answers_padded[:, 1:], num_classes=input_dim), 
          batch_size=64, 
          epochs=10)

# Uso do modelo para prever respostas
def chat(input_text):
    input_seq = tokenizer.texts_to_sequences([input_text])
    input_padded = tf.keras.preprocessing.sequence.pad_sequences(input_seq, maxlen=train_questions_padded.shape[1])
    input_padded = np.tile(input_padded, (train_answers_padded.shape[0], 1))  # Replica a entrada para ter o mesmo número de amostras
    predicted = model.predict([input_padded, train_answers_padded[:, :-1]])
    predicted_word_indices = np.argmax(predicted, axis=2)
    response = ' '.join([tokenizer.index_word[idx] for idx in predicted_word_indices[0]])
    return response


#----------comandos-chave---------
comando_chave1= {'sair', 'exit', 'quit'}
#----------comandos-chave---------


# Exemplo de conversação
while True:
    user_input = input("Usuário: ")
    if user_input.lower() in comando_chave1:
        break
    response = chat(user_input)
    print("Lemon:", response)
