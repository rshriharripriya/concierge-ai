import os
import sys
import re
import hashlib
from typing import List, Dict, Tuple
from dotenv import load_dotenv
from supabase import create_client
from langchain_huggingface import HuggingFaceEndpointEmbeddings
import uuid


# PDF support
try:
    import pypdf
    PDF_SUPPORT = True
except ImportError:
    print("⚠️  Warning: pypdf not installed. PDF support disabled.")
    PDF_SUPPORT = False


# Load environment variables
load_dotenv(dotenv_path=".env.local")


# Initialize Supabase client
supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_KEY")


if not supabase_url or not supabase_key:
    print("❌ Error: SUPABASE_URL or SUPABASE_KEY not found in .env.local")
    sys.exit(1)


supabase = create_client(supabase_url, supabase_key)


# Add parent dir to path to allow imports from api
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from backend.services.hf_embeddings import HuggingFaceEmbeddings


# Initialize Embedding Model (API)
print("🔄 Loading embedding model (API)...")
model = HuggingFaceEmbeddings(
    model="sentence-transformers/all-MiniLM-L6-v2",
    api_token=os.getenv("HF_TOKEN")
)
print("✅ Model loaded")


def recursive_character_text_splitter(text, chunk_size=1000, chunk_overlap=200):
    """
    Simple implementation of recursive character text splitting.
    """
    if not text:
        return []
    
    chunks = []
    start = 0
    text_len = len(text)
    
    while start < text_len:
        end = start + chunk_size
        if end >= text_len:
            chunks.append(text[start:])
            break
        
        # Try to find a good breaking point
        search_end = min(end + 50, text_len)
        chunk_candidate = text[start:search_end]
        
        break_point = -1
        
        # Look for double newline
        last_dnl = chunk_candidate.rfind('\n\n', 0, chunk_size)
        if last_dnl != -1:
            break_point = last_dnl + 2
        else:
            # Look for newline
            last_nl = chunk_candidate.rfind('\n', 0, chunk_size)
            if last_nl != -1:
                break_point = last_nl + 1
            else:
                 # Look for space
                last_space = chunk_candidate.rfind(' ', 0, chunk_size)
                if last_space != -1:
                    break_point = last_space + 1
        
        if break_point != -1:
            chunks.append(text[start:start+break_point])
            # Calculate next start
            step = break_point - chunk_overlap
            if step <= 0:
                step = 1 # Must advance at least 1 char
            
            start += step
        else:
             # Hard break
            chunks.append(text[start:end])
            step = (end - start) - chunk_overlap
            if step <= 0:
                step = 1
            start += step
            
    return chunks


def extract_text_from_pdf(pdf_path):
    """Extract text from PDF with better formatting preservation."""
    print(f"📄 Extracting text from {pdf_path}...")
    try:
        reader = pypdf.PdfReader(pdf_path)
        text = ""
        for page_num, page in enumerate(reader.pages):
            page_text = page.extract_text()
            if page_text:
                # Clean up excessive whitespace while preserving structure
                page_text = re.sub(r'\n{3,}', '\n\n', page_text)
                text += page_text + "\n"
        return text
    except Exception as e:
        print(f"❌ Error reading PDF {pdf_path}: {e}")
        return None


def detect_sections_irs(content: str) -> List[Tuple[str, str, int]]:
    """
    Enhanced section detection specifically for IRS documents.
    Returns list of (section_title, section_content, hierarchy_level) tuples.
    
    IRS document patterns:
    - SECTION 1., SECTION 2. (main sections)
    - .01, .02, .03 (subsections under SECTIONs)
    - TABLE 1, TABLE 2 (data tables)
    - Part I, Part II (major divisions)
    """
    
    # Define patterns with hierarchy levels
    patterns = [
        # Level 1: Major divisions (highest)
        (r'^\s*PART\s+[IVX\d]+[\s\.\-:].*$', 1),
        (r'^\s*Part\s+[IVX\d]+[\s\.\-:].*$', 1),
        (r'^\s*CHAPTER\s+\d+[\s\.\-:].*$', 1),
        (r'^\s*Chapter\s+\d+[\s\.\-:].*$', 1),
        
        # Level 2: Main sections
        (r'^\s*SECTION\s+\d+\..*$', 2),
        (r'^\s*Section\s+\d+\..*$', 2),
        
        # Level 3: Tables and subsections
        (r'^\s*TABLE\s+\d+[\s\-].*$', 3),
        (r'^\s*Table\s+\d+[\s\-].*$', 3),
        (r'^\s*\.0\d+\s+.*$', 3),  # .01, .02, .03 subsections
    ]
    
    lines = content.split('\n')
    sections = []
    current_title = None
    current_content = []
    current_level = 0
    
    for line_idx, line in enumerate(lines):
        matched = False
        
        for pattern, level in patterns:
            if re.match(pattern, line.strip(), re.MULTILINE | re.IGNORECASE):
                # Save previous section
                if current_title and current_content:
                    sections.append((
                        current_title, 
                        '\n'.join(current_content).strip(),
                        current_level
                    ))
                
                # Start new section
                current_title = line.strip()
                current_content = []
                current_level = level
                matched = True
                break
        
        if not matched:
            current_content.append(line)
    
    # Don't forget last section
    if current_title and current_content:
        sections.append((
            current_title, 
            '\n'.join(current_content).strip(),
            current_level
        ))
    
    # If no sections detected, return entire content
    if not sections:
        return [("Complete Document", content, 0)]
    
    return sections


def compute_hash(text: str) -> str:
    return hashlib.sha256(text.encode('utf-8')).hexdigest()


def check_duplicate(content_hash: str) -> bool:
    try:
        result = supabase.table('knowledge_documents')\
            .select('id')\
            .eq('metadata->>content_hash', content_hash)\
            .execute()
        return len(result.data) > 0
    except Exception as e:
        return False


def ingest_document(title, content, source_file, metadata_override=None):
    """
    Ingest a single document's content (chunked by section) into the vector database.
    """
    # Detect sections using IRS-specific logic
    sections = detect_sections_irs(content)
    
    if len(sections) > 1:
        print(f"   📖 Detected {len(sections)} sections in '{title}'")
        # Print section breakdown
        for section_title, _, level in sections:
            indent = "  " * level
            print(f"   {indent}├─ {section_title[:60]}...")
    
    total_chunks = 0
    
    for section_title, section_content, hierarchy_level in sections:
        # Skip empty sections
        if not section_content or len(section_content.strip()) < 50:
            continue
        
        # For IRS docs, use larger chunks for sections with tables
        chunk_size = 2000 if "TABLE" in section_title.upper() else 1000
        chunks = recursive_character_text_splitter(section_content, chunk_size=chunk_size)
        
        for i, chunk in enumerate(chunks):
            try:
                # Deduplication
                content_hash = compute_hash(chunk)
                if check_duplicate(content_hash):
                    # print(f"   ⏭  Skipping duplicate chunk")
                    continue
                
                # Generate embedding
                embedding = model.embed_query(chunk)
                
                # Prepare metadata
                metadata = {
                    "title": title,
                    "source": source_file,
                    "chunk_index": i,
                    "section": section_title,
                    "hierarchy_level": hierarchy_level,
                    "content_hash": content_hash,
                    "doc_type": "irs_document"
                }
                if metadata_override:
                    metadata.update(metadata_override)
                
                # Create display title
                display_title = f"{title} - {section_title}" if section_title != "Complete Document" else title
                
                # Prepare data payload
                data = {
                    "content": chunk,
                    "title": display_title,
                    "source": source_file,
                    "metadata": metadata,
                    "content_embedding": embedding
                }
                
                # Insert into Supabase
                supabase.table('knowledge_documents').insert(data).execute()
                total_chunks += 1
                
            except Exception as e:
                print(f"❌ Failed to insert chunk {i} for {section_title}: {e}")
    
    if total_chunks > 0:
        print(f"✅ Ingested {total_chunks} chunks for '{title}'\n")
    else:
        print(f"⚠️  No chunks ingested for '{title}' (possible duplicates)\n")


if __name__ == "__main__":
    base_dirs_to_check = [
        os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'IRS DOCS')),
        os.path.abspath(os.path.join(os.getcwd(), 'IRS DOCS')),
        "/Users/rshri/Concierge_AI/concierge-ai/IRS DOCS"
    ]
    
    target_dir = None
    for d in base_dirs_to_check:
        print(f"🔍 Checking for IRS DOCS at: {d}")
        if os.path.exists(d) and os.path.isdir(d):
            target_dir = d
            break
    
    if not target_dir:
        print("❌ Could not find 'IRS DOCS' directory.")
        print("\n💡 Tip: Create a folder called 'IRS DOCS' and place your PDFs there.")
        sys.exit(1)
    
    # Check for CLI argument
    if len(sys.argv) > 1:
        target_file = sys.argv[1]
        print(f"🎯 Target file specified: {target_file}")
        
        if not os.path.exists(target_file):
            print(f"❌ File not found: {target_file}")
            sys.exit(1)
            
        files_processed = 0
        file_path = target_file
        file_name = os.path.basename(file_path)
        
        print(f"{'='*60}")
        print(f"Processing: {file_name}")
        print(f"{'='*60}")
        
        if file_name.lower().endswith('.pdf'):
            content = extract_text_from_pdf(file_path)
            if content:
                ingest_document(
                    title=file_name.replace('.pdf', ''),
                    content=content,
                    source_file=file_name
                )
                files_processed = 1
            else:
                print(f"⚠️  No content extracted from {file_name}\n")
        elif file_name.lower().endswith('.txt'):
             try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                ingest_document(
                    title=file_name.replace('.txt', ''),
                    content=content,
                    source_file=file_name
                )
                files_processed = 1
             except Exception as e:
                print(f"❌ Error reading text file {file_name}: {e}\n")
    
    else:
        # Normal directory traversal
        print(f"📂 Found IRS DOCS directory at: {target_dir}\n")
        
        files_processed = 0
        for root, _, files in os.walk(target_dir):
            for file in files:
                if file.lower().endswith('.pdf'):
                    file_path = os.path.join(root, file)
                    print(f"{'='*60}")
                    print(f"Processing: {file}")
                    print(f"{'='*60}")
                    
                    content = extract_text_from_pdf(file_path)
                    if content:
                        ingest_document(
                            title=file.replace('.pdf', ''),
                            content=content,
                            source_file=file
                        )
                        files_processed += 1
                    else:
                        print(f"⚠️  No content extracted from {file}\n")
                
                elif file.lower().endswith('.txt'):
                    file_path = os.path.join(root, file)
                    print(f"{'='*60}")
                    print(f"Processing: {file}")
                    print(f"{'='*60}")
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                        ingest_document(
                            title=file.replace('.txt', ''),
                            content=content,
                            source_file=file
                        )
                        files_processed += 1
                    except Exception as e:
                        print(f"❌ Error reading text file {file}: {e}\n")

    print(f"\n{'='*60}")
    print(f"✨ Ingestion complete!")
    print(f"📊 Processed {files_processed} files from IRS DOCS")
    print(f"{'='*60}")
