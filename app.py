import os
import re
import sqlite3
from datetime import datetime
from functools import wraps

from flask import (
    Flask,
    flash,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from werkzeug.security import check_password_hash, generate_password_hash

from database.db import (
    create_user,
    get_db,
    get_user_by_email,
    get_user_by_id,
    init_db,
    seed_db,
    update_user_name,
    update_user_password,
)

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev-secret-change-in-production")
app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"

with app.app_context():
    init_db()
    seed_db()


# ------------------------------------------------------------------ #
# Validation                                                          #
# ------------------------------------------------------------------ #

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

COMMON_PASSWORDS = {
    "password", "password1", "12345678", "qwerty123",
    "abc12345", "letmein1", "iloveyou1", "admin123",
}


def validate_password(password):
    """Return an error message, or None when the password is strong enough."""
    if len(password) < 8:
        return "Password must be at least 8 characters."
    if not (re.search(r"[A-Za-z]", password) and re.search(r"\d", password)):
        return "Password must include at least one letter and one number."
    if password.lower() in COMMON_PASSWORDS:
        return "That password is too common. Please choose another one."
    return None


def validate_registration(name, email, password):
    """Return an error message, or None when the details are valid."""
    if not name:
        return "Please enter your name."
    if not EMAIL_RE.match(email):
        return "Please enter a valid email address."
    return validate_password(password)


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if "user_id" not in session:
            flash("Please sign in to continue.")
            return redirect(url_for("login"))
        return view(*args, **kwargs)
    return wrapped


# ------------------------------------------------------------------ #
# Routes                                                              #
# ------------------------------------------------------------------ #

@app.route("/")
def landing():
    return render_template("landing.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        error = validate_registration(name, email, password)
        if error is None and get_user_by_email(email):
            error = "An account with that email already exists."
        if error:
            return render_template("register.html", error=error, name=name, email=email)

        try:
            create_user(name, email, password)
        except sqlite3.IntegrityError:
            return render_template(
                "register.html",
                error="An account with that email already exists.",
                name=name,
                email=email,
            )

        flash("Account created. Please sign in.")
        return redirect(url_for("login"))

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        user = get_user_by_email(email)
        if user is None or not check_password_hash(user["password_hash"], password):
            return render_template(
                "login.html", error="Invalid email or password.", email=email
            )

        session.clear()
        session["user_id"] = user["id"]
        session["user_name"] = user["name"]
        return redirect(url_for("landing"))

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("landing"))


@app.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        if not name:
            flash("Please enter your name.")
        else:
            update_user_name(session["user_id"], name)
            session["user_name"] = name
            flash("Profile updated.")
        return redirect(url_for("profile"))

    user = get_user_by_id(session["user_id"])
    member_since = datetime.strptime(
        user["created_at"][:19], "%Y-%m-%d %H:%M:%S"
    ).strftime("%d %b %Y")
    return render_template("profile.html", user=user, member_since=member_since)


@app.route("/profile/password", methods=["POST"])
@login_required
def update_password():
    current_password = request.form.get("current_password", "")
    new_password = request.form.get("new_password", "")

    user = get_user_by_id(session["user_id"])
    if not check_password_hash(user["password_hash"], current_password):
        flash("Current password is incorrect.")
        return redirect(url_for("profile"))

    error = validate_password(new_password)
    if error:
        flash(error)
        return redirect(url_for("profile"))

    update_user_password(user["id"], generate_password_hash(new_password))
    flash("Password updated.")
    return redirect(url_for("profile"))


@app.route("/terms")
def terms():
    return render_template("terms.html")


@app.route("/privacy")
def privacy():
    return render_template("privacy.html")


# ------------------------------------------------------------------ #
# Placeholder routes — students will implement these                  #
# ------------------------------------------------------------------ #

@app.route("/expenses/add")
def add_expense():
    return "Add expense — coming in Step 7"


@app.route("/expenses/<int:id>/edit")
def edit_expense(id):
    return "Edit expense — coming in Step 8"


@app.route("/expenses/<int:id>/delete")
def delete_expense(id):
    return "Delete expense — coming in Step 9"


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)
