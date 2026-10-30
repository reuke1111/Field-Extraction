"""
Synthetic welfare scheme document generator for Haqdarshak AI/ML hiring assignment.
Generates:
1. Document A: English digital PDF (multi-page)
2. Document B: Hindi digital PDF (Devanagari, multi-page)
3. Document C: Scanned image-based PDF (PIL rendered page images embedded as PDF without text layer)
4. Conflicting catalogue source: JSON listing disagreeing on Document A benefit amount (₹40,000 vs ₹50,000)
5. Ground truth dataset (ground_truth.json) and source metadata (source_metadata.json)

ALL DOCUMENTS ARE EXPLICITLY MARKED AS SYNTHETIC / FICTIONAL FOR EVALUATION PURPOSES ONLY.
"""

import os
import json
from pathlib import Path
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from PIL import Image, ImageDraw, ImageFont

# Base paths
BASE_DIR = Path(__file__).resolve().parent.parent
SAMPLE_DOCS_DIR = BASE_DIR / "sample_documents"
SYNTHETIC_DIR = BASE_DIR / "synthetic_data"

SAMPLE_DOCS_DIR.mkdir(parents=True, exist_ok=True)
SYNTHETIC_DIR.mkdir(parents=True, exist_ok=True)

# Register Devanagari Font if on Windows
FONT_NAME_HINDI = "Helvetica"
windows_nirmala = r"C:\Windows\Fonts\Nirmala.ttc"
if os.path.exists(windows_nirmala):
    try:
        pdfmetrics.registerFont(TTFont("NirmalaDevanagari", windows_nirmala, subfontIndex=0))
        FONT_NAME_HINDI = "NirmalaDevanagari"
    except Exception as e:
        print(f"Warning: Could not register Nirmala font: {e}")


def generate_doc_a_english():
    """
    Document A: English Multi-Page Digital PDF
    Scheme: State Women Entrepreneurship Assistance Scheme
    """
    pdf_path = SAMPLE_DOCS_DIR / "doc_a_english_scheme.pdf"
    doc = SimpleDocTemplate(
        str(pdf_path),
        pagesize=letter,
        rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40
    )
    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=16,
        leading=20,
        textColor=colors.HexColor('#1A365D')
    )
    heading_style = ParagraphStyle(
        'SectionHeading',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=16,
        textColor=colors.HexColor('#2B6CB0'),
        spaceBefore=10,
        spaceAfter=4
    )
    body_style = ParagraphStyle(
        'Body',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=14,
        textColor=colors.HexColor('#2D3748')
    )
    disclaimer_style = ParagraphStyle(
        'Disclaimer',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9,
        leading=12,
        textColor=colors.red
    )

    story = []

    # Page 1
    story.append(Paragraph("[SYNTHETIC / FICTIONAL DOCUMENT FOR TECHNICAL ASSESSMENT ONLY]", disclaimer_style))
    story.append(Spacer(1, 10))
    story.append(Paragraph("GOVERNMENT OF STATE WELFARE ADMINISTRATION", ParagraphStyle('Gov', fontName='Helvetica-Bold', fontSize=10, leading=12, textColor=colors.gray)))
    story.append(Spacer(1, 4))
    story.append(Paragraph("Notification No: SWEAS/2026/EST-402", ParagraphStyle('Ref', fontName='Helvetica', fontSize=9, leading=11)))
    story.append(Spacer(1, 10))
    story.append(Paragraph("STATE WOMEN ENTREPRENEURSHIP ASSISTANCE SCHEME (SWEAS)", title_style))
    story.append(Spacer(1, 10))

    story.append(Paragraph("1. Administrative Department", heading_style))
    story.append(Paragraph("This scheme is administered under the Department of Women Development and Social Welfare.", body_style))
    story.append(Spacer(1, 8))

    story.append(Paragraph("2. Financial Benefits and Assistance", heading_style))
    story.append(Paragraph("Under the State Women Entrepreneurship Assistance Scheme, approved beneficiaries will receive a one-time financial benefit of ₹50,000 directly credited via Direct Benefit Transfer (DBT) to support micro-enterprise capitalization and raw material procurement.", body_style))
    story.append(Spacer(1, 8))

    story.append(Paragraph("3. Target Beneficiaries & Eligibility Criteria", heading_style))
    story.append(Paragraph("The scheme is dedicated to eligible women entrepreneurs. To qualify, an applicant must satisfy all of the following conditions:", body_style))
    story.append(Paragraph("• The applicant must be a female individual aged between 21 and 55 years at the date of application.", body_style))
    story.append(Paragraph("• The applicant must be a bonafide resident of the state for a minimum period of 3 years.", body_style))
    story.append(Paragraph("• Total annual family household income must not exceed ₹3,00,000.", body_style))
    story.append(Paragraph("• The applicant must possess an active single-holder bank account seeded with Aadhaar.", body_style))
    story.append(Spacer(1, 15))

    # Page Break to Page 2
    story.append(PageBreak())

    # Page 2
    story.append(Paragraph("[SYNTHETIC / FICTIONAL DOCUMENT - PAGE 2 OF 2]", disclaimer_style))
    story.append(Spacer(1, 10))

    story.append(Paragraph("4. Mandatory Required Documents", heading_style))
    story.append(Paragraph("Applicants must upload self-attested digital copies of the following documents during submission:", body_style))
    story.append(Paragraph("1. Valid Aadhaar Card for proof of identity and biometric verification.", body_style))
    story.append(Paragraph("2. Proof of Residence (Domicile certificate or voter identity card confirming 3 years state residency).", body_style))
    story.append(Paragraph("3. Udyam Registration Certificate for the micro-business enterprise.", body_style))
    story.append(Paragraph("4. Bank Passbook copy or cancelled cheque showing account number and IFSC code.", body_style))
    story.append(Spacer(1, 10))

    story.append(Paragraph("5. Application Procedure", heading_style))
    story.append(Paragraph("Eligible applicants must submit applications online via the official state welfare citizen service portal. Applicants must authenticate using Aadhaar OTP, complete the prescribed entrepreneurship profile form, attach the mandatory documents, and submit the application electronically. No physical paper submissions will be accepted at district offices.", body_style))
    story.append(Spacer(1, 10))

    story.append(Paragraph("6. Application Deadline", heading_style))
    story.append(Paragraph("The deadline for receipt of applications for the current fiscal cycle is 2026-12-31 at 23:59 hours IST. Applications received after this date will not be entertained.", body_style))
    story.append(Spacer(1, 10))

    story.append(Paragraph("7. Official Portal & Reference Link", heading_style))
    story.append(Paragraph("The official portal link for electronic registration is: https://example-state-portal.gov.invalid/schemes/women-entrepreneurship", body_style))

    doc.build(story)
    print(f"Generated Document A: {pdf_path}")
    return str(pdf_path)


def generate_doc_b_hindi():
    """
    Document B: Hindi Multi-Page Digital PDF (Devanagari text)
    Scheme: मुख्यमंत्री ग्रामीण हस्तशिल्प प्रोत्साहन योजना
    """
    pdf_path = SAMPLE_DOCS_DIR / "doc_b_hindi_scheme.pdf"
    doc = SimpleDocTemplate(
        str(pdf_path),
        pagesize=letter,
        rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40
    )
    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        'DocTitleHindi',
        parent=styles['Heading1'],
        fontName=FONT_NAME_HINDI,
        fontSize=15,
        leading=20,
        textColor=colors.HexColor('#7B341E')
    )
    heading_style = ParagraphStyle(
        'SectionHeadingHindi',
        parent=styles['Heading2'],
        fontName=FONT_NAME_HINDI,
        fontSize=12,
        leading=16,
        textColor=colors.HexColor('#9C4221'),
        spaceBefore=10,
        spaceAfter=4
    )
    body_style = ParagraphStyle(
        'BodyHindi',
        parent=styles['Normal'],
        fontName=FONT_NAME_HINDI,
        fontSize=10,
        leading=15,
        textColor=colors.HexColor('#2D3748')
    )
    disclaimer_style = ParagraphStyle(
        'DisclaimerHindi',
        parent=styles['Normal'],
        fontName=FONT_NAME_HINDI,
        fontSize=9,
        leading=12,
        textColor=colors.red
    )

    story = []

    # Page 1
    story.append(Paragraph("[काल्पनिक एवं मूल्यांकन हेतु निर्मित दस्तावेज - SYNTHETIC / FICTIONAL ONLY]", disclaimer_style))
    story.append(Spacer(1, 10))
    story.append(Paragraph("राज्य शासन - ग्रामोद्योग निदेशालय", heading_style))
    story.append(Paragraph("अधिसूचना क्रमांक: हस्तशिल्प/2026/891", body_style))
    story.append(Spacer(1, 10))
    story.append(Paragraph("मुख्यमंत्री ग्रामीण हस्तशिल्प प्रोत्साहन योजना", title_style))
    story.append(Spacer(1, 10))

    story.append(Paragraph("1. संबंधित विभाग (Department)", heading_style))
    story.append(Paragraph("यह योजना राज्य के कुटीर एवं ग्रामोद्योग विभाग द्वारा संचालित की जा रही है।", body_style))
    story.append(Spacer(1, 8))

    story.append(Paragraph("2. योजना के लाभ (Benefits)", heading_style))
    story.append(Paragraph("इस योजना के तहत पात्र कारीगरों को टूलकिट एवं कार्यशील पूंजी हेतु ₹25,000 की एकमुश्त वित्तीय अनुदान सहायता बैंक खाते में प्रदान की जाएगी।", body_style))
    story.append(Spacer(1, 8))

    story.append(Paragraph("3. पात्रता शर्तें (Eligibility Criteria)", heading_style))
    story.append(Paragraph("योजना का लाभ प्राप्त करने हेतु निम्नलिखित पात्रता अनिवार्य है:", body_style))
    story.append(Paragraph("• आवेदक राज्य का मूल निवासी होना चाहिए।", body_style))
    story.append(Paragraph("• आवेदक की आयु 18 वर्ष से 60 वर्ष के मध्य होनी चाहिए।", body_style))
    story.append(Paragraph("• आवेदक पारंपरिक ग्रामीण हस्तशिल्प अथवा कुटीर उद्योग से जुड़ा सक्रिय कारीगर होना चाहिए।", body_style))
    story.append(Spacer(1, 15))

    # Page Break to Page 2
    story.append(PageBreak())

    # Page 2
    story.append(Paragraph("[काल्पनिक दस्तावेज - पृष्ठ 2]", disclaimer_style))
    story.append(Spacer(1, 10))

    story.append(Paragraph("4. आवश्यक दस्तावेज (Required Documents)", heading_style))
    story.append(Paragraph("आवेदन के साथ निम्नलिखित प्रमाण पत्र संलग्न करना आवश्यक है:", body_style))
    story.append(Paragraph("1. आधार कार्ड की छायाप्रति।", body_style))
    story.append(Paragraph("2. राज्य का निवास प्रमाण पत्र।", body_style))
    story.append(Paragraph("3. राष्ट्रीयकृत बैंक की पासबुक अथवा निरस्त चेक।", body_style))
    story.append(Paragraph("4. हस्तशिल्पी अथवा कारीगर पहचान पत्र (पहचान कार्ड)।", body_style))
    story.append(Spacer(1, 10))

    story.append(Paragraph("5. आवेदन प्रक्रिया (Application Procedure)", heading_style))
    story.append(Paragraph("इच्छुक लाभार्थी निकटतम ग्राम पंचायत कार्यालय अथवा जिला उद्योग केंद्र (DIC) में निर्धारित प्रारूप में भौतिक आवेदन पत्र जमा कर सकते हैं अथवा विभागीय ऑनलाइन पोर्टल के माध्यम से ई-मित्र केंद्र पर आवेदन कर सकते हैं।", body_style))
    story.append(Spacer(1, 10))

    story.append(Paragraph("6. आवेदन की अंतिम तिथि (Deadline)", heading_style))
    story.append(Paragraph("योजना में पंजीकरण करने की अंतिम तिथि 31 मार्च 2027 निर्धारित की गई है।", body_style))
    story.append(Spacer(1, 10))

    story.append(Paragraph("7. आधिकारिक वेबसाइट लिंक (Official Link)", heading_style))
    story.append(Paragraph("विभागीय आधिकारिक सूचना एवं पोर्टल लिंक: https://example-state-gramudyog.gov.invalid/schemes/rural-handicraft", body_style))

    doc.build(story)
    print(f"Generated Document B: {pdf_path}")
    return str(pdf_path)


def generate_doc_c_scanned():
    """
    Document C: Scanned/Image-based Agriculture Support Scheme PDF.
    This PDF contains pure page images (no digital text layer) to genuinely exercise OCR.
    Scheme: Krishi Protsahan & Seed Support Initiative
    """
    pdf_path = SAMPLE_DOCS_DIR / "doc_c_scanned_scheme.pdf"
    
    # Create high-resolution page images using PIL
    width, height = 1600, 2200
    img = Image.new("RGB", (width, height), color=(250, 250, 248))
    draw = ImageDraw.Draw(img)

    # Use standard default font or basic true-type font
    try:
        font_title = ImageFont.truetype(r"C:\Windows\Fonts\arialbd.ttf", 44)
        font_head = ImageFont.truetype(r"C:\Windows\Fonts\arialbd.ttf", 32)
        font_body = ImageFont.truetype(r"C:\Windows\Fonts\arial.ttf", 26)
        font_disclaimer = ImageFont.truetype(r"C:\Windows\Fonts\arialbd.ttf", 24)
    except Exception:
        font_title = ImageFont.load_default()
        font_head = ImageFont.load_default()
        font_body = ImageFont.load_default()
        font_disclaimer = ImageFont.load_default()

    y = 60
    # Disclaimer
    draw.text((80, y), "[SYNTHETIC / SCANNED FICTIONAL DOCUMENT FOR OCR PIPELINE TEST ONLY]", fill=(180, 20, 20), font=font_disclaimer)
    y += 50
    draw.line([(80, y), (1520, y)], fill=(150, 150, 150), width=2)
    y += 30

    # Header
    draw.text((80, y), "STATE DEPARTMENT OF AGRICULTURE & FARMER EMPOWERMENT", fill=(40, 70, 40), font=font_head)
    y += 50
    draw.text((80, y), "Circular Ref: AGRI-SEED/2026/CIRC-108", fill=(80, 80, 80), font=font_body)
    y += 50
    draw.text((80, y), "KRISHI PROTSAHAN & HIGH-YIELD SEED SUPPORT INITIATIVE", fill=(20, 40, 20), font=font_title)
    y += 70

    sections = [
        ("1. Administering Department:", "This agricultural intervention is administered directly by the Department of Agriculture and Farmer Empowerment."),
        ("2. Scheme Financial Benefits:", "Eligible small and marginal farmers shall receive an annual financial assistance of Rs 12,000 for purchasing certified high-yield seeds and bio-fertilizers."),
        ("3. Eligibility Criteria:", "Applicants must be resident farmers owning cultivable agricultural land of less than 2 hectares. The farmer must possess an active Kisan Credit Card and bank account seeded with Aadhaar."),
        ("4. Required Documents:", "Required documentation includes Land Record Patta / RoR certificate, Aadhaar Card copy, Bank Passbook, and self-declaration of small-holder farming status."),
        ("5. Application Procedure:", "Applications must be submitted in physical form at the local Block Agriculture Office or via the Common Service Centre (CSC) farmer window."),
        ("6. Submission Deadline:", "The strict deadline for submitting applications for the Kharif cycle is 2026-11-30."),
        ("7. Official Information Link:", "Information bulletin link: https://example-state-agri.gov.invalid/initiatives/krishi-seed-support")
    ]

    for title, desc in sections:
        draw.text((80, y), title, fill=(20, 60, 20), font=font_head)
        y += 42
        
        # Simple word wrap for description
        words = desc.split()
        line = ""
        for w in words:
            test_line = f"{line} {w}".strip()
            if len(test_line) > 76:
                draw.text((100, y), line, fill=(30, 30, 30), font=font_body)
                y += 36
                line = w
            else:
                line = test_line
        if line:
            draw.text((100, y), line, fill=(30, 30, 30), font=font_body)
            y += 46
        y += 15

    # Simulate realistic scanner noise/grain
    draw.line([(80, y), (1520, y)], fill=(200, 200, 200), width=1)
    y += 20
    draw.text((80, y), "OFFICIAL GOVERNMENT GAZETTE - SCANNED COPY - DISTRICT ARCHIVES", fill=(120, 120, 120), font=font_disclaimer)

    # Save as pure image PDF (no selectable text layer)
    img.save(str(pdf_path), "PDF", resolution=150.0)
    print(f"Generated Document C (Scanned): {pdf_path}")
    return str(pdf_path)


def generate_catalogue_conflict():
    """
    Conflicting catalogue source: Synthetic MyScheme-style listing for Document A.
    Intentionally disagrees on the benefit amount:
    Government PDF: ₹50,000
    Synthetic Catalogue Listing: ₹40,000
    """
    catalogue_path = SAMPLE_DOCS_DIR / "doc_a_catalogue_listing.json"
    data = {
        "source_metadata": {
            "source_id": "CAT-001",
            "source_name": "Synthetic Welfare Scheme Catalogue Listing",
            "source_type": "catalogue_listing",
            "source_url": "https://example-catalogue.invalid/schemes/state-women-entrepreneurship",
            "captured_at": "2026-10-15",
            "is_synthetic": True,
            "disclaimer": "SYNTHETIC / FICTIONAL CATALOGUE LISTING FOR CONFLICT DETECTION TESTING"
        },
        "scheme_ref": "SCHEME-001",
        "scheme_name": "State Women Entrepreneurship Assistance Scheme",
        "department": "Department of Women Development and Social Welfare",
        "benefit_amount": "40000",
        "benefit_type": "financial",
        "benefit_frequency": "one-time",
        "benefit_currency": "INR",
        "evidence_quote": "Beneficiaries under this listing are eligible for a one-time grant assistance of Rs 40,000 for seed venture setup.",
        "section": "Benefits",
        "eligibility_conditions": "Women entrepreneurs aged 21-55 years with annual family income below Rs 3,00,000.",
        "required_documents": "Aadhaar Card, Residence proof, Bank account details, Udyam registration certificate.",
        "application_procedure": "Apply online through the State Citizen Portal.",
        "deadline": "2026-12-31",
        "official_link": "https://example-state-portal.gov.invalid/schemes/women-entrepreneurship"
    }

    with open(catalogue_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"Generated Conflicting Catalogue Source: {catalogue_path}")
    return str(catalogue_path)


def generate_ground_truth():
    """
    Generates manually verified ground-truth records for all synthetic test documents.
    """
    ground_truth = {
        "metadata": {
            "description": "Ground truth annotations for Haqdarshak AI Scheme Extraction evaluation.",
            "version": "1.0.0",
            "created_at": "2026-10-30",
            "eval_cases": ["DOC-001", "DOC-002", "DOC-003", "CAT-001"]
        },
        "schemes": {
            "SCHEME-001": {
                "scheme_ref": "SCHEME-001",
                "source_id": "DOC-001",
                "document_filename": "doc_a_english_scheme.pdf",
                "language": "en",
                "document_type": "digital_pdf",
                "expected_fields": {
                    "scheme_name": {
                        "value": "State Women Entrepreneurship Assistance Scheme",
                        "status": "found",
                        "page": 1,
                        "section": "Title",
                        "evidence": "STATE WOMEN ENTREPRENEURSHIP ASSISTANCE SCHEME (SWEAS)"
                    },
                    "department": {
                        "value": "Department of Women Development and Social Welfare",
                        "status": "found",
                        "page": 1,
                        "section": "1. Administrative Department",
                        "evidence": "This scheme is administered under the Department of Women Development and Social Welfare."
                    },
                    "benefits": {
                        "value": "50000",
                        "status": "found",
                        "page": 1,
                        "section": "2. Financial Benefits and Assistance",
                        "evidence": "approved beneficiaries will receive a one-time financial benefit of ₹50,000 directly credited via Direct Benefit Transfer (DBT)",
                        "structured": {
                            "benefit_type": "financial",
                            "amount": "50000",
                            "currency": "INR",
                            "frequency": "one-time",
                            "conditions": "to support micro-enterprise capitalization and raw material procurement"
                        }
                    },
                    "eligibility_conditions": {
                        "value": "Female individual aged 21-55, state resident for 3 years, annual family income <= ₹3,00,000",
                        "status": "found",
                        "page": 1,
                        "section": "3. Target Beneficiaries & Eligibility Criteria",
                        "evidence": "female individual aged between 21 and 55 years at the date of application"
                    },
                    "required_documents": {
                        "value": "Aadhaar Card, Proof of Residence, Udyam Registration Certificate, Bank Passbook copy",
                        "status": "found",
                        "page": 2,
                        "section": "4. Mandatory Required Documents",
                        "evidence": "Valid Aadhaar Card for proof of identity and biometric verification"
                    },
                    "application_procedure": {
                        "value": "Submit application online via official state welfare citizen service portal with Aadhaar OTP authentication",
                        "status": "found",
                        "page": 2,
                        "section": "5. Application Procedure",
                        "evidence": "Eligible applicants must submit applications online via the official state welfare citizen service portal."
                    },
                    "deadline": {
                        "value": "2026-12-31",
                        "status": "found",
                        "page": 2,
                        "section": "6. Application Deadline",
                        "evidence": "The deadline for receipt of applications for the current fiscal cycle is 2026-12-31 at 23:59 hours IST."
                    },
                    "official_link": {
                        "value": "https://example-state-portal.gov.invalid/schemes/women-entrepreneurship",
                        "status": "found",
                        "page": 2,
                        "section": "7. Official Portal & Reference Link",
                        "evidence": "The official portal link for electronic registration is: https://example-state-portal.gov.invalid/schemes/women-entrepreneurship"
                    }
                }
            },
            "SCHEME-002": {
                "scheme_ref": "SCHEME-002",
                "source_id": "DOC-002",
                "document_filename": "doc_b_hindi_scheme.pdf",
                "language": "hi",
                "document_type": "digital_pdf",
                "expected_fields": {
                    "scheme_name": {
                        "value": "मुख्यमंत्री ग्रामीण हस्तशिल्प प्रोत्साहन योजना",
                        "status": "found",
                        "page": 1,
                        "section": "Title",
                        "evidence": "मुख्यमंत्री ग्रामीण हस्तशिल्प प्रोत्साहन योजना"
                    },
                    "department": {
                        "value": "कुटीर एवं ग्रामोद्योग विभाग",
                        "status": "found",
                        "page": 1,
                        "section": "1. संबंधित विभाग",
                        "evidence": "यह योजना राज्य के कुटीर एवं ग्रामोद्योग विभाग द्वारा संचालित की जा रही है।"
                    },
                    "benefits": {
                        "value": "25000",
                        "status": "found",
                        "page": 1,
                        "section": "2. योजना के लाभ",
                        "evidence": "पात्र कारीगरों को टूलकिट एवं कार्यशील पूंजी हेतु ₹25,000 की एकमुश्त वित्तीय अनुदान सहायता बैंक खाते में प्रदान की जाएगी।",
                        "structured": {
                            "benefit_type": "grant",
                            "amount": "25000",
                            "currency": "INR",
                            "frequency": "one-time",
                            "conditions": "टूलकिट एवं कार्यशील पूंजी हेतु"
                        }
                    },
                    "eligibility_conditions": {
                        "value": "राज्य का मूल निवासी, आयु 18 से 60 वर्ष, पारंपरिक ग्रामीण हस्तशिल्प सक्रिय कारीगर",
                        "status": "found",
                        "page": 1,
                        "section": "3. पात्रता शर्तें",
                        "evidence": "आवेदक की आयु 18 वर्ष से 60 वर्ष के मध्य होनी चाहिए।"
                    },
                    "required_documents": {
                        "value": "आधार कार्ड, राज्य निवास प्रमाण पत्र, बैंक पासबुक, हस्तशिल्पी कारीगर पहचान पत्र",
                        "status": "found",
                        "page": 2,
                        "section": "4. आवश्यक दस्तावेज",
                        "evidence": "आधार कार्ड की छायाप्रति।"
                    },
                    "application_procedure": {
                        "value": "ग्राम पंचायत अथवा जिला उद्योग केंद्र (DIC) में भौतिक आवेदन अथवा ऑनलाइन ई-मित्र पोर्टल",
                        "status": "found",
                        "page": 2,
                        "section": "5. आवेदन प्रक्रिया",
                        "evidence": "ग्राम पंचायत कार्यालय अथवा जिला उद्योग केंद्र (DIC) में निर्धारित प्रारूप में भौतिक आवेदन पत्र जमा कर सकते हैं"
                    },
                    "deadline": {
                        "value": "31 मार्च 2027",
                        "status": "found",
                        "page": 2,
                        "section": "6. आवेदन की अंतिम तिथि",
                        "evidence": "योजना में पंजीकरण करने की अंतिम तिथि 31 मार्च 2027 निर्धारित की गई है।"
                    },
                    "official_link": {
                        "value": "https://example-state-gramudyog.gov.invalid/schemes/rural-handicraft",
                        "status": "found",
                        "page": 2,
                        "section": "7. आधिकारिक वेबसाइट लिंक",
                        "evidence": "विभागीय आधिकारिक सूचना एवं पोर्टल लिंक: https://example-state-gramudyog.gov.invalid/schemes/rural-handicraft"
                    }
                }
            },
            "SCHEME-003": {
                "scheme_ref": "SCHEME-003",
                "source_id": "DOC-003",
                "document_filename": "doc_c_scanned_scheme.pdf",
                "language": "en",
                "document_type": "scanned_pdf",
                "expected_fields": {
                    "scheme_name": {
                        "value": "Krishi Protsahan & High-Yield Seed Support Initiative",
                        "status": "found",
                        "page": 1,
                        "section": "Title",
                        "evidence": "KRISHI PROTSAHAN & HIGH-YIELD SEED SUPPORT INITIATIVE"
                    },
                    "department": {
                        "value": "Department of Agriculture & Farmer Empowerment",
                        "status": "found",
                        "page": 1,
                        "section": "1. Administering Department",
                        "evidence": "administered directly by the Department of Agriculture and Farmer Empowerment."
                    },
                    "benefits": {
                        "value": "12000",
                        "status": "found",
                        "page": 1,
                        "section": "2. Scheme Financial Benefits",
                        "evidence": "annual financial assistance of Rs 12,000 for purchasing certified high-yield seeds and bio-fertilizers",
                        "structured": {
                            "benefit_type": "subsidy",
                            "amount": "12000",
                            "currency": "INR",
                            "frequency": "annual",
                            "conditions": "purchasing certified high-yield seeds and bio-fertilizers"
                        }
                    },
                    "eligibility_conditions": {
                        "value": "Resident farmer owning < 2 hectares agricultural land, Kisan Credit Card and bank account seeded with Aadhaar",
                        "status": "found",
                        "page": 1,
                        "section": "3. Eligibility Criteria",
                        "evidence": "owning cultivable agricultural land of less than 2 hectares."
                    },
                    "required_documents": {
                        "value": "Land Record Patta / RoR certificate, Aadhaar Card copy, Bank Passbook, self-declaration",
                        "status": "found",
                        "page": 1,
                        "section": "4. Required Documents",
                        "evidence": "Land Record Patta / RoR certificate, Aadhaar Card copy, Bank Passbook"
                    },
                    "application_procedure": {
                        "value": "Submit physical form at Block Agriculture Office or Common Service Centre (CSC)",
                        "status": "found",
                        "page": 1,
                        "section": "5. Application Procedure",
                        "evidence": "submitted in physical form at the local Block Agriculture Office or via the Common Service Centre"
                    },
                    "deadline": {
                        "value": "2026-11-30",
                        "status": "found",
                        "page": 1,
                        "section": "6. Submission Deadline",
                        "evidence": "strict deadline for submitting applications for the Kharif cycle is 2026-11-30."
                    },
                    "official_link": {
                        "value": "https://example-state-agri.gov.invalid/initiatives/krishi-seed-support",
                        "status": "found",
                        "page": 1,
                        "section": "7. Official Information Link",
                        "evidence": "https://example-state-agri.gov.invalid/initiatives/krishi-seed-support"
                    }
                }
            }
        },
        "conflicts": [
            {
                "conflict_id": "CONF-001",
                "scheme_ref": "SCHEME-001",
                "field": "benefits",
                "source_1": {
                    "source_id": "DOC-001",
                    "source_name": "doc_a_english_scheme.pdf",
                    "source_type": "government_pdf",
                    "captured_at": "2026-10-30",
                    "value": "50000",
                    "evidence_text": "approved beneficiaries will receive a one-time financial benefit of ₹50,000 directly credited via Direct Benefit Transfer (DBT)",
                    "page": 1
                },
                "source_2": {
                    "source_id": "CAT-001",
                    "source_name": "doc_a_catalogue_listing.json",
                    "source_type": "catalogue_listing",
                    "captured_at": "2026-10-15",
                    "value": "40000",
                    "evidence_text": "Beneficiaries under this listing are eligible for a one-time grant assistance of Rs 40,000 for seed venture setup.",
                    "page": 1
                },
                "expected_resolution": "unresolved_until_human_review"
            }
        ]
    }

    gt_path = SYNTHETIC_DIR / "ground_truth.json"
    with open(gt_path, "w", encoding="utf-8") as f:
        json.dump(ground_truth, f, indent=2, ensure_ascii=False)
    print(f"Generated Ground Truth Dataset: {gt_path}")
    return str(gt_path)


def generate_source_metadata():
    """
    Metadata for initial synthetic dataset ingestion.
    """
    metadata = {
        "DOC-001": {
            "source_id": "DOC-001",
            "filename": "doc_a_english_scheme.pdf",
            "source_type": "government_pdf",
            "scheme_ref": "SCHEME-001",
            "captured_at": "2026-10-30",
            "expected_language": "en"
        },
        "DOC-002": {
            "source_id": "DOC-002",
            "filename": "doc_b_hindi_scheme.pdf",
            "source_type": "government_pdf",
            "scheme_ref": "SCHEME-002",
            "captured_at": "2026-10-30",
            "expected_language": "hi"
        },
        "DOC-003": {
            "source_id": "DOC-003",
            "filename": "doc_c_scanned_scheme.pdf",
            "source_type": "government_pdf",
            "scheme_ref": "SCHEME-003",
            "captured_at": "2026-10-30",
            "expected_language": "en"
        },
        "CAT-001": {
            "source_id": "CAT-001",
            "filename": "doc_a_catalogue_listing.json",
            "source_type": "catalogue_listing",
            "scheme_ref": "SCHEME-001",
            "captured_at": "2026-10-15",
            "expected_language": "en"
        }
    }
    meta_path = SYNTHETIC_DIR / "source_metadata.json"
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)
    print(f"Generated Source Metadata: {meta_path}")
    return str(meta_path)


def generate_all():
    print("Generating all synthetic documents and datasets...")
    generate_doc_a_english()
    generate_doc_b_hindi()
    generate_doc_c_scanned()
    generate_catalogue_conflict()
    generate_ground_truth()
    generate_source_metadata()
    print("All synthetic documents successfully created.")

if __name__ == "__main__":
    generate_all()
