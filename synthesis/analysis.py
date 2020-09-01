from keyword import iskeyword

equality_predicate = " <--> "
def _is_valid_variable(text):
    if len(text)==0:
        return False
    for c in text:
        if _is_not_var_symbol(c):
            return False
    return True
def _get_asignment_pos(text):
    level = 0
    for pos, c in enumerate(text):
        if _is_left_parenthesis_symbol(c):
            level += 1
        if _is_right_parenthesis_symbol(c):
            level -= 1
        if level==0 and c=="=" and pos>0 and not _is_math_symbol(text[pos-1]) and pos<len(text)-1 and text[pos+1]!="=":
            return pos
    return -1
def _is_math_symbol(text):
    valid_symbols = "<>=!"
    if text in valid_symbols:
        return True
    return False
def _is_not_var_symbol(text):
    valid_symbols = ".,!@#$%^/&*()-+={}[]:\t=<>`'\" "
    if text in valid_symbols:
        return True
    return False
def _is_separator(text):
    valid_symbols = ",{}[]:\t "
    if text in valid_symbols:
        return True
    return False
def _is_left_parenthesis_symbol(text):
    parenthesis_symbols = "({[\"'"
    if text in parenthesis_symbols:
        return True
    return False
def _is_right_parenthesis_symbol(text):
    parenthesis_symbols = ")}]\"'"
    if text in parenthesis_symbols:
        return True
    return False
def _count_strarting_spaces(text, tab=4):
    count = 0
    for c in text:
        if c==' ':
            count += 1
        elif c=='\t':
            count += tab
        else:
            break
    return count

def alter_var_names(expressions, var_name_map):
    """
    Example:
        >>> alter_var_names(["who's afraid of the big bad VAR1"], "find the VAR1"], {"VAR1": "ReVAR1"})
        ["who's afraid of the big bad ReVAR1"], "find the ReVAR1"]
    """
    return [_deflatten(expression, var_name_map) for expression in expressions]

def flatten(expressions_to_flatten, variable_name, variable_count = 0):
    expressions = list()
    for expression in expressions_to_flatten:
        if expression.strip().startswith("return "):
            expression = (" "*expression.index("return "))+"return("+expression.strip()[7:]+")"
        new_expression = ""
        new_variable_expression = ""
        level = 0
        for c in expression:
            if _is_left_parenthesis_symbol(c):
                if level==0:
                    new_expression += c
                level += 1
            if _is_right_parenthesis_symbol(c):
                level -= 1
            if level==0 or (level==1 and _is_separator(c) and not _is_right_parenthesis_symbol(c)):
                if len(new_variable_expression)>0:
                    if _is_valid_variable(new_variable_expression) or _get_asignment_pos(new_variable_expression)!=-1:
                        #print(new_variable_expression, _is_asignment(new_variable_expression))
                        new_expression += new_variable_expression
                    else:
                        variable_count += 1
                        new_expression += variable_name+str(variable_count)
                        found_variable_expressions = flatten([variable_name+str(variable_count)+equality_predicate+new_variable_expression], variable_name, variable_count)
                        expressions.extend(found_variable_expressions)
                        variable_count += len(found_variable_expressions)-1
                    new_variable_expression = ""
                new_expression += c
            else:
                if not _is_left_parenthesis_symbol(c) or level>1:
                    new_variable_expression += c
        expressions.append(new_expression)
    return expressions

def _deflatten(expression, variable_expressions):
    new_expression = ""
    current_var = ""
    for c in expression+" ":
        if _is_not_var_symbol(c):
            new_expression += variable_expressions.get(current_var, current_var)
            current_var = ""
            new_expression += c
        else:
            current_var += c
    return new_expression[:-1]

def deflatten(expressions):
    variable_expressions = {}
    kept_expressions = list()
    for expression in expressions:
        if equality_predicate in expression:
            splt = expression.split(equality_predicate)
            variable_expressions[splt[0]] = splt[1]
        else:
            kept_expressions.append(expression)
    kept_expressions = [_deflatten(expression, variable_expressions) for expression in kept_expressions]
    while True:
        prev_kept_expressions = kept_expressions
        kept_expressions = [_deflatten(expression, variable_expressions) for expression in kept_expressions] 
        diffs = False
        for i in range(len(kept_expressions)):
            if prev_kept_expressions[i]!=kept_expressions[i]:
                diffs = True
                break
        if not diffs:
            break
    spaces = 0
    for expression in kept_expressions:
        spaces = _count_strarting_spaces(expression)
        if spaces>0:
            break
    return_statements = list()
    unique_kept_expressions = list()
    for expression in kept_expressions:
        if expression.strip().startswith("return(") and _count_strarting_spaces(expression)==spaces:
            if not expression.strip()[7:-1] in return_statements:
                return_statements.append(expression.strip()[7:-1])
        elif not expression in unique_kept_expressions:
            unique_kept_expressions.append(expression)
            
    if len(return_statements)>0:
        unique_kept_expressions.append(" "*spaces+"return "+", ".join(return_statements))
    return unique_kept_expressions

def get_possible_variables(expressions):
    """
    Searches for assignments and values in parenthesis for variables.
    Assumes that var.parameter are libraries, since var would be method present in inputs or be assigned to anyway.
    Example:
        >>> get_possible_variables(["y_hat = model.predict(x_test)", "AUC(y_test, y_hat)"])
        ['y_hat', 'AUC', 'y_test', 'y_hat']
    """
    variables = list()
    for expression in expressions:
        assignment_pos = _get_asignment_pos(expression)
        if assignment_pos!=-1:
            expression = expression[:assignment_pos]
        current_var = ""
        last_symbol = ""
        for c in expression+" ":
            if _is_not_var_symbol(c):
                if _is_valid_variable(current_var) and last_symbol!="." and not iskeyword(current_var):
                    variables.append(current_var)
                current_var = ""
                last_symbol = c
            else:
                current_var += c
    return variables


def get_terms(expressions, ignore_variables=True):
    """
    Finds the terms by splitting the .
    If ignore_variable is True (default) then terms starting with "___" (which denote renamed variables)
    as well as terms before assignments ("___y_test" and "y_hat" in the example respectively) are ignored.
    Example:
        >>> get_terms(["y_hat = model.predict(random)", "AUC(___y_test, random)"])
        ['model', 'predict', 'random', 'AUC', 'random']
    """
    terms = list()
    for expression in expressions:
        if equality_predicate in expression:
            expression = expression.split(equality_predicate)[1]
        else:
            assignment_pos = _get_asignment_pos(expression)
            if assignment_pos!=-1:
                expression = expression[assignment_pos:]
        current_var = ""
        for c in expression+" ":
            if _is_not_var_symbol(c):
                if (_is_valid_variable(current_var) or not ignore_variables) and not current_var.startswith("___"):
                    terms.append(current_var)
                current_var = ""
            else:
                current_var += c
    return [term for term in terms if len(term)!=0]


def get_input_variables(expressions, known_variables):
    """
    Extracts which of the given variables are used by the given expressions to calculate quantities before they are
    assigned any value.
    Example:
        >>> get_input_variables(["y_test = y_test + noise()", "y_hat = model.predict(x_test)", "AUC(y_test, y_hat)"],
        ...         ["baseline", "model", "x_test", "y_test", "y_hat", "random_var", "y_test"])
        ['baseline', 'x_test', 'x_test']
    """
    known_variables = list(known_variables)
    variables = list()
    for expression in expressions:
        assigned_variable = None
        if equality_predicate in expression:
            assigned_variable = expression.split(equality_predicate)[0].strip()
            expression = expression.split(equality_predicate)[1]
        else:
            assignment_pos = _get_asignment_pos(expression)
            if assignment_pos != -1:
                assigned_variable = expression[:assignment_pos].strip()
                expression = expression[assignment_pos:]
        current_var = ""
        last_symbol = ""
        for c in expression+" ":
            if _is_not_var_symbol(c):
                if _is_valid_variable(current_var) and last_symbol!="." and current_var in known_variables:
                    variables.append(current_var)
                current_var = ""
                last_symbol = c
            else:
                current_var += c
        if assigned_variable is not None and assigned_variable in known_variables:
            known_variables.remove(assigned_variable)
    return variables


def get_output_variables(expressions):
    """
    Extracts the variables in the given expressions are assigned to.
    Example:
        >>> get_output_variables(["y_test = y_test + noise()", "y_hat = model.predict(x_test)", "AUC(y_test, y_hat)"])
        ['y_test', 'y_hat']
    """
    variables = list()
    for expression in expressions:
        if equality_predicate in expression:
            variables.append(expression.split(equality_predicate)[0].strip())
        else:
            assignment_pos = _get_asignment_pos(expression)
            if assignment_pos!=-1:
                variables.append(expression[:assignment_pos].strip())
    return variables


def get_argument_variables(expressions):
    """
    Searches the given expressions for method declarations and extracts the variables that are arguments.
    Example:
        >>> get_output_variables(["def test(x_test, y_test)", "y_test = y_test + noise()", "y_hat = model.predict(x_test)"])
    """
    variables = list()
    for expression in expressions:
        if expression.strip().startswith("def "):
            current_var = ''
            for c in expression[4:]:
                if _is_not_var_symbol(c):
                    if _is_valid_variable(current_var):
                        variables.append(current_var)
                    current_var = ""
                else:
                    current_var += c
    return variables
    
def get_expressions(text):
    """
    ret = list()
    top_level = 0
    current_expression = ""
    for line in text.split("\n"):
        spaces = _count_strarting_spaces(line)
        if top_level==0:
            top_level = spaces
        current_expression += line+"\n"
        if spaces<=top_level:
            ret.append(current_expression[:-1])
            current_expression = ""
    """
    return text.split("\n")


def unique(l):
    u = list()
    for i in l:
        if not i in u:
            u.append(i)
    return u