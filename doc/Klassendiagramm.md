 ```mermaid
 classDiagram
    Tag --> Gericht
    Laden --> Zutat
    Gericht --> Zutat
    Zutat --> Lieferant
    Zutat --> Kategorie
    Zutat --> Einheit

    class Excel{
        +String dateiname
        +File read_file()
        +Page read_page()
        +Tag read_tag()
        +Gericht read_gericht()
        +Zutat read_zutat()
    }

    class Tag{
        +String Datum
        +String Wochentag
        +Gericht[] Gericht
    }

    class Gericht{
        +String Mahlzeit
        +String Uhrzeit
        +Zutat[] Zutat
    }

    class Laden{
        +String name
        +Zutat[] zutat
    }

    class Zutat{
        +Lieferant Lieferant
        +Kategorie Kategorie
        +Int Menge
        +Einheit Einheit
        +String Artikelname
        +double Faktor
    }

    class Lieferant{
        <<enumeration>>
        Becka Beck
        Schmutz
        Jermi
        Reichardt
        Netto
        Aldi
        Metro
        Bauer Barth
        Sonstiges
        NONE
    }

    class Kategorie{
        <<enumeration>>
        Gemüse-Obst
        Tiefkühl
        Teigwaren
        Kühlware
        Sonstiges
        Konserven
        Gewürze
    }

    class Einheit{
        <<enumeration>>
        kg
        Bund
        Zehen
        Packung
        Portionen
        Stk
        Liter
    }
 ```

