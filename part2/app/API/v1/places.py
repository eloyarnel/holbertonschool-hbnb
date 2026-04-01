from __future__ import annotations

from typing import Any, Dict, List

from flask import current_app
from flask_restx import Namespace, Resource, abort, fields

# Namespace for all place-related endpoints
api = Namespace("places", description="Place operations")

# Nested models for related data
amenity_summary = api.model(
    "AmenitySummary",
    {
        "id": fields.String,
        "name": fields.String,
    },
)

owner_summary = api.model(
    "OwnerSummary",
    {
        "id": fields.String,
        "first_name": fields.String,
        "last_name": fields.String,
        "email": fields.String,
    },
)

review_summary = api.model(
    "ReviewSummary",
    {
        "id": fields.String,
        "rating": fields.Integer,
        "comment": fields.String,
        "user_id": fields.String,
    },
)

# Full place model with nested relationships
place_model = api.model(
    "Place",
    {
        "id": fields.String(readonly=True),
        "name": fields.String(required=True),
        "description": fields.String,
        "price": fields.Float(required=True),
        "latitude": fields.Float(required=True),
        "longitude": fields.Float(required=True),
        "owner_id": fields.String(required=True),
        "owner": fields.Nested(owner_summary),
        "amenities": fields.List(fields.Nested(amenity_summary)),
        "reviews": fields.List(fields.Nested(review_summary)),
        "average_rating": fields.Float,
    },
)

# Model for creating a place
place_create_model = api.model(
    "PlaceCreate",
    {
        "name": fields.String(required=True),
        "description": fields.String,
        "price": fields.Float(required=True),
        "latitude": fields.Float(required=True),
        "longitude": fields.Float(required=True),
        "owner_id": fields.String(required=True),
        "amenity_ids": fields.List(fields.String),
    },
)

# Model for partial updates
place_update_model = api.model(
    "PlaceUpdate",
    {
        "name": fields.String,
        "description": fields.String,
        "price": fields.Float,
        "latitude": fields.Float,
        "longitude": fields.Float,
        "amenity_ids": fields.List(fields.String),
    },
)

# Query parameters for filtering places
list_parser = api.parser()
list_parser.add_argument("min_price", type=float, location="args")
list_parser.add_argument("max_price", type=float, location="args")
list_parser.add_argument("lat", type=float, location="args")
list_parser.add_argument("lng", type=float, location="args")
list_parser.add_argument("radius", type=float, location="args")
list_parser.add_argument("amenity_id", type=str, action="append", location="args")


def _get_facade():
    """Retrieve the configured facade instance."""
    facade = current_app.extensions.get("facade") or current_app.config.get("FACADE")
    if facade is None:
        abort(500, "Facade not configured on application")
    return facade


@api.route("/")
class PlaceList(Resource):
    """Handle collection-level operations for places."""

    @api.expect(list_parser)
    @api.marshal_list_with(place_model)
    def get(self):
        """List places with optional filters."""
        args = list_parser.parse_args()

        # Build filter dictionary excluding None values
        filters = {
            k: v for k, v in args.items()
            if v is not None and k != "amenity_id"
        }

        # Convert amenity_id → amenity_ids
        if args.get("amenity_id"):
            filters["amenity_ids"] = args.get("amenity_id")

        facade = _get_facade()
        return facade.list_places(filters)

    @api.expect(place_create_model, validate=True)
    @api.marshal_with(place_model, code=201)
    def post(self):
        """Create a new place."""
        payload = api.payload or {}

        # Check required fields exist
        required_fields = ["name", "price", "latitude", "longitude", "owner_id"]
        missing = [f for f in required_fields if f not in payload]
        if missing:
            abort(400, f"Missing required field(s): {', '.join(missing)}")

        # Clean and validate strings
        name = (payload.get("name") or "").strip()
        owner_id = (payload.get("owner_id") or "").strip()

        if not name:
            abort(400, "name is required")
        if not owner_id:
            abort(400, "owner_id is required")

        place_data = {
            "name": name,
            "description": (payload.get("description") or "").strip(),
            "price": payload.get("price"),
            "latitude": payload.get("latitude"),
            "longitude": payload.get("longitude"),
            "owner_id": owner_id,
            "amenity_ids": payload.get("amenity_ids") or [],
        }

        facade = _get_facade()
        try:
            place = facade.create_place(place_data)
        except ValueError as exc:
            abort(400, str(exc))

        if place is None:
            abort(404, "Owner or amenities not found")

        return place, 201


@api.route("/<string:place_id>")
@api.response(404, "Place not found")
class PlaceItem(Resource):
    """Handle operations on a single place."""

    @api.marshal_with(place_model)
    def get(self, place_id):
        """Retrieve a place by ID."""
        facade = _get_facade()
        place = facade.get_place(place_id)

        if place is None:
            abort(404, "Place not found")

        return place

    @api.expect(place_update_model, validate=True)
    @api.marshal_with(place_model)
    def put(self, place_id):
        """Update a place."""
        payload = api.payload or {}

        if not payload:
            abort(400, "No data provided for update")

        update_data = dict(payload)

        # Clean name if provided
        if "name" in update_data:
            update_data["name"] = (update_data.get("name") or "").strip()
            if not update_data["name"]:
                abort(400, "name is required")

        facade = _get_facade()
        try:
            place = facade.update_place(place_id, update_data)
        except ValueError as exc:
            abort(400, str(exc))

        if place is None:
            abort(404, "Place not found")

        return place


__all__ = ["api"]
