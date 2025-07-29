# In spyq/__init__.py
import sys
import os
from pathlib import Path
from typing import Optional, List, Dict, Any
import importlib.util
import importlib.machinery
import ast
import json

from pathlib import Path
import re

def _get_version() -> str:
    """Read version from pyproject.toml."""
    try:
        # Try to read from installed package metadata first
        from importlib.metadata import version, PackageNotFoundError
        try:
            return version('spyq')
        except PackageNotFoundError:
            pass
            
        # Fall back to reading pyproject.toml directly (development mode)
        pyproject_path = Path(__file__).parent.parent.parent / 'pyproject.toml'
        if not pyproject_path.exists():
            pyproject_path = Path(__file__).parent.parent.parent.parent / 'pyproject.toml'
            
        if pyproject_path.exists():
            pyproject_content = pyproject_path.read_text(encoding='utf-8')
            version_match = re.search(
                r'^version\s*=\s*["\']([^\"\']+)[\"\']',
                pyproject_content,
                re.MULTILINE
            )
            if version_match:
                return version_match.group(1)
    except Exception:
        pass
    
    # Fallback version if all else fails
    return "0.0.0"

__version__ = _get_version()


class SPYQImportHook:
    def __init__(self):
        self.original_import = None
        self.config = self._load_config()

    def _load_config(self) -> Dict[str, Any]:
        # Try to load config from ~/.config/spyq/config.json
        config_path = Path.home() / ".config" / "spyq" / "config.json"
        if config_path.exists():
            try:
                with open(config_path, 'r') as f:
                    return json.load(f)
            except Exception:
                pass

        # Default config
        return {
            "max_file_lines": 300,
            "max_function_lines": 50,
            "max_function_params": 4,
            "max_nesting_depth": 4,
            "require_docstrings": True,
            "require_type_hints": True,
            "forbid_global_vars": True,
            "forbid_bare_except": True,
            "forbid_print_statements": True
        }

    def validate_source(self, source: str, filename: str) -> List[Dict[str, Any]]:
        """Validate Python source code against configured rules."""
        issues = []

        try:
            tree = ast.parse(source, filename=filename)

            # Check file length
            if 'max_file_lines' in self.config:
                line_count = len(source.splitlines())
                if line_count > self.config['max_file_lines']:
                    issues.append({
                        'line': 1,
                        'col': 0,
                        'message': f'File too long ({line_count} > {self.config["max_file_lines"]} lines)',
                        'type': 'error'
                    })

            # Add more validations here...

        except SyntaxError as e:
            issues.append({
                'line': e.lineno or 1,
                'col': e.offset or 0,
                'message': f'Syntax error: {e.msg}',
                'type': 'error'
            })

        return issues

    def find_spec(self, fullname, path=None, target=None):
        """Find the module spec and install our loader if it's a Python file."""
        # Get the default spec using the original finder
        if hasattr(self, 'original_find_spec'):
            spec = self.original_find_spec(fullname, path, target)
        else:
            # Fallback for older Python versions
            try:
                spec = importlib.util.find_spec(fullname, path)
            except (ImportError, AttributeError):
                return None
        
        # Only process Python files with a valid loader and origin
        if (spec is not None and 
            hasattr(spec, 'loader') and 
            hasattr(spec, 'origin') and 
            spec.origin is not None and 
            isinstance(spec.origin, str) and 
            spec.origin.endswith('.py')):
            # Create a new loader that wraps the original one
            spec.loader = SPYQLoader(spec.loader, self)
        
        return spec


class SPYQLoader:
    def __init__(self, original_loader, hook):
        self.original_loader = original_loader
        self.hook = hook

    def create_module(self, spec):
        return self.original_loader.create_module(spec)

    def exec_module(self, module):
        # Get the source code
        source = self.original_loader.get_source(module.__name__)
        if source is not None:
            # Validate the source
            issues = self.hook.validate_source(source, getattr(module, '__file__', '<string>'))
            if issues:
                for issue in issues:
                    print(
                        f"{module.__file__}:{issue['line']}:{issue['col']}: {issue['type'].upper()}: {issue['message']}")
                if any(issue['type'] == 'error' for issue in issues):
                    print("Validation failed - aborting execution")
                    sys.exit(1)

        # Execute the module
        return self.original_loader.exec_module(module)

    # Forward all other attributes to the original loader
    def __getattr__(self, name):
        return getattr(self.original_loader, name)


def install_import_hook():
    """Install the SPYQ import hook."""
    if not hasattr(sys, 'meta_path'):
        return None
    
    # Don't install the hook if it's already installed
    for finder in sys.meta_path:
        if isinstance(finder, SPYQImportHook):
            return finder
    
    hook = SPYQImportHook()
    
    # Save the original find_spec from importlib.machinery
    if not hasattr(sys, '_spyq_original_find_spec'):
        import importlib.machinery
        sys._spyq_original_find_spec = importlib.machinery.PathFinder.find_spec
        
        # Patch the PathFinder
        def patched_find_spec(fullname, path=None, target=None):
            spec = sys._spyq_original_find_spec(fullname, path, target)
            if (spec is not None and 
                hasattr(spec, 'loader') and 
                hasattr(spec, 'origin') and 
                spec.origin is not None and 
                isinstance(spec.origin, str) and 
                spec.origin.endswith('.py')):
                spec.loader = SPYQLoader(spec.loader, hook)
            return spec
            
        importlib.machinery.PathFinder.find_spec = patched_find_spec
    
    # Insert our finder at the beginning of meta_path
    sys.meta_path.insert(0, hook)
    return hook


# Install the hook automatically when the module is imported
if 'SPYQ_DISABLE' not in os.environ:
    install_import_hook()