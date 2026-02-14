from flask import render_template, request, session, redirect, current_app
from bson import ObjectId
from . import tambola_bp

# ---------- LOGIN ----------
@tambola_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        login_id = request.form["login_id"].strip()
        password = request.form["password"].strip()

        user = current_app.bank_db.users.find_one({
            "login_id": login_id,
            "password": password
        })

        if not user:
            return render_template("tambola/tambola_login.html", error="Invalid credentials")

        session["tambola_user"] = str(user["_id"])
        session["tambola_name"] = user["login_id"]

        current_app.bank_db.tambola_wallet.update_one(
            {"user_id": user["_id"]},
            {"$setOnInsert": {"balance": 0}},
            upsert=True
        )

        return redirect("/tambola/lobby")

    return render_template("tambola/tambola_login.html")


# ---------- LOBBY ----------
@tambola_bp.route("/lobby")
def lobby():
    if "tambola_user" not in session:
        return redirect("/tambola/login")

    wallet = current_app.bank_db.tambola_wallet.find_one(
        {"user_id": ObjectId(session["tambola_user"])}
    )

    return render_template(
        "tambola/tambola_lobby.html",
        username=session["tambola_name"],
        balance=wallet["balance"]
    )


# ---------- ADD ----------
@tambola_bp.route("/wallet/add", methods=["POST"])
def add_money():
    amt = int(request.form["amount"])
    uid = ObjectId(session["tambola_user"])

    current_app.bank_db.users.update_one(
        {"_id": uid},
        {"$inc": {"balance": -amt}}
    )

    current_app.bank_db.tambola_wallet.update_one(
        {"user_id": uid},
        {"$inc": {"balance": amt}}
    )

    return redirect("/tambola/lobby")


# ---------- PLAY ----------
@tambola_bp.route("/play")
def play():
    if "tambola_user" not in session:
        return redirect("/tambola/login")

    wallet = current_app.bank_db.tambola_wallet.find_one(
        {"user_id": ObjectId(session["tambola_user"])}
    )

    if wallet["balance"] < 10:
        return redirect("/tambola/lobby")

    return render_template(
        "tambola/tambola_game.html",
        username=session["tambola_name"],
        balance=wallet["balance"]
    )
