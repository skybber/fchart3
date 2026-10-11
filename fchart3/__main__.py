"""
Wrapper script to let fchart3 be found on Windows without needing an fchart3.bat file in venv\Scripts
"""
import os
import runpy

def main():
    """Launcher for the main fchart3 application."""
    script_path = os.path.join(os.path.dirname(__file__), 'fchart3_cli.py')
    runpy.run_path(script_path, run_name='__main__')

def atlas_main():
    """Launcher for the fchart3-atlas tool."""
    script_path = os.path.join(os.path.dirname(__file__), 'fchart3_atlas_cli.py')
    runpy.run_path(script_path, run_name='__main__')

if __name__ == '__main__':
    main()
