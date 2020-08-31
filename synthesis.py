import analysis as ly
import blocks as bl
from analysis import get_description, flatten
from blocks import Block

FLATTENING = False

def _construct_blocks(texts):
    blocks = list()
    for text_id, text in enumerate(texts):
        # produce expressions
        if FLATTENING:
            expressions = ly.flatten(ly.get_expressions(text), "___var")
        else:
            expressions = ly.get_expressions(text)
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
        print(variable_descriptions)
        
        # find each block io
        for block in bl.get_expression_blocks(expressions):
            block.find_io(variables)
            for variable in block.inputs:
                block.variable_descriptions[variable] = variable_descriptions[variable]
            for variable in block.outputs:
                if variable in variable_descriptions:
                    block.variable_descriptions[variable] = variable_descriptions[variable] + get_description([block.comments], variable)
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
    words1 = list(set(words1))
    words2 = list(set(words2))
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


def _gather_return_to_end(expressions):
    min_spaces = min([ly._count_strarting_spaces(expresion) for expresion in expressions])
    all_expressions = list()
    return_expression = ""
    for expression in expressions:
        if ly._count_strarting_spaces(expression)==min_spaces and expression.lstrip().startswith("return "):
            if len(return_expression) != 0:
                return_expression += ", "
            return_expression += expression.lstrip()[7:]
        else:
            all_expressions.append(expression)
    if len(return_expression)!=0:
        all_expressions.append(" "*min_spaces+"return "+return_expression)
    return all_expressions


def _fix_assignment_order(expressions, expression_groups, variables):
    blocks = dict()
    for expression, group in zip(expressions, expression_groups):
        if group not in blocks:
            blocks[group] = Block()
        blocks[group].expressions.append(expression)
    blocks = list(blocks.values())
    for block in blocks:
        block.find_io(variables)
    # bubblesort
    for i in range(len(blocks)):
        for j in range(i+1, len(blocks)):
            if len(set(blocks[i].inputs)) != len(set(blocks[i].inputs)-set(blocks[j].outputs)):
                blocks[i], blocks[j] = blocks[j], blocks[i]


    all_expressions = list()
    for block in blocks:
        all_expressions.extend(block.expressions)
    return _gather_return_to_end(all_expressions)


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

def synthesize(problem, texts, VARIABLE_STRICTNESS = None, BLOCK_STRICTNESS = 1, CODE_SIZE_PENALTY = 0.01): 
    remaining_problem = problem
    blocks = _construct_blocks(texts)
    outcome = bl.Block()
    outcome.aligned = {}
    outcome.all_variables = list()
    outcome.expression_groups = list()
    
    print("=== DATABASE ===")
    for block in blocks:
        print('Forall:', ', '.join(block.inputs))
        print('Exist:', ', '.join(block.outputs))
        print(block.comments+" "+ly.get_description(block.expressions))
        print("\n".join(block.expressions))
    if VARIABLE_STRICTNESS is None:
        VARIABLE_STRICTNESS = 1
        for block in blocks:
            for var1, desc1 in block.variable_descriptions.items():
                for var2, desc2 in block.variable_descriptions.items():
                    if var1!=var2:
                        VARIABLE_STRICTNESS = max(VARIABLE_STRICTNESS,  _similarity(desc1, desc2)/3)
        print('AUTO DETECTED VARIABLE STRICTNESS:', VARIABLE_STRICTNESS)
    while True:
        print("\n=== NEXT ITERATION ===")
        best_block = max(blocks, key = (lambda block: _similarity(block.comments+" "+ly.get_description(block.expressions), remaining_problem)-len(block.expressions)*CODE_SIZE_PENALTY))
        #if _similarity(best_block.comments+" "+ly.get_description(best_block.expressions), remaining_problem)-len(best_block.expressions)*CODE_SIZE_PENALTY<BLOCK_STRICTNESS:
        if _similarity(best_block.comments+" "+ly.get_description(best_block.expressions), remaining_problem)<BLOCK_STRICTNESS:
            break
        #print(best_block.expressions)
        already_assigned = list()
        for var1 in best_block.variable_descriptions.keys():
            if len(outcome.all_variables)<=len(already_assigned) or len(outcome.variable_descriptions)<=len(already_assigned):
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
        if not FLATTENING:
            best_block.convert_to_level(4)
        outcome.expressions.extend(best_block.expressions)
        outcome.expression_groups.extend([best_block]*len(best_block.expressions))
        for variable in best_block.variable_descriptions.keys():
            if not variable in outcome.aligned:
                outcome.variable_descriptions[variable] = outcome.variable_descriptions.get(variable, "")+" "+best_block.variable_descriptions[variable]
        best_block_vars = best_block.inputs
        best_block_vars.extend(best_block.outputs)
        best_block_vars = ly.unique(best_block_vars)
        outcome.all_variables.extend(best_block_vars)
        outcome.find_io(outcome.all_variables)
        remaining_problem = _difference(remaining_problem, best_block.comments+" "+ly.get_description(best_block.expressions))
        print('Forall:', ', '.join(outcome.inputs))
        print('Exist:', ', '.join(outcome.outputs))
        print(remaining_problem)
        print("\n".join(outcome.expressions))
        for v1, v2 in outcome.aligned.items():
            print(v1,'===',v2)
    
    print("\n=== OUTCOME ===")
    outcome.all_variables = ly.unique(outcome.all_variables)
    outcome.expressions = ly.alter_var_names(outcome.expressions, outcome.aligned)
    outcome.expressions = _fix_assignment_order(outcome.expressions, outcome.expression_groups, outcome.all_variables)
    outcome.expression_groups = None
    if FLATTENING:
        outcome.expressions = ly.deflatten(outcome.expressions)

    outcome.find_io(outcome.all_variables)
    real_var_names_map = {var_name: var_name[var_name.find('_',4)+1:] for var_name in outcome.all_variables}
    outcome.expressions.insert(0, 'def solution('+', '.join(ly.unique([real_var_names_map[input] for input in outcome.inputs]))+"):")
    return "\n".join([expression for expression in ly.alter_var_names(outcome.expressions, real_var_names_map)])