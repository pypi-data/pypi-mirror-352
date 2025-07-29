from setuptools import setup
from setuptools.command.install import install


class NoCompileInstall(install):
    """Custom install command that disables bytecode compilation.
    
    This is necessary for PyneCore's AST transformation system to work correctly.
    The import hooks need to process Python source files (.py) at runtime,
    but if bytecode files (.pyc) exist, Python will use them instead,
    bypassing our transformations.
    """
    
    def run(self):
        # Disable bytecode compilation during install
        import sys
        old_dont_write_bytecode = sys.dont_write_bytecode
        try:
            sys.dont_write_bytecode = True
            super().run()
        finally:
            sys.dont_write_bytecode = old_dont_write_bytecode


setup(
    # All configuration comes from pyproject.toml
    # This setup.py only exists to provide a custom install command
    cmdclass={
        'install': NoCompileInstall,
    }
)