from __future__ import annotations

from . import BaseModel

class Amenity(BaseModel):
    """Represents an amenity in the domain layer."""

    def __init__(self, name: str, **kwargs) -> None:
        # Initialize shared BaseModel fields first
        super().__init__(**kwargs)

        # Validate the provided name before assigning it
        self._validate_name(name)
        self.name = name

    def rename(self, name: str) -> None:
        # Validate the new name before updating the attribute
        self._validate_name(name)
        self.name = name

        # Update the modification timestamp after the change
        self.touch()

    @staticmethod
    def _validate_name(name: str) -> None:
        # Name must be a non-empty string after trimming whitespace
        if not isinstance(name, str) or not name.strip():
            raise ValueError("name must be a non-empty string")

    def to_dict(self):
        # Start with the base dictionary representation
        data = super().to_dict()

        # Add Amenity-specific fields
        data.update({"name": self.name})
        return data

__all__ = ["Amenity"]
