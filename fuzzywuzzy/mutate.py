import ast
import astor
import random
import sys

class Mutator(ast.NodeTransformer):
    def __init__(self):
        super().__init__()
        self.mutations = [self.mutate_comparison, self.mutate_binary_op, self.mutate_delete_stmt]
    
    def mutate_comparison(self, node):
        """Negate a single comparison operator."""
        comparison_map = {
            ast.Gt: ast.Lt, ast.Lt: ast.Gt,
            ast.GtE: ast.LtE, ast.LtE: ast.GtE,
            ast.Eq: ast.NotEq, ast.NotEq: ast.Eq
        }
        if isinstance(node.ops[0], tuple(comparison_map.keys())):
            node.ops[0] = comparison_map[type(node.ops[0])]()
        return node
    
    def mutate_binary_op(self, node):
        """Swap binary operators + and -, * and //."""
        binary_op_map = {ast.Add: ast.Sub, ast.Sub: ast.Add, ast.Mult: ast.FloorDiv, ast.FloorDiv: ast.Mult}
        if isinstance(node.op, tuple(binary_op_map.keys())):
            node.op = binary_op_map[type(node.op)]()
        return node
    
    def mutate_delete_stmt(self, node):
        """Delete an assignment or function call statement."""
        if isinstance(node, (ast.Assign, ast.Expr)):
            return None  # Removes the node
        return node
    
    def visit(self, node):
        if random.random() < 0.3:  # 30% chance to mutate any applicable node
            node = random.choice(self.mutations)(node)
        return super().visit(node)

def mutate_file(filename, num_mutants):
    with open(filename, "r") as f:
        source_code = f.read()
    
    tree = ast.parse(source_code)
    random.seed(0)  # Ensure deterministic mutations
    
    for i in range(num_mutants):
        mutator = Mutator()
        mutated_tree = mutator.visit(ast.fix_missing_locations(tree))
        mutated_code = astor.to_source(mutated_tree)
        
        with open(f"{i}.py", "w") as f:
            f.write(mutated_code)
    
if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python3 mutate.py <source_file.py> <num_mutants>")
        sys.exit(1)
    
    source_file = sys.argv[1]
    num_mutants = int(sys.argv[2])
    mutate_file(source_file, num_mutants)