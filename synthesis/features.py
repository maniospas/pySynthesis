from synthesis.analysis import  get_terms, get_input_variables, get_output_variables


def get_description(expressions, variable=None):
    description = ""
    min_predicate_length = 2
    for expression in expressions:
        if variable is None:
            for term in get_terms([expression]):
                if len(term)>=min_predicate_length and not term=="def":
                    description += term+" "
        else:
            if variable in get_input_variables([expression], [variable]) or variable in get_output_variables([expression]):
                pred = "before"
                for term in get_terms([expression], ignore_variables=False):
                    if term=="def":
                        continue
                    if term == variable:
                        pred = "before"
                        #description += variable.replace("_", " ")+" "
                        continue
                    if variable+"."+term in expression:
                        description += "member"+term+" "
                        #print(variable, "MEMBER", term)
                    else:
                        description += term+" "
                    #elif len(subterm)>=min_predicate_length:
                    #else:
                    #    description += pred+term+" "
                    #description += term+" "
    description = " ".join(list(set(description.split(" "))))
    if len(description)==0 and variable is None:
        raise Exception("Make sure that expressions have at least one predicate (this problem often appears if an expression string is passed on instead of a list of expression strings)")
    return description


import nltk.tokenize
def _word_tokenize(text):
    words = nltk.tokenize.word_tokenize(text)
    ret = list()
    for word in words:
        ret.extend(word.split("_"))
    return ret
from nltk.corpus import stopwords
from nltk.stem.porter import PorterStemmer
stemmer = PorterStemmer()
stopWords = set(stopwords.words('english'))
stopWords.add("return")

def similarity(text1, text2):
    sim = 0
    words1 = [stemmer.stem(word1) for word1 in _word_tokenize(text1.lower()) if len(word1)>=1 and not '_' in word1 and not word1 in stopWords]
    words2 = [stemmer.stem(word2) for word2 in _word_tokenize(text2.lower()) if len(word2)>=1 and not '_' in word2 and not word2 in stopWords]
    #words1 = ly.unique(words1)
    #words2 = ly.unique(words2)
    for word1 in set(words1):
        for word2 in set(words2):
            if word1==word2:
                sim += 1
    return sim #* 10 / min([len(words1), len(words2)])


def variable_similarity(text1, text2):
    return similarity(text1, text2)


def difference(text1, text2):
    words_original = [word1 for word1 in _word_tokenize(text1)]
    word_map = {word1: stemmer.stem(word1.lower()) for word1 in words_original if len(word1)>=1 and not '_' in word1 and not word1.lower() in stopWords}
    words2 = [stemmer.stem(word2) for word2 in _word_tokenize(text2.lower()) if len(word2)>=1 and not '_' in word2 and not word2 in stopWords]
    result = ""
    for word in words_original:
        if not word_map.get(word,"") in words2:
            result += word + " "
        else:
            words2.remove(word_map.get(word,"")) #remove one entry only
    return result.strip()

def combine(text1, text2):
    return text1+" "+text2

def finished_imports():
    pass