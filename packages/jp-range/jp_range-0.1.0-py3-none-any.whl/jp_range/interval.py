from __future__ import annotations

from typing import Optional

from pydantic import BaseModel


class Interval(BaseModel):
    """Represents a numeric interval."""

    lower: Optional[float] = None
    upper: Optional[float] = None
    lower_inclusive: bool = False
    upper_inclusive: bool = False

    def __str__(self) -> str:
        lower_bracket = "[" if self.lower_inclusive else "("
        upper_bracket = "]" if self.upper_inclusive else ")"
        lower_val = str(self.lower) if self.lower is not None else "-inf"
        upper_val = str(self.upper) if self.upper is not None else "inf"
        return f"{lower_bracket}{lower_val}, {upper_val}{upper_bracket}"

    def contains(self, value: float) -> bool:
        """Return True if the value is inside this interval."""
        if self.lower is not None:
            if self.lower_inclusive:
                if value < self.lower:
                    return False
            else:
                if value <= self.lower:
                    return False
        if self.upper is not None:
            if self.upper_inclusive:
                if value > self.upper:
                    return False
            else:
                if value >= self.upper:
                    return False
        return True
