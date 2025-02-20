import ast
import astor
import sys
import random
import os

class Mutator(ast.NodeTransformer):
    def __init__(self, seed):
        """Initialize mutator with a specific random seed for determinism."""
        random.seed(seed)

    def visit_Compare(self, node):
        """Negate a comparison operation (>= → <, == → !=, etc.)."""
        comparison_map = {
            ast.GtE: ast.Lt, ast.LtE: ast.Gt,
            ast.Eq: ast.NotEq, ast.NotEq: ast.Eq,
            ast.Gt: ast.LtE, ast.Lt: ast.GtE
        }
        if isinstance(node.ops[0], tuple(comparison_map.keys())):
            new_op = comparison_map[type(node.ops[0])]()
            node.ops[0] = ast.copy_location(new_op, node.ops[0])
        return node

    def visit_BinOp(self, node):
        """Swap binary operators (+ ↔ -, * ↔ //)."""
        binop_map = {
            ast.Add: ast.Sub, ast.Sub: ast.Add,
            ast.Mult: ast.FloorDiv, ast.FloorDiv: ast.Mult
        }
        if isinstance(node.op, tuple(binop_map.keys())):
            new_op = binop_map[type(node.op)]()
            node.op = ast.copy_location(new_op, node.op)
        return node

    def visit_Assign(self, node):
        """Delete an assignment statement randomly."""
        if random.random() < 0.3:
            return None
        return node

    def visit_Expr(self, node):
        """Delete function call expressions randomly."""
        if isinstance(node.value, ast.Call) and random.random() < 0.3:
            return None
        return node

def mutate_code(source_code, seed):
    """Apply AST mutations to the input source code."""
    tree = ast.parse(source_code)
    mutator = Mutator(seed)
    mutated_tree = mutator.visit(tree)
    ast.fix_missing_locations(mutated_tree)
    return astor.to_source(mutated_tree)

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

    for i in range(num_mutants):
        mutated_code = mutate_code(source_code, seed=i)  # Deterministic mutations
        mutant_filename = "{}.py".format(i)
        with open(mutant_filename, "w") as f:
            f.write(mutated_code)

    print("Generated {} mutants.".format(num_mutants))

if __name__ == "__main__":
    main()

