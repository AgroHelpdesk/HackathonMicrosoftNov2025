"""
Create Azure AI Search Index for Agro Auto-Resolve Knowledge Base

This script creates a search index with the following capabilities:
- Full-text search across document content
- Vector search for semantic similarity
- Metadata filtering (file type, source, date)
- Semantic ranking for improved relevance
"""

import json
import sys
from pathlib import Path
from azure.core.credentials import AzureKeyCredential
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.indexes.models import (
    SearchIndex,
    SearchField,
    SearchFieldDataType,
    SimpleField,
    SearchableField,
    VectorSearch,
    HnswAlgorithmConfiguration,
    VectorSearchProfile,
    SemanticConfiguration,
    SemanticField,
    SemanticPrioritizedFields,
    SemanticSearch
)
from azure.identity import DefaultAzureCredential

# Load configuration
script_dir = Path(__file__).parent
config_path = script_dir / "config.json"

if not config_path.exists():
    print(f"Error: Configuration file not found at {config_path}")
    print("Please run deploy_resources.ps1 first.")
    sys.exit(1)

with open(config_path, 'r') as f:
    config = json.load(f)

# Configuration
SEARCH_SERVICE_NAME = config['aiSearchServiceName']
SEARCH_ENDPOINT = f"https://{SEARCH_SERVICE_NAME}.search.windows.net"
INDEX_NAME = config['searchIndexName']

print("=" * 60)
print("Azure AI Search Index Creation")
print("=" * 60)
print(f"Search Service: {SEARCH_SERVICE_NAME}")
print(f"Index Name: {INDEX_NAME}")
print()

# Create search index client using Azure CLI credentials
credential = DefaultAzureCredential()

try:
    index_client = SearchIndexClient(
        endpoint=SEARCH_ENDPOINT,
        credential=credential
    )
    
    print("✓ Connected to Azure AI Search service")
except Exception as e:
    print(f"✗ Failed to connect to Azure AI Search: {e}")
    print("\nMake sure you are logged in to Azure CLI:")
    print("  az login")
    sys.exit(1)

# Define the search index schema
fields = [
    SimpleField(
        name="id",
        type=SearchFieldDataType.String,
        key=True,
        filterable=True
    ),
    SearchableField(
        name="content",
        type=SearchFieldDataType.String,
        searchable=True,
        analyzer_name="standard.lucene"  # Standard Lucene analyzer
    ),
    SearchableField(
        name="title",
        type=SearchFieldDataType.String,
        searchable=True,
        analyzer_name="standard.lucene"
    ),
    SimpleField(
        name="fileName",
        type=SearchFieldDataType.String,
        filterable=True,
        facetable=True
    ),
    SimpleField(
        name="fileType",
        type=SearchFieldDataType.String,
        filterable=True,
        facetable=True
    ),
    SimpleField(
        name="blobPath",
        type=SearchFieldDataType.String,
        filterable=True
    ),
    SimpleField(
        name="uploadDate",
        type=SearchFieldDataType.DateTimeOffset,
        filterable=True,
        sortable=True
    ),
    SimpleField(
        name="chunkIndex",
        type=SearchFieldDataType.Int32,
        filterable=True,
        sortable=True
    ),
    SimpleField(
        name="totalChunks",
        type=SearchFieldDataType.Int32,
        filterable=True
    )
]

# Configure semantic search for better relevance
semantic_config = SemanticConfiguration(
    name="agro-semantic-config",
    prioritized_fields=SemanticPrioritizedFields(
        title_field=SemanticField(field_name="title"),
        content_fields=[SemanticField(field_name="content")]
    )
)

semantic_search = SemanticSearch(
    configurations=[semantic_config]
)

# Create the index
index = SearchIndex(
    name=INDEX_NAME,
    fields=fields,
    semantic_search=semantic_search
)

print("\nCreating search index...")
print(f"  - Fields: {len(fields)}")
print(f"  - Language Analyzer: Standard Lucene")
print(f"  - Semantic Search: Enabled")

try:
    # Delete existing index if it exists
    try:
        index_client.get_index(INDEX_NAME)
        print(f"\n⚠ Index '{INDEX_NAME}' already exists. Deleting...")
        index_client.delete_index(INDEX_NAME)
        print("✓ Existing index deleted")
    except:
        pass
    
    # Create new index
    result = index_client.create_index(index)
    print(f"\n✓ Search index '{INDEX_NAME}' created successfully!")
    
    # Display index details
    print("\n" + "=" * 60)
    print("Index Details")
    print("=" * 60)
    print(f"Name: {result.name}")
    print(f"Fields: {len(result.fields)}")
    print(f"Semantic Search: {'Enabled' if result.semantic_search else 'Disabled'}")
    print("\nSearchable Fields:")
    for field in result.fields:
        if hasattr(field, 'searchable') and field.searchable:
            print(f"  - {field.name} ({field.type})")
    
    print("\n" + "=" * 60)
    print("Next Steps")
    print("=" * 60)
    print("1. Run the indexing script to populate the index:")
    print("   python infrastructure/index_documents.py")
    print("\n2. Verify the index in Azure Portal:")
    print(f"   https://portal.azure.com/#@/resource/subscriptions/.../resourceGroups/{config['resourceGroupName']}/providers/Microsoft.Search/searchServices/{SEARCH_SERVICE_NAME}/indexes")
    
except Exception as e:
    print(f"\n✗ Error creating index: {e}")
    sys.exit(1)
