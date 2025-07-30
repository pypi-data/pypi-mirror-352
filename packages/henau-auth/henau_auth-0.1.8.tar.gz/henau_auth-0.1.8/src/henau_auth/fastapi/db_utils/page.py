from peewee import Query
from typing import Tuple, Any, Dict
from .to_dict import to_dict
from typing import TypeVar, Generic, List
from pydantic import BaseModel


def paginate(
    query: Query, page: int = 1, size: int = 10, **kewargs
) -> Tuple[list, Dict[str, Any]]:
    """
    Peewee 通用分页方法

    Args:
        query: peewee 查询对象
        page: 当前页码，从1开始
        size: 每页记录数

    Returns:
        tuple: (分页结果列表, 分页信息字典)
    """
    page = int(page)
    size = int(size)
    if page < 1:
        page = 1
    if size < 1:
        size = 10

    total = query.count()
    total_pages = (total + size - 1) // size

    if page > total_pages:
        page = total_pages

    results = query.paginate(page, size)

    pagination_info = {
        "page": page,
        "size": size,
        "total": total,
        "total_pages": total_pages,
        "has_prev": page > 1,
        "has_next": page < total_pages,
    }

    return {"records": to_dict(results, **kewargs), "pagination": pagination_info}


T = TypeVar("T")


class PaginationModel(BaseModel):
    page: int
    size: int
    total: int
    total_pages: int
    has_prev: bool
    has_next: bool


class PageSchemas(BaseModel, Generic[T]):
    records: List[T]
    pagination: PaginationModel
