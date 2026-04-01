from __future__ import annotations

from . import BaseModel

class Review(BaseModel):
    """Represents a review in the domain layer."""

    def __init__(
        self, rating: int, comment: str, user_id: str, place_id: str, **kwargs
    ) -> None:
        # Initialize shared BaseModel fields first
        super().__init__(**kwargs)

        # Validate review data before storing it
        self._validate(rating, comment, user_id, place_id)

        # Store the review attributes
        self.rating = rating
        self.comment = comment
        self.user_id = user_id
        self.place_id = place_id

    def edit(self, rating: int | None = None, comment: str | None = None) -> None:
        # Update the rating if a new value is provided
        if rating is not None:
            self._validate(
                rating,
                comment or self.comment,
                self.user_id,
                self.place_id,
            )
            self.rating = rating

        # Update the comment if a new value is provided
        if comment is not None:
            self.comment = comment

        # Refresh the modification timestamp after changes
        self.touch()

    @staticmethod
    def _validate(rating: int, comment: str, user_id: str, place_id: str) -> None:
        # Rating must be an integer between 1 and 5
        if rating is None or not (1 <= rating <= 5):
            raise ValueError("rating must be between 1 and 5")

        # Comment must be a non-empty string
        if not isinstance(comment, str) or not comment.strip():
            raise ValueError("comment must be a non-empty string")

        # User ID must be a non-empty string
        if not isinstance(user_id, str) or not user_id.strip():
            raise ValueError("user_id must be a non-empty string")

        # Place ID must be a non-empty string
        if not isinstance(place_id, str) or not place_id.strip():
            raise ValueError("place_id must be a non-empty string")

    def to_dict(self):
        # Start with the base dictionary representation
        data = super().to_dict()

        # Add review-specific fields
        data.update(
            {
                "rating": self.rating,
                "comment": self.comment,
                "user_id": self.user_id,
                "place_id": self.place_id,
            }
        )
        return data

__all__ = ["Review"]
