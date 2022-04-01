from nltk.tokenize import WhitespaceTokenizer
import collections
from random import choices, seed, choice
from time import time_ns
import re


tk = WhitespaceTokenizer()
with open('your_file.txt', 'r', encoding='UTF-8') as corpus:
    text = corpus.read()
    word_list = tk.tokenize(text)

trigrams_list = [(word_list[i] + ' ' + word_list[i+1], word_list[i+2]) for i in range(len(word_list) - 2)]
freq_counter = collections.Counter(trigrams_list)
markov_dict = {}

for (head, tail), count in freq_counter.items():
    markov_dict.setdefault(head, {})
    markov_dict[head][tail] = count


for _ in range(10):
    seed(time_ns())

    while True:
        current_words = choice([key for key in markov_dict.keys()])

        if current_words[0].isupper() and not bool(re.match('.*[.!?].*', current_words)):
            break

    print(current_words, end=' ')
    i = 0
    sentence_continues = True

    while sentence_continues:
        i += 1

        while True:
            new_word = choices([tail for tail in markov_dict[current_words].keys()],
                               [count for count in markov_dict[current_words].values()])[0]

            if i > 2 and bool(re.match('.*[.!?]', new_word)):
                sentence_continues = False
            break

        print(new_word, end=' ')
        current_words = current_words.split()[1] + ' ' + new_word

    print()
