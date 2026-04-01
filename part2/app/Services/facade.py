from __future__ import annotations

from math import sqrt
from typing import Any, Dict, List, Optional

from app.models import Amenity, Place, Review, User
from app.persistence import InMemoryRepository

def _haversine_like(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    """Return a rough Euclidean distance approximation for demo purposes."""
    return sqrt((lat1 - lat2) ** 2 + (lng1 - lng2) ** 2)

class HBnBFacade:
    """Facade that coordinates domain logic and repository operations."""

    def __init__(self) -> None:
        # Create one in-memory repository per entity type
        self.users = InMemoryRepository[User]()
        self.places = InMemoryRepository[Place]()
        self.reviews = InMemoryRepository[Review]()
        self.amenities = InMemoryRepository[Amenity]()

    # Users
    def register_user(self, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        # Reject the creation if another user already uses the same email
        if self.users.find_by_fields(email=data["email"]):
            return None

        # Create, store, and serialize the new user
        user = User(**data)
        self.users.save(user)
        return user.to_dict()

    def list_users(self) -> List[Dict[str, Any]]:
        # Return all users as serialized dictionaries
        return [u.to_dict() for u in self.users.list()]

    def get_user(self, user_id: str) -> Optional[Dict[str, Any]]:
        # Retrieve a user by ID and serialize it if found
        user = self.users.get(user_id)
        return user.to_dict() if user else None

    def update_user(
        self, user_id: str, data: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        # Retrieve the target user first
        user = self.users.get(user_id)
        if not user:
            return None

        # Update editable profile fields through the domain method
        user.update_profile(
            first_name=data.get("first_name"),
            last_name=data.get("last_name"),
            email=data.get("email"),
            password=data.get("password"),
        )

        # Update admin status separately if present in the payload
        if "is_admin" in data:
            user.is_admin = data["is_admin"]

        return user.to_dict()

    def delete_user(self, user_id: str) -> bool:
        # Retrieve the user before attempting deletion
        user = self.users.get(user_id)
        if not user:
            return False

        # Delete all places owned by the user
        for place in list(user.places):
            self.delete_place(place.id)

        # Delete all reviews written by the user
        for review in list(user.reviews):
            self.delete_review(review.id)

        # Remove the user from the repository
        return self.users.delete(user_id)

    # Amenities
    def create_amenity(self, data: Dict[str, Any]) -> Dict[str, Any]:
        # Create, store, and serialize a new amenity
        amenity = Amenity(**data)
        self.amenities.save(amenity)
        return amenity.to_dict()

    def list_amenities(self) -> List[Dict[str, Any]]:
        # Return all amenities as serialized dictionaries
        return [a.to_dict() for a in self.amenities.list()]

    def get_amenity(self, amenity_id: str) -> Optional[Dict[str, Any]]:
        # Retrieve an amenity by ID and serialize it if found
        amenity = self.amenities.get(amenity_id)
        return amenity.to_dict() if amenity else None

    def update_amenity(
        self, amenity_id: str, data: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        # Retrieve the amenity before applying updates
        amenity = self.amenities.get(amenity_id)
        if not amenity:
            return None

        # Rename the amenity if a new name was provided
        if "name" in data:
            amenity.rename(data["name"])

        return amenity.to_dict()

    def delete_amenity(self, amenity_id: str) -> bool:
        # Retrieve the amenity before deleting it
        amenity = self.amenities.get(amenity_id)
        if not amenity:
            return False

        # Remove the amenity from every place that references it
        for place in self.places.list():
            if amenity in place.amenities:
                place.amenities.remove(amenity)
                place.touch()

        # Delete the amenity from the repository
        return self.amenities.delete(amenity_id)

    # Places
    def create_place(self, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        # Ensure the referenced owner exists
        owner = self.users.get(data["owner_id"])
        if not owner:
            return None

        # Resolve amenity IDs into Amenity objects
        amenity_objs: List[Amenity] = []
        for amenity_id in data.get("amenity_ids", []):
            amenity = self.amenities.get(amenity_id)
            if not amenity:
                return None
            amenity_objs.append(amenity)

        # Create and store the new place
        place = Place(
            name=data["name"],
            description=data.get("description"),
            price=data["price"],
            latitude=data["latitude"],
            longitude=data["longitude"],
            owner_id=data["owner_id"],
            amenities=amenity_objs,
        )
        self.places.save(place)

        # Link the place to its owner
        owner.add_place(place)

        return self._place_to_dict(place)

    def list_places(
        self, filters: Dict[str, Any] | None = None
    ) -> List[Dict[str, Any]]:
        # Default to an empty filter set when none is provided
        filters = filters or {}

        def matches(place: Place) -> bool:
            # Apply minimum price filter
            if (
                (min_price := filters.get("min_price")) is not None
                and place.price < min_price
            ):
                return False

            # Apply maximum price filter
            if (
                (max_price := filters.get("max_price")) is not None
                and place.price > max_price
            ):
                return False

            # Apply location radius filter when all geographic values are present
            lat = filters.get("lat")
            lng = filters.get("lng")
            radius = filters.get("radius")
            if lat is not None and lng is not None and radius is not None:
                if _haversine_like(lat, lng, place.latitude, place.longitude) > radius:
                    return False

            # Apply amenity filter by checking that all requested amenities exist
            amenity_ids = filters.get("amenity_ids")
            if amenity_ids:
                place_ids = {a.id for a in place.amenities}
                if not set(amenity_ids).issubset(place_ids):
                    return False

            return True

        # Return only the serialized places that match the filter predicate
        return [self._place_to_dict(p) for p in self.places.filter(matches)]

    def get_place(self, place_id: str) -> Optional[Dict[str, Any]]:
        # Retrieve a place by ID and serialize it if found
        place = self.places.get(place_id)
        return self._place_to_dict(place) if place else None

    def update_place(
        self, place_id: str, data: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        # Retrieve the place before updating it
        place = self.places.get(place_id)
        if not place:
            return None

        # Replace the full amenity list if amenity IDs were provided
        if amenity_ids := data.get("amenity_ids"):
            new_amenities: List[Amenity] = []
            for amenity_id in amenity_ids:
                amenity = self.amenities.get(amenity_id)
                if not amenity:
                    return None
                new_amenities.append(amenity)
            place.amenities = new_amenities

        # Collect scalar field updates for the domain update method
        updates: Dict[str, Any] = {}
        for field in ["name", "description", "price", "latitude", "longitude"]:
            if field in data and data[field] is not None:
                updates[field] = data[field]

        place.update_place(**updates)
        return self._place_to_dict(place)

    def delete_place(self, place_id: str) -> bool:
        # Retrieve the place before attempting deletion
        place = self.places.get(place_id)
        if not place:
            return False

        # Remove the place from the owner's collection
        owner = self.users.get(place.owner_id)
        if owner and place in owner.places:
            owner.places.remove(place)

        # Delete every review associated with the place
        for review in list(place.reviews):
            self.delete_review(review.id)

        # Delete the place from the repository
        return self.places.delete(place_id)

    # Reviews
    def create_review(self, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        # Ensure both the user and place exist
        user = self.users.get(data["user_id"])
        place = self.places.get(data["place_id"])
        if not user or not place:
            return None

        # Create and store the new review
        review = Review(
            rating=data["rating"],
            comment=data.get("comment"),
            user_id=data["user_id"],
            place_id=data["place_id"],
        )
        self.reviews.save(review)

        # Link the review to both the user and the place
        user.add_review(review)
        place.add_review(review)

        return review.to_dict()

    def list_reviews(self) -> List[Dict[str, Any]]:
        # Return all reviews as serialized dictionaries
        return [r.to_dict() for r in self.reviews.list()]

    def get_review(self, review_id: str) -> Optional[Dict[str, Any]]:
        # Retrieve a review by ID and serialize it if found
        review = self.reviews.get(review_id)
        return review.to_dict() if review else None

    def update_review(
        self, review_id: str, data: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        # Retrieve the review before updating it
        review = self.reviews.get(review_id)
        if not review:
            return None

        # Apply editable review fields
        review.edit(rating=data.get("rating"), comment=data.get("comment"))
        return review.to_dict()

    def delete_review(self, review_id: str) -> bool:
        # Retrieve the review before attempting deletion
        review = self.reviews.get(review_id)
        if not review:
            return False

        # Remove the review from the related user and place collections
        user = self.users.get(review.user_id)
        place = self.places.get(review.place_id)
        if user and review in user.reviews:
            user.reviews.remove(review)
        if place and review in place.reviews:
            place.reviews.remove(review)

        # Delete the review from the repository
        return self.reviews.delete(review_id)

    # Helpers
    def _place_to_dict(self, place: Place) -> Dict[str, Any]:
        # Build an extended serialized representation for a place
        owner = self.users.get(place.owner_id)
        data = place.to_dict()

        # Include owner details and fully serialized related objects
        data["owner"] = owner.to_dict() if owner else None
        data["reviews"] = [r.to_dict() for r in place.reviews]
        data["amenities"] = [a.to_dict() for a in place.amenities]
        data["average_rating"] = place.average_rating()

        return data

__all__ = ["HBnBFacade"]
