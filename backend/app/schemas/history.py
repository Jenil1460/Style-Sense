from pydantic import BaseModel
from typing import List, Optional, Any, Dict
from datetime import datetime

class HistoryItemResponse(BaseModel):
    id: str
    user_id: str
    item_type: str
    item_id: str
    is_deleted: bool
    created_at: datetime
    # The actual populated document from the joined collection
    data: Optional[Dict[str, Any]] = None

class PaginatedHistoryResponse(BaseModel):
    items: List[HistoryItemResponse]
    total: int
    page: int
    limit: int
    total_pages: int
