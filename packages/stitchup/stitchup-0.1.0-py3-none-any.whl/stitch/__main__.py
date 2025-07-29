import importlib.util
import sys, ast, os
import importlib

class FromImportVisitor(ast.NodeTransformer):
    def visit_ImportFrom(self, node):
        module_name = node.module
        imported_symbols = node.names
        sys.path.append(os.getcwd())
        spec = importlib.util.find_spec(module_name)
        if spec and spec.origin:
            module_location = spec.origin
        with open(module_location, 'r') as f:
            module_code = f.read()
        # parse only the imports
        node = ast.parse(module_code)
        transformed_nodes = []
        for exported_symbol in node.body:
            if isinstance(exported_symbol, ast.FunctionDef) or isinstance(exported_symbol, ast.ClassDef):
                if exported_symbol.name in [symbol.name for symbol in imported_symbols]:
                    transformed_nodes.append(exported_symbol)
            if isinstance(exported_symbol, ast.ImportFrom):
                transformed_exported_symbols = self.visit(exported_symbol)
                if isinstance(transformed_exported_symbols, list):
                    for symbol in transformed_exported_symbols:
                        ast.fix_missing_locations(symbol)
                        transformed_nodes.append(symbol)
                elif transformed_exported_symbols is not None:
                    ast.fix_missing_locations(transformed_exported_symbols)
                    transformed_nodes.append(transformed_exported_symbols)
        return transformed_nodes
def main():
    src_file = sys.argv[1]
    dest_file = sys.argv[2]
    with open(src_file, 'r') as f:
        src_code = f.read()
    src_node = ast.parse(src_code)
    visitor = FromImportVisitor()
    transformed_src_node = visitor.visit(src_node)
    ast.fix_missing_locations(transformed_src_node)

    with open(dest_file, 'w') as f:
        f.write(ast.unparse(transformed_src_node))

if __name__ == '__main__':
    main()