from synthesis import postprocess, analysis as ly, blocks as bl, features

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
        # get variable descriptions and new names
        variable_rename_inverse_map = {"___block"+str(text_id)+"_"+var_name: var_name for var_name in variables}
        variable_raname_map = {var_name: "___block"+str(text_id)+"_"+var_name for var_name in variables}
        variable_descriptions = {variable_raname_map[variable]: features.get_description(expressions, variable) for variable in variables}
        # rename variables
        variables = list(variable_raname_map.values())
        #argument_variables = [variable_raname_map[var_name] for var_name in argument_variables]
        expressions = ly.alter_var_names(expressions, variable_raname_map)

        print(variable_descriptions)
        
        # find blocks and transform them to make suitable for synthesis
        for block in bl.get_expression_blocks(expressions):
            block.find_io(variables)
            block.features = features.get_description([block.comments]+block.expressions)
            for variable in block.inputs:
                block.variable_descriptions[variable] = variable_descriptions[variable]
            for variable in block.outputs:
                if variable in variable_descriptions:
                    block.variable_descriptions[variable] = variable_descriptions[variable]
            blocks.append(block)
    return blocks



def import_from(file):
    lines = list()
    with open(file) as f:
        accum = ""
        for line in f:
            if line.strip().startswith("def ") and len(accum)>0:
                lines.append(accum)
                accum = ""
            accum += line
        lines.append(accum)
    return lines

def synthesize(problem, texts, VARIABLE_STRICTNESS = None, BLOCK_STRICTNESS = 0, CODE_SIZE_PENALTY = 0.01):
    blocks = _construct_blocks(texts)
    remaining_problem = features.get_description([problem])
    outcome = bl.Block()
    outcome.aligned = {}
    outcome.all_variables = list()
    outcome.expression_groups = list()

    print("=== DATABASE ===")
    for block in blocks:
        print('Forall:', ', '.join(block.inputs))
        print('Exist:', ', '.join(block.outputs))
        print('Features:', block.features)
        print("\n".join(block.expressions))

    """
    if VARIABLE_STRICTNESS is None:
        VARIABLE_STRICTNESS = 1
        for block in blocks:
            if _similarity(block.features, remaining_problem)-len(block.expressions)*CODE_SIZE_PENALTY>=BLOCK_STRICTNESS:
                for var1, desc1 in block.variable_descriptions.items():
                    for var2, desc2 in block.variable_descriptions.items():
                        if var1!=var2:
                            VARIABLE_STRICTNESS = max(VARIABLE_STRICTNESS,  _similarity(desc1, desc2)/2)
        print('AUTO DETECTED VARIABLE STRICTNESS:', VARIABLE_STRICTNESS)
    """
    while True:
        best_block = max(blocks, key = (lambda block: features.similarity(block.features, remaining_problem)-len(block.expressions)*CODE_SIZE_PENALTY))
        if features.similarity(best_block.features, remaining_problem)-len(best_block.expressions)*CODE_SIZE_PENALTY<BLOCK_STRICTNESS:
            break
        already_assigned = list()
        for var1 in best_block.variable_descriptions.keys():
            if len(outcome.variable_descriptions)<=len(already_assigned):
                break
            var1_keywords = best_block.variable_descriptions[var1]
            best_var = max([var for var in outcome.variable_descriptions.keys() if var not in already_assigned], key = (lambda var2: features.variable_similarity(var1_keywords, outcome.variable_descriptions[var2])))
            for var in outcome.variable_descriptions.keys():
                if var not in already_assigned:
                    print(var1, var, features.variable_similarity(var1_keywords, outcome.variable_descriptions[best_var]))
                    print('\t', var1_keywords)
                    print('\t', outcome.variable_descriptions[best_var])
            if features.variable_similarity(var1_keywords, outcome.variable_descriptions[best_var])>=VARIABLE_STRICTNESS:
                outcome.aligned[var1] = best_var
                outcome.variable_descriptions[best_var] += " "+best_block.variable_descriptions[var1]
                outcome.variable_descriptions[var1] = outcome.variable_descriptions[best_var]
                already_assigned.append(best_var)
        for var1 in best_block.variable_descriptions:
            if var1 not in already_assigned:
                if var1 not in outcome.variable_descriptions:
                    outcome.variable_descriptions[var1] = best_block.variable_descriptions[var1]

        outcome.expressions.extend(best_block.expressions)
        outcome.expression_groups.extend([best_block]*len(best_block.expressions))
        outcome.all_variables.extend(best_block.inputs)
        outcome.all_variables.extend(best_block.outputs)
        outcome.all_variables = ly.unique(outcome.all_variables)
        outcome.find_io(outcome.all_variables)
        remaining_problem = features.difference(remaining_problem, best_block.features)

        # show currently implemented solution
        print("\n=== NEXT ITERATION ===")
        print('Forall:', ', '.join(outcome.inputs))
        print('Exist:', ', '.join(outcome.outputs))
        print(remaining_problem)
        print("\n".join(outcome.expressions))
        for v1, v2 in outcome.aligned.items():
            print(v1,'===',v2)

    outcome.all_variables = ly.unique(outcome.all_variables)
    outcome.expressions = ly.alter_var_names(outcome.expressions, outcome.aligned)
    outcome.expressions = postprocess.fix_code_order(outcome.expressions, outcome.expression_groups, outcome.all_variables) # don't use expression_groups after this point
    if FLATTENING:
        outcome.expressions = ly.deflatten(outcome.expressions)
    return postprocess.convert_to_code(outcome, outcome.all_variables)