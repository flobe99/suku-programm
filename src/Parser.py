import argparse
import os
from config import workbooks_default, laden_default, lieferanten_default

class Parser:
    def argument():
        base_dir = os.path.dirname(os.path.abspath(__file__))

        parser = argparse.ArgumentParser(description="Zeltlager")
        parser.add_argument("-m", "--mode", help="Selected Mode", choices=["calculation", "einkaufsliste", "lieferantenliste"], default="calculation")
        parser.add_argument("-f", "--filename", help="Input Excel File", default="EssensplanCalc2025_test.xlsx")
        parser.add_argument("-fbp", "--file-base-path", help="File Base Path", default="C:/Users/betz_f/Downloads")
        parser.add_argument("-o", "--output", help="Target folder")
        parser.add_argument(
            "-w", "--workbooks",
            help="Excel workbooks",
            default= workbooks_default)
        parser.add_argument(
            "-l", "--laden",
            help="Einkaufsladen liste",
            default= laden_default)
        parser.add_argument(
            "-li", "--lieferanten",
            help="Lieferanten liste",
            default= lieferanten_default)
        
        args = parser.parse_args()
        
        if not args.output:
            if args.mode == "calculation":
                args.output = os.path.join(base_dir, "..", "_dist", "Calculation")
            elif args.mode == "einkaufsliste":
                args.output = os.path.join(base_dir, "..", "_dist", "Einkaufsliste")
            elif args.mode == "lieferantenliste":
                args.output = os.path.join(base_dir, "..", "_dist", "Lieferantenliste")

        return args
