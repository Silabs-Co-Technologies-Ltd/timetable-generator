from __future__ import annotations

from functools import wraps
from typing import Callable, TypeVar

from flask import Blueprint, flash, g, redirect, render_template, request, session, url_for

from app.extensions import db
from app.models import USER_ROLES, User

bp = Blueprint("auth", __name__, url_prefix="/auth")
F = TypeVar("F", bound=Callable[..., object])


def login_required(view: F) -> F:
    @wraps(view)
    def wrapped_view(*args: object, **kwargs: object) -> object:
        if g.user is None:
            flash("Please sign in to continue.", "error")
            return redirect(url_for("auth.login", next=request.full_path if request.query_string else request.path))
        return view(*args, **kwargs)

    return wrapped_view  # type: ignore[return-value]


def roles_required(*roles: str) -> Callable[[F], F]:
    def decorator(view: F) -> F:
        @wraps(view)
        def wrapped_view(*args: object, **kwargs: object) -> object:
            if g.user is None:
                flash("Please sign in to continue.", "error")
                return redirect(url_for("auth.login", next=request.full_path if request.query_string else request.path))
            if g.user.role not in roles:
                return render_template("auth/forbidden.html", allowed_roles=roles), 403
            return view(*args, **kwargs)

        return wrapped_view  # type: ignore[return-value]

    return decorator


@bp.before_app_request
def load_logged_in_user() -> None:
    user_id = session.get("user_id")
    g.user = User.query.get(user_id) if user_id else None
    if g.user is not None and not g.user.is_active:
        session.clear()
        g.user = None


@bp.route("/login", methods=["GET", "POST"])
def login() -> object:
    if request.method == "POST":
        email = request.form["email"].strip().lower()
        password = request.form["password"]
        user = User.query.filter_by(email=email, is_active=True).first()
        if user is None or not user.check_password(password):
            flash("Invalid email or password.", "error")
        else:
            session.clear()
            session["user_id"] = user.id
            flash(f"Welcome back, {user.name}.", "success")
            return redirect(request.args.get("next") or url_for("main.dashboard"))
    return render_template("auth/login.html")


@bp.post("/logout")
def logout() -> object:
    session.clear()
    flash("You have been signed out.", "success")
    return redirect(url_for("auth.login"))


@bp.route("/users", methods=["GET", "POST"])
@roles_required("admin")
def users() -> object:
    if request.method == "POST":
        role = request.form["role"]
        if role not in USER_ROLES:
            flash("Invalid role selected.", "error")
            return redirect(url_for("auth.users"))
        user = User(
            name=request.form["name"].strip(),
            email=request.form["email"].strip().lower(),
            role=role,
            is_active=bool(request.form.get("is_active", "on")),
        )
        user.set_password(request.form["password"])
        db.session.add(user)
        db.session.commit()
        flash("User account created.", "success")
        return redirect(url_for("auth.users"))
    return render_template("auth/users.html", roles=USER_ROLES, users=User.query.order_by(User.name).all())
