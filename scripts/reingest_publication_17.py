#!/usr/bin/env python3
"""
Complete re-ingestion script for Publication 17 (2025).
Uses the SAME HuggingFace embedding model as rag_service.py
"""
import os
import re
import sys
from pathlib import Path
from dotenv import load_dotenv
from supabase import create_client
import fitz  # PyMuPDF
import time
from huggingface_hub import InferenceClient
import requests
from typing import List, Dict, Tuple, Optional

# Load environment
env_path = Path(__file__).parent.parent / '.env.local'
load_dotenv(dotenv_path=env_path)

print("=" * 70)
print("Publication 17 (2025) Re-Ingestion")
print("Chunk → Embed → Upload with Proper Metadata")
print("=" * 70 + "\n")

# Initialize Supabase
print("🔄 Connecting to Supabase...")
supabase = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_KEY")
)
print("✅ Connected\n")

# ─── Configuration ────────────────────────────────────────────────────────────
TAX_YEAR = 2025
CHUNK_SIZE = 1200
CHUNK_OVERLAP = 150
RATE_LIMIT_DELAY = 0.3  # ✅ 0.3s not 60s!
HF_MODEL = "sentence-transformers/all-MiniLM-L6-v2"  # ✅ SAME as rag_service.py
HF_TOKEN = os.getenv("HF_TOKEN")
hf_client = InferenceClient(token=HF_TOKEN)
HF_API_URL = f"https://api-inference.huggingface.co/models/{HF_MODEL}"
# Known chapter titles from Pub 17 (2025) table of contents
# Used to validate detected chapters and reject garbage
# Replace KNOWN_CHAPTERS with this:
CHAPTER_PAGE_RANGES = {
    "1":  {"title": "Filing Information",                     "start": 6,   "end": 20},
    "2":  {"title": "Filing Status",                          "start": 21,  "end": 25},
    "3":  {"title": "Dependents",                             "start": 26,  "end": 36},
    "4":  {"title": "Tax Withholding and Estimated Tax",      "start": 37,  "end": 45},
    "5":  {"title": "Wages, Salaries, and Other Earnings",    "start": 47,  "end": 53},
    "6":  {"title": "Interest Income",                        "start": 54,  "end": 61},
    "7":  {"title": "Social Security and Railroad Benefits",  "start": 62,  "end": 65},
    "8":  {"title": "Other Income",                           "start": 66,  "end": 76},
    "9":  {"title": "Individual Retirement Arrangements",     "start": 77,  "end": 91},
    "10": {"title": "Standard Deduction",                     "start": 92,  "end": 95},
    "11": {"title": "Taxes",                                  "start": 96,  "end": 100},
    "12": {"title": "Other Itemized Deductions",              "start": 101, "end": 105},
    "13": {"title": "How To Figure Your Tax",                 "start": 106, "end": 107},
    "14": {"title": "Child Tax Credit",                       "start": 108, "end": 110},
}

# ──────────────────────────────────────────────────────────────────────────────

def generate_embedding(text: str) -> Optional[List[float]]:
    """Generate embedding using InferenceClient - SAME as hf_embeddings.py"""
    try:
        result = hf_client.feature_extraction(
            text,
            model=HF_MODEL
        )
        # Result is numpy array - convert to list
        import numpy as np
        arr = np.array(result)
        
        # Mean pool if token-level embeddings returned
        if arr.ndim == 2:
            arr = arr.mean(axis=0)
        
        return arr.tolist()
    
    except Exception as e:
        print(f"   ❌ Embedding failed: {e}")
        return None


def extract_chapter_info(text: str) -> Tuple[Optional[str], Optional[str]]:
    """
    Only check the TOP of the page for chapter headers.
    Cross-references appear mid-page, real headers appear at the top.
    """
    # ✅ Only look at first 300 chars of page (where real headers live)
    page_top = text[:300]

    pattern = r'(?:^|\n)\s*Chapter\s+(\d+)\s*[\.\:\-]?\s*([A-Za-z][A-Za-z\s\&\,\-]{3,50}?)(?:\n|\.|\s{2,}|$)'

    for match in re.finditer(pattern, page_top, re.IGNORECASE | re.MULTILINE):
        chapter_num = match.group(1).strip()

        if chapter_num in KNOWN_CHAPTERS:
            return chapter_num, KNOWN_CHAPTERS[chapter_num]

    return None, None



def extract_tables_from_page(page) -> List[str]:
    """Extract tables from page and format as readable text"""
    tables = []
    try:
        tabs = page.find_tables()
        if tabs and len(tabs.tables) > 0:
            for table in tabs.tables:
                table_data = table.extract()
                table_text = "\n\n[TABLE]\n"
                for row in table_data:
                    if row:
                        cells = [str(cell).strip() for cell in row if cell]
                        if cells:
                            table_text += " | ".join(cells) + "\n"
                table_text += "[/TABLE]\n"
                tables.append(table_text)
    except Exception as e:
        print(f"   ⚠️ Table extraction failed: {e}")
    return tables


def chunk_text(text: str, chunk_size: int = 1200, overlap: int = 150) -> List[str]:
    """Split text into overlapping chunks at sentence boundaries"""
    chunks = []
    start = 0
    text_length = len(text)

    while start < text_length:
        end = min(start + chunk_size, text_length)

        if end < text_length:
            search_start = max(start, end - 150)
            for delimiter in ['. ', '.\n', '! ', '!\n', '? ', '?\n']:
                sentence_end = text.rfind(delimiter, search_start, end)
                if sentence_end > start:
                    end = sentence_end + len(delimiter)
                    break

        chunk = text[start:end].strip()
        if chunk and len(chunk) > 50:
            chunks.append(chunk)

        start = end - overlap if end < text_length else text_length

    return chunks


def save_chapter_chunks(
    chapter_num: str,
    chapter_title: str,
    chapter_text: str,
    dry_run: bool = False
) -> int:
    """Chunk chapter text, generate embeddings, and save to database."""

    chapter_text = re.sub(r'\s+', ' ', chapter_text).strip()
    chunks = chunk_text(chapter_text, CHUNK_SIZE, CHUNK_OVERLAP)

    print(f"   📝 Split into {len(chunks)} chunks")

    if dry_run:
        print(f"   🔍 DRY RUN - Would save {len(chunks)} chunks")
        return len(chunks)

    saved_count = 0

    for i, chunk_content in enumerate(chunks, 1):
        # Build clean title
        title = f"Publication 17 ({TAX_YEAR}) - Chapter {chapter_num}: {chapter_title}"
        if len(chunks) > 1:
            title += f" (Part {i}/{len(chunks)})"

        # Generate embedding with SAME model as RAG service
        print(f"   🔄 Chunk {i}/{len(chunks)}: Embedding...", end='', flush=True)
        embedding_vector = generate_embedding(chunk_content)

        if not embedding_vector:
            print(" ❌ SKIPPED")
            continue

        print(f" ✅ ({len(embedding_vector)} dims)")

        # Build metadata
        metadata = {
            'tax_years': [TAX_YEAR],
            'is_current': True,
            'chapter': f"Chapter {chapter_num}",
            'chapter_number': int(chapter_num),
            'chapter_title': chapter_title,
            'source': f'Publication 17 ({TAX_YEAR})',
            'document_type': 'IRS Publication',
            'chunk_index': i - 1,   # 0-indexed
            'total_chunks': len(chunks),
            'primary_tax_year': TAX_YEAR
        }

        # Insert into database
        try:
            supabase.table('knowledge_documents').insert({
                'title': title,
                'content': chunk_content,
                'metadata': metadata,
                'content_embedding': embedding_vector  # ✅ Correct column name
            }).execute()

            saved_count += 1

        except Exception as e:
            print(f"   ❌ Failed to save chunk {i}: {e}")

        time.sleep(RATE_LIMIT_DELAY)  # ✅ 0.3s not 60s

    return saved_count


def find_page_offset(doc) -> int:
    """
    Detect offset between PDF page numbers (0-indexed) and
    printed page numbers shown in the document.
    Scans first 15 pages looking for printed page number "6"
    which is where Chapter 1 starts per TOC.
    """
    for i in range(min(15, len(doc))):
        text = doc[i].get_text()
        # Page 6 of pub 17 contains "Filing Information" and "6"
        if "Filing Information" in text and "What's New" in text:
            offset = i - 5  # printed page 6 = index i, so offset = i - (6-1)
            print(f"   Found Chapter 1 at PDF index {i}, offset = {offset}")
            return offset
    print("   ⚠️ Could not detect offset, assuming 0")
    return 0


def ingest_publication_17(pdf_path: str, dry_run: bool = False) -> Dict[str, int]:
    """Page-range based ingestion using TOC page numbers directly"""

    if not os.path.exists(pdf_path):
        print(f"❌ PDF not found: {pdf_path}")
        sys.exit(1)

    print(f"📄 Opening PDF: {pdf_path}\n")
    doc = fitz.open(pdf_path)

    # Detect offset between printed page numbers and PDF 0-index
    print("🔍 Detecting page offset...")
    offset = find_page_offset(doc)

    stats = {
        'total_pages': len(doc),
        'chapters_found': 0,
        'total_chunks': 0
    }

    for chapter_num, info in CHAPTER_PAGE_RANGES.items():
        title = info['title']

        # Convert printed page numbers → 0-indexed PDF pages
        start_idx = info['start'] - 1 + offset
        end_idx   = info['end']   - 1 + offset

        # Clamp to doc bounds
        start_idx = max(0, min(start_idx, len(doc) - 1))
        end_idx   = max(0, min(end_idx,   len(doc) - 1))

        print(f"📖 Chapter {chapter_num}: {title}")
        print(f"   Pages {info['start']}-{info['end']} → PDF index {start_idx}-{end_idx}")

        # Extract all text + tables for this chapter
        chapter_text = ""
        for page_idx in range(start_idx, end_idx + 1):
            page = doc[page_idx]
            chapter_text += page.get_text() + "\n"

            tables = extract_tables_from_page(page)
            for table in tables:
                chapter_text += table

        if not chapter_text.strip():
            print(f"   ⚠️ No text found, skipping\n")
            continue

        print(f"   📄 Extracted {len(chapter_text)} chars")

        # Save chunks
        chunks_saved = save_chapter_chunks(
            chapter_num,
            title,
            chapter_text,
            dry_run
        )
        stats['total_chunks'] += chunks_saved
        stats['chapters_found'] += 1
        print(f"✅ Saved {chunks_saved} chunks\n")

    doc.close()
    return stats



def main():
    import argparse

    parser = argparse.ArgumentParser(description="Re-ingest IRS Publication 17 (2025)")
    parser.add_argument('--pdf', required=True, help='Path to Publication 17 PDF')
    parser.add_argument('--dry-run', action='store_true', help='Test without saving')
    parser.add_argument('--skip-delete', action='store_true', help='Skip deleting old chunks')

    args = parser.parse_args()

    print("📋 Configuration:")
    print(f"   PDF: {args.pdf}")
    print(f"   Tax Year: {TAX_YEAR}")
    print(f"   Chunk Size: {CHUNK_SIZE} chars")
    print(f"   Embedding: HuggingFace {HF_MODEL} (384 dims)")
    print(f"   DB Column: content_embedding")
    print(f"   Dry Run: {args.dry_run}")
    print()

    if not args.dry_run:
        response = input("⚠️  Delete existing Pub 17 chunks and re-ingest? (yes/no): ")
        if response.strip().lower() != 'yes':
            print("❌ Cancelled")
            return

        if not args.skip_delete:
            print("\n🗑️  Deleting existing Publication 17 chunks...")
            supabase.table('knowledge_documents').delete()\
                .or_('title.ilike.%p17%,title.ilike.%Publication 17 (2025)%')\
                .execute()
            print("✅ Deleted old chunks\n")

    print("=" * 70)
    print("Starting Ingestion")
    print("=" * 70 + "\n")

    stats = ingest_publication_17(args.pdf, args.dry_run)

    print("\n" + "=" * 70)
    print("📊 Results:")
    print(f"   Pages: {stats['total_pages']}")
    print(f"   Chapters: {stats['chapters_found']}")
    print(f"   Chunks: {stats['total_chunks']}")
    print("=" * 70)

    if not args.dry_run:
        print("\n✅ Done! Test with: 'What is the standard deduction for this year?'")


if __name__ == "__main__":
    main()
