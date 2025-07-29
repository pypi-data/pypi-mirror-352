import pytest
from pydantic import BaseModel, ValidationError
from crypticorn.common import PaginationParams


class Item(BaseModel):
    name: str
    value: int


@pytest.mark.asyncio
async def test_pagination():
    with pytest.raises(TypeError, match="PaginationParams must be used with a Pydantic BaseModel as a generic parameter"):
        PaginationParams[int]()
    with pytest.raises(ValueError, match="Invalid sort field: 'foo' — must be one of: \\['name', 'value'\\]"):
        PaginationParams[Item](sort="foo")

    pagination_params = PaginationParams[Item](sort="name", order="asc")
    assert pagination_params.sort == "name"
    assert pagination_params.order == "asc"
    assert pagination_params.page == 1
    assert pagination_params.size == 10


@pytest.mark.asyncio
async def test_pagination_order_validation():
    # Test invalid order values
    with pytest.raises(ValidationError):
        PaginationParams[Item](order="invalid")


@pytest.mark.asyncio
async def test_pagination_sort_order_interaction():
    # Test that sort and order must be provided together
    with pytest.raises(ValueError, match="Sort and order must be provided together"):
        PaginationParams[Item](sort="name")
    
    with pytest.raises(ValueError, match="Sort and order must be provided together"):
        PaginationParams[Item](order="asc")
    
    # Test valid combination
    params = PaginationParams[Item](sort="name", order="asc")
    assert params.sort == "name"
    assert params.order == "asc"


@pytest.mark.asyncio
async def test_pagination_default_values():
    params = PaginationParams[Item]()
    assert params.page == 1
    assert params.size == 10
    assert params.sort is None
    assert params.order is None


@pytest.mark.asyncio
async def test_pagination_custom_values():
    params = PaginationParams[Item](page=2, size=20, sort="value", order="desc")
    assert params.page == 2
    assert params.size == 20
    assert params.sort == "value"
    assert params.order == "desc"
