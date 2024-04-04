import yake
import string
import nltk
import pandas as pd
from collections import Counter

from utils.keyword_utils import tuple_list_to_strings, count_frequency

punctuations = string.punctuation.replace('.', '').replace(',', '')
translator = str.maketrans('', '', punctuations)

class Keyword_Analysis:
    def __init__(self, data, num_keywords=15, # stopwords=nltk.corpus.stopwords.words('english'), not to use stopwords
                 catch_word=["safe", "safer","safety", "safely", "secure", "security", "securely", "securer", "secured","secures"], 
                 colname='descriptionHtml', identifier='guid'):
        self.keywords = {} # a dictionary of patent:keywords
        self.data = data # input dataset
        self.catch_word = catch_word # safe words to catch; can be replaced by other words
        self.colname = colname # column name to use
        self.identifier = identifier # identifier to use
        # functions to use
        self.num_keywords = num_keywords # number of keywords to catch
        self.yake = yake.KeywordExtractor(top = self.num_keywords, lan = 'en', stopwords=None, n = 3) # keywords extractor; allow up to 3-grams
        self.punctuations = string.punctuation.replace('.', '').replace(',', '') # punctuation to remove
        self.translator = str.maketrans('', '', self.punctuations) # translator to use
        
    def get_word_count(self, catch_word = True, keyword = False): 
        ''' 
        Get the frequency of catch words or keywords in the dataset
        Allow up to 3-grams
        input: catch_word (bool): whether to count the frequency of catch words. Default is True
               keyword (bool): whether to count the frequency of keywords. Default is False
        output: data. The dataframe with the separate columns of catch word frequencies, and a keyword column filled with a dictionary
                      The dictionary in the keyword column is the frequency of keywords
        '''
        length = len(self.data)
        data = self.data.copy()
        if catch_word:
            for word in self.catch_word:
                data[word] = 0
        if keyword:
            data['keyword'] = [{}] * length
        # go over the loop
        for i in range(length):
            # get the abstract and name of a patent
            try: 
                abstract = self.data[self.colname].iloc[i].translate(self.translator)
                identifier = self.data[self.identifier].iloc[i]
                # tokenize the text into 1-3 grams
                all_words = nltk.word_tokenize(abstract)
                bigrams = list(nltk.bigrams(all_words))
                trigrams = list(nltk.trigrams(all_words))
                ngrams=bigrams+trigrams 
                ngrams=tuple_list_to_strings(ngrams)+all_words 
                # count catch word frequency
                if catch_word: 
                    for word in self.catch_word:
                        word_count = ngrams.count(word)
                        data.at[i, word] = word_count
                # count keyword frequency 
                if keyword: 
                    try: 
                        keywords_list = self.keywords[identifier] # get the keywords list from the dictionary
                        keyword_count = count_frequency(keywords_list, ngrams) # count the frequency of keywords
                        data.at[i, 'keyword'] = keyword_count
                    except KeyError:
                        print("No keywords found for patent", identifier)
            except AttributeError:
                data.at[i, 'keyword'] = pd.NA
        return data
    
    def get_keywords(self):
        ''' 
        Get the keywords from the dataset
        output: data, the dataframe with the keywords column
        '''
        data = self.data.copy()
        length = len(self.data)
        data['keyword'] = [{}] * length
        for i in range(length):
            try:
                abstract = self.data[self.colname].iloc[i].translate(self.translator)
                identifier = self.data[self.identifier].iloc[i]
                keywords = self.yake.extract_keywords(abstract)
                keywords = [keyword[0] for keyword in keywords]
                self.keywords[identifier] = keywords
                data.at[i, 'keyword'] = keywords
            except AttributeError:
                data.at[i, 'keyword'] = pd.NA
        return data
    
    def get_keyword_frequency(self):
        ''' 
        Get the frequency of keywords in the dataset
        output: a dictionary of keyword frequencies
        '''
        key_freq = {}
        length = len(self.data)
        for i in range(length):
            identifier = self.data[self.identifier].iloc[i]
            keywords = self.keywords[identifier]
            key_freq[identifier] = count_frequency(keywords, keywords)
        return key_freq

    def keyword_freq(self, data):
        '''
        Get the frequency of keywords for all patents in the dataset
        
        input: data. The dataframe with the keywords column
        output: df_word_counts. The dataframe with the word and frequency columns
        '''
        all_words = [word for sublist in data['keyword'] if sublist is not pd.NA for word in sublist]
        # Use Counter to count frequencies
        word_counts = Counter(all_words)
        # Convert the Counter object to a DataFrame
        df_word_counts = pd.DataFrame(word_counts.items(), columns=['Word', 'Frequency']).sort_values(by='Frequency', ascending=False).reset_index(drop=True)
        return df_word_counts

if __name__ == "__main__":
    # SA = Safeword_Analysis()
    dataset = pd.read_csv('/Users/liusimin/Desktop/Gun Safety/papers/all_patents_abstract.csv')
    # print(dataset.head())
    # subset = data.iloc[10000:10010].reset_index(drop=True)
    KA = Keyword_Analysis(data=dataset, num_keywords = 10)
    keyword = KA.get_keywords()
    print(keyword.head())
    # catch = KA.get_word_count(True, True)
    # print(catch.head())
    
    
