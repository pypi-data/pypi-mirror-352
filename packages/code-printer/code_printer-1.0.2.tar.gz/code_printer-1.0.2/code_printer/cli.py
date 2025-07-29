"""
Command Line Interface for Code Printer
"""

import argparse
import sys
from .core import CodePrinter

def main():
    """Main CLI function"""
    parser = argparse.ArgumentParser(
        description="🐍 Code Printer - Print predefined code snippets",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  code-printer 1          # Print code #1
  code-printer --all      # Print all codes
  code-printer --list     # List available codes
  code-printer --search print  # Search for codes containing 'print'
        """
    )
    
    parser.add_argument(
        'code_number', 
        nargs='?', 
        type=int, 
        help='Code number to print (1-12)'
    )
    
    parser.add_argument(
        '--all', 
        action='store_true', 
        help='Print all codes'
    )
    
    parser.add_argument(
        '--list', 
        action='store_true', 
        help='List available codes with previews'
    )
    
    parser.add_argument(
        '--search', 
        type=str, 
        help='Search for codes containing a keyword'
    )
    
    parser.add_argument(
        '--version', 
        action='version', 
        version='%(prog)s 1.0.2'
    )
    
    args = parser.parse_args()
    
    printer = CodePrinter()
    
    try:
        if args.all:
            printer.print_all_codes()
        elif args.list:
            printer.list_codes()
        elif args.search:
            printer.search(args.search)
        elif args.code_number:
            if not printer.print(args.code_number):
                sys.exit(1)
        else:
            # Default behavior - show help and list codes
            print("🐍 Code Printer - Your personal code snippet library")
            print()
            printer.list_codes()
            print()
            print("💡 Run 'code-printer --help' for more options")
    
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()