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
            if variable in get_output_variables([expression]):
                for term in get_terms([expression]):
                    for subterm in term.split("_"):
                        description += "before"+stemmer.stem(subterm)+" "
            elif variable in get_input_variables([expression], [variable]):
                pred = "after"
                for term in get_terms([expression]):
                    if term=="def":
                        break
                    if term == variable:
                        pred = "before"
                        for subterm in term.split("_"):
                            description += "name"+stemmer.stem(subterm)+" "
                        continue
                    if variable+"."+term in expression:
                        description += "member"+term+" "
                        #print(variable, "MEMBER", term)
                    #else:
                    #    description += term+" "
                    #elif len(subterm)>=min_predicate_length:
                    else:
                        for subterm in term.split("_"):
                            description += pred+stemmer.stem(subterm)+" "
                    #description += term+" "
    description = " ".join(list(set(description.split(" "))))
    if len(description)==0 and variable is None and len(expressions)!=0:
        raise Exception("Make sure that expressions have at least one predicate (this problem often appears if an expression string is passed on instead of a list of expression strings)")
    return description


import nltk.tokenize
def _word_tokenize(text):
    words = nltk.tokenize.word_tokenize(text)
    #ret = list()
    #for word in words:
    #    ret.extend(word.split("_"))
    return words
from nltk.corpus import stopwords
from nltk.stem.porter import PorterStemmer
stemmer = PorterStemmer()
stopWords = set(stopwords.words('english'))
stopWords.add("return")

def similarity(text1, text2):
    sim = 0
    words1 = [word1 for word1 in _word_tokenize(text1.lower()) if len(word1)>=1 and not '_' in word1 and not word1 in stopWords]
    words2 = [word2 for word2 in _word_tokenize(text2.lower()) if len(word2)>=1 and not '_' in word2 and not word2 in stopWords]
    #words1 = ly.unique(words1)
    #words2 = ly.unique(words2)
    for word1 in words1:
        for word2 in words2:
            if word1==word2:
                sim += 1 if word1.startswith("member") or word1.startswith("name") else 0.4
            else:
                if word1.startswith("before"):
                    word1 = word1[len("before"):]
                elif word1.startswith("after"):
                    word1 = word1[len("after"):]
                #elif word1.startswith("name"):
                #    word1 = word1[len("name"):]
                if word2.startswith("before"):
                    word2 = word2[len("before"):]
                elif word2.startswith("after"):
                    word2 = word2[len("after"):]
                #elif word2.startswith("name"):
                #    word2 = word2[len("name"):]
                if word1==word2:
                    sim -= 0.01
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