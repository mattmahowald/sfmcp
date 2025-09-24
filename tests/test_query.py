from __future__ import annotations
import pytest
from pydantic import ValidationError
from sfmcp.tools.query import QueryArgs

def test_query_args_validation():
    with pytest.raises(ValidationError):
        QueryArgs.model_validate({"soql": 123})  # must be str
