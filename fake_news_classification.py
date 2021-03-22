# -*- coding: utf-8 -*-
"""Fake News Classification.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/19u_m1jZho7xzAYo2uDn8qcn0JR-I0Jpy

# **Creating a Fake News Classification System**
A Comparison of Naive Bayes and Smoothed Unigram-Bigram Language Modeling

Real news example:
```
The OpenAI technology, known as GPT-2, is designed to predict the next word given all the previous words it is shown within some text. The language-based model has been trained on a dataset of 8 million web pages.
```

Fake news example:
```
In a shocking finding, scientist discovered a herd of unicorns living in a remote, previously unexplored valley, in the Andes Mountains. Even more surprising to the researchers was the fact that the unicorns spoke perfect English.
```
"""

from google.colab import drive
drive.mount('/content/drive', force_remount=True)

!pip install -U nltk

"""**PREPROCESSING**"""

import os
import io
from nltk import word_tokenize, sent_tokenize
import nltk
nltk.download('punkt')

root_path = os.path.join(os.getcwd(), "drive", "My Drive/Colab Notebooks") # replace based on your Google drive organization
dataset_path = os.path.join(root_path, "4740_p1_dataset") # same here

with io.open(os.path.join(dataset_path, "trueDataTrain.txt"), encoding='utf8') as real_file:
  real_news = real_file.read()
with io.open(os.path.join(dataset_path, "trueDataValidation.txt"), encoding='utf8') as real_file:
  real_news_validation = real_file.read()
with io.open(os.path.join(dataset_path, "fakeDataTrain.txt"), encoding='utf8') as fake_file:
  fake_news = fake_file.read()
with io.open(os.path.join(dataset_path, "fakeDataValidation.txt"), encoding='utf8') as real_file:
  fake_news_validation = real_file.read()

# Convert all words to lowercase and tokenize (split sentences around spaces and punctuation). 
# Need two datasets: one for training the model, and another for validation. 
tokenized_real_news_training = [list(map(str.lower, word_tokenize(sent))) for sent in sent_tokenize(real_news)]
tokenized_fake_news_training = [list(map(str.lower, word_tokenize(sent))) for sent in sent_tokenize(fake_news)]
tokenized_real_news_validation = [list(map(str.lower, word_tokenize(sent))) for sent in sent_tokenize(real_news_validation)]
tokenized_fake_news_validation = [list(map(str.lower, word_tokenize(sent))) for sent in sent_tokenize(fake_news_validation)]

import numpy as np

print("Sanity check: ")
print(tokenized_real_news_training[0])
print(tokenized_fake_news_training[0])

# Function to insert <s> (sentence markers) at the beginning of sentences.
def insert_sentence_markers(tokenized_news): 
  for sentence in tokenized_news: 
    for i, word in enumerate(sentence): 
      if i is 0: 
        sentence.insert(0, '<s>')
      if word == '.' and i != len(sentence)-1:
        sentence.insert(i+1, '</s>')
        sentence.insert(i+2, '<s>')
    sentence.append('</s>')
  return tokenized_news

tokenized_fake_news_training = insert_sentence_markers(tokenized_fake_news_training)
tokenized_fake_news_validation = insert_sentence_markers(tokenized_fake_news_validation)
tokenized_real_news_training = insert_sentence_markers(tokenized_real_news_training)
tokenized_real_news_validation = insert_sentence_markers(tokenized_real_news_validation)

# Creating lists of words in fake news and real news datasets (fake versus real vocabulary).
fake_words = [word for sentence in tokenized_fake_news_training for word in sentence]
real_words = [word for sentence in tokenized_real_news_training for word in sentence]

# Unigram = singular words in datasets.
unigram_dictionary = set()
for word in fake_words: 
  unigram_dictionary.add(word)
for word in real_words: 
  unigram_dictionary.add(word)

# Bigrams = pairs of words in datasets.
bigram_dictionary = set()
for sentence in tokenized_fake_news_training:
  for i, word in enumerate(sentence):
    if i is not 0:
      bigram_dictionary.add((sentence[i-1], word))

for sentence in tokenized_real_news_training:
  for i, word in enumerate(sentence):
    if i is not 0:
      bigram_dictionary.add((sentence[i-1], word))

# Counting up words in datasets.
fake_word_counts = np.zeros(len(unigram_dictionary))
real_word_counts = np.zeros(len(unigram_dictionary))

# Mapping words to indices (for efficiency in later processing).
word_to_idx = {}
idx_to_word = {}
for i, word in enumerate(unigram_dictionary):
  word_to_idx[word] = i
  idx_to_word[i] = word

for word in fake_words:
  fake_word_counts[word_to_idx[word]] += 1
for word in real_words: 
  real_word_counts[word_to_idx[word]] += 1

# Counting up bigrams in datasets, and mapping to indices. 
fake_bigram_counts = np.zeros(len(bigram_dictionary))
real_bigram_counts = np.zeros(len(bigram_dictionary))

word_to_bigram_idx = {}
idx_to_bigram_word = {}
for i, pair in enumerate(bigram_dictionary):
  word_to_bigram_idx[pair] = i
  idx_to_bigram_word[i] = pair

for sentence in tokenized_fake_news_training:
  for i, word in enumerate(sentence):
    if i is not 0:
      fake_bigram_counts[word_to_bigram_idx[(sentence[i-1], word)]] += 1
for sentence in tokenized_real_news_training:
  for i, word in enumerate(sentence):
    if i is not 0:
      real_bigram_counts[word_to_bigram_idx[(sentence[i-1], word)]] += 1

# Setting up unigram and bigram real and fake dictionaries to be used later.

unigram_fake_dict = {}
unigram_real_dict = {}
bigram_real_dict = {}
bigram_fake_dict = {}


for i, count in enumerate(fake_word_counts): 
  unigram_fake_dict[idx_to_word[i]] = count

for i, count in enumerate(real_word_counts): 
  unigram_real_dict[idx_to_word[i]] = count

for i, count in enumerate(fake_bigram_counts): 
  bigram_fake_dict[idx_to_bigram_word[i]] = count

for i, count in enumerate(real_bigram_counts): 
  bigram_real_dict[idx_to_bigram_word[i]] = count

"""**UNSMOOTHED LANGUAGE MODELS**

Unigram Model (Singular Words)
"""

# Computes the probabilities for a unigram model
def unsmoothed_unigram(lst):
  dictionary = {}
  total_fake = np.sum(fake_word_counts)
  total_real = np.sum(real_word_counts)
  for word in lst: 
    fake_uni = fake_word_counts[word_to_idx[word]] / total_fake
    real_uni = real_word_counts[word_to_idx[word]] / total_real
    dictionary[word] = (fake_uni, real_uni)
  return dictionary

# unsmoothed_unigram is now a dictionary that stores words and maps them to their probabilities in the real and fake news datasets. 
print(unsmoothed_unigram(['donald', 'trump', 'the']))

"""Bigram Model (Pairs of Words)

$p(w_n\mid w_{n-1})=\frac{C(w_{n-1}w_n)}{C(w_{n-1})}$
- Want to find the probability of a word given the previous word based on counts in the current training datasets. 
"""

def unsmoothed_bigram(lst):
  dictionary = {}
  total_fake = np.sum(fake_bigram_counts)
  total_real = np.sum(real_bigram_counts)
  for word in lst: 
    fake_uni = fake_bigram_counts[word_to_bigram_idx[word]] / fake_word_counts[word_to_idx[word[0]]]
    real_uni = real_bigram_counts[word_to_bigram_idx[word]] / real_word_counts[word_to_idx[word[0]]]
    dictionary[word] = (fake_uni, real_uni)
  return dictionary

# unsmoothed_bigram is similar to unigram above but for pairs of words (to map succession).
print(unsmoothed_bigram([('the','donald'), ('donald','trump')]))

"""**SMOOTHED LANGUAGE MODEL**

Step 1: Unknown Word Handling

Handling unknown words by converting tokens that are not in the "top k" most common words to '<UNK>' during pre-processing. k = 4/5 of the total length of word tokens in the trainint set, so k is dependent on the size of the training dataset. Decided on this value for k by playing around with various inputs and corresponding perplexities in an attempt to optimize perplexity. Next, need to look at the sorted word counts that we determined above, remove the bottom 1/5, and replace those with '<UNK>'. 

Also used the validation testing data below to determine perplexities with various k values in order to optimize which one we were choosing.

This step is crucial for the smoothed language model in order to handle any unknown words that the model may come across in testing/future data.
"""

def handle_unk(word_counts):
  k = int(4 * len(word_counts) / 5) #DESIGN DECISION: choose k val for least common words and convert to <UNK>
  items = sorted(word_counts.items(), key=lambda x: x[1], reverse=True)
  topk = dict(list(items)[:k])
  bottomk = dict(list(items)[k:])
  
  len_unk = len(bottomk)
  topk["<UNK>"] = len_unk
  return topk

# Test:
print(handle_unk({"to": 40, "and": 39, "tree": 12, "sun": 3, "flower": 3, "mine": 1, "the": 50, "a": 40}))

unigram_fake_dict = handle_unk(unigram_fake_dict)
unigram_real_dict = handle_unk(unigram_real_dict)

def handle_unk_bigrams(tokenized_training, unigram_dic):
  dic = {}
  for sentence in tokenized_training:
    for i, word in enumerate(sentence):
      if i is not 0:
        if sentence[i-1] in unigram_dic: 
          pair1 = sentence[i-1]
        else: 
          pair1 = '<UNK>'
          
        if word in unigram_dic: 
          pair2 = word
        else: 
          pair2 = '<UNK>'
      
        if (pair1, pair2) in dic: 
          dic[(pair1, pair2)] = dic[(pair1, pair2)] +1
        else: 
          dic[(pair1, pair2)] = 1
  return dic

bigram_real_dict = handle_unk_bigrams(tokenized_real_news_training, unigram_real_dict)
bigram_fake_dict = handle_unk_bigrams(tokenized_fake_news_training, unigram_fake_dict)

"""Step 2: Add-K Smoothing"""

def add_k_unigram(dic, k):
  s = sum(dic.values())
  new_dic = {}
  for word in dic: 
    new_dic[word] = (dic[word] + k) / (s + k*len(dic))
  return new_dic

def add_k_bigram(uni_dic, bi_dic, k):
  new_dic = {}
  for pair1, pair2 in bi_dic: 
    new_dic[(pair1, pair2)] = (bi_dic[(pair1, pair2)] + k) / (uni_dic[pair1] + k*len(uni_dic))
  return new_dic

unigram_fake_probs = add_k_unigram(unigram_fake_dict, .1)
unigram_real_probs = add_k_unigram(unigram_real_dict, .1)
bigram_real_probs = add_k_bigram(unigram_real_dict, bigram_real_dict, .1)
bigram_fake_probs = add_k_bigram(unigram_fake_dict, bigram_fake_dict, .1)

"""Step 3: Computing Perplexity

Smoothing the data changes all of the probabilities slightly in order to shift some of the probability mass from frequent terms to unknowns and 0-values. Need to compute perplexity after smoothing because this change can alter each probability, and therefore change perplexity.

Computing perplexity as follows:
\begin{align*}
PP &= \left(\prod_i^N\frac{1}{P\left(W_i\mid W_{i-1}, ...W_{i-n+1}\right)}\right)^{\frac{1}{N}}\\
&=\exp \frac{1}{N}\sum_{i}^N-\log P\left(W_i\mid W_{i-1}, ...W_{i-n+1}\right)
\end{align*}
where $N$ is the total number of tokens in the test corpus and $P\left(W_i\mid W_{i-1}, ...W_{i-n+1}\right)$
is the n-gram probability of your model. Under the second definition above, perplexity
is a function of the average (per-word) log probability: use this to avoid numerical
computation errors.

In this case, lower perplexity indicates a better model.
"""

def calculate_unigram_perp(uni_dic, validation_set):
  words = [word for sentence in validation_set for word in sentence]
  sum = 0.0
  for word in words: 
    if word in uni_dic:
      sum += - np.log(uni_dic[word])
    else: 
      sum += - np.log(uni_dic['<UNK>'])
  return np.exp(sum / len(words))

uni_perp_fake = calculate_unigram_perp(unigram_fake_probs, tokenized_fake_news_validation)
uni_perp_fr = calculate_unigram_perp(unigram_fake_probs, tokenized_real_news_validation)
uni_perp_real = calculate_unigram_perp(unigram_real_probs, tokenized_real_news_validation)
uni_perp_rf = calculate_unigram_perp(unigram_real_probs, tokenized_fake_news_validation)

print(uni_perp_fake)
print(uni_perp_fr)
print(uni_perp_real)
print(uni_perp_rf)

def calculate_bigram_perp(uni_dic, bi_dic, validation_set):
  words = [word for sentence in validation_set for word in sentence]
  sum = 0
  for i, word in enumerate(words): 
    if i is not 0:
      if (words[i-1], word) in bi_dic:
        sum += - np.log(bi_dic[(words[i-1], word)])
      else: 
        if words[i-1] not in uni_dic and word not in uni_dic: 
          if ('<UNK>', '<UNK>') in bi_dic:
            sum += - np.log(bi_dic[('<UNK>', '<UNK>')])
        elif words[i-1] not in uni_dic: 
          if ('<UNK>', word) in bi_dic:
            sum += - np.log(bi_dic[('<UNK>', word)])
        else: 
          if (words[i-1], '<UNK>') in bi_dic: 
            sum += - np.log(bi_dic[(words[i-1], '<UNK>')])
  return np.exp(sum / len(words))

bi_perp_fake = calculate_bigram_perp(unigram_fake_probs, bigram_fake_probs, tokenized_fake_news_validation)
bi_perp_fr = calculate_bigram_perp(unigram_fake_probs, bigram_fake_probs, tokenized_real_news_validation)
bi_perp_real = calculate_bigram_perp(unigram_real_probs, bigram_real_probs, tokenized_real_news_validation)
bi_perp_rf = calculate_bigram_perp(unigram_real_probs, bigram_real_probs, tokenized_fake_news_validation)

print(bi_perp_fake)
print(bi_perp_fr)
print(bi_perp_real)
print(bi_perp_rf)

"""**ALTERNATIVE METHOD: MULTINOMIAL NAIVE BAYES**

Suppose we have a news article *d* and its label *c* (either 0 or 1).
\begin{align*}
P(c|d)=\frac{P(d|c)P(c)}{P(d)}
\end{align*}
Likelihood: $P(d|c)$. In real/fake corpus, how likely *d* would appear.

Prior: $P(c)$. The probability of real/fake news in general.

Posterior: $P(c|d)$. Given *d*, how likely is it that it is real/fake.

Goal: $\underset{c\in \{0,1\}}{\operatorname{argmax}} P(c|d)$, which is equivalent to $\underset{c\in \{0,1\}}{\operatorname{argmax}} P(d|c)P(c)$.

The equivalence holds because $P(d)$ is the same for any $c$. Thus the denominator can be dropped.

Denote $d=\{x_1, x_2, ..., x_n\}$ where $x_i$'s are words in the news *d* (sometimes called features). Unlike n-gram language modelling, we make the multinomial Naive Bayes independence assumption here, where we assume positions of words do not matter. Formally, 
\begin{align*}
&\underset{c\in \{0,1\}}{\operatorname{argmax}} P(d|c)P(c)\\
=&\underset{c\in \{0,1\}}{\operatorname{argmax}} P(x_1, ..., x_n|c)P(c)\\
=&\underset{c\in \{0,1\}}{\operatorname{argmax}} P(x_1|c)P(x_2|c)...P(x_n|c)
\end{align*}

Now only need to collect the occurences of each word for the classification. This bag-of-words feature is a dictionary that maps word to its occurrences, without considering order. 
"""

from sklearn.naive_bayes import MultinomialNB
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
import numpy as np

labels = []

# Get all sentences from fake and real, and put each in 2d array with real or fake tag.
fake_sentences = nltk.sent_tokenize(fake_news)
real_sentences = nltk.sent_tokenize(real_news)

for sent in fake_sentences:
  labels.append(0)
for sent in real_sentences:
  labels.append(1)

sentences = fake_sentences + real_sentences

# Convert text data to probability value vectors.
vec2 = CountVectorizer()
X = vec2.fit_transform(sentences)

classification = MultinomialNB()
classification.fit(X, labels)

# Test on validation data.
fake_test = nltk.sent_tokenize(fake_news_validation)
real_test = nltk.sent_tokenize(real_news_validation)
test = fake_test + real_test

predicts = classification.predict(vec2.transform(test))