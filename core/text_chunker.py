"""
Page-aware text chunking module.
Ensures page references are strictly preserved and section headers are retained.
"""

from typing import List, Dict, Any

class DocumentChunk:
    def __init__(self, chunk_id: str, text: str, page_number: int, section: str = ""):
        self.chunk_id = chunk_id
        self.text = text
        self.page_number = page_number
        self.section = section

    def to_dict(self) -> Dict[str, Any]:
        return {
            "chunk_id": self.chunk_id,
            "text": self.text,
            "page_number": self.page_number,
            "section": self.section
        }

class PageAwareChunker:
    def __init__(self, max_chunk_chars: int = 1500, overlap_chars: int = 150):
        self.max_chunk_chars = max_chunk_chars
        self.overlap_chars = overlap_chars

    def chunk_document_pages(self, pages: List[Dict[str, Any]]) -> List[DocumentChunk]:
        """
        Chunks text on a per-page basis so page boundaries and evidence citations
        are never confused or cross-pollinated across different pages.
        """
        chunks = []
        chunk_idx = 0

        for page in pages:
            page_num = page["page_number"]
            page_text = page["text"].strip()
            if not page_text:
                continue

            # If page text fits easily within chunk limit, preserve as single coherent page chunk
            if len(page_text) <= self.max_chunk_chars:
                chunk_idx += 1
                chunks.append(DocumentChunk(
                    chunk_id=f"CHK-{chunk_idx:03d}",
                    text=page_text,
                    page_number=page_num,
                    section=f"Page {page_num}"
                ))
            else:
                # Split along paragraph or double newline boundaries
                paragraphs = page_text.split("\n\n")
                current_buffer = ""
                for p in paragraphs:
                    if len(current_buffer) + len(p) <= self.max_chunk_chars:
                        current_buffer += ("\n\n" + p if current_buffer else p)
                    else:
                        if current_buffer:
                            chunk_idx += 1
                            chunks.append(DocumentChunk(
                                chunk_id=f"CHK-{chunk_idx:03d}",
                                text=current_buffer.strip(),
                                page_number=page_num,
                                section=f"Page {page_num}"
                            ))
                        current_buffer = p

                if current_buffer:
                    chunk_idx += 1
                    chunks.append(DocumentChunk(
                        chunk_id=f"CHK-{chunk_idx:03d}",
                        text=current_buffer.strip(),
                        page_number=page_num,
                        section=f"Page {page_num}"
                    ))

        return chunks
