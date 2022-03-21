# imports and includes 
import numpy as np 
import pandas as pd
from textblob import TextBlob
import re
import nltk # nltk is used to tokenize the reviews

nltk.download('punkt') # downloaded all puntklist from nltk and stored in a file
from nltk.tokenize import word_tokenize # word_tokenize is used to tokenize the reviews 
from nltk import pos_tag # pos_tagger is used to tag the words in the reviews in the form of (word, pos) 

nltk.download('stopwords') 
#averaged perceptron tagger is a perceptron tagger that uses averaged perceptron algorithm to train a classifier.
nltk.download('averaged_perceptron_tagger') 

nltk.download('wordnet') # wordnet is a lexical database for the English language.
from nltk.corpus import wordnet # corpus is a list of reviews
from nltk.stem import WordNetLemmatizer # lemmatizer is used to lemmatize the words in the reviews

wordnet_lemmatizer = WordNetLemmatizer() 

# pke is library for keyword extraction and summarization 
from pke.unsupervised import YAKE  
from nltk.corpus import stopwords
import spacy # spacy is used to analyze the reviews

nlp = spacy.load("en_core_web_sm") # en_core_web_sm is a pretrained model for english language


def clean(text): # function to clean the reviews
    # Removes all special characters and numericals leaving the alphabets
    text = re.sub('[^A-Za-z]+', ' ', str(text)) # Removes all special characters and numericals leaving the alphabets
    return text


pos_dict = {'J': wordnet.ADJ, 'V': wordnet.VERB, 'N': wordnet.NOUN, 'R': wordnet.ADV} # dictionary for wordnet tags.


# function to get the sentiment of the reviews
def token_stop_pos(text): # function to tokenize the reviews and tag them
    tags = pos_tag(word_tokenize(text)) # 
    newlist = [] # list to store the tagged words
    for word, tag in tags: # iterate over the tagged words
        if word.lower() not in set(stopwords.words('english')): # if the word is not in the stopwords list
            newlist.append(tuple([word, pos_dict.get(tag[0])])) # append the word and its tag to the list
    return newlist # function to get the keywords


def lemmatize(pos_data): # lemmatize the words in the reviews
    lemma_rew = " " # lemmatized reviews
    for word, pos in pos_data: # iterate over the tagged words
        if not pos:
            lemma = word
            lemma_rew = lemma_rew + " " + lemma # append the lemmatized word to the lemmatized reviews
        else:
            lemma = wordnet_lemmatizer.lemmatize(word, pos=pos) # else lemmatize the word where pos is the tag
            lemma_rew = lemma_rew + " " + lemma # append the lemmatized word to the lemmatized reviews
    return lemma_rew


def getSubjectivity(review): # function to get the subjectivity of the reviews
    return TextBlob(review).sentiment.subjectivity # function to get the keywords from the reviews


# function to calculate polarity
def getPolarity(review): # function to get the polarity of the reviews
    return TextBlob(review).sentiment.polarity # textBlob is a sentiment polarity and subjectivity funstion for the reviews


# function to analyze the reviews
def analysis(score): # function to analyze the reviews
    if score < 0: 
        return 'Negative'
    elif score == 0:
        return 'Neutral'
    else:
        return 'Positive'


def keyword_extraction(text): # function to extract the keywords from the reviews
    extractor = YAKE() # yake is a keyword extraction and summarization library for python

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
    return np.array([token.vector for token in nlp(sentence)]).mean(axis=0) # token.vector in nlp(sentence) is the vector of the word in the sentence

def construct_dim_vector(descriptive_words):
    return np.array([construct_sentence_vector(sentence) for sentence in descriptive_words]).mean(axis=0) # construct sentence vector of a descriptive words

def euclidian_distance(X, Y): # function to calculate the euclidian distance
    return np.sqrt(np.sum(np.power(X - Y, 2))) #returning euclidian distance and cosine similarity

def cosine_sim(X, Y):
    return np.dot(X, Y) / (np.linalg.norm(X) * np.linalg.norm(Y)) # np.dot is dot product of two vectors and np.linalg.norm is the norm of a vector

def classes_lexicon():
    df = pd.read_csv(r"D:\NPS-2\NPS_Backend\keyword_mapping.csv", encoding='cp1252') 
    group = df.groupby('Tag Category:') # group the dataframe by the tag category
    df2 = group.apply(lambda x: x['Keywords'].unique()) # apply the function to get the unique keywords
    lexicon = df2.to_dict() # convert the dataframe to dictionary 
    classes = list(lexicon.keys()) # get the list of classes
    return classes, lexicon # return the classes and lexicon
