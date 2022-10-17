from synthesis import analysis


class Block:
    def __init__(self):
        self.expressions = list()
        self.comments = ""
        self.variable_descriptions = {}
    def empty(self):
        return len(self.expressions)==0
    def find_io(self, variables):
        output_vars = list()
        input_vars = list()
        transformed_vars = list()
        for expression in self.expressions:
            expression_input_vars = analysis.get_input_variables([expression], variables)
            expression_output_vars = analysis.get_output_variables([expression])
            input_vars.extend([input_var for input_var in expression_input_vars if input_var not in output_vars])
            output_vars.extend(expression_output_vars)
            transformed_vars.extend([input_var for input_var in expression_input_vars if input_var in output_vars])
        self.inputs = analysis.unique(input_vars)
        self.outputs = analysis.unique(output_vars)
        self.transformed_vars = analysis.unique(transformed_vars)
    def convert_to_level(self, top_level):
        min_spaces = min([analysis._count_strarting_spaces(expresion) for expresion in self.expressions])
        if min_spaces < top_level:
            raise Exception("Block is of lower level")
        self.expressions = [" " * (
                    analysis._count_strarting_spaces(expresion) - min_spaces + top_level) + expresion.lstrip() for expresion in self.expressions]


def get_expression_blocks(expressions):
    block = Block()
    blocks = [block]
    in_comments = False
    top_level = 0
    for expression in expressions:
        if expression.strip().startswith("def "):
            continue
        spaces = analysis._count_strarting_spaces(expression)
        if top_level==0:
            top_level = spaces
        if len(expression.strip())==0:
            if not block.empty():
                block = Block()
                blocks.append(block)
        elif (expression.strip().startswith("\"\"\"") or expression.strip().startswith("'''")) and not in_comments:
            if not block.empty() and top_level==spaces:
                block = Block()
                blocks.append(block)
            if len(block.comments)>0:
                block.comments += "\n"
            block.comments += expression
            in_comments = True
        elif (expression.strip().endswith("\"\"\"") or expression.strip().endswith("'''")) and in_comments:
            block.comments += expression+"\n"
            in_comments = False
        elif in_comments:
            block.comments += expression+"\n"
        elif expression.strip().startswith("#") and top_level==spaces:
            if not block.empty(): #and top_level==spaces:
                block = Block()
                blocks.append(block)
            if len(block.comments)>0:
                block.comments += "\n"
            block.comments += expression
        else:
            block.expressions.append(expression)
        """elif expression.strip().endswith(":"):
            if not block.empty():
                block = Block()
                blocks.append(block)
            block.expressions.append(expression) [TODO: make this more enteligent]"""
    blocks = [block for block in blocks if not block.empty()]
    blocks_with_nested = list(blocks)
    for block in blocks:
        try:
            block.convert_to_level(4)
            min_space = min([analysis._count_strarting_spaces(expresion) for expresion in block.expressions])
            nested_blocks = get_expression_blocks([expresion for expresion in block.expressions if min_space < analysis._count_strarting_spaces(expresion)])
            blocks_with_nested.extend(nested_blocks)
        except:
            pass
    
    return blocks_with_nested