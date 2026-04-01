from __future__ import annotations

from typing import Any, Dict, List

from flask import current_app
from flask_restx import Namespace, Resource, abort, fields

# Namespace for all user-related endpoints
api = Namespace("users", description="User operations")

# Response model (password excluded for security)
user_model = api.model(
    "User",
    {
        "id": fields.String(readonly=True),
        "first_name": fields.String(required=True),
        "last_name": fields.String(required=True),
        "email": fields.String(required=True),
        "is_admin": fields.Boolean(default=False),
    },
)

# Model for creating users (includes password)
user_create_model = api.model(
    "UserCreate",
    {
        "first_name": fields.String(required=True),
        "last_name": fields.String(required=True),
        "email": fields.String(required=True),
        "password": fields.String(required=True),
        "is_admin": fields.Boolean(default=False),
    },
)

# Model for partial updates
user_update_model = api.model(
    "UserUpdate",
    {
        "first_name": fields.String,
        "last_name": fields.String,
        "email": fields.String,
        "password": fields.String,
        "is_admin": fields.Boolean,
    },
)


def _get_facade():
    """Retrieve the configured facade instance."""
    facade = current_app.extensions.get("facade") or current_app.config.get("FACADE")
    if facade is None:
        abort(500, "Facade not configured on application")
    return facade


@api.route("/")
class UserList(Resource):
    """Handle collection-level operations for users."""

    @api.marshal_list_with(user_model)
    def get(self):
        """List all users."""
        facade = _get_facade()
        return facade.list_users()

    @api.expect(user_create_model, validate=True)
    @api.marshal_with(user_model, code=201)
    def post(self):
        """Create a new user."""
        payload = api.payload or {}

        # Check required fields exist
        required_fields = ["first_name", "last_name", "email", "password"]
        missing = [f for f in required_fields if f not in payload]
        if missing:
            abort(400, f"Missing required field(s): {', '.join(missing)}")

        # Clean and validate input
        first_name = (payload.get("first_name") or "").strip()
        last_name = (payload.get("last_name") or "").strip()
        email = (payload.get("email") or "").strip().lower()
        password = (payload.get("password") or "").strip()

        if not first_name:
            abort(400, "first_name is required")
        if not last_name:
            abort(400, "last_name is required")
        if not email:
            abort(400, "email is required")
        if not password:
            abort(400, "password is required")

        user_data = {
            "first_name": first_name,
            "last_name": last_name,
            "email": email,
            "password": password,
            "is_admin": payload.get("is_admin", False),
        }

        facade = _get_facade()
        try:
            user = facade.register_user(user_data)
        except ValueError as exc:
            abort(400, str(exc))

        return user, 201


@api.route("/<string:user_id>")
@api.response(404, "User not found")
class UserItem(Resource):
    """Handle operations on a single user."""

    @api.marshal_with(user_model)
    def get(self, user_id):
        """Retrieve a user by ID."""
        facade = _get_facade()
        user = facade.get_user(user_id)

        if user is None:
            abort(404, "User not found")

        return user

    @api.expect(user_update_model, validate=True)
    @api.marshal_with(user_model)
    def put(self, user_id):
        """Update a user."""
        payload = api.payload or {}

        if not payload:
            abort(400, "No data provided for update")

        update_data = dict(payload)

        # Clean fields if present
        if "first_name" in update_data:
            update_data["first_name"] = (update_data["first_name"] or "").strip()
        if "last_name" in update_data:
            update_data["last_name"] = (update_data["last_name"] or "").strip()
        if "email" in update_data:
            update_data["email"] = (update_data["email"] or "").strip().lower()
        if "password" in update_data:
            update_data["password"] = (update_data["password"] or "").strip()

        facade = _get_facade()
        try:
            user = facade.update_user(user_id, update_data)
        except ValueError as exc:
            abort(400, str(exc))

        if user is None:
            abort(404, "User not found")

        return user


__all__ = ["api"]
