#!/usr/bin/env python3
"""
Generate PDF documentation from DOCUMENTATION.md
Uses reportlab for PDF generation.
"""
import re
from pathlib import Path

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor, black, white
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, 
    Preformatted
)
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY


def create_styles():
    """Create custom styles for the PDF."""
    styles = getSampleStyleSheet()
    
    # All custom names to avoid conflicts
    styles.add(ParagraphStyle(
        name='DocTitle_Custom',
        parent=styles['Title'],
        fontSize=28,
        textColor=HexColor('#00d4ff'),
        spaceAfter=30,
        alignment=TA_CENTER,
    ))
    
    styles.add(ParagraphStyle(
        name='H1_Custom',
        parent=styles['Heading1'],
        fontSize=20,
        textColor=HexColor('#0a0e17'),
        spaceBefore=25,
        spaceAfter=12,
    ))
    
    styles.add(ParagraphStyle(
        name='H2_Custom',
        parent=styles['Heading2'],
        fontSize=15,
        textColor=HexColor('#141b2d'),
        spaceBefore=18,
        spaceAfter=8,
    ))
    
    styles.add(ParagraphStyle(
        name='H3_Custom',
        parent=styles['Heading3'],
        fontSize=12,
        textColor=HexColor('#1e2738'),
        spaceBefore=12,
        spaceAfter=6,
    ))
    
    styles.add(ParagraphStyle(
        name='Body_Custom',
        parent=styles['Normal'],
        fontSize=10,
        leading=14,
        spaceAfter=6,
        alignment=TA_JUSTIFY,
    ))
    
    styles.add(ParagraphStyle(
        name='Code_Custom',
        fontName='Courier',
        fontSize=8,
        leading=10,
        leftIndent=10,
        rightIndent=10,
        spaceAfter=8,
        backColor=HexColor('#f5f5f5'),
    ))
    
    styles.add(ParagraphStyle(
        name='Bullet_Custom',
        parent=styles['Normal'],
        fontSize=10,
        leftIndent=20,
        spaceAfter=3,
    ))
    
    styles.add(ParagraphStyle(
        name='TableHeader_Custom',
        parent=styles['Normal'],
        fontSize=9,
        textColor=white,
        alignment=TA_CENTER,
    ))
    
    styles.add(ParagraphStyle(
        name='TableCell_Custom',
        parent=styles['Normal'],
        fontSize=9,
        leading=11,
    ))
    
    return styles


def clean_text(text):
    """Clean markdown formatting from text."""
    # First escape all special HTML characters
    text = text.replace('&', '&amp;')
    text = text.replace('<', '&lt;')
    text = text.replace('>', '&gt;')
    
    # Now apply markdown formatting with ReportLab-safe tags
    # Bold
    text = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', text)
    text = re.sub(r'__(.+?)__', r'<b>\1</b>', text)
    
    # Italic
    text = re.sub(r'\*(.+?)\*', r'<i>\1</i>', text)
    text = re.sub(r'_(.+?)_', r'<i>\1</i>', text)
    
    # Inline code - use simple font tag
    text = re.sub(r'`(.+?)`', r'<font face="Courier">\1</font>', text)
    
    # Links - just show the text
    text = re.sub(r'\[(.+?)\]\(.+?\)', r'\1', text)
    
    return text


def create_table(rows, styles):
    """Create a table from rows."""
    if not rows:
        return Spacer(1, 0)
    
    data = []
    for i, row in enumerate(rows):
        if i == 0:
            data.append([Paragraph(clean_text(cell), styles['TableHeader_Custom']) for cell in row])
        else:
            data.append([Paragraph(clean_text(cell), styles['TableCell_Custom']) for cell in row])
    
    num_cols = len(rows[0])
    col_width = (6.5 * inch) / num_cols
    
    table = Table(data, colWidths=[col_width] * num_cols)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), HexColor('#0a0e17')),
        ('TEXTCOLOR', (0, 0), (-1, 0), white),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 9),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
        ('TOPPADDING', (0, 0), (-1, 0), 6),
        ('BACKGROUND', (0, 1), (-1, -1), HexColor('#f8f9fa')),
        ('TEXTCOLOR', (0, 1), (-1, -1), black),
        ('GRID', (0, 0), (-1, -1), 0.5, HexColor('#dddddd')),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING', (0, 0), (-1, -1), 4),
        ('RIGHTPADDING', (0, 0), (-1, -1), 4),
        ('TOPPADDING', (0, 1), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 4),
    ]))
    
    return table


def parse_markdown(md_content, styles):
    """Parse markdown and convert to ReportLab elements."""
    elements = []
    lines = md_content.split('\n')
    
    i = 0
    in_code = False
    code_lines = []
    in_table = False
    table_rows = []
    
    while i < len(lines):
        line = lines[i]
        
        # Code blocks
        if line.strip().startswith('```'):
            if in_code:
                if code_lines:
                    code_text = '\n'.join(code_lines)
                    elements.append(Preformatted(code_text, styles['Code_Custom']))
                code_lines = []
                in_code = False
            else:
                in_code = True
            i += 1
            continue
        
        if in_code:
            code_lines.append(line)
            i += 1
            continue
        
        # Tables
        if '|' in line and line.strip().startswith('|'):
            if not in_table:
                in_table = True
                table_rows = []
            cells = [c.strip() for c in line.split('|')[1:-1]]
            # Skip separator rows
            if cells and not all(set(c) <= set('-: ') for c in cells):
                table_rows.append(cells)
            i += 1
            continue
        elif in_table:
            if table_rows:
                elements.append(create_table(table_rows, styles))
            in_table = False
            table_rows = []
        
        # Empty lines
        if not line.strip():
            i += 1
            continue
        
        # Horizontal rules
        if line.strip() in ['---', '***', '___']:
            elements.append(Spacer(1, 8))
            i += 1
            continue
        
        # Headers
        if line.startswith('# '):
            text = clean_text(line[2:])
            if 'Flight Kiosk System' in text:
                elements.append(Paragraph(text, styles['DocTitle_Custom']))
            else:
                elements.append(Paragraph(text, styles['H1_Custom']))
            i += 1
            continue
        
        if line.startswith('## '):
            elements.append(Paragraph(clean_text(line[3:]), styles['H2_Custom']))
            i += 1
            continue
        
        if line.startswith('### '):
            elements.append(Paragraph(clean_text(line[4:]), styles['H3_Custom']))
            i += 1
            continue
        
        # Blockquotes
        if line.startswith('> '):
            elements.append(Paragraph(f"<i>{clean_text(line[2:])}</i>", styles['Body_Custom']))
            i += 1
            continue
        
        # Bullet points
        if line.strip().startswith('- ') or line.strip().startswith('* '):
            text = clean_text(line.strip()[2:])
            elements.append(Paragraph(f"* {text}", styles['Bullet_Custom']))
            i += 1
            continue
        
        # Checkboxes
        if '- [ ]' in line or '- [x]' in line or '- [/]' in line:
            mark = '[x]' if '[x]' in line else ('[/]' if '[/]' in line else '[ ]')
            text = line.split(mark, 1)[-1].strip()
            sym = 'X' if mark == '[x]' else ('/' if mark == '[/]' else 'O')
            elements.append(Paragraph(f"[{sym}] {clean_text(text)}", styles['Bullet_Custom']))
            i += 1
            continue
        
        # Numbered lists
        if re.match(r'^\d+\. ', line.strip()):
            num = re.match(r'^(\d+)\.', line.strip()).group(1)
            text = re.sub(r'^\d+\. ', '', line.strip())
            elements.append(Paragraph(f"{num}. {clean_text(text)}", styles['Bullet_Custom']))
            i += 1
            continue
        
        # Regular paragraph
        text = clean_text(line)
        if text.strip():
            elements.append(Paragraph(text, styles['Body_Custom']))
        
        i += 1
    
    return elements


def generate_pdf(md_path, pdf_path):
    """Generate PDF from markdown file."""
    print(f"Reading: {md_path}")
    
    with open(md_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    print("Creating PDF...")
    
    doc = SimpleDocTemplate(
        str(pdf_path),
        pagesize=A4,
        rightMargin=0.7*inch,
        leftMargin=0.7*inch,
        topMargin=0.7*inch,
        bottomMargin=0.7*inch,
    )
    
    styles = create_styles()
    elements = parse_markdown(content, styles)
    
    print(f"Building PDF with {len(elements)} elements...")
    doc.build(elements)
    
    print(f"Done! PDF saved to: {pdf_path}")


if __name__ == "__main__":
    base = Path(__file__).parent
    md = base / "DOCUMENTATION.md"
    pdf = base / "DOCUMENTATION.pdf"
    
    if not md.exists():
        print(f"Error: {md} not found!")
        exit(1)
    
    generate_pdf(md, pdf)
