from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
import io
from reportlab.lib.pagesizes import landscape

def generate_passbook_pdf(user, transactions):
    from utils import mask_aadhar
    styles = getSampleStyleSheet()
    elements = []

    # Title with logo and PASS BOOK text
    logo_path = "static/image/Code_yatra_bank_logo.png"
    try:
        logo = Image(logo_path, width=60, height=60)
    except:
        logo = Paragraph("LOGO", styles['Normal'])

    title_style = ParagraphStyle(
        'title_style',
        parent=styles['Title'],
        alignment=TA_CENTER,
        fontSize=24,
        spaceAfter=6,
    )
    passbook_style = ParagraphStyle(
        'passbook_style',
        parent=styles['Normal'],
        alignment=TA_CENTER,
        fontSize=14,
        spaceAfter=12,
        leading=18,
    )

    title_text = Paragraph("CODE YATRA BANK", title_style)
    passbook_text = Paragraph("PASS BOOK", passbook_style)

    title_table = Table([[logo, title_text]], colWidths=[70, 250])
    title_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
    ]))
    elements.append(title_table)
    elements.append(passbook_text)
    elements.append(Spacer(1, 12))

    # Bank info and customer details side by side
    masked_aadhar_val = mask_aadhar(user.aadhar) if user.aadhar else ''

    bank_info_data = [
        ("BRANCH :", "CODE YATRA, INDIA"),
        ("IFSC :", user.ifsc_code),
        ("MICR :", user.micr_code),
        ("CIF No :", user.cif_no),
        ("Contact :", "022-22223333"),
    ]

    bank_info_paragraphs = []
    for label, value in bank_info_data:
        p = Paragraph(f"<b>{label}</b> {value}", ParagraphStyle('bank_info_style', parent=styles['Normal'], alignment=TA_LEFT))
        bank_info_paragraphs.append(p)

    customer_data = [
        ("ACCOUNT HOLDER NAME :", user.name),
        ("CUSTOMER ID :", user.cif_no),
        ("ACCOUNT NUMBER :", user.account_no),
        ("OPENING DATE :", user.created_at.strftime('%d-%m-%Y') if user.created_at else ''),
        ("DATE OF BIRTH :", user.dob.strftime('%d-%m-%Y') if user.dob else ''),
        ("ADDRESS :", user.address),
        ("MOBILE NUMBER :", user.phone),
        ("EMAIL ID :", user.email),
        ("PAN NUMBER :", user.pan),
        ("AADHAAR NUMBER :", masked_aadhar_val),
    ]

    customer_paragraphs = []
    for label, value in customer_data:
        p = Paragraph(f"<b>{label}</b> {value}", ParagraphStyle('customer_info_style', parent=styles['Normal'], alignment=TA_RIGHT))
        customer_paragraphs.append(p)

    # Create a table with two columns: bank info and customer details (stacked paragraphs)
    data = [[bank_info_paragraphs, customer_paragraphs]]
    table = Table(data, colWidths=[280, 280])
    table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
    ]))
    elements.append(table)
    elements.append(Spacer(1, 24))

    # Transactions table
    data = [['Transaction ID', 'Type', 'Sender Account', 'Receiver Account', 'Amount', 'Currency', 'Status', 'Method', 'Balance After', 'Transaction Time']]
    for txn in transactions:
        txn_id = txn.get('transaction_id') or txn.get('txn_id', '')
        txn_type = txn.get('type', '')
        sender = txn.get('sender_account', txn.get('sender_acc', ''))
        receiver = txn.get('receiver_account', txn.get('receiver_acc', ''))
        amount = f"Rs {txn.get('amount', 0):.2f}"
        currency = txn.get('currency', 'INR')
        status = txn.get('status', 'completed')
        method = txn.get('method', 'Transfer')
        balance_after = f"Rs {txn.get('balance_after_transaction', 0):.2f}"
        txn_time = f"{txn.get('transaction_time', {}).get('date', txn.get('date', ''))} {txn.get('transaction_time', {}).get('time', '')}"
        data.append([txn_id, txn_type, sender, receiver, amount, currency, status, method, balance_after, txn_time])

    col_widths = [110, 50, 100, 100, 70, 50, 60, 80, 90, 120]
    table = Table(data, colWidths=col_widths)
    style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ])
    for i in range(1, len(data)):
        if i % 2 == 0:
            style.add('BACKGROUND', (0, i), (-1, i), colors.whitesmoke)
    table.setStyle(style)
    elements.append(table)

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=landscape(letter))
    doc.build(elements)
    buffer.seek(0)
    return buffer
