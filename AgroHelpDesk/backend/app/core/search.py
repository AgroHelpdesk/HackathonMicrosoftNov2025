from app.config import settings
from app.utils.logger import get_logger

logger = get_logger("search")

# Optional: only attempt if keys provided
try:
    from azure.search.documents import SearchClient
    from azure.core.credentials import AzureKeyCredential
    SEARCH_AVAILABLE = settings.AZURE_SEARCH_ENDPOINT and settings.AZURE_SEARCH_KEY and settings.AZURE_SEARCH_INDEX_NAME
except Exception:
    SEARCH_AVAILABLE = False

search_client = None
if SEARCH_AVAILABLE:
    search_client = SearchClient(
        endpoint=settings.AZURE_SEARCH_ENDPOINT,
        index_name=settings.AZURE_SEARCH_INDEX_NAME,
        credential=AzureKeyCredential(settings.AZURE_SEARCH_KEY)
    )

async def search_documents(query: str, top: int = 3):
    if not SEARCH_AVAILABLE or not search_client:
        logger.info("Search not configured; returning empty results")
        return []
    results = search_client.search(search_text=query, top=top)
    return [r for r in results]
