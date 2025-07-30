from __future__ import annotations

import json
from collections.abc import Callable
from dataclasses import asdict, is_dataclass
from datetime import date, datetime
from decimal import Decimal
from enum import Enum
from pathlib import Path
from typing import TYPE_CHECKING, Any
from uuid import UUID

# Optional dependencies
HAS_PYDANTIC = False
HAS_MM_RESULT = False

try:
    from pydantic import BaseModel

    HAS_PYDANTIC = True
except ImportError:
    pass

try:
    from mm_result import Result

    HAS_MM_RESULT = True
except ImportError:
    pass

if TYPE_CHECKING and not HAS_PYDANTIC:
    from pydantic import BaseModel
if TYPE_CHECKING and not HAS_MM_RESULT:
    from mm_result import Result


class ExtendedJSONEncoder(json.JSONEncoder):
    """JSON encoder with extended type support for common Python objects.

    Handles serialization of:
    - Built-in types: UUID, Decimal, Path, datetime/date, set/frozenset, bytes, complex
    - Python structures: dataclasses, Enums, Exceptions
    - Optional dependencies: Pydantic BaseModel, mm-result Result types

    Optional dependencies are checked once at module load time for efficiency.
    """

    def default(self, obj: Any) -> Any:  # noqa: ANN401
        # Built-in common types
        if isinstance(obj, UUID):
            return str(obj)
        if isinstance(obj, Decimal):
            return str(obj)
        if isinstance(obj, Path):
            return str(obj)
        if isinstance(obj, (datetime, date)):
            return obj.isoformat()
        if isinstance(obj, (set, frozenset)):
            return list(obj)
        if isinstance(obj, bytes):
            return obj.decode("utf-8", errors="replace")
        if isinstance(obj, complex):
            return {"real": obj.real, "imag": obj.imag}

        # Dataclasses
        if is_dataclass(obj) and not isinstance(obj, type):
            return asdict(obj)

        # Enums
        if isinstance(obj, Enum):
            return obj.value

        # Exceptions
        if isinstance(obj, Exception):
            return str(obj)

        # Optional dependencies
        if HAS_PYDANTIC and isinstance(obj, BaseModel):
            return obj.model_dump()
        if HAS_MM_RESULT and isinstance(obj, Result):
            return obj.to_dict()

        return super().default(obj)


def to_json(data: Any, default: Callable[[Any], Any] | None = None, **kwargs: Any) -> str:  # noqa: ANN401
    """Serialize object to JSON with extended type support.

    Args:
        data: Object to serialize
        default: Function to handle objects not supported by encoder
        **kwargs: Additional arguments passed to json.dumps

    Returns:
        JSON string representation of the object
    """
    return json.dumps(data, cls=ExtendedJSONEncoder, default=default, **kwargs)
