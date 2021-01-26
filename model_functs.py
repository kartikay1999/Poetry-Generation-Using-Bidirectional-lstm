from keras.preprocessing.sequence import pad_sequences
import pickle
from tqdm import tqdm
import re


with open('tokenizers/shakes_tokenizer.pickle', 'rb') as handle:
    tokenizer = pickle.load(handle)


def generate_text(seed_text, next_words, model, max_sequence_len):
    for _ in tqdm(range(next_words)):
        token_list = tokenizer.texts_to_sequences([seed_text])[0]
        token_list = pad_sequences([token_list], maxlen=max_sequence_len-1, padding='pre')
        predicted = model.predict_classes(token_list, verbose=0)
        
        output_word = ""
        for word,index in tokenizer.word_index.items():
            if index == predicted:
                output_word = word
                break
        seed_text += " "+output_word
    return seed_text.title()


def suggestions(seed_text, model, max_sequence_len):
    generated=''
    while True:
        token_list = tokenizer.texts_to_sequences([seed_text])[0]
        token_list = pad_sequences([token_list], maxlen=max_sequence_len-1, padding='pre')
        predicted = model.predict_classes(token_list, verbose=0)
        
        output_word = ""
        for word,index in tokenizer.word_index.items():
            if index == predicted:
                output_word = word
                break
        seed_text += " "+output_word
        generated+=' '+output_word
        if(len(generated.split(' '))>5):
            if re.search('[^a-zA-Z|^\s]',generated)!=None:
                break
        
    return generated





