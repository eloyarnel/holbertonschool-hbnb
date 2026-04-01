from __future__ import annotations

from typing import List

from . import BaseModel
from .place import Place
from .review import Review

class User(BaseModel):
    """Represents a user in the domain layer."""

    def __init__(
        self,
        first_name: str,
        last_name: str,
        email: str,
        password: str,
        is_admin: bool = False,
        places: List[Place] | None = None,
        reviews: List[Review] | None = None,
        **kwargs,
    ) -> None:
        # Initialize shared BaseModel fields first
        super().__init__(**kwargs)

        # Validate user data before assigning attributes
        self._validate(first_name, last_name, email, password)

        # Store the main user attributes
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.password = password
        self.is_admin = is_admin

        # Initialize related collections, defaulting to empty lists
        self.places: List[Place] = places or []
        self.reviews: List[Review] = reviews or []

    def update_profile(
        self,
        first_name: str | None = None,
        last_name: str | None = None,
        email: str | None = None,
        password: str | None = None,
    ) -> None:
        # Update the first name if a new value is provided
        if first_name is not None:
            self._validate(first_name, self.last_name, self.email, self.password)
            self.first_name = first_name

        # Update the last name if a new value is provided
        if last_name is not None:
            self._validate(self.first_name, last_name, self.email, self.password)
            self.last_name = last_name

        # Update the email if a new value is provided
        if email is not None:
            self._validate(self.first_name, self.last_name, email, self.password)
            self.email = email

        # Update the password if a new value is provided
        if password is not None:
            self._validate(self.first_name, self.last_name, self.email, password)
            self.password = password

        # Refresh the modification timestamp after applying updates
        self.touch()

    def add_place(self, place: Place) -> None:
        # Add the place only if it is not already linked to the user
        if place not in self.places:
            self.places.append(place)
            self.touch()

    def add_review(self, review: Review) -> None:
        # Add a new review written by the user
        self.reviews.append(review)
        self.touch()

    @staticmethod
    def _validate(first_name: str, last_name: str, email: str, password: str) -> None:
        # Ensure all required string fields are non-empty
        for field_name, value in [
            ("first_name", first_name),
            ("last_name", last_name),
            ("email", email),
            ("password", password),
        ]:
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{field_name} must be a non-empty string")

        # Perform a basic email format check
        if "@" not in email:
            raise ValueError("email must contain '@'")

    def to_dict(self):
        # Start with the base dictionary representation
        data = super().to_dict()

        # Add user-specific fields
        data.update(
            {
                "first_name": self.first_name,
                "last_name": self.last_name,
                "email": self.email,
                "is_admin": self.is_admin,
                # Password is intentionally excluded from serialization
            }
        )
        return data

__all__ = ["User"]
