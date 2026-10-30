"""
Deterministic Mock LLM Provider for offline execution and testing.
Returns grounded field records matching source text without requiring API credentials.
Explicitly labels outputs as MOCK and reports cost as unavailable.
"""

import time
import json
from typing import Dict, Any, Tuple
from llm.base import BaseLLMProvider

class MockLLMProvider(BaseLLMProvider):
    def __init__(self, model_name: str = "mock-extraction-model-v1", model_version: str = "1.0.0-offline"):
        self._model_name = model_name
        self._model_version = model_version

    @property
    def provider_name(self) -> str:
        return "mock"

    @property
    def model_name(self) -> str:
        return self._model_name

    @property
    def model_version(self) -> str:
        return self._model_version

    def extract_scheme_fields(
        self,
        document_text: str,
        document_metadata: Dict[str, Any],
        prompt_version: str
    ) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        start_time = time.time()
        filename = document_metadata.get("filename", "").lower()
        source_id = document_metadata.get("source_id", "DOC-UNKNOWN")

        # Determine which scheme is being processed
        if "doc_a" in filename or "women" in document_text.lower():
            extracted = {
                "scheme_name": {
                    "value": "State Women Entrepreneurship Assistance Scheme",
                    "evidence_text": "STATE WOMEN ENTREPRENEURSHIP ASSISTANCE SCHEME (SWEAS)",
                    "page": 1,
                    "section": "Title",
                    "confidence": 0.98,
                    "status": "found",
                    "note": None
                },
                "department": {
                    "value": "Department of Women Development and Social Welfare",
                    "evidence_text": "This scheme is administered under the Department of Women Development and Social Welfare.",
                    "page": 1,
                    "section": "1. Administrative Department",
                    "confidence": 0.96,
                    "status": "found",
                    "note": None
                },
                "benefits": {
                    "value": "50000",
                    "benefit_type": "financial",
                    "amount": "50000",
                    "currency": "INR",
                    "frequency": "one-time",
                    "conditions": "to support micro-enterprise capitalization and raw material procurement",
                    "evidence_text": "approved beneficiaries will receive a one-time financial benefit of ₹50,000 directly credited via Direct Benefit Transfer (DBT)",
                    "page": 1,
                    "section": "2. Financial Benefits and Assistance",
                    "confidence": 0.99,
                    "status": "found",
                    "note": None
                },
                "eligibility_conditions": {
                    "value": "Female individual aged 21-55 years, 3 years state residency, family income <= ₹3,00,000",
                    "evidence_text": "The applicant must be a female individual aged between 21 and 55 years at the date of application.",
                    "page": 1,
                    "section": "3. Target Beneficiaries & Eligibility Criteria",
                    "confidence": 0.95,
                    "status": "found",
                    "note": None
                },
                "required_documents": {
                    "value": "Aadhaar Card, Proof of Residence, Udyam Registration Certificate, Bank Passbook copy",
                    "evidence_text": "Valid Aadhaar Card for proof of identity and biometric verification.",
                    "page": 2,
                    "section": "4. Mandatory Required Documents",
                    "confidence": 0.94,
                    "status": "found",
                    "note": None
                },
                "application_procedure": {
                    "value": "Apply online via official state welfare citizen service portal with Aadhaar OTP authentication",
                    "evidence_text": "Eligible applicants must submit applications online via the official state welfare citizen service portal.",
                    "page": 2,
                    "section": "5. Application Procedure",
                    "confidence": 0.95,
                    "status": "found",
                    "note": None
                },
                "deadline": {
                    "value": "2026-12-31",
                    "evidence_text": "The deadline for receipt of applications for the current fiscal cycle is 2026-12-31 at 23:59 hours IST.",
                    "page": 2,
                    "section": "6. Application Deadline",
                    "confidence": 0.97,
                    "status": "found",
                    "note": None
                },
                "official_link": {
                    "value": "https://example-state-portal.gov.invalid/schemes/women-entrepreneurship",
                    "evidence_text": "The official portal link for electronic registration is: https://example-state-portal.gov.invalid/schemes/women-entrepreneurship",
                    "page": 2,
                    "section": "7. Official Portal & Reference Link",
                    "confidence": 0.99,
                    "status": "found",
                    "note": None
                }
            }
        elif "doc_b" in filename or "हस्तशिल्प" in document_text or "ग्रामोद्योग" in document_text:
            extracted = {
                "scheme_name": {
                    "value": "मुख्यमंत्री ग्रामीण हस्तशिल्प प्रोत्साहन योजना",
                    "evidence_text": "मुख्यमंत्री ग्रामीण हस्तशिल्प प्रोत्साहन योजना",
                    "page": 1,
                    "section": "शीर्षक",
                    "confidence": 0.98,
                    "status": "found",
                    "note": None
                },
                "department": {
                    "value": "कुटीर एवं ग्रामोद्योग विभाग",
                    "evidence_text": "यह योजना राज्य के कुटीर एवं ग्रामोद्योग विभाग द्वारा संचालित की जा रही है।",
                    "page": 1,
                    "section": "1. संबंधित विभाग",
                    "confidence": 0.96,
                    "status": "found",
                    "note": None
                },
                "benefits": {
                    "value": "25000",
                    "benefit_type": "grant",
                    "amount": "25000",
                    "currency": "INR",
                    "frequency": "one-time",
                    "conditions": "टूलकिट एवं कार्यशील पूंजी हेतु",
                    "evidence_text": "पात्र कारीगरों को टूलकिट एवं कार्यशील पूंजी हेतु ₹25,000 की एकमुश्त वित्तीय अनुदान सहायता बैंक खाते में प्रदान की जाएगी।",
                    "page": 1,
                    "section": "2. योजना के लाभ",
                    "confidence": 0.99,
                    "status": "found",
                    "note": None
                },
                "eligibility_conditions": {
                    "value": "राज्य का मूल निवासी, आयु 18 से 60 वर्ष, पारंपरिक ग्रामीण हस्तशिल्प सक्रिय कारीगर",
                    "evidence_text": "आवेदक की आयु 18 वर्ष से 60 वर्ष के मध्य होनी चाहिए।",
                    "page": 1,
                    "section": "3. पात्रता शर्तें",
                    "confidence": 0.95,
                    "status": "found",
                    "note": None
                },
                "required_documents": {
                    "value": "आधार कार्ड, राज्य निवास प्रमाण पत्र, बैंक पासबुक, हस्तशिल्पी कारीगर पहचान पत्र",
                    "evidence_text": "आधार कार्ड की छायाप्रति।",
                    "page": 2,
                    "section": "4. आवश्यक दस्तावेज",
                    "confidence": 0.94,
                    "status": "found",
                    "note": None
                },
                "application_procedure": {
                    "value": "ग्राम पंचायत अथवा जिला उद्योग केंद्र (DIC) में भौतिक आवेदन अथवा विभागीय पोर्टल",
                    "evidence_text": "ग्राम पंचायत कार्यालय अथवा जिला उद्योग केंद्र (DIC) में निर्धारित प्रारूप में भौतिक आवेदन पत्र जमा कर सकते हैं",
                    "page": 2,
                    "section": "5. आवेदन प्रक्रिया",
                    "confidence": 0.95,
                    "status": "found",
                    "note": None
                },
                "deadline": {
                    "value": "31 मार्च 2027",
                    "evidence_text": "योजना में पंजीकरण करने की अंतिम तिथि 31 मार्च 2027 निर्धारित की गई है।",
                    "page": 2,
                    "section": "6. आवेदन की अंतिम तिथि",
                    "confidence": 0.97,
                    "status": "found",
                    "note": None
                },
                "official_link": {
                    "value": "https://example-state-gramudyog.gov.invalid/schemes/rural-handicraft",
                    "evidence_text": "विभागीय आधिकारिक सूचना एवं पोर्टल लिंक: https://example-state-gramudyog.gov.invalid/schemes/rural-handicraft",
                    "page": 2,
                    "section": "7. आधिकारिक वेबसाइट लिंक",
                    "confidence": 0.99,
                    "status": "found",
                    "note": None
                }
            }
        elif "doc_c" in filename or "krishi" in document_text.lower() or "agriculture" in document_text.lower():
            extracted = {
                "scheme_name": {
                    "value": "Krishi Protsahan & High-Yield Seed Support Initiative",
                    "evidence_text": "KRISHI PROTSAHAN & HIGH-YIELD SEED SUPPORT INITIATIVE",
                    "page": 1,
                    "section": "Title",
                    "confidence": 0.96,
                    "status": "found",
                    "note": None
                },
                "department": {
                    "value": "Department of Agriculture & Farmer Empowerment",
                    "evidence_text": "administered directly by the Department of Agriculture and Farmer Empowerment.",
                    "page": 1,
                    "section": "1. Administering Department",
                    "confidence": 0.94,
                    "status": "found",
                    "note": None
                },
                "benefits": {
                    "value": "12000",
                    "benefit_type": "subsidy",
                    "amount": "12000",
                    "currency": "INR",
                    "frequency": "annual",
                    "conditions": "purchasing certified high-yield seeds and bio-fertilizers",
                    "evidence_text": "annual financial assistance of Rs 12,000 for purchasing certified high-yield seeds and bio-fertilizers",
                    "page": 1,
                    "section": "2. Scheme Financial Benefits",
                    "confidence": 0.98,
                    "status": "found",
                    "note": None
                },
                "eligibility_conditions": {
                    "value": "Resident farmer owning < 2 hectares agricultural land, Kisan Credit Card and bank account seeded with Aadhaar",
                    "evidence_text": "owning cultivable agricultural land of less than 2 hectares.",
                    "page": 1,
                    "section": "3. Eligibility Criteria",
                    "confidence": 0.92,
                    "status": "found",
                    "note": None
                },
                "required_documents": {
                    "value": "Land Record Patta / RoR certificate, Aadhaar Card copy, Bank Passbook, self-declaration",
                    "evidence_text": "Land Record Patta / RoR certificate, Aadhaar Card copy, Bank Passbook",
                    "page": 1,
                    "section": "4. Required Documents",
                    "confidence": 0.93,
                    "status": "found",
                    "note": None
                },
                "application_procedure": {
                    "value": "Submit physical form at local Block Agriculture Office or Common Service Centre (CSC)",
                    "evidence_text": "submitted in physical form at the local Block Agriculture Office or via the Common Service Centre",
                    "page": 1,
                    "section": "5. Application Procedure",
                    "confidence": 0.94,
                    "status": "found",
                    "note": None
                },
                "deadline": {
                    "value": "2026-11-30",
                    "evidence_text": "strict deadline for submitting applications for the Kharif cycle is 2026-11-30.",
                    "page": 1,
                    "section": "6. Submission Deadline",
                    "confidence": 0.96,
                    "status": "found",
                    "note": None
                },
                "official_link": {
                    "value": "https://example-state-agri.gov.invalid/initiatives/krishi-seed-support",
                    "evidence_text": "https://example-state-agri.gov.invalid/initiatives/krishi-seed-support",
                    "page": 1,
                    "section": "7. Official Information Link",
                    "confidence": 0.98,
                    "status": "found",
                    "note": None
                }
            }
        else:
            # Generic grounded fallback
            first_line = document_text.split("\n")[0][:100] if document_text else "Unknown Scheme"
            extracted = {
                "scheme_name": {
                    "value": first_line,
                    "evidence_text": first_line,
                    "page": 1,
                    "section": "Header",
                    "confidence": 0.80,
                    "status": "found",
                    "note": None
                },
                "department": {"value": None, "evidence_text": None, "page": None, "section": None, "confidence": 0.0, "status": "not_found", "note": "Department not explicitly mentioned in document."},
                "benefits": {"value": None, "benefit_type": "unknown", "amount": None, "currency": "INR", "frequency": None, "conditions": None, "evidence_text": None, "page": None, "section": None, "confidence": 0.0, "status": "not_found", "note": "No explicit benefits found."},
                "eligibility_conditions": {"value": None, "evidence_text": None, "page": None, "section": None, "confidence": 0.0, "status": "not_found", "note": "No eligibility criteria specified."},
                "required_documents": {"value": None, "evidence_text": None, "page": None, "section": None, "confidence": 0.0, "status": "not_found", "note": "No required documents listed."},
                "application_procedure": {"value": None, "evidence_text": None, "page": None, "section": None, "confidence": 0.0, "status": "not_found", "note": "Application procedure not specified."},
                "deadline": {"value": None, "evidence_text": None, "page": None, "section": None, "confidence": 0.0, "status": "not_found", "note": "No deadline found in document."},
                "official_link": {"value": None, "evidence_text": None, "page": None, "section": None, "confidence": 0.0, "status": "not_found", "note": "No official website link found."}
            }

        latency = time.time() - start_time
        input_token_est = len(document_text) // 4 + 250
        output_token_est = len(json.dumps(extracted)) // 4

        execution_metadata = {
            "input_tokens": input_token_est,
            "output_tokens": output_token_est,
            "total_tokens": input_token_est + output_token_est,
            "latency_seconds": round(latency, 4),
            "estimated_cost_usd": None,
            "cost_status": "unavailable_for_mock",
            "provider": self.provider_name,
            "model_name": self.model_name,
            "model_version": self.model_version
        }

        return extracted, execution_metadata
