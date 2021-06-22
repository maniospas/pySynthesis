from synthesis.analysis import  get_terms, get_input_variables, get_output_variables


def get_description(expressions, variable=None, allow_repetitions=False):
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
                    description += "assigned" 
                    for subterm in variable.split("_"):
                        description += "name"+stemmer.stem(subterm)+" "
                    for subterm in term.split("_"):
                        description += "before"+stemmer.stem(subterm)+" "
            elif variable in get_input_variables([expression], [variable]):
                pred = "after"
                for term in get_terms([expression]):
                    if term=="def":
                        description += "afterdef "
                        break
                    elif term == variable:
                        pred = "before"
                        for subterm in term.split("_"):
                            description += "name"+stemmer.stem(subterm)+" "
                    elif variable+"."+term in expression:
                        description += "member"+term+" "
                        #for subterm in term.split("_"):
                        #    description += pred+stemmer.stem(subterm)+" "
                        #print(variable, "MEMBER", term)
                    #else:
                    #    description += term+" "
                    #elif len(subterm)>=min_predicate_length:
                    else:
                        for subterm in term.split("_"):
                            description += pred+stemmer.stem(subterm)+" "
                    #description += term+" "
    if not allow_repetitions:
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

def tokenize(text, allow_stopwords=False):
    # external access point
    return [word for word in _word_tokenize(text.lower()) if len(word) >= 1 and not '_' in word and (allow_stopwords or (len(word)>1 and not word in stopWords))]

def similarity(text1, text2):
    sim = 0
    words1 = [word1 for word1 in _word_tokenize(text1.lower()) if len(word1)>=1 and not '_' in word1 and not word1 in stopWords]
    words2 = [word2 for word2 in _word_tokenize(text2.lower()) if len(word2)>=1 and not '_' in word2 and not word2 in stopWords]
    words1 = set(words1)
    words2 = set(words2)
    for word1iter in words1:
        for word2iter in words2:
            word1 = word1iter
            word2 = word2iter
            if word1==word2:#and "after" not in word1 and "before" not in word1:
                if word1.startswith("member"):
                    sim += 1
                elif word1.startswith("name"):
                    sim += 1
                else:
                    sim += 0.1
            """else:
                #if "assigned"==word1 or "assigned"==word2:
                #    sim -= 0.01
                #    continue
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
                    sim -= PENALIZATION_TERM
        """
    return sim #* 10 / min([len(words1), len(words2)])


def variable_similarity(text1, text2):
    return similarity(text1, text2)


def difference(text1, text2):
    words_original = [word1 for word1 in _word_tokenize(text1) if word1 not in stopWords]
    stemmed_words = {word1: stemmer.stem(word1.lower()) for word1 in words_original if len(word1)>=1 and not '_' in word1 and not word1.lower() in stopWords}
    words2 = [stemmer.stem(word2) for word2 in _word_tokenize(text2.lower()) if len(word2)>=1 and not '_' in word2 and not word2 in stopWords]
    result = ""
    count_removals = dict()
    for word in words2:
        count_removals[word] = count_removals.get(word, 0) + 1
    for word in words_original:
        stemmed_word = stemmed_words.get(word,"") 
        if count_removals.get(stemmed_word, 0) > 0:
            count_removals[stemmed_word] -= 1
        else:
            result += word + " "
    return result.strip()

def combine(text1, text2):
    return text1+" "+text2#+" assigned"

def finished_imports():
    pass