from __future__ import annotations

from statistics import mean
from typing import List, Optional

from . import BaseModel
from .amenity import Amenity
from .review import Review


class Place(BaseModel):
    """Place domain entity."""

    def __init__(
        self,
        name: str,
        description: str | None,
        price: float,
        latitude: float,
        longitude: float,
        owner_id: str,
        amenities: Optional[List[Amenity]] = None,
        reviews: Optional[List[Review]] = None,
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)
        self._validate(name, price, latitude, longitude, owner_id)
        self.name = name
        self.description = description
        self.price = price
        self.latitude = latitude
        self.longitude = longitude
        self.owner_id = owner_id
        self.amenities: List[Amenity] = amenities or []
        self.reviews: List[Review] = reviews or []

    def add_amenity(self, amenity: Amenity) -> None:
        if amenity not in self.amenities:
            self.amenities.append(amenity)
            self.touch()

    def remove_amenity(self, amenity: Amenity) -> None:
        if amenity in self.amenities:
            self.amenities.remove(amenity)
            self.touch()

    def add_review(self, review: Review) -> None:
        self.reviews.append(review)
        self.touch()

    def average_rating(self) -> float | None:
        if not self.reviews:
            return None
        return mean([r.rating for r in self.reviews])

    def update_place(
        self,
        name: str | None = None,
        description: str | None = None,
        price: float | None = None,
        latitude: float | None = None,
        longitude: float | None = None,
    ) -> None:
        if name is not None:
            self._validate(name, price or self.price, latitude or self.latitude, longitude or self.longitude, self.owner_id)
            self.name = name
        if description is not None:
            self.description = description
        if price is not None:
            self._validate(self.name, price, self.latitude, self.longitude, self.owner_id)
            self.price = price
        if latitude is not None:
            self._validate(self.name, self.price, latitude, self.longitude, self.owner_id)
            self.latitude = latitude
        if longitude is not None:
            self._validate(self.name, self.price, self.latitude, longitude, self.owner_id)
            self.longitude = longitude
        self.touch()

    @staticmethod
    def _validate(name: str, price: float, latitude: float, longitude: float, owner_id: str) -> None:
        if not isinstance(name, str) or not name.strip():
            raise ValueError("name must be a non-empty string")
        if price is None or price < 0:
            raise ValueError("price must be a non-negative number")
        if latitude is None or not (-90 <= latitude <= 90):
            raise ValueError("latitude must be between -90 and 90")
        if longitude is None or not (-180 <= longitude <= 180):
            raise ValueError("longitude must be between -180 and 180")
        if not isinstance(owner_id, str) or not owner_id.strip():
            raise ValueError("owner_id must be a non-empty string")

    def to_dict(self):
        data = super().to_dict()
        data.update(
            {
                "name": self.name,
                "description": self.description,
                "price": self.price,
                "latitude": self.latitude,
                "longitude": self.longitude,
                "owner_id": self.owner_id,
                "amenities": [a.to_dict() for a in self.amenities],
                "reviews": [r.to_dict() for r in self.reviews],
                "average_rating": self.average_rating(),
            }
        )
        return data

__all__ = ["Place"]
