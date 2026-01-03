from io import BytesIO
from datetime import datetime
from typing import Dict
import os

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle


def _now_str() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def build_mini_statement_pdf(
    bank_name: str,
    customer: Dict,
    transactions_df,
    logo_path: str | None = None,
) -> bytes:
    """
    Returns PDF as bytes (ready for Streamlit download_button).
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=1.5 * cm,
        rightMargin=1.5 * cm,
        topMargin=1.2 * cm,
        bottomMargin=1.2 * cm,
        title=f"{bank_name} - Mini Statement",
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "TitleStyle",
        parent=styles["Title"],
        fontSize=18,
        leading=22,
        textColor=colors.HexColor("#123C7A"),
        spaceAfter=10,
    )
    subtitle_style = ParagraphStyle(
        "SubtitleStyle",
        parent=styles["Normal"],
        fontSize=10,
        textColor=colors.HexColor("#444444"),
        spaceAfter=6,
    )
    label_style = ParagraphStyle(
        "LabelStyle",
        parent=styles["Normal"],
        fontSize=10,
        textColor=colors.HexColor("#222222"),
        leading=14,
    )

    story = []

    # Header: logo + bank name
    header_table_data = []
    logo_elem = ""
    if logo_path and os.path.exists(logo_path):
        try:
            logo_elem = Image(logo_path, width=3.2 * cm, height=1.2 * cm)
        except Exception:
            logo_elem = ""

    header_table_data.append([logo_elem, Paragraph(bank_name, title_style)])
    header_tbl = Table(header_table_data, colWidths=[3.6 * cm, 13.6 * cm])
    header_tbl.setStyle(
        TableStyle(
            [
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("ALIGN", (0, 0), (0, 0), "LEFT"),
                ("ALIGN", (1, 0), (1, 0), "LEFT"),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ]
        )
    )
    story.append(header_tbl)
    story.append(Paragraph(f"Mini Statement • Generated at: {_now_str()}", subtitle_style))
    story.append(Spacer(1, 10))

    # Customer details block
    cust_name = customer.get("full_name", "NA")
    cust_id = customer.get("customer_id", "NA")
    acc_no = customer.get("account_no", "NA")
    acc_type = customer.get("account_type", "NA")
    phone = customer.get("phone", "NA")
    email = customer.get("email", "NA")
    balance = customer.get("current_balance", 0.0)

    info_left = [
        f"<b>Customer Name:</b> {cust_name}",
        f"<b>Customer ID:</b> {cust_id}",
        f"<b>Account No:</b> {acc_no}",
        f"<b>Account Type:</b> {acc_type}",
    ]
    info_right = [
        f"<b>Phone:</b> {phone}",
        f"<b>Email:</b> {email}",
        f"<b>Current Balance:</b> INR {float(balance):,.2f}",
        f"<b>Status:</b> {customer.get('account_status', 'NA')}",
    ]

    info_tbl = Table(
        [
            [Paragraph("<br/>".join(info_left), label_style),
             Paragraph("<br/>".join(info_right), label_style)]
        ],
        colWidths=[8.6 * cm, 8.6 * cm],
    )
    info_tbl.setStyle(
        TableStyle(
            [
                ("BOX", (0, 0), (-1, -1), 0.8, colors.HexColor("#D0D7E2")),
                ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F6F8FB")),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 10),
                ("RIGHTPADDING", (0, 0), (-1, -1), 10),
                ("TOPPADDING", (0, 0), (-1, -1), 8),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
            ]
        )
    )
    story.append(info_tbl)
    story.append(Spacer(1, 12))

    # Transactions table
    story.append(Paragraph("<b>Recent Transactions</b>", styles["Heading3"]))
    story.append(Spacer(1, 6))

    if transactions_df is None or transactions_df.empty:
        story.append(Paragraph("No transactions found.", styles["Normal"]))
    else:
        df = transactions_df.copy()

        # Keep columns in professional order
        cols = ["txn_ts", "txn_id", "txn_type", "amount", "balance_after", "status", "remarks"]
        available = [c for c in cols if c in df.columns]

        # Format numeric columns
        if "amount" in df.columns:
            df["amount"] = df["amount"].apply(lambda x: f"INR {float(x):,.2f}" if str(x).strip() != "" else "")
        if "balance_after" in df.columns:
            df["balance_after"] = df["balance_after"].apply(lambda x: f"INR {float(x):,.2f}" if str(x).strip() != "" else "")

        table_data = [ [c.replace("_", " ").upper() for c in available] ]
        for _, row in df[available].iterrows():
            table_data.append([str(row[c]) if row[c] is not None else "" for c in available])

        txn_tbl = Table(table_data, repeatRows=1, colWidths=[3.2*cm, 2.3*cm, 2.5*cm, 3.0*cm, 3.2*cm, 2.2*cm, 4.0*cm])
        txn_tbl.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#123C7A")),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("FONTSIZE", (0, 0), (-1, 0), 9),

                    ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#D0D7E2")),
                    ("FONTSIZE", (0, 1), (-1, -1), 8),
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F6F8FB")]),
                    ("LEFTPADDING", (0, 0), (-1, -1), 6),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                    ("TOPPADDING", (0, 0), (-1, -1), 4),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                ]
            )
        )
        story.append(txn_tbl)

    story.append(Spacer(1, 14))
    story.append(Paragraph("This is a system-generated statement for reference only.", subtitle_style))
    story.append(Paragraph(f"© {datetime.now().year} {bank_name}", subtitle_style))

    doc.build(story)
    pdf_bytes = buffer.getvalue()
    buffer.close()
    return pdf_bytes
