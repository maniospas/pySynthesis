import analysis as ly
import blocks as bl
from analysis import get_description

def _construct_blocks(texts):
    blocks = list()
    for text_id, text in enumerate(texts):
        # produce expressions
        expressions = ly.flatten(ly.get_expressions(text), "___var")
        # find variables
        argument_variables = ly.get_argument_variables(expressions)
        variables = ly.get_output_variables(expressions)
        variables.extend(argument_variables)
        variables = ly.unique(variables)
        # rename variables
        variable_raname_map = {var_name: "___block"+str(text_id)+"_"+var_name for var_name in variables}
        variables = list(variable_raname_map.values())
        argument_variables = [variable_raname_map[var_name] for var_name in argument_variables]
        expressions = ly.alter_var_names(expressions, variable_raname_map)
        
        variable_descriptions = {variable: get_description(expressions, variable) for variable in variables}
        
        # find each block io
        for block in bl.get_expression_blocks(expressions):
            block.find_io(variables)
            for variable in block.inputs:
                block.variable_descriptions[variable] = variable_descriptions[variable]
            for variable in block.outputs:
                if variable in variable_descriptions:
                    block.variable_descriptions[variable] = variable_descriptions[variable]
            blocks.append(block)
    return blocks

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
def _similarity(text1, text2):
    sim = 0
    words1 = [stemmer.stem(word1) for word1 in _word_tokenize(text1.lower()) if len(word1)>=1 and not '_' in word1 and not word1 in stopWords]
    words2 = [stemmer.stem(word2) for word2 in _word_tokenize(text2.lower()) if len(word2)>=1 and not '_' in word2 and not word2 in stopWords]
    for word1 in set(words1):
        for word2 in set(words2):
            if word1==word2:
                sim += 1
    return sim

def _difference(text1, text2):
    words_original = [word1 for word1 in _word_tokenize(text1)]
    word_map = {word1: stemmer.stem(word1.lower()) for word1 in words_original if len(word1)>=1 and not '_' in word1 and not word1.lower() in stopWords}
    words2 = [stemmer.stem(word2) for word2 in _word_tokenize(text2.lower()) if len(word2)>=1 and not '_' in word2 and not word2 in stopWords]
    result = ""
    for word in words_original:
        if not word_map.get(word,"") in words2:
            result += word + " ";
    return result.strip()

def import_from(file):
    texts = list()
    with open(file) as f:
        accum = ""
        for line in f:
            if line.strip().startswith("def ") and len(accum)>0:
                texts.append(accum)
                accum = ""
            accum += line
        texts.append(accum)
    return texts

def synthesize(problem, texts, VARIABLE_STRICTNESS = 2, BLOCK_STRICTNESS = 0, CODE_SIZE_PENALTY = 0.01): 
    remaining_problem = problem
    blocks = _construct_blocks(texts)
    outcome = bl.Block()
    outcome.aligned = {}
    outcome.all_variables = list()
    while True:
        best_block = max(blocks, key = (lambda block: _similarity(block.comments+" "+ly.get_description(block.expressions), remaining_problem)-len(block.expressions)*CODE_SIZE_PENALTY))
        if _similarity(best_block.comments+" "+ly.get_description(best_block.expressions), remaining_problem)-len(best_block.expressions)*CODE_SIZE_PENALTY<BLOCK_STRICTNESS:
            break
        #print(best_block.expressions)
        already_assigned = list()
        for var1 in best_block.variable_descriptions.keys():
            if len(outcome.all_variables)<=len(already_assigned):
                break
            var1_keywords = best_block.variable_descriptions[var1]
            best_var = max([var for var in outcome.variable_descriptions.keys() if var not in already_assigned], key = (lambda var2: _similarity(var1_keywords, outcome.variable_descriptions[var2])))
            """
            for var2 in outcome.variable_descriptions.keys():
                if var2 not in already_assigned:
                    val = _similarity(var1_keywords, outcome.variable_descriptions[var2])
                    print(var1, var2, val, var1_keywords, '|', outcome.variable_descriptions[var2])
            """
            if _similarity(var1_keywords, outcome.variable_descriptions[best_var])>=VARIABLE_STRICTNESS:
                outcome.aligned[var1] = best_var
                outcome.variable_descriptions[best_var] += " "+best_block.variable_descriptions[var1]
                #print('Selected', outcome.aligned)
                already_assigned.append(best_var)
        outcome.expressions.extend(best_block.expressions)
        for variable in best_block.variable_descriptions.keys():
            if not variable in outcome.aligned:
                outcome.variable_descriptions[variable] = outcome.variable_descriptions.get(variable, "")+" "+best_block.variable_descriptions[variable]
        best_block_vars = best_block.inputs
        best_block_vars.extend(best_block.outputs)
        best_block_vars = ly.unique(best_block_vars)
        outcome.all_variables.extend(best_block_vars)
        outcome.find_io(outcome.all_variables)
        remaining_problem = _difference(remaining_problem, best_block.comments+" "+ly.get_description(best_block.expressions))
        print(remaining_problem)
    outcome.all_variables = ly.unique(outcome.all_variables)
    outcome.expressions = ly.alter_var_names(outcome.expressions, outcome.aligned)
    outcome.expressions = ly.deflatten(outcome.expressions)

    outcome.find_io(outcome.all_variables)
    real_var_names_map = {var_name: var_name[var_name.find('_',4)+1:] for var_name in outcome.all_variables}
    outcome.expressions.insert(0, 'def solution('+', '.join(ly.unique([real_var_names_map[input] for input in outcome.inputs]))+"):")
    return "\n".join([expression for expression in ly.alter_var_names(outcome.expressions, real_var_names_map)])