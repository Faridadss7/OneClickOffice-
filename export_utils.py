# export_utils.py
import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO
from reportlab.platypus import SimpleDocTemplate, Table as PDFTable, TableStyle, Paragraph, Spacer, Image as RLImage
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from PIL import Image
import os

# --- Excel ---
def df_to_excel_bytes(df):
    buf = BytesIO()
    with pd.ExcelWriter(buf, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Feuille1")
    buf.seek(0)
    return buf

# --- Graphique matplotlib -> BytesIO (PNG) ---
def df_to_png_bytes(df, x_col=None, y_col=None, chart_type="Barres", title=None):
    plt.close("all")
    fig, ax = plt.subplots(figsize=(8,4.5))
    title = title or "OneClickOffice Graphique"
    try:
        if chart_type == "Camembert":
            if x_col:
                grouped = df.groupby(x_col)[y_col].sum() if y_col else df.sum(numeric_only=True)
                grouped.plot.pie(autopct="%1.1f%%", startangle=140, ax=ax)
                ax.set_ylabel("")
            else:
                numeric = df.select_dtypes(include="number").columns
                if len(numeric) > 0:
                    df[numeric].iloc[0].plot.pie(autopct="%1.1f%%", startangle=140, ax=ax)
        elif chart_type == "Ligne":
            x = df[x_col] if x_col else df.index.astype(str)
            y = df[y_col] if y_col else df.select_dtypes(include="number").iloc[:,0]
            ax.plot(x, y, marker="o")
            ax.set_xlabel(x_col if x_col else "")
            ax.set_ylabel(y_col if y_col else "")
        else:  # Barres
            if x_col and y_col:
                df.plot.bar(x=x_col, y=y_col, ax=ax)
            else:
                nums = df.select_dtypes(include="number")
                if not nums.empty:
                    nums.sum(axis=1).plot.bar(ax=ax)
        ax.set_title(title)
    except Exception as e:
        ax.text(0.5, 0.5, f"Erreur graphique: {e}", ha="center")
    plt.tight_layout()
    buf = BytesIO()
    fig.savefig(buf, format="png")
    plt.close(fig)
    buf.seek(0)
    return buf

# --- PDF with table + image (both from memory) ---
def df_table_and_chart_to_pdf_bytes(df, png_bytes=None, title="OneClickOffice Rapport"):
    buf = BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4)
    elements = []
    styles = getSampleStyleSheet()
    elements.append(Paragraph(title, styles["Title"]))
    elements.append(Spacer(1, 12))

    # Table data
    data = [list(df.columns)] + df.fillna("").astype(str).values.tolist()
    table = PDFTable(data, hAlign="LEFT")
    table.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#4B8BBE")),
        ("TEXTCOLOR", (0,0), (-1,0), colors.white),
        ("ALIGN", (0,0), (-1,-1), "LEFT"),
        ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
        ("BOTTOMPADDING", (0,0), (-1,0), 8),
        ("GRID", (0,0), (-1,-1), 0.25, colors.black),
    ]))
    elements.append(table)
    elements.append(Spacer(1, 12))

    if png_bytes:
        png_bytes.seek(0)
        elements.append(RLImage(png_bytes, width=420, height=260))
    doc.build(elements)
    buf.seek(0)
    return buf

# --- Flyer generator ---
def generate_flyer_pdf_bytes(text_lines, bg_color="#FFFFFF", text_color="#000000", width=595, height=420, title="OneClickOffice Flyer"):
    buf = BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=(width, height))
    elements = []
    styles = getSampleStyleSheet()
    elements.append(Paragraph(title, styles["Title"]))
    elements.append(Spacer(1,12))
    for line in text_lines:
        elements.append(Paragraph(line, styles["Normal"]))
        elements.append(Spacer(1,6))
    doc.build(elements)
    buf.seek(0)
    return buf