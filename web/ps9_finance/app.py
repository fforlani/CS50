import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime
import json

from helpers import apology, login_required, lookup, usd, total, checkPassword

# Configure application
app = Flask(__name__)
# make this function visible in jinja code
app.jinja_env.globals.update(usd=usd)
app.jinja_env.globals.update(total=total)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///finance.db")

# Make sure API key is set
if not os.environ.get("API_KEY"):
    raise RuntimeError("API_KEY not set")


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/")
@login_required
def index():
    """Show portfolio of stocks"""
    # retrieve stocks purhased by user and the remaining cash, computing also the currentPrice to show and not the transaction price
    stocks = db.execute("SELECT symbol,name,shares FROM portfolio WHERE user_id = ? ORDER BY symbol", session["user_id"])
    # login is required, so session store the current user and i can retrieve cash info
    cash = db.execute("SELECT cash FROM users WHERE id = ?", session["user_id"])[0]['cash']
    for stock in stocks:
        stock['currentPrice'] = lookup(stock['symbol'])['price']
    return render_template("index.html", data=stocks, cash=cash)


@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    """Buy shares of stock"""

    # method is get when user click on buy button: i jave to display buy page. Otherwise it means user purchased an item
    if request.method == "GET":
        return render_template("buy.html")

    # checking integrity of user input
    symbol = request.form.get("symbol").upper()
    data = lookup(symbol)
    if not symbol or not data:
        return apology("Enter a valid symbol")
    shares = request.form.get("shares")
    if not shares:
        return apology("Enter a number of shares")
    shares = int(shares)
    if shares <= 0:
        return apology("Enter a positive number of shares")
    # checking that user has enough money to purchase the stock
    cash = db.execute("SELECT cash FROM users where id=?", session["user_id"])[0]['cash']
    if data['price']*shares > cash:
        return apology("Sorry, you don't have enough money")

    # update db: user cash , insert transaction in mktMovement , change/insert shares of the required stock
    db.execute("UPDATE users SET cash=? WHERE id=?", cash-data['price']*shares, session["user_id"])
    db.execute("INSERT INTO mktMovement (user_id, symbol, price, date, shares) VALUES (?,?,?,?,?)", session["user_id"], symbol, data['price'], datetime.now(), shares)
    # check if the stock is in the portfolio, if yes update existing records, otherwise add a new row
    oldShares = db.execute("SELECT shares FROM portfolio WHERE user_id=? AND symbol=?", session["user_id"], symbol)
    if oldShares:
        db.execute("UPDATE portfolio SET shares=? WHERE user_id=? AND symbol=?", oldShares[0]['shares']+shares, session["user_id"], symbol)
    else:
        db.execute("INSERT INTO portfolio (user_id, symbol, shares, name) VALUES (?,?,?,?)", session["user_id"], symbol, shares, data['name'])
    flash("Bought!")
    return redirect("/")

@app.route("/history")
@login_required
def history():
    """Show history of transactions"""
    # retrieve all user transaction adding type information (if the transaction is a purchase or not)
    history = db.execute("SELECT symbol,shares,price,date FROM mktMovement WHERE user_id = ? ORDER BY date DESC", session['user_id'])
    for movement in history:
        movement['type'] = 'Purchase' if movement['shares'] > 0 else 'Sold'
        movement['shares'] = abs(movement['shares'])
    return render_template("history.html", data = history)


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]
        flash("Successful login")
        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/quote", methods=["GET", "POST"])
@login_required
def quote():
    """Get stock quote."""

    # method is get when user click on quote button: i have to display quote page. Otherwise I have o display stock info
    if request.method == "GET":
        return render_template("quote.html")

    symbol = request.form.get("symbol").upper()
    data = lookup(symbol)
    if not symbol or not data:
        return apology("Enter a valid symbol")

    return render_template("quoted.html", data=data)


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    # method is get when user click on register button: i have to display register page. Otherwise means user submitted the form for registring
    if request.method == "GET":
        return render_template("register.html")

    #checking user input validity
    username = request.form.get("username")
    id = db.execute("SELECT * FROM users WHERE username=?", username)
    if not username or id:
        return apology("Enter a valid username")
    password = request.form.get("password")
    confirmation = request.form.get("confirmation")
    if not password or password != confirmation or not checkPassword(password):
        return apology("Enter a valid password")

    # inserting the new user in the db. password is saved as hashed
    db.execute("INSERT INTO users (username,hash) VALUES (?,?)", username, generate_password_hash(password))
    user_id = db.execute("SELECT id FROM users WHERE username=?", username)[0]['id']
    session["user_id"] = user_id    #user login
    flash("Registered!")
    return redirect("/")


@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    """Sell shares of stock"""

    stocks = db.execute("SELECT symbol,shares FROM portfolio WHERE user_id = ?", session["user_id"])

    # method is get when user click on sell button: i have to display sell page. Otherwise means user submitted form to sell stock
    if request.method == "GET":
        return render_template("sell.html", stocks = stocks)

    # checing user input validity
    symbol = request.form.get("symbol")
    if not symbol:
        return apology("Enter a valid symbol")
    symbol = symbol.upper()
    data = lookup(symbol)
    if symbol not in [stock['symbol'] for stock in stocks] or not data:
        return apology("Enter a valid symbol")
    oldShares = db.execute("SELECT shares FROM portfolio WHERE user_id = ? AND symbol = ?", session["user_id"], symbol)[0]['shares']
    shares = request.form.get("shares")
    if not shares:
        return apology("Enter a valid number of shares")
    shares = int(shares)
    if  shares <= 0 or shares > oldShares:
        return apology("Enter a valid number of shares")

    # sell the required number of stocks updating user cash, inserting new transaction in mktMovement and updating existing shares in portfolio
    cash = db.execute("SELECT cash FROM users where id=?", session["user_id"])[0]['cash']
    db.execute("UPDATE users SET cash=? WHERE id=?", cash+data['price']*shares, session["user_id"])
    # mktMovement stores selling transaction as a negative number of shares
    db.execute("INSERT INTO mktMovement (user_id, symbol, price, date, shares) VALUES (?,?,?,?,?)", session["user_id"], symbol, data['price'], datetime.now(), -shares)
    if shares == oldShares:
        db.execute("DELETE FROM portfolio WHERE user_id = ? AND symbol=?", session['user_id'], symbol)
    else:
        db.execute("UPDATE portfolio SET shares=? WHERE user_id=? AND symbol=?", oldShares-shares, session["user_id"], symbol)
    flash("Sold!")
    return redirect("/")

@app.route("/private", methods=["GET", "POST"])
@login_required
def privateArea():

    if request.method == "GET":
        return render_template("private.html")

    #submit button pass the info if the user wants to add cash or change password
    action = request.form.get("button")
    if action == "cash":
        amount = request.form.get("amount")
        if not amount:
            return apology("Enter an amount of cash")
        amount = int(amount)
        cash = db.execute("SELECT cash FROM users where id=?", session["user_id"])[0]['cash']
        db.execute("UPDATE users SET cash=? WHERE id=?", cash+amount, session["user_id"])
        flash("Cash added")
        return redirect("/private")

    elif action == "reset":
        oldPassword = request.form.get("oldPassword")
        hashed = db.execute("SELECT * FROM users WHERE id = ?", session['user_id'])[0]['hash']
        if not oldPassword or not check_password_hash(hashed, oldPassword):
            return apology("Enter the correct current password")
        newPassword = request.form.get("newPassword")
        confirmation = request.form.get("confirmation")
        if not newPassword or not confirmation or newPassword != confirmation:
            return apology("New password and confirmation must agree")
        if not checkPassword(newPassword):
            return apology("Enter a valid password")

        db.execute("UPDATE users SET hash = ? WHERE id = ?", generate_password_hash(newPassword), session['user_id'])
        flash("Password changed")
        return redirect("/private")