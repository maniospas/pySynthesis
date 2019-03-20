import analysis

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
        for expression in self.expressions:
            expression_input_vars = analysis.get_input_variables([expression], variables)
            expression_output_vars = analysis.get_output_variables([expression])
            input_vars.extend([input_var for input_var in expression_input_vars if input_var not in output_vars])
            output_vars.extend(expression_output_vars)
        input_vars = analysis.unique(input_vars)
        output_vars = analysis.unique(output_vars)
        self.inputs = input_vars
        self.outputs = output_vars

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
        elif expression.strip().startswith("#"):
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
    return [block for block in blocks if not block.empty()]