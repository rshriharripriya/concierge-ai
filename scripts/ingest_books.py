#!/usr/bin/env python3
"""
Enhanced document ingestion script with automatic chunking for books and long documents.

Features:
- Automatic chunking with configurable size and overlap
- Preserves paragraph boundaries
- Metadata preservation (title, source, category, chapter)
- Deduplication based on content hash
- Progress tracking
- Support for plain text, markdown, and structured formats

Usage:
    python scripts/ingest_books.py
    python scripts/ingest_books.py --chunk-size 700 --overlap 150
    python scripts/ingest_books.py --file knowledge_data/books/tax_guide.txt
"""

import os
import sys
import hashlib
import argparse
import re
from typing import List, Dict, Tuple
from dotenv import load_dotenv
from supabase import create_client
from langchain_huggingface import HuggingFaceEndpointEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

# PDF support
try:
    from pypdf import PdfReader
    PDF_SUPPORT = True
except ImportError:
    print("⚠️  Warning: pypdf not installed. PDF support disabled.")
    print("   Install with: pip install pypdf")
    PDF_SUPPORT = False

# Load environment variables
load_dotenv(dotenv_path=".env.local")

# Initialize Supabase
supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_KEY")
hf_token = os.getenv("HF_TOKEN")

if not all([supabase_url, supabase_key, hf_token]):
    print("❌ Error: Missing required environment variables")
    print("   Required: SUPABASE_URL, SUPABASE_KEY, HF_TOKEN")
    sys.exit(1)

supabase = create_client(supabase_url, supabase_key)

# Initialize Embedding Model
print("🔄 Loading embedding model...")
embeddings = HuggingFaceEndpointEmbeddings(
    huggingfacehub_api_token=hf_token,
    model="sentence-transformers/all-MiniLM-L6-v2"
)
print("✅ Embedding model loaded")


def create_text_splitter(chunk_size: int = 700, chunk_overlap: int = 150):
    """
    Create a text splitter optimized for semantic chunking.
    
    Args:
        chunk_size: Target size in tokens (approx 4 chars = 1 token)
        chunk_overlap: Overlap between chunks to preserve context
    
    Returns:
        RecursiveCharacterTextSplitter instance
    """
    # Convert tokens to characters (rough approximation: 1 token ≈ 4 chars)
    char_chunk_size = chunk_size * 4
    char_overlap = chunk_overlap * 4
    
    return RecursiveCharacterTextSplitter(
        chunk_size=char_chunk_size,
        chunk_overlap=char_overlap,
        length_function=len,
        separators=[
            "\n\n===",  # Custom document separator
            "\n\n##",  # Markdown headers
            "\n\n#",   # More headers
            "\n\n",    # Paragraph breaks
            "\n",      # Line breaks
            ". ",      # Sentences
            " ",       # Words
            ""         # Characters
        ],
        is_separator_regex=False,
    )


def extract_text_from_pdf(pdf_path: str) -> str:
    """Extract text from PDF file."""
    if not PDF_SUPPORT:
        raise ImportError("pypdf not installed. Run: pip install pypdf")
    
    try:
        reader = PdfReader(pdf_path)
        text_parts = []
        
        print(f"   📄 Extracting text from {len(reader.pages)} pages...")
        
        for page_num, page in enumerate(reader.pages, 1):
            text = page.extract_text()
            if text.strip():
                text_parts.append(text)
        
        full_text = '\n\n'.join(text_parts)
        print(f"   ✅ Extracted {len(full_text)} characters")
        
        return full_text
    
    except Exception as e:
        print(f"   ❌ Error extracting PDF: {e}")
        raise


def format_filename(filename: str) -> Tuple[str, str]:
    """
    Format messy PDF/book filenames into clean title and author.
    
    Example:
        _OceanofPDF.com_The_Personal_Finance_101_Boxed_Set_-_Michele_Cagan.pdf
        -> ("The Personal Finance 101 Boxed Set", "Michele Cagan")
    
    Args:
        filename: Raw filename
    
    Returns:
        (title, author) tuple
    """
    # Remove file extension
    name = filename
    for ext in ['.pdf', '.txt', '.md', '.epub']:
        name = name.replace(ext, '')
    
    # Remove common prefixes (OceanofPDF, etc.)
    prefixes = ['_OceanofPDF.com_', 'OceanofPDF.com_', '_', '.']
    for prefix in prefixes:
        if name.startswith(prefix):
            name = name[len(prefix):]
    
    # Split by common author separators
    author = None
    if ' - ' in name:
        parts = name.split(' - ')
        if len(parts) == 2:
            name, author = parts
    elif ' by ' in name.lower():
        parts = re.split(r' by ', name, flags=re.IGNORECASE)
        if len(parts) == 2:
            name, author = parts
    
    # Clean up title: replace underscores with spaces, title case
    title = name.replace('_', ' ').strip()
    title = ' '.join(word.capitalize() for word in title.split())
    
    # Clean up author if found
    if author:
        author = author.replace('_', ' ').strip()
        author = ' '.join(word.capitalize() for word in author.split())
    
    return title, author


def detect_chapters(content: str) -> List[Tuple[str, str]]:
    """
    Detect chapter boundaries in book content.
    
    Looks for patterns like:
    - "Chapter 1", "CHAPTER 1:", "Chapter One"
    - "1. Introduction"
    - Numbered sections
    
    Args:
        content: Book text content
    
    Returns:
        List of (chapter_title, chapter_content) tuples
    """
    # Regex patterns for chapter detection
    patterns = [
        r'^Chapter \d+[:.\-]?.*$',  # Chapter 1: Title or Chapter 1. Title
        r'^CHAPTER \d+[:.\-]?.*$',  # CHAPTER 1: TITLE
        r'^\d+\. [A-Z].*$',          # 1. INTRODUCTION
        r'^Part \d+[:.\-]?.*$',      # Part 1: Title
    ]
    
    combined_pattern = '|'.join(f'({p})' for p in patterns)
    
    # Split content by lines
    lines = content.split('\n')
    
    chapters = []
    current_chapter_title = None
    current_chapter_content = []
    
    for line in lines:
        # Check if line is a chapter heading
        if re.match(combined_pattern, line.strip(), re.MULTILINE):
            # Save previous chapter if exists
            if current_chapter_title and current_chapter_content:
                chapters.append((
                    current_chapter_title,
                    '\n'.join(current_chapter_content).strip()
                ))
            
            # Start new chapter
            current_chapter_title = line.strip()
            current_chapter_content = []
        else:
            current_chapter_content.append(line)
    
    # Add last chapter
    if current_chapter_title and current_chapter_content:
        chapters.append((
            current_chapter_title,
            '\n'.join(current_chapter_content).strip()
        ))
    
    # If no chapters detected, return entire content as single chapter
    if not chapters:
        return [('Complete Text', content)]
    
    return chapters


def extract_metadata_from_content(content: str) -> Dict[str, str]:
    """
    Extract metadata from structured content (TITLE:, SOURCE:, CATEGORY: lines).
    
    Args:
        content: Text content with potential metadata lines
    
    Returns:
        Dictionary of metadata and cleaned content
    """
    metadata = {}
    lines = content.split('\n')
    content_lines = []
    
    for line in lines:
        if line.startswith('TITLE:'):
            metadata['title'] = line.replace('TITLE:', '').strip()
        elif line.startswith('SOURCE:'):
            metadata['source'] = line.replace('SOURCE:', '').strip()
        elif line.startswith('CATEGORY:'):
            metadata['category'] = line.replace('CATEGORY:', '').strip()
        else:
            content_lines.append(line)
    
    cleaned_content = '\n'.join(content_lines).strip()
    
    # Generate title from first line if not found
    if 'title' not in metadata and content_lines:
        first_line = content_lines[0].strip()
        # Remove === markers
        first_line = first_line.replace('===', '').strip()
        metadata['title'] = first_line[:100]  # Limit to 100 chars
    
    return metadata, cleaned_content


def compute_hash(text: str) -> str:
    """Compute SHA256 hash of text for deduplication."""
    return hashlib.sha256(text.encode('utf-8')).hexdigest()


def check_duplicate(content_hash: str) -> bool:
    """Check if document with this hash already exists in database."""
    try:
        result = supabase.table('knowledge_documents')\
            .select('id')\
            .eq('metadata->>content_hash', content_hash)\
            .execute()
        return len(result.data) > 0
    except Exception as e:
        print(f"⚠️  Error checking duplicate: {e}")
        return False


def ingest_document(
    content: str,
    metadata: Dict[str, str],
    chunk_index: int,
    total_chunks: int,
    text_splitter
) -> int:
    """
    Ingest a single document chunk into the database.
    
    Returns:
        1 if successful, 0 if failed or duplicate
    """
    try:
        # Compute hash for deduplication
        content_hash = compute_hash(content)
        
        # Check for duplicate
        if check_duplicate(content_hash):
            print(f"   ⏭  Chunk {chunk_index}/{total_chunks} - Duplicate, skipping")
            return 0
        
        # Generate embedding
        embedding = embeddings.embed_query(content)
        
        # Prepare database payload
        full_metadata = {
            **metadata,
            'content_hash': content_hash,
            'chunk_index': chunk_index,
            'total_chunks': total_chunks,
            'chunk_size': len(content)
        }
        
        # Create title with chunk info if multiple chunks
        title = metadata.get('title', 'Unknown')
        if total_chunks > 1:
            display_title = f"{title} (Part {chunk_index}/{total_chunks})"
        else:
            display_title = title
        
        data = {
            "content": content,
            "title": display_title,
            "source": metadata.get('source', 'manual_ingest'),
            "category": metadata.get('category'),
            "metadata": full_metadata,
            "content_embedding": embedding
        }
        
        # Insert into database
        supabase.table('knowledge_documents').insert(data).execute()
        
        # Show preview
        preview = content[:100].replace('\n', ' ')
        print(f"   ✅ Chunk {chunk_index}/{total_chunks} - {len(content)} chars - {preview}...")
        
        return 1
        
    except Exception as e:
        print(f"   ❌ Chunk {chunk_index}/{total_chunks} failed: {e}")
        return 0


def process_file(
    file_path: str,
    text_splitter,
    default_metadata: Dict[str, str] = None,
    chunk_by_chapter: bool = True
) -> int:
    """
    Process a single file: read, chunk, and ingest.
    
    Returns:
        Number of chunks successfully ingested
    """
    print(f"\n📖 Processing: {file_path}")
    
    if not os.path.exists(file_path):
        print(f"   ❌ File not found: {file_path}")
        return 0
    
    # Read file based on type
    try:
        if file_path.endswith('.pdf'):
            if not PDF_SUPPORT:
                print(f"   ❌ PDF support not available. Install pypdf: pip install pypdf")
                return 0
            raw_content = extract_text_from_pdf(file_path)
        else:
            # Text files
            with open(file_path, 'r', encoding='utf-8') as f:
                raw_content = f.read()
    except Exception as e:
        print(f"   ❌ Error reading file: {e}")
        return 0
    
    # Check if file uses structured format (=== DOCUMENT markers)
    if '=== DOCUMENT' in raw_content:
        return process_structured_file(raw_content, file_path, text_splitter, default_metadata)
    else:
        return process_plain_file(raw_content, file_path, text_splitter, default_metadata, chunk_by_chapter)


def process_structured_file(
    content: str,
    file_path: str,
    text_splitter,
    default_metadata: Dict[str, str] = None
) -> int:
    """Process file with === DOCUMENT === markers (current format)."""
    sections = content.split('=== DOCUMENT')
    total_inserted = 0
    
    print(f"   Found {len(sections)-1} sections in structured format")
    
    for i, section in enumerate(sections):
        if not section.strip():
            continue
        
        # Extract metadata
        metadata, cleaned_content = extract_metadata_from_content(section)
        
        # Merge with defaults
        if default_metadata:
            metadata = {**default_metadata, **metadata}
        
        # Add file source
        metadata['source_file'] = os.path.basename(file_path)
        
        # Chunk the section
        chunks = text_splitter.split_text(cleaned_content)
        
        print(f"\n   📄 Section {i}: {metadata.get('title', 'Unknown')} ({len(chunks)} chunks)")
        
        # Ingest each chunk
        for j, chunk in enumerate(chunks, 1):
            total_inserted += ingest_document(
                content=chunk,
                metadata=metadata,
                chunk_index=j,
                total_chunks=len(chunks),
                text_splitter=text_splitter
            )
    
    return total_inserted


def process_plain_file(
    content: str,
    file_path: str,
    text_splitter,
    default_metadata: Dict[str, str] = None,
    chunk_by_chapter: bool = True
) -> int:
    """Process plain text file (book, article, etc.)."""
    filename = os.path.basename(file_path)
    
    # Format filename nicely
    title, author = format_filename(filename)
    
    # Create formatted source string
    if author:
        formatted_source = f"{title} by {author}"
    else:
        formatted_source = title
    
    print(f"   📚 Book: {formatted_source}")
    
    # Try to detect chapters
    chapters = detect_chapters(content) if chunk_by_chapter else []
    
    if len(chapters) > 1:
        print(f"   📖 Detected {len(chapters)} chapters - chunking by chapter")
        return process_by_chapters(
            chapters=chapters,
            file_path=file_path,
            book_title=title,
            author=author,
            formatted_source=formatted_source,
            text_splitter=text_splitter,
            default_metadata=default_metadata
        )
    else:
        print(f"   Processing as single document (auto-chunking)")
        
        # Base metadata
        metadata = {
            'title': title,
            'source': formatted_source,
            'source_file': filename,
            'book_name': title,
            **(default_metadata or {})
        }
        
        if author:
            metadata['author'] = author
        
        # Chunk the entire content
        chunks = text_splitter.split_text(content)
        
        print(f"   Created {len(chunks)} chunks")
        
        total_inserted = 0
        for i, chunk in enumerate(chunks, 1):
            total_inserted += ingest_document(
                content=chunk,
                metadata=metadata,
                chunk_index=i,
                total_chunks=len(chunks),
                text_splitter=text_splitter
            )
        
        return total_inserted


def process_by_chapters(
    chapters: List[Tuple[str, str]],
    file_path: str,
    book_title: str,
    author: str,
    formatted_source: str,
    text_splitter,
    default_metadata: Dict[str, str] = None
) -> int:
    """Process book by chapters for better semantic organization."""
    filename = os.path.basename(file_path)
    total_inserted = 0
    
    for chapter_num, (chapter_title, chapter_content) in enumerate(chapters, 1):
        print(f"\n   📄 {chapter_title}")
        
        # Create metadata for this chapter
        metadata = {
            'title': f"{book_title} - {chapter_title}",
            'source': formatted_source,
            'source_file': filename,
            'book_name': book_title,
            'chapter': chapter_title,
            'chapter_number': chapter_num,
            **(default_metadata or {})
        }
        
        if author:
            metadata['author'] = author
        
        # Chunk this chapter
        chunks = text_splitter.split_text(chapter_content)
        
        print(f"      {len(chunks)} chunks")
        
        # Ingest chunks for this chapter
        for i, chunk in enumerate(chunks, 1):
            total_inserted += ingest_document(
                content=chunk,
                metadata=metadata,
                chunk_index=i,
                total_chunks=len(chunks),
                text_splitter=text_splitter
            )
    
    return total_inserted


def main():
    parser = argparse.ArgumentParser(
        description="Ingest books and documents into knowledge base with automatic chunking"
    )
    parser.add_argument(
        '--file',
        type=str,
        help='Single file to ingest (otherwise ingests all files in knowledge_data/)'
    )
    parser.add_argument(
        '--chunk-size',
        type=int,
        default=700,
        help='Target chunk size in tokens (default: 700)'
    )
    parser.add_argument(
        '--overlap',
        type=int,
        default=150,
        help='Chunk overlap in tokens (default: 150)'
    )
    parser.add_argument(
        '--category',
        type=str,
        default='tax',
        help='Default category for documents (default: tax)'
    )
    parser.add_argument(
        '--no-chapters',
        action='store_true',
        help='Disable chapter-based chunking (use simple chunking instead)'
    )
    
    args = parser.parse_args()
    
    # Create text splitter
    text_splitter = create_text_splitter(
        chunk_size=args.chunk_size,
        chunk_overlap=args.overlap
    )
    
    print(f"\n🚀 Starting ingestion (chunk_size={args.chunk_size} tokens, overlap={args.overlap} tokens)\n")
    
    # Determine files to process
    if args.file:
        files = [args.file]
    else:
        # Look for files in knowledge_data/
        knowledge_dirs = [
            'knowledge_data',
            '../knowledge_data',
            'concierge-ai/knowledge_data',
            'knowledge_data/books'
        ]
        
        files = []
        for directory in knowledge_dirs:
            if os.path.exists(directory):
                for filename in os.listdir(directory):
                    if filename.endswith(('.txt', '.md', '.pdf')):
                        files.append(os.path.join(directory, filename))
        
        if not files:
            print("❌ No files found in knowledge_data/")
            print("   Place .txt or .md files in knowledge_data/ directory")
            return
    
    # Process all files
    total_chunks = 0
    default_metadata = {'category': args.category}
    
    # Add chapter-based chunking flag to default metadata
    chunk_by_chapter = not args.no_chapters
    
    for file_path in files:
        chunks_inserted = process_file(file_path, text_splitter, default_metadata, chunk_by_chapter)
        total_chunks += chunks_inserted
    
    print(f"\n{'='*60}")
    print(f"✅ Ingestion Complete!")
    print(f"   Total chunks inserted: {total_chunks}")
    print(f"   Files processed: {len(files)}")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    main()
