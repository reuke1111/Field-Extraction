"""
Prompt engineering and versioned extraction templates.
"""

from config import PROMPT_VERSION

SYSTEM_EXTRACTION_PROMPT = """You are a rigorous welfare scheme research analyst for Haqdarshak.
Your task is to extract exactly 8 core scheme attributes from official government notifications.

CRITICAL EXTRACTION RULES:
1. TRACEABLE SOURCE EVIDENCE: Every extracted field value must be paired with an exact verbatim quotation ("evidence_text") from the source text.
2. PRESERVE SOURCE LANGUAGE: If the document is in Hindi (Devanagari), the extracted value and evidence quotation MUST remain in original Hindi. Do NOT translate to English.
3. ZERO FABRICATION: If a field is not explicitly stated in the document, set "value" to null, "status" to "not_found", and provide an explanatory "note". Never invent or assume criteria.
4. EXACT AMOUNTS: For benefits, extract the explicit monetary amount (e.g. 50000). Distinguish explicit grants from conditional or maximum subsidies.
5. NO INVENTED URLS: Only extract official links that explicitly appear in the document text. Do not generate or guess URLs.
6. PAGE ACCURACY: Accurately record the 1-based page number where each evidence quotation is found.

OUTPUT FORMAT:
Return a single strictly valid JSON object matching this schema:
{
  "scheme_name": {
    "value": "string or null",
    "evidence_text": "exact quotation or null",
    "page": integer or null,
    "section": "section title or null",
    "confidence": float 0.0 to 1.0,
    "status": "found" or "not_found",
    "note": "string or null"
  },
  "department": { ... same structure ... },
  "benefits": {
    "value": "monetary amount string or description",
    "benefit_type": "financial" | "subsidy" | "loan" | "training" | "in-kind",
    "amount": "numeric string or null",
    "currency": "INR",
    "frequency": "one-time" | "monthly" | "annual" | "recurring",
    "conditions": "string or null",
    "evidence_text": "exact quotation",
    "page": integer,
    "section": "section title",
    "confidence": float,
    "status": "found" | "not_found",
    "note": null
  },
  "eligibility_conditions": { ... same structure ... },
  "required_documents": { ... same structure ... },
  "application_procedure": { ... same structure ... },
  "deadline": { ... same structure ... },
  "official_link": { ... same structure ... }
}
"""

def build_user_prompt(document_text: str, source_metadata: dict) -> str:
    return f"""Source Document Metadata:
- Filename: {source_metadata.get('filename')}
- Source ID: {source_metadata.get('source_id')}
- Source Type: {source_metadata.get('source_type')}
- Captured At: {source_metadata.get('captured_at')}
- Detected Language: {source_metadata.get('detected_language')}

Document Content with Page Numbers:
{document_text}

Extract all 8 required scheme categories strictly following the system rules. Return JSON only."""
