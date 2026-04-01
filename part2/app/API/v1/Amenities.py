from __future__ import annotations

from typing import Any, Dict, List

from flask import current_app
from flask_restx import Namespace, Resource, abort, fields

# Namespace groups all amenity-related routes
api = Namespace("amenities", description="Amenity operations")

# Response model (includes read-only id)
amenity_model = api.model(
    "Amenity",
    {
        "id": fields.String(readonly=True, description="Amenity identifier"),
        "name": fields.String(required=True, description="Amenity name"),
    },
)

# Input model for create/update (no id required)
amenity_create_model = api.model(
    "AmenityCreate",
    {
        "name": fields.String(required=True, description="Amenity name"),
    },
)


def _get_facade():
    """Retrieve the configured facade instance from the Flask app."""
    facade = current_app.extensions.get("facade") or current_app.config.get(
        "FACADE"
    )
    if facade is None:
        abort(500, "Facade not configured on application")
    return facade


@api.route("/")
class AmenityList(Resource):
    """Handle collection-level operations for amenities."""

    @api.marshal_list_with(amenity_model)
    def get(self) -> List[Dict[str, Any]]:
        """Return all amenities."""
        facade = _get_facade()
        return facade.list_amenities()

    @api.expect(amenity_create_model, validate=True)
    @api.marshal_with(amenity_model, code=201)
    def post(self) -> Dict[str, Any]:
        """Create a new amenity."""
        payload = api.payload or {}

        # Clean and validate name
        name = (payload.get("name") or "").strip()
        if not name:
            abort(400, "name is required")

        facade = _get_facade()
        try:
            amenity = facade.create_amenity({"name": name})
        except ValueError as exc:
            abort(400, str(exc))

        return amenity, 201


@api.route("/<string:amenity_id>")
@api.response(404, "Amenity not found")
class AmenityItem(Resource):
    """Handle operations on a single amenity."""

    @api.marshal_with(amenity_model)
    def get(self, amenity_id: str) -> Dict[str, Any]:
        """Retrieve an amenity by ID."""
        facade = _get_facade()
        amenity = facade.get_amenity(amenity_id)

        if amenity is None:
            abort(404, "Amenity not found")

        return amenity

    @api.expect(amenity_create_model, validate=True)
    @api.marshal_with(amenity_model)
    def put(self, amenity_id: str) -> Dict[str, Any]:
        """Update an existing amenity."""
        payload = api.payload or {}

        # Validate name
        name = (payload.get("name") or "").strip()
        if not name:
            abort(400, "name is required")

        facade = _get_facade()
        try:
            amenity = facade.update_amenity(amenity_id, {"name": name})
        except ValueError as exc:
            abort(400, str(exc))

        if amenity is None:
            abort(404, "Amenity not found")

        return amenity


__all__ = ["api"]
