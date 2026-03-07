#!/usr/bin/env python3
"""
Use LLM to intelligently detect tax years from book content.
"""
import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from supabase import create_client
from litellm import completion
import json
import time

# Load environment
env_path = Path(__file__).parent.parent / '.env.local'
load_dotenv(dotenv_path=env_path)

print("=" * 70)
print("Fix Tax Years Using LLM Analysis")
print("=" * 70 + "\n")

# Initialize
print("🔄 Connecting to Supabase...")
supabase = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_KEY")
)
print("✅ Connected\n")

def should_skip_document(title: str, current_metadata: dict) -> tuple[bool, str]:
    """Check if document should be skipped from LLM analysis"""
    
    title_lower = title.lower()
    # Skip IRS Revenue Procedures and Notices (they're usually correct already)
    if title.startswith('rp-') or title.startswith('n-'):
        return True, "IRS Revenue Procedure/Notice - trust existing metadata"
    

    # Skip IRA/retirement docs (they're often misnamed)
    if any(keyword in title_lower for keyword in ['590-a', '590-b', 'pub. 505', 'pub. 590','p17' ]):
        return True, "IRA/retirement doc with potentially wrong title"
    
    # Skip if title mentions one pub but content is from another
    if 'p17' in title_lower and ('590' in title_lower or '505' in title_lower):
        return True, "Conflicting publication numbers in title"
    
    # Skip notices without clear content
    if title.startswith('n-') and len(current_metadata.get('content', '')) < 500:
        return True, "Short notice with insufficient content"

    
    
    return False, ""


def detect_tax_year_with_llm(title: str, content_sample: str) -> dict:
    """Use LLM to detect tax year from content"""
    
    prompt = f"""Analyze this tax document excerpt and determine which tax year(s) it covers.

Title: {title}

Content Sample (first 2000 chars):
{content_sample[:2000]}

Return ONLY a JSON object with this exact format:
{{
  "tax_years": [2023],
  "confidence": 0.95,
  "reasoning": "Document explicitly mentions '2023 tax rates'"
}}

Example Output:
{{
  "tax_years": [2023, 2024],
  "confidence": 0.90,
  "reasoning": "Document explicitly mentions '2023 tax rates' and '2024 tax rates'"
}}
 
CRITICAL RULES:
1. "2024 Edition" books published in 2024 typically cover tax year 2023
2. Revenue Procedures like "rp-24-40" issued in 2024 cover 2025 (next year)
3. Look for explicit year mentions like "for 2023", "taxable years beginning in 2025"
4. Use dollar amounts to verify year

2023 TAX YEAR INDICATORS:
- Standard Deduction: Single $13,850, Married $27,700
- 10% Bracket: Single up to $11,000, Married up to $22,000
- 37% Bracket: Single over $578,125, Married over $693,750

2024 TAX YEAR INDICATORS:
- Standard Deduction: Single $14,600, Married $29,200
- 10% Bracket: Single up to $11,600, Married up to $23,200
- 37% Bracket: Single over $609,350, Married over $731,200

2025 TAX YEAR INDICATORS:
- Standard Deduction: Single $15,750, Married $31,500
- 10% Bracket: Single up to $11,925, Married up to $23,850
- 37% Bracket: Single over $626,350, Married over $751,600

DOCUMENT TYPE RULES:
- "rp-YY-XX" (Revenue Procedure 20YY-XX) → covers year 20(YY+1)
- "n-YY-XX" (Notice 20YY-XX) → covers year 20YY
- "Publication 17 (YYYY)" → covers year YYYY
- "Taxes For Dummies YYYY Edition" → covers year YYYY-1
"""

    
    try:
        response = completion(
            model="groq/llama-3.3-70b-versatile",  # Fast and accurate
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,
            max_tokens=500
        )
        
        result_text = response.choices[0].message.content.strip()
        
        # Remove markdown code blocks if present
        if result_text.startswith("```"):
            result_text = result_text.split("```")[1]
            if result_text.startswith("json"):
                result_text = result_text[4:]
            result_text = result_text.strip()
        
        result = json.loads(result_text)
        return result
        
    except Exception as e:
        print(f"   ⚠️ LLM detection failed: {e}")
        return {
            "tax_years": [],
            "confidence": 0.0,
            "reasoning": f"Error: {e}"
        }


def main():
    """Main execution"""
    import argparse
    parser = argparse.ArgumentParser(description="Fix tax years using LLM analysis")
    parser.add_argument('--book-filter', default='%Dummies%', help='Filter for book titles (SQL LIKE pattern)')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be changed without updating')
    parser.add_argument('--limit', type=int, default=50, help='Max documents to process')
    
    args = parser.parse_args()
    
    # Get documents that need fixing
    print(f"🔍 Finding documents matching: {args.book_filter}\n")
    result = supabase.table('knowledge_documents')\
        .select('id, title, content, metadata')\
        .ilike('title', args.book_filter)\
        .limit(args.limit)\
        .execute()
    
    if not result.data:
        print("✅ No documents found matching filter")
        return
    
    # Group by title (to process book once, not every chunk)
    docs_by_title = {}
    for doc in result.data:
        title = doc['title']
        if title not in docs_by_title:
            docs_by_title[title] = []
        docs_by_title[title].append(doc)
    
    print(f"📊 Found {len(result.data)} chunks from {len(docs_by_title)} unique documents\n")
    
    # Process each unique document
    updates = []
    for i, (title, chunks) in enumerate(docs_by_title.items(), 1):
        print(f"\n[{i}/{len(docs_by_title)}] Analyzing: {title[:60]}...")
        
        # Use first chunk's content as sample
        sample_content = chunks[0]['content']
        current_metadata = chunks[0]['metadata']
        
        print(f"   Current: tax_years={current_metadata.get('tax_years')}, primary={current_metadata.get('primary_tax_year')}")
        
        # CHECK IF WE SHOULD SKIP THIS DOCUMENT
        should_skip, skip_reason = should_skip_document(title, current_metadata)
        if should_skip:
            print(f"   ⏭️ Skipping: {skip_reason}")
            continue
            
        # Detect with LLM
        detection = detect_tax_year_with_llm(title, sample_content)
        
        print(f"   LLM says: tax_years={detection['tax_years']} (confidence: {detection['confidence']:.2f})")
        print(f"   Reasoning: {detection['reasoning']}")
        
        # Only update if confident
        if detection['confidence'] >= 0.7 and detection['tax_years']:
            new_tax_years = detection['tax_years']
            
            # Compute is_current (current filing season is for 2025 taxes)
            is_current = 2025 in new_tax_years
            
            # Store update for all chunks of this document
            for chunk in chunks:
                updates.append({
                    'id': chunk['id'],
                    'title': title,
                    'new_tax_years': new_tax_years,
                    'new_is_current': is_current
                })
            
            print(f"   ✅ Will update to: tax_years={new_tax_years}, is_current={is_current}")
        else:
            print(f"   ⏭️ Skipping (low confidence or no years detected)")
        
        # Rate limiting
        if i < len(docs_by_title):
            time.sleep(30) 
            print("   ⏰ Waiting 30 seconds before next LLM call") 
    
    # Show summary
    print("\n" + "=" * 70)
    print(f"Summary: {len(updates)} chunks to update")
    print("=" * 70)
    
    if not updates:
        print("✅ No updates needed")
        return
    
    # Show sample
    print("\nSample updates:")
    for update in updates[:5]:
        print(f"  {update['title'][:60]}")
        print(f"    → tax_years={update['new_tax_years']}, is_current={update['new_is_current']}")
    
    if args.dry_run:
        print("\n🔍 DRY RUN - No changes made")
        return
    
    # Confirm
    print()
    response = input(f"Apply {len(updates)} updates to Supabase? (yes/no): ").strip().lower()
    if response != 'yes':
        print("❌ Cancelled")
        return
    
    # Apply updates
    print("\n" + "=" * 70)
    print("Applying updates...")
    print("=" * 70 + "\n")
    
    success = 0
    failed = 0
    
    for update in updates:
        try:
            supabase.table('knowledge_documents').update({
                'metadata': {
                    **update,  # Preserve other metadata fields
                    'tax_years': update['new_tax_years'],
                    'is_current': update['new_is_current']
                }
            }).eq('id', update['id']).execute()
            success += 1
        except Exception as e:
            print(f"❌ Failed to update {update['id']}: {e}")
            failed += 1
    
    print(f"\n✅ Updated: {success}")
    print(f"❌ Failed: {failed}")


if __name__ == "__main__":
    main()
