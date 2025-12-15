# Book Ingestion Examples

## Example 1: Filename Formatting

### Input Filenames
```
_OceanofPDF.com_The_Personal_Finance_101_Boxed_Set_-_Michele_Cagan.pdf
Tax_Guide_2024_-_John_Smith.txt
home_office_deductions.md
```

### Output (Formatted)
```
📚 Book: The Personal Finance 101 Boxed Set by Michele Cagan
📚 Book: Tax Guide 2024 by John Smith
📚 Book: Home Office Deductions
```

### In Database (source field)
```sql
"The Personal Finance 101 Boxed Set by Michele Cagan"
"Tax Guide 2024 by John Smith"
"Home Office Deductions"
```

---

## Example 2: Chapter-Based Chunking

### Input Book Structure
```
Chapter 1: Introduction to Tax Basics
Understanding the tax system...
(500 words of content)

Chapter 2: Deductions and Credits
Common deductions you can claim...
(800 words of content)

Chapter 3: Filing Your Return
Step-by-step filing guide...
(600 words of content)
```

### Output
```
📖 Processing: Tax_Guide_2024.txt
   📚 Book: Tax Guide 2024
   📖 Detected 3 chapters - chunking by chapter

   📄 Chapter 1: Introduction to Tax Basics
      2 chunks
   ✅ Chunk 1/2 - 2100 chars - Understanding the tax system...
   ✅ Chunk 2/2 - 1900 chars - The IRS provides several tools...

   📄 Chapter 2: Deductions and Credits
      3 chunks
   ✅ Chunk 1/3 - 2200 chars - Common deductions you can claim...
   ✅ Chunk 2/3 - 2150 chars - Business expense deductions...
   ✅ Chunk 3/3 - 1800 chars - Tax credits differ from deductions...

   📄 Chapter 3: Filing Your Return
      2 chunks
   ✅ Chunk 1/2 - 2000 chars - Step-by-step filing guide...
   ✅ Chunk 2/2 - 1600 chars - Electronic filing is faster...
```

### Database Entries (metadata)
```json
{
  "title": "Tax Guide 2024 - Chapter 1: Introduction to Tax Basics",
  "source": "Tax Guide 2024",
  "book_name": "Tax Guide 2024",
  "chapter": "Chapter 1: Introduction to Tax Basics",
  "chapter_number": 1,
  "chunk_index": 1,
  "total_chunks": 2
}
```

---

## Chapter Detection Patterns

The script automatically detects these chapter patterns:

```
Chapter 1: Title           ✅
Chapter 1. Title           ✅
CHAPTER 1: TITLE           ✅
Part 1: Introduction       ✅
1. INTRODUCTION            ✅ (if followed by uppercase)
Chapter One                ❌ (words not detected yet)
Section A                  ❌ (not detected)
```

---

## Usage Examples

### Basic ingestion (with chapters)
```bash
python scripts/ingest_books.py --file knowledge_data/books/tax_guide.txt
```

### Disable chapter detection  
```bash
python scripts/ingest_books.py --file knowledge_data/books/tax_guide.txt --no-chapters
```

### Custom chunk size
```bash
python scripts/ingest_books.py --chunk-size 1000 --overlap 200
```

### Ingest all books in directory
```bash
python scripts/ingest_books.py
```

---

## Benefits of Chapter-Based Chunking

1. **Better Semantic Grouping** - Related content stays together
2. **Clearer Source Attribution** - Users see "Chapter 2: Deductions"
3. **Improved Retrieval** - More precise matching to user queries
4. **Metadata Richness** - Can filter/search by chapter

### RAG Response Example

**User Query:** "How do I claim home office deductions?"

**Retrieved Chunks:**
- Source: The Personal Finance 101 Boxed Set by Michele Cagan - Chapter 5: Business Deductions
- Source: Tax Guide 2024 by John Smith - Chapter 7: Self-Employment

**Displayed to User:**
```
Sources:
[1] The Personal Finance 101 Boxed Set by Michele Cagan - Chapter 5
[2] Tax Guide 2024 by John Smith - Chapter 7
```

Much clearer than just "tax_guide.txt (Part 12/47)"!
