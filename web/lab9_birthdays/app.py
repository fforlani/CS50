import os

from cs50 import SQL
from flask import Flask, flash, jsonify, redirect, render_template, request, session

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///birthdays.db")

days = range(1, 32)
months = range(1, 13)

@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":

        # TODO: Add the user's entry into the database
        name = request.form.get("name")
        day = request.form.get("day")
        month = request.form.get("month")

        if not name:
            return render_template("error.html", message="enter a valid name")
        if not day or int(day) not in days or not month or int(month) not in months:
            return render_template("error.html", message="enter a valid date")

        birthday = day+"/"+month
        db.execute("INSERT INTO bd (name, birthday) VALUES (?,?)", name, birthday)
        return redirect("/")

    else:

        # TODO: Display the entries in the database on index.html
        data = db.execute("SELECT name,birthday FROM bd")
        return render_template("index.html", days=days, months=months, data=data)