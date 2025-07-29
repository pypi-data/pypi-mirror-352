# In spyq/install.py
import os
import sys
import site
from pathlib import Path


def create_sitecustomize():
    """Create sitecustomize.py with SPYQ hook"""
    content = '''import sys
import os
import site

# Add user site-packages to path
site.addsitedir(os.path.expanduser("~/.local/lib/python{sys_version}/site-packages"))

# Check if not in a virtual environment
if not hasattr(sys, 'real_prefix') and 'VIRTUAL_ENV' not in os.environ:
    try:
        import spyq
        # Check if not running spyq itself
        if not any('spyq' in str(p).lower() for p in sys.argv):
            spyq.install_import_hook()
    except ImportError as e:
        sys.stderr.write(f"SPYQ import error: {e}\\n")
'''

    # Get Python version
    py_version = f"{sys.version_info.major}.{sys.version_info.minor}"
    user_site = site.getusersitepackages()
    sitecustomize_path = os.path.join(user_site, "sitecustomize.py")

    # Create directory if it doesn't exist
    os.makedirs(user_site, exist_ok=True)

    # Write sitecustomize.py
    with open(sitecustomize_path, 'w') as f:
        f.write(content.format(sys_version=py_version))

    return sitecustomize_path


def create_default_config():
    """Create default SPYQ config"""
    config_content = '''{
    "max_file_lines": 300,
    "max_function_lines": 50,
    "max_function_params": 4,
    "max_nesting_depth": 4,
    "require_docstrings": true,
    "require_type_hints": true,
    "forbid_global_vars": true,
    "forbid_bare_except": true,
    "forbid_print_statements": true
}'''
    config_dir = os.path.expanduser("~/.config/spyq")
    os.makedirs(config_dir, exist_ok=True)
    config_path = os.path.join(config_dir, "config.json")

    # Only write if file doesn't exist
    if not os.path.exists(config_path):
        with open(config_path, 'w') as f:
            f.write(config_content)

    return config_path


def install():
    """Install SPYQ hooks"""
    try:
        sitecustomize = create_sitecustomize()
        config = create_default_config()
        print(f"SPYQ hook installed: {sitecustomize}")
        print(f"Default config: {config}")
        return 0
    except Exception as e:
        print(f"Error installing SPYQ: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(install())