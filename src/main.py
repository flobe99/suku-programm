from Calculation import Calculation
from Einkaufsliste import Einkaufsliste
from Parser import Parser

if __name__ == "__main__":

    args = Parser.argument()

    if args.mode == "calculation":
        _calc = Calculation()
        _calc.run(
            file_base_path=args.file_base_path,
            filename=args.filename,
            workbooks=args.workbooks,
            output=args.output
            )

    elif args.mode == "einkaufsliste":
        _einkaufsliste = Einkaufsliste()
        _einkaufsliste.run(
            file_base_path=args.file_base_path,
            filename=args.filename,
            workbooks=args.workbooks,
            output=args.output,
            läden=args.laden
            )

    elif args.mode == "lieferantenliste":
        _einkaufsliste = Einkaufsliste()
        _einkaufsliste.run(
            file_base_path=args.file_base_path,
            filename=args.filename,
            workbooks=args.workbooks,
            output=args.output,
            läden=args.lieferanten
            )

    else:
        print("Unbekannter Modus:", args.mode)

