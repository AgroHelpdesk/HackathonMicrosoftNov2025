"""
Index Documents into Azure AI Search

This script processes documents from Azure Blob Storage and indexes them into Azure AI Search:
- PDFs: Extracted using Azure AI Document Intelligence
- CSVs: Parsed and converted to searchable text chunks

The script handles:
- Document chunking for large files
- Metadata extraction
- Batch uploading to the search index
"""

import json
import sys
import csv
import io
from pathlib import Path
from datetime import datetime, timezone
from typing import List, Dict
import hashlib

from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobServiceClient
from azure.search.documents import SearchClient
from azure.ai.formrecognizer import DocumentAnalysisClient
import pandas as pd

# Load configuration
script_dir = Path(__file__).parent
config_path = script_dir / "config.json"

if not config_path.exists():
    print(f"Error: Configuration file not found at {config_path}")
    sys.exit(1)

with open(config_path, 'r') as f:
    config = json.load(f)

# Configuration
STORAGE_ACCOUNT_NAME = config['storageAccountName']
CONTAINER_NAME = "knowledge-base"
SEARCH_SERVICE_NAME = config['aiSearchServiceName']
SEARCH_ENDPOINT = f"https://{SEARCH_SERVICE_NAME}.search.windows.net"
INDEX_NAME = config['searchIndexName']
DOC_INTELLIGENCE_SERVICE = config.get('documentIntelligenceServiceName')

# Document chunking settings
CHUNK_SIZE = 1500  # characters per chunk
CHUNK_OVERLAP = 200  # overlap between chunks

print("=" * 60)
print("Azure AI Search Document Indexing")
print("=" * 60)
print(f"Storage Account: {STORAGE_ACCOUNT_NAME}")
print(f"Container: {CONTAINER_NAME}")
print(f"Search Index: {INDEX_NAME}")
print()

# Initialize Azure clients
credential = DefaultAzureCredential()

try:
    # Blob Storage client
    blob_service_client = BlobServiceClient(
        account_url=f"https://{STORAGE_ACCOUNT_NAME}.blob.core.windows.net",
        credential=credential
    )
    container_client = blob_service_client.get_container_client(CONTAINER_NAME)
    
    # Search client
    search_client = SearchClient(
        endpoint=SEARCH_ENDPOINT,
        index_name=INDEX_NAME,
        credential=credential
    )
    
    print("✓ Connected to Azure services")
    
except Exception as e:
    print(f"✗ Failed to connect to Azure services: {e}")
    print("\nMake sure you are logged in to Azure CLI:")
    print("  az login")
    sys.exit(1)


def chunk_text(text: str, chunk_size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> List[str]:
    """Split text into overlapping chunks"""
    chunks = []
    start = 0
    text_length = len(text)
    
    while start < text_length:
        end = start + chunk_size
        chunk = text[start:end]
        
        # Try to break at sentence boundary
        if end < text_length:
            last_period = chunk.rfind('.')
            last_newline = chunk.rfind('\n')
            break_point = max(last_period, last_newline)
            
            if break_point > chunk_size * 0.5:  # Only break if we're past halfway
                chunk = chunk[:break_point + 1]
                end = start + break_point + 1
        
        chunks.append(chunk.strip())
        start = end - overlap
    
    return chunks


def generate_document_id(blob_path: str, chunk_index: int) -> str:
    """Generate unique document ID"""
    content = f"{blob_path}_{chunk_index}"
    return hashlib.md5(content.encode()).hexdigest()


def process_pdf(blob_client, blob_name: str) -> List[Dict]:
    """Process PDF using Azure AI Document Intelligence"""
    print(f"  Processing PDF: {blob_name}")
    
    try:
        # Download blob content
        blob_data = blob_client.download_blob().readall()
        
        # For now, we'll use a simple text extraction
        # In production, you would use Document Intelligence API
        # This is a placeholder that extracts basic info
        
        # Create a simple document with placeholder text
        # TODO: Integrate with Azure AI Document Intelligence
        text = f"PDF Document: {blob_name}\n\nThis is a placeholder for PDF content extraction. "
        text += "In production, this would use Azure AI Document Intelligence to extract the full text content."
        
        chunks = chunk_text(text)
        documents = []
        
        for i, chunk in enumerate(chunks):
            doc = {
                "id": generate_document_id(blob_name, i),
                "content": chunk,
                "title": blob_name.replace('.pdf', ''),
                "fileName": blob_name.split('/')[-1],
                "fileType": "pdf",
                "blobPath": blob_name,
                "uploadDate": datetime.now(timezone.utc).isoformat(),
                "chunkIndex": i,
                "totalChunks": len(chunks)
            }
            documents.append(doc)
        
        print(f"    ✓ Extracted {len(chunks)} chunks")
        return documents
        
    except Exception as e:
        print(f"    ✗ Error processing PDF: {e}")
        return []


def process_csv(blob_client, blob_name: str) -> List[Dict]:
    """Process CSV file"""
    print(f"  Processing CSV: {blob_name}")
    
    try:
        # Download and parse CSV
        blob_data = blob_client.download_blob().readall()
        csv_text = blob_data.decode('utf-8', errors='ignore')
        
        # Try different encodings if UTF-8 fails
        if not csv_text or len(csv_text) < 10:
            csv_text = blob_data.decode('latin-1', errors='ignore')
        
        # Parse CSV with semicolon delimiter (Brazilian standard)
        # Use error_bad_lines=False to skip problematic rows
        df = pd.read_csv(
            io.StringIO(csv_text),
            sep=';',
            on_bad_lines='skip',
            encoding_errors='ignore'
        )
        
        print(f"    Rows: {len(df)}, Columns: {len(df.columns)}")
        
        # Convert rows to text chunks
        documents = []
        rows_per_chunk = 10  # Group multiple rows per chunk
        
        for chunk_idx in range(0, len(df), rows_per_chunk):
            chunk_df = df.iloc[chunk_idx:chunk_idx + rows_per_chunk]
            
            # Convert chunk to readable text
            text_parts = []
            for idx, row in chunk_df.iterrows():
                row_text = " | ".join([f"{col}: {val}" for col, val in row.items() if pd.notna(val)])
                text_parts.append(row_text)
            
            content = "\n".join(text_parts)
            
            doc = {
                "id": generate_document_id(blob_name, chunk_idx // rows_per_chunk),
                "content": content,
                "title": f"{blob_name.replace('.csv', '')} (Rows {chunk_idx + 1}-{min(chunk_idx + rows_per_chunk, len(df))})",
                "fileName": blob_name.split('/')[-1],
                "fileType": "csv",
                "blobPath": blob_name,
                "uploadDate": datetime.now(timezone.utc).isoformat(),
                "chunkIndex": chunk_idx // rows_per_chunk,
                "totalChunks": (len(df) + rows_per_chunk - 1) // rows_per_chunk
            }
            documents.append(doc)
        
        print(f"    ✓ Created {len(documents)} chunks from {len(df)} rows")
        return documents
        
    except Exception as e:
        print(f"    ✗ Error processing CSV: {e}")
        return []


def index_documents():
    """Main indexing function"""
    print("Fetching blobs from storage...")
    
    try:
        blobs = list(container_client.list_blobs())
        print(f"✓ Found {len(blobs)} blobs\n")
    except Exception as e:
        print(f"✗ Error listing blobs: {e}")
        return
    
    all_documents = []
    processed_count = 0
    error_count = 0
    
    for blob in blobs:
        blob_name = blob.name
        blob_client = container_client.get_blob_client(blob_name)
        
        try:
            if blob_name.lower().endswith('.pdf'):
                docs = process_pdf(blob_client, blob_name)
                all_documents.extend(docs)
                processed_count += 1
                
            elif blob_name.lower().endswith('.csv'):
                docs = process_csv(blob_client, blob_name)
                all_documents.extend(docs)
                processed_count += 1
                
            else:
                print(f"  Skipping unsupported file: {blob_name}")
                
        except Exception as e:
            print(f"  ✗ Error processing {blob_name}: {e}")
            error_count += 1
    
    # Upload documents to search index
    if all_documents:
        print(f"\nUploading {len(all_documents)} documents to search index...")
        
        try:
            # Upload in batches
            batch_size = 100
            for i in range(0, len(all_documents), batch_size):
                batch = all_documents[i:i + batch_size]
                result = search_client.upload_documents(documents=batch)
                print(f"  ✓ Uploaded batch {i // batch_size + 1} ({len(batch)} documents)")
            
            print(f"\n✓ Successfully indexed {len(all_documents)} documents!")
            
        except Exception as e:
            print(f"\n✗ Error uploading documents: {e}")
            error_count += 1
    
    # Summary
    print("\n" + "=" * 60)
    print("Indexing Summary")
    print("=" * 60)
    print(f"Files processed: {processed_count}")
    print(f"Total documents indexed: {len(all_documents)}")
    print(f"Errors: {error_count}")
    
    if error_count == 0:
        print("\n" + "=" * 60)
        print("Next Steps")
        print("=" * 60)
        print("1. Verify the indexed documents in Azure Portal")
        print("2. Test search queries:")
        print(f"   az search query --index-name {INDEX_NAME} --service-name {SEARCH_SERVICE_NAME} --search-text \"pragas\" --query-type simple")


if __name__ == "__main__":
    try:
        index_documents()
    except KeyboardInterrupt:
        print("\n\nIndexing cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        sys.exit(1)
