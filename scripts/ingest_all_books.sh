#!/bin/bash
# Batch ingest all PDF books in knowledge_data/books/
# Run this script from the concierge-ai directory

echo "🚀 Starting batch PDF ingestion..."
echo ""

# Array of all PDF books
books=(
    "knowledge_data/books/_OceanofPDF.com_JK_Lassers_Small_Business_Taxes_2021_-_Barbara_Weltman.pdf"
    "knowledge_data/books/_OceanofPDF.com_Lower_Your_Taxes-BIG_TIME_2023-2024_-_Sandy_Botkin.pdf"
    # Add other PDFs here automatically
)

# Process each book
for book in "${books[@]}"; do
    if [ -f "$book" ]; then
        echo "📖 Processing: $book"
        python scripts/ingest_books.py --file "$book"
        
        if [ $? -eq 0 ]; then
            echo "✅ Success: $book"
        else
            echo "❌ Failed: $book"
        fi
        echo ""
    else
        echo "⚠️  File not found: $book"
    fi
done

echo "✅ Batch ingestion complete!"
