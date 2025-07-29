from typing import cast
import ast


class InputTransformer(ast.NodeTransformer):
    """
    Transform input function calls:
    1. Add _id parameter to input calls
    2. Add getattr for source inputs at the start of functions
    3. Add required imports (lib, na) if not present
    Must be applied after SeriesTransformer.
    """

    def __init__(self):
        self.function_source_vars = {}  # function_name -> {var_name -> source_str}
        self.current_function = None
        self.has_source_inputs = False
        self.imported_names: set[str] = set()  # Track what's already imported

    @staticmethod
    def _is_input_call(node: ast.Call) -> bool:
        """Check if node is lib.input() or lib.input.xxx() call"""
        # Handle lib.input(...) pattern
        if isinstance(node.func, ast.Attribute) and node.func.attr == 'input':
            return isinstance(node.func.value, ast.Name) and node.func.value.id == 'lib'

        # Handle lib.input.xxx(...) pattern
        if not isinstance(node.func, ast.Attribute):
            return False

        if not isinstance(node.func.value, ast.Attribute):
            return False

        return (isinstance(node.func.value.value, ast.Name) and
                node.func.value.value.id == 'lib' and
                node.func.value.attr == 'input')

    def visit_arguments(self, node: ast.arguments) -> ast.arguments:
        """Add _id to input calls in function arguments and collect source vars"""
        if self.current_function is None:
            return node

        # Loop through arguments and defaults together
        for arg, default in zip(node.args[-len(node.defaults):], node.defaults):
            if default and isinstance(default, ast.Call):
                if self._is_input_call(default):
                    # Add id keyword argument with argument name
                    default.keywords.append(
                        ast.keyword(
                            arg='_id',
                            value=ast.Constant(value=arg.arg)
                        )
                    )

                    # Check if it's a source input
                    is_source_call = False
                    is_input_call = False

                    if isinstance(default.func, ast.Attribute) and default.func.attr == 'source':
                        # This is lib.input.source call
                        is_source_call = True
                    elif isinstance(default.func, ast.Attribute) and default.func.attr == 'input':
                        # This is lib.input call
                        is_input_call = True

                    # Only proceed if it's a source call or input call with arguments
                    if (is_source_call or is_input_call) and default.args:
                        if isinstance(default.args[0], ast.Constant) and is_source_call:
                            # Handle string constant in lib.input.source
                            if self.current_function not in self.function_source_vars:
                                self.function_source_vars[self.current_function] = {}
                            self.function_source_vars[self.current_function][arg.arg] = cast(ast.Constant,
                                                                                             default.args[0]).value
                            self.has_source_inputs = True
                        elif isinstance(default.args[0], ast.Attribute):
                            # Handle attribute reference (e.g., lib.close)
                            attr = cast(ast.Attribute, default.args[0])
                            if isinstance(attr.value, ast.Name) and attr.value.id == 'lib':
                                # For lib.xxx pattern, store the attribute name
                                if self.current_function not in self.function_source_vars:
                                    self.function_source_vars[self.current_function] = {}
                                self.function_source_vars[self.current_function][arg.arg] = attr.attr
                                self.has_source_inputs = True

        return node

    def visit_FunctionDef(self, node: ast.FunctionDef) -> ast.FunctionDef:
        """Insert getattr calls at the start of functions for source inputs"""
        # Save previous function name
        previous_function = self.current_function
        self.current_function = node.name

        # Process function arguments and body
        node = cast(ast.FunctionDef, self.generic_visit(node))

        # Add getattr for each source input in this function
        source_vars = self.function_source_vars.get(self.current_function, {})
        for var_name, source_str in source_vars.items():
            # Create: var_name = getattr(lib, var_name, lib.na)
            assign = ast.Assign(
                targets=[ast.Name(id=var_name, ctx=ast.Store())],
                value=ast.Call(
                    func=ast.Name(id='getattr', ctx=ast.Load()),
                    args=[
                        ast.Name(id='lib', ctx=ast.Load()),
                        ast.Name(id=var_name, ctx=ast.Load()),
                        ast.Attribute(
                            value=ast.Name(id='lib', ctx=ast.Load()),
                            attr='na',
                            ctx=ast.Load()
                        )
                    ],
                    keywords=[]
                )
            )
            node.body.insert(0, assign)

        # Restore previous function name
        self.current_function = previous_function
        return node

    def visit_Module(self, node: ast.Module) -> ast.Module:
        """Add required imports if not present"""
        # Process the module first to collect existing imports
        node = cast(ast.Module, self.generic_visit(node))

        if not self.has_source_inputs:
            return node

        return node
