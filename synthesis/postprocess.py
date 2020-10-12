from synthesis.blocks import Block
from synthesis import analysis as ly


def _gather_return_to_end(expressions, single_output=False):
    if len(expressions)==0:
        raise Exception("List of expressions is empty")
    min_spaces = min([ly._count_strarting_spaces(expresion) for expresion in expressions])
    all_expressions = list()
    return_expression = ""
    for expression in expressions:
        if ly._count_strarting_spaces(expression)==min_spaces and expression.lstrip().startswith("return "):
            if single_output:
                return_expression = ""
            elif len(return_expression) != 0:
                return_expression += ", "
            return_expression += expression.lstrip()[7:]# change this between += and = to
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
    return all_expressions


def fix_code_order(expressions, expression_groups, variables, single_output=False):
    return _gather_return_to_end(_fix_assignment_order(expressions, expression_groups, variables), single_output)


def convert_to_code(outcome, all_variables):
    outcome.find_io(all_variables)
    real_var_names_map = {var_name: var_name[var_name.find('_',4)+1:] for var_name in outcome.all_variables}
    prevs = set()
    for var_name in list(real_var_names_map.keys()):
        temp_name = real_var_names_map[var_name]
        i = 1
        while temp_name in prevs:
            i += 1
            temp_name = real_var_names_map[var_name]+str(i)
        prevs.add(temp_name)
        real_var_names_map[var_name] = temp_name
        #print(var_name, temp_name)
    #if len(real_var_names_map)!=len(set(real_var_names_map.values())):
    #    print("WARNING: duplicate variable names in", real_var_names_map)
    outcome.expressions.insert(0, 'def solution('+', '.join(ly.unique([real_var_names_map[input] for input in outcome.inputs]))+"):")
    return "\n".join([expression for expression in ly.alter_var_names(outcome.expressions, real_var_names_map)]), len(outcome.inputs)
