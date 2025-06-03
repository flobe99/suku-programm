from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import cm

class PDF:

    def save_tag_as_table(tag, filename="speiseplan_table.pdf"):

        def draw_header(canvas, doc):
            canvas.saveState()
            canvas.setFont('Helvetica-Bold', 10)
            canvas.drawRightString(A4[0] - 2*cm, A4[1] - 1.5*cm, "Zeltlager 2025")
            canvas.restoreState()

        doc = SimpleDocTemplate(filename, pagesize=A4)
        styles = getSampleStyleSheet()
        elements = []

        elements.append(Paragraph(f"{tag.wochentag} – {tag.datum}", styles['Title']))
        elements.append(Spacer(1, 12))

        for _gericht in tag.gericht:
            header_text = f"<b>{_gericht.mahlzeit}</b> – {_gericht.gerichtname} ({_gericht.uhrzeit})"
            elements.append(Paragraph(header_text, styles['Heading2']))
            elements.append(Spacer(1, 6))

            data = [[
                'Menge',
                'Einheit',
                'Artikelname',
                'Faktor',
                'Kategorie',
                'Lieferant',
                'Sonstiges'
            ]]

            cell_style = ParagraphStyle(name='CellStyle', fontSize=9, leading=11)

            for z in _gericht.zutat:
                data.append([
                    f"{z.menge:.3f}",
                    Paragraph(z.einheit, cell_style),
                    Paragraph(z.artikelname, cell_style),
                    Paragraph(f"{z.faktor:.3f}" if z.faktor is not None else '-', cell_style),
                    Paragraph(z.kategorie or '-', cell_style),
                    Paragraph(z.lieferant, cell_style),
                    Paragraph(z.sonstiges or '-', cell_style)
                ])
            
            col_widths = [1.5*cm, 1.75*cm, 6*cm, 1.5*cm, 2*cm, 2.5*cm, 2.5*cm]
            table = Table(data, colWidths=col_widths, repeatRows=1)
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
            ]))

            elements.append(table)
            elements.append(Spacer(1, 12))

        doc.build(elements, onFirstPage=draw_header, onLaterPages=draw_header)

    def save_zutaten_as_table(laden, filename="speiseplan_table.pdf"):
        def draw_header(canvas, doc):
            canvas.saveState()
            canvas.setFont('Helvetica-Bold', 10)
            canvas.drawRightString(A4[0] - 2*cm, A4[1] - 1.5*cm, "Zeltlager 2025")
            canvas.restoreState()

        doc = SimpleDocTemplate(filename, pagesize=A4)
        styles = getSampleStyleSheet()
        elements = []

        elements.append(Paragraph(f"{laden.Name}", styles['Title']))
        elements.append(Spacer(1, 12))
        
        data = [[
            'Menge',
            'Einheit',
            'Artikelname',
            'Kategorie',
            'Sonstiges',
            'Tage',
            ''
        ]]

        cell_style = ParagraphStyle(name='CellStyle', fontSize=9, leading=11)
        for daten in laden.Zutaten:
            data.append([
                f"{daten["menge"]:.3f}",
                Paragraph(daten["einheit"], cell_style),
                Paragraph(daten["artikelname"], cell_style),
                Paragraph(daten["kategorie"] or '-', cell_style),
                Paragraph(daten["sonstiges"] or '-', cell_style),
                Paragraph(daten["tag"] or '-', cell_style)
            ])
            
        col_widths = [1.5*cm, 1.75*cm, 4*cm, 2.5*cm, 3*cm, 4*cm,1*cm]
        table = Table(data, colWidths=col_widths, repeatRows=1)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
        ]))

        elements.append(table)
        elements.append(Spacer(1, 12))

        doc.build(elements, onFirstPage=draw_header, onLaterPages=draw_header)
