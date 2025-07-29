from typing import cast
import os
import sys
import ast
import importlib.util
import importlib.machinery
from pathlib import Path


class PyneLoader(importlib.machinery.SourceFileLoader):
    """Loader that handles AST transformation"""

    # noinspection PyMethodOverriding
    def source_to_code(self, data, path, *, _optimize=-1):
        """Transform source to code if needed"""
        tree = ast.parse(data)
        path = Path(path)

        # Store file path in AST for transformers
        tree._module_file_path = str(path.resolve())  # type: ignore

        # Only transform if it has @pyne decorator
        if (tree.body and isinstance(tree.body[0], ast.Expr) and
                isinstance(cast(ast.Expr, tree.body[0]).value, ast.Constant) and
                isinstance(cast(ast.Constant, cast(ast.Expr, tree.body[0]).value).value, str) and
                '@pyne' in cast(ast.Constant, cast(ast.Expr, tree.body[0]).value).value):

            # Remove test cases from the output, because they can coorupt the output
            transformed = tree
            transformed.body = [node for node in transformed.body
                                if not (isinstance(node, ast.FunctionDef)
                                        and node.name.startswith('__test_') and node.name.endswith('__'))]

            # Transform AST - lazy import transformers only when needed
            from pynecore.transformers.import_lifter import ImportLifterTransformer
            from pynecore.transformers.import_normalizer import ImportNormalizerTransformer
            from pynecore.transformers.persistent_series import PersistentSeriesTransformer
            from pynecore.transformers.lib_series import LibrarySeriesTransformer
            from pynecore.transformers.function_isolation import FunctionIsolationTransformer
            from pynecore.transformers.module_property import ModulePropertyTransformer
            from pynecore.transformers.series import SeriesTransformer
            from pynecore.transformers.persistent import PersistentTransformer
            from pynecore.transformers.input_transformer import InputTransformer
            from pynecore.transformers.safe_convert_transformer import SafeConvertTransformer

            transformed = ImportLifterTransformer().visit(transformed)
            transformed = ImportNormalizerTransformer().visit(transformed)
            transformed = PersistentSeriesTransformer().visit(transformed)
            transformed = LibrarySeriesTransformer().visit(transformed)
            transformed = FunctionIsolationTransformer().visit(transformed)
            transformed = ModulePropertyTransformer().visit(transformed)
            transformed = SeriesTransformer().visit(transformed)
            transformed = PersistentTransformer().visit(transformed)
            transformed = InputTransformer().visit(transformed)
            transformed = SafeConvertTransformer().visit(transformed)

            ast.fix_missing_locations(transformed)

            # Debug output if requested
            if os.environ.get('PYNE_AST_DEBUG'):
                print("-" * 100)
                print(f"Transformed {path}:")
                try:
                    from rich.syntax import Syntax  # type: ignore
                    from rich import print as rprint  # type: ignore
                    rprint(Syntax(ast.unparse(transformed), "python", word_wrap=True, line_numbers=False))
                except ImportError:
                    print(ast.unparse(transformed))
                print("-" * 100)
            elif os.environ.get('PYNE_AST_DEBUG_RAW'):
                print(ast.unparse(transformed))

            if os.environ.get('PYNE_AST_SAVE'):
                Path("/tmp/pyne").mkdir(parents=True, exist_ok=True)

                with open(f"/tmp/pyne/{path.stem}.py", "w") as f:
                    f.write(ast.unparse(transformed))

            tree = transformed

        # Let Python handle bytecode caching
        return compile(tree, path, 'exec', optimize=_optimize)


class PyneImportHook:
    """Import hook that uses PyneLoader"""

    # noinspection PyMethodMayBeStatic,PyUnusedLocal
    def find_spec(self, fullname: str, path, target=None):
        """Find and create module spec"""
        if path is None:
            path = sys.path

        if "." in fullname:
            *_, name = fullname.split(".")
        else:
            name = fullname

        for entry in path:
            if entry == "":
                entry = "."
            py_path = Path(entry) / f"{name}.py"
            if py_path.exists():
                return importlib.util.spec_from_file_location(
                    fullname,
                    py_path,
                    loader=PyneLoader(fullname, str(py_path))
                )
        return None


# Install the import hook
sys.meta_path.insert(0, PyneImportHook())
