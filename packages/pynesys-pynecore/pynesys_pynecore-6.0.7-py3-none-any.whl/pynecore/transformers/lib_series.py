import ast
from typing import Dict, Set, cast


class LibrarySeriesTransformer(ast.NodeTransformer):
    """
    AST transformer that prepares library Series variables for the SeriesTransformer.
    When a library variable is used with indexing, it creates a local Series variable
    declaration that SeriesTransformer can then process.
    """

    def __init__(self):
        self.lib_series_vars: Dict[
            str, Dict[str, tuple[str, ast.AST]]] = {}  # module -> {attr -> (local_name, type_annotation)}
        self.used_series: Set[tuple[str, str]] = set()  # (module, attr) pairs that are used as Series
        self.declarations_to_insert: Dict[str, list[ast.AnnAssign]] = {}  # function_name -> declarations
        self.current_function: str | None = None

    @staticmethod
    def _make_series_name(attr: str) -> str:
        """Generate unique name for the local Series variable"""
        # Replace dots with underscores in attr
        attr = attr.replace('.', '_')
        return f'_lib_{attr}'

    @staticmethod
    def _create_attribute_chain(chain: list[str]) -> ast.expr:
        """Create an attribute chain from a list of names"""
        result: ast.expr = ast.Name(id=chain[0], ctx=ast.Load())
        for name in chain[1:]:
            result = ast.Attribute(
                value=result,
                attr=name,
                ctx=ast.Load()
            )
        return result

    def visit_FunctionDef(self, node: ast.FunctionDef) -> ast.FunctionDef:
        """Track current function and insert Series declarations"""
        self.current_function = node.name

        # Process function body first
        node = cast(ast.FunctionDef, self.generic_visit(node))

        # Insert declarations for used Series at the start of the function
        if self.current_function in self.declarations_to_insert:
            node.body = self.declarations_to_insert[self.current_function] + node.body

        self.current_function = None
        return node

    def process_series_usage(self, module: str, attr_chain: list[str], type_annotation: ast.AST | None = None) -> str:
        """
        Process a Series usage from a library, creating declaration if needed.
        Returns the local variable name to use.
        """
        if module not in self.lib_series_vars:
            self.lib_series_vars[module] = {}

        # Create underscore version for the variable name
        attr_key = '_'.join(attr_chain)
        if attr_key not in self.lib_series_vars[module]:
            local_name = self._make_series_name(attr_key)
            self.lib_series_vars[module][attr_key] = (local_name, type_annotation)

        local_name = self.lib_series_vars[module][attr_key][0]

        # If this Series hasn't been used in current function yet
        if (module, attr_key) not in self.used_series and self.current_function:
            self.used_series.add((module, attr_key))

            # Create Series declaration with proper attribute chain
            decl = ast.AnnAssign(
                target=ast.Name(id=local_name, ctx=ast.Store()),
                annotation=type_annotation or ast.Name(id='Series', ctx=ast.Load()),
                value=self._create_attribute_chain([module] + attr_chain),  # ez már expr típust ad vissza
                simple=1
            )

            # Store declaration to be inserted
            if self.current_function not in self.declarations_to_insert:
                self.declarations_to_insert[self.current_function] = []
            self.declarations_to_insert[self.current_function].append(decl)

        return local_name

    def visit_Subscript(self, node: ast.Subscript) -> ast.AST:
        """Convert library Series access when used with indexing"""

        # Get the full attribute chain
        def get_attribute_chain(_node):
            if isinstance(_node, ast.Name):
                return [_node.id]
            elif isinstance(_node, ast.Attribute):
                return get_attribute_chain(_node.value) + [_node.attr]
            return []

        if isinstance(node.value, ast.Attribute):
            attr_chain = get_attribute_chain(node.value)
            if attr_chain and attr_chain[0] == 'lib':
                # Use the complete chain after 'lib'
                local_name = self.process_series_usage('lib', attr_chain[1:])
                # Replace lib.xxx.yyy[idx] with local_name[idx]
                node.value = ast.Name(id=local_name, ctx=ast.Load())

        return self.generic_visit(node)
