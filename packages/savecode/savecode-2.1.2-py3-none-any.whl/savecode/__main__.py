"""
Allows `python -m savecode …` to work exactly like the console-script entry point.
"""

from savecode.cli import main

if __name__ == "__main__":
    main()
