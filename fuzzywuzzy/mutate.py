import ast
import astor
import sys
import random
import os
import copy

class Mutator(ast.NodeTransformer):
    def __init__(self, seed, mutation_budget=10):
        """Initialize mutator with a fixed random seed and a mutation budget."""
        random.seed(seed)
        self.mutation_budget = mutation_budget  # Increased mutation budget
        self.mutation_candidates = []

    def visit(self, node):
        """Collect all valid mutation candidates before mutating."""
        if isinstance(node, (ast.Compare, ast.BinOp, ast.BoolOp, ast.Assign, ast.Expr, ast.If, ast.FunctionDef, ast.Call)):
            self.mutation_candidates.append(node)
        return super().visit(node)

    def apply_mutations(self):
        """Apply a fixed number of mutations at random locations."""
        if not self.mutation_candidates:
            return  # No mutation possible

        selected_nodes = random.sample(self.mutation_candidates, min(self.mutation_budget, len(self.mutation_candidates)))
        for node in selected_nodes:
            self.mutate_node(node)

    def mutate_node(self, node):
        """Apply a mutation based on the type of node."""
        if isinstance(node, ast.Compare):  # Negate comparisons
            comparison_map = {ast.GtE: ast.Lt, ast.LtE: ast.Gt, ast.Gt: ast.LtE, ast.Lt: ast.GtE, ast.Eq: ast.NotEq, ast.NotEq: ast.Eq}
            if isinstance(node.ops[0], tuple(comparison_map.keys())):
                node.ops[0] = comparison_map[type(node.ops[0])]()
        
        elif isinstance(node, ast.BinOp):  # Swap binary operators and add constants
            binop_map = {ast.Add: ast.Sub, ast.Sub: ast.Add, ast.Mult: ast.Pow, ast.Pow: ast.Mult, ast.FloorDiv: ast.Div, ast.Div: ast.FloorDiv}
            if isinstance(node.op, tuple(binop_map.keys())):
                node.op = binop_map[type(node.op)]()
            # Adding a constant operation
            if isinstance(node.left, ast.Num) and isinstance(node.right, ast.Num):
                node.left = ast.Num(random.randint(1, 100))  # Random constant change
        
        elif isinstance(node, ast.BoolOp):  # Swap Boolean logic
            if isinstance(node.op, ast.And):
                node.op = ast.Or()
            elif isinstance(node.op, ast.Or):
                node.op = ast.And()
        
        elif isinstance(node, ast.Assign):  # Delete assignments safely
            node.value = ast.Num(0)  # Replace with a dummy value to avoid undefined variables
        
        elif isinstance(node, ast.Expr):  # Delete function calls carefully
            if isinstance(node.value, ast.Call):
                return ast.Expr(ast.Num(1))  # Replace with a dummy expression
        
        elif isinstance(node, ast.If):  # Negate if conditions
            node.test = ast.UnaryOp(op=ast.Not(), operand=node.test)
        
        elif isinstance(node, ast.FunctionDef):  # Modify function arguments
            if node.args.args:
                random_arg = random.choice(node.args.args)
                node.args.args.remove(random_arg)  # Remove random argument
        
        elif isinstance(node, ast.Call):  # Change function calls
            if isinstance(node.func, ast.Name):
                node.func.id = random.choice(['print', 'len', 'sum'])  # Randomize function call

def mutate_code(source_code, seed, mutation_budget=10):
    """Apply AST mutations to the input source code."""
    tree = ast.parse(source_code)
    mutator = Mutator(seed, mutation_budget)
    mutator.visit(tree)  # Collect mutation candidates
    mutator.apply_mutations()  # Apply mutations
    ast.fix_missing_locations(tree)

    try:
        return ast.unparse(tree)  # Python 3.9+
    except AttributeError:
        return astor.to_source(tree)  # For Python 3.5-3.8

def main():
    if len(sys.argv) != 3:
        print("Usage: python mutate.py <source_file.py> <num_mutants>")
        sys.exit(1)

    source_file = sys.argv[1]
    try:
        num_mutants = int(sys.argv[2])
    except ValueError:
        print("Error: num_mutants must be an integer.")
        sys.exit(1)

    if not os.path.exists(source_file):
        print("Error: {} not found.".format(source_file))
        sys.exit(1)

    with open(source_file, "r") as f:
        source_code = f.read()

    seen_mutants = set()
    
    for i in range(num_mutants):
        mutated_code = mutate_code(source_code, seed=i, mutation_budget=10)  # Increased mutation budget
        if mutated_code in seen_mutants:
            continue  # Skip duplicate mutants
        seen_mutants.add(mutated_code)

        mutant_filename = "{}.py".format(i)
        with open(mutant_filename, "w") as f:
            f.write(mutated_code)

    print("Generated {} unique mutants.".format(len(seen_mutants)))

if __name__ == "__main__":
    main()
