import numpy as np
import pandas as pd
from textblob import TextBlob
import re
import nltk

nltk.download('punkt')
from nltk.tokenize import word_tokenize
from nltk import pos_tag

nltk.download('stopwords')
nltk.download('averaged_perceptron_tagger')

from nltk.corpus import stopwords

nltk.download('wordnet')
from nltk.corpus import wordnet
from nltk.stem import WordNetLemmatizer

wordnet_lemmatizer = WordNetLemmatizer()
# from rake_nltk import Rake

# rake = Rake()
from pke.unsupervised import YAKE
from nltk.corpus import stopwords
import spacy

nlp = spacy.load("en_core_web_sm")


# POS tagger dictionary

# Define a function to clean the text
def clean(text):
    # Removes all special characters and numericals leaving the alphabets
    text = re.sub('[^A-Za-z]+', ' ', str(text))
    return text


pos_dict = {'J': wordnet.ADJ, 'V': wordnet.VERB, 'N': wordnet.NOUN, 'R': wordnet.ADV}


def token_stop_pos(text):
    tags = pos_tag(word_tokenize(text))
    newlist = []
    for word, tag in tags:
        if word.lower() not in set(stopwords.words('english')):
            newlist.append(tuple([word, pos_dict.get(tag[0])]))
    return newlist


def lemmatize(pos_data):
    lemma_rew = " "
    for word, pos in pos_data:
        if not pos:
            lemma = word
            lemma_rew = lemma_rew + " " + lemma
        else:
            lemma = wordnet_lemmatizer.lemmatize(word, pos=pos)
            lemma_rew = lemma_rew + " " + lemma
    return lemma_rew


def getSubjectivity(review):
    return TextBlob(review).sentiment.subjectivity


# function to calculate polarity
def getPolarity(review):
    return TextBlob(review).sentiment.polarity


# function to analyze the reviews
def analysis(score):
    if score < 0:
        return 'Negative'
    elif score == 0:
        return 'Neutral'
    else:
        return 'Positive'


def keyword_extraction(text):
    extractor = YAKE()

    # 2. Load document
    extractor.load_document(input=text,
                            language='en',
                            normalization=None)

    # 3. Generate candidate 1-gram and 2-gram keywords
    stoplist = stopwords.words('english')
    extractor.candidate_selection(n=2, stoplist=stoplist)

    # 4. Calculate scores for the candidate keywords
    extractor.candidate_weighting(window=2,
                                  stoplist=stoplist,
                                  use_stems=False)

    # 5. Select 5 highest ranked keywords
    # Remove redundant keywords with similarity above 80%
    key_phrases = extractor.get_n_best(n=5, threshold=0.8)
    key = []
    for k in key_phrases:
        key.append(k[0])

    return key


def construct_sentence_vector(sentence):
    return np.array([token.vector for token in nlp(sentence)]).mean(axis=0)


def construct_dim_vector(descriptive_words):
    return np.array([construct_sentence_vector(sentence) for sentence in descriptive_words]).mean(axis=0)


def euclidian_distance(X, Y):
    return np.sqrt(np.sum(np.power(X - Y, 2)))


def cosine_sim(X, Y):
    return np.dot(X, Y) / (np.linalg.norm(X) * np.linalg.norm(Y))


def classes_lexicon():
    df = pd.read_csv(r"D:\NPS-2\NPS_Backend\keyword_mapping.csv", encoding='cp1252')
    group = df.groupby('Tag Category:')
    df2 = group.apply(lambda x: x['Keywords'].unique())
    lexicon = df2.to_dict()
    classes = list(lexicon.keys())
    return classes, lexicon
