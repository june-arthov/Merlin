import os
import sys
# Path hack to ensure we can run from anywhere
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from merlin.main_entry import main_cli

def main():
    main_cli()

if __name__ == "__main__":
    main()
