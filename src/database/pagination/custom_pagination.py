from __future__ import annotations
from typing import TypeVar, Generic, Any, Sequence, Optional

from typing import Annotated

from fastapi import Query
from fastapi_pagination.bases import AbstractPage, AbstractParams, RawParams
from pydantic import BaseModel

T = TypeVar("T")


class CustomParams(BaseModel, AbstractParams):
    page: Annotated[int, Query(1, ge=1)]
    per_page: Annotated[int, Query(10, ge=1, le=50)]

    def to_raw_params(self) -> RawParams:
        return RawParams(
            limit=self.per_page,
            offset=(self.page - 1) * self.per_page,
            include_total=True,
        )


class CustomPage(AbstractPage[T], Generic[T]):
    results: list[T]
    total_results: int
    prev_page: str | None
    next_page: str | None

    __params_type__ = CustomParams

    @classmethod
    def create(  # type: ignore
        cls,
        items: Sequence[T],
        params: CustomParams,
        *,
        total: Optional[int] = None,
        **kwargs: Any,
    ) -> CustomPage[T]:
        assert total is not None, "total must be provided"

        path = kwargs.get("path", "")
        query_params = dict(kwargs.get("query_params", {}))

        # Previous page
        prev_page = None
        if params.page > 1:
            query_params["page"] = params.page - 1
            query_params["per_page"] = params.per_page
            prev_query = "&".join(f"{k}={v}" for k, v in query_params.items())
            prev_page = f"{path}?{prev_query}"

        # Next page
        next_page = None
        if params.page * params.per_page < total:
            query_params["page"] = params.page + 1
            query_params["per_page"] = params.per_page
            next_query = "&".join(f"{k}={v}" for k, v in query_params.items())
            next_page = f"{path}?{next_query}"

        return cls(
            results=list(items),
            total_results=total,
            prev_page=prev_page,
            next_page=next_page,
        )
