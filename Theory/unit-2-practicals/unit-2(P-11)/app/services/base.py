import math

from app.config import settings


def paginate(query, page: int, limit: int) -> dict:
    limit = min(limit, settings.MAX_PAGE_SIZE)
    total = query.order_by(None).count()
    items = query.offset((page - 1) * limit).limit(limit).all()
    return {"items": items, "page": page, "limit": limit, "total": total,
            "total_pages": math.ceil(total / limit) if total else 0}
