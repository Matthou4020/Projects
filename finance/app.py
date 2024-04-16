import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required, lookup, usd

# Configure application
app = Flask(__name__)

# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///finance.db")


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/", methods=["GET", "POST"])
@login_required
def index():

    if request.method == "GET":
        # Obtain user's current cash_balance for display
        balance = db.execute("""SELECT cash
                                    FROM users
                                    WHERE id = ?;
                                    """,
                             (session["user_id"]))
        cash_balance = balance[0]["cash"]

        # Find shares owned
        total_shares = db.execute("""SELECT SUM (shares)
                                AS total_shares
                                FROM transactions
                                WHERE user_id = ?
                                AND is_owned = ?;
                                """,
                                  session["user_id"], True)

        # If user has no shares, return template with has_shares set to False
        if total_shares[0]["total_shares"] is None:
            has_shares = False
            return render_template("index.html", has_shares=has_shares, cash_balance=cash_balance, grand_total=cash_balance)

        # Create a variable that says if user currently owns anything.
        if total_shares[0]["total_shares"] is not None:
            total_shares = int(total_shares[0]["total_shares"])
            has_shares = True

            # Get all symbols in which the user has shares:
            symbols = db.execute("""
                        SELECT symbol
                        FROM transactions
                            WHERE user_id = ?
                            AND is_owned = ?
                            GROUP BY symbol;
                            """,
                                 session["user_id"], True)

            # Join each symbol's total of shares in a list
            sums = []
            for symbol in symbols:
                gettotalshares = db.execute("""
                                        SELECT SUM (shares)
                                        AS total_shares
                                        FROM transactions
                                        WHERE symbol = ?
                                        AND user_id = ? ;
                                        """,
                                            symbol["symbol"], session["user_id"])
                sums.append(gettotalshares[0]["total_shares"])

            # current price of each stock
            prices = []
            for symbol in symbols:
                stock = lookup(symbol["symbol"])
                prices.append(stock["price"])

            # total value of each holding
            holding_value = []
            for i in range(len(symbols)):
                holding_value.append(round(sums[i] * prices[i], 2))

            # how many different symbols are there, which have shares?
            index_symbols = []
            for i in range(len(symbols)):
                index_symbols.append(symbols[i]["symbol"])

            # combining for better visual display
            combined = []
            for i in range(len(index_symbols)):
                combined.append({"symbol": index_symbols[i], "share": sums[i],
                                "price": prices[i], "holding_value": holding_value[i]})

            # grand_total for display along cash_balance
            grand_total = round(sum(holding_value) + cash_balance, 2)

            return render_template("index.html", has_shares=has_shares, combined=combined, cash_balance=cash_balance, grand_total=grand_total)


@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    if request.method == "GET":
        return render_template("buy.html")

    elif request.method == "POST":
        symbol = request.form.get("symbol").upper()
        shares = request.form.get("shares")
        if not shares or not symbol:
            return apology("Invalid request. Invalid number of shares or inexistent symbol")

        try:
            shares = int(shares)
        except ValueError:
            return apology("Number of shares has to be a real number")
        if shares < 0:
            return apology("shares must be more than 0")

        if lookup(symbol) is None:
            return apology("Invalid symbol")

        # Check if enough funds
        stock = lookup(symbol)
        total = shares * stock["price"]
        available_funds = db.execute("SELECT cash FROM users WHERE id = ?;", session["user_id"])
        if available_funds[0]["cash"] < total:
            return apology("Not enough funds for this purchase.")

        # update current user's cash balance
        db.execute("""UPDATE users
                        SET cash = cash - ?
                        WHERE id = ?;""",
                   total, session["user_id"])

        # If no entry for this symbol, create transaction entry
        check = db.execute("""
                              SELECT symbol
                              FROM transactions
                              WHERE symbol = ?
                              """,
                           symbol)

        if len(check) < 1:
            db.execute("""INSERT INTO transactions (shares, symbol, price, user_id)
                            VALUES (?, ?, ?, ?);""",
                       shares, symbol, stock["price"], session["user_id"])

        # Otherwise, just update the current entry
        else:
            # add new shares
            db.execute("""UPDATE transactions
                            SET shares = shares + ?
                            WHERE symbol = ?
                            AND user_id = ?;""",
                       shares, symbol, session["user_id"])

        # In both cases, update transactions' status
        db.execute("""UPDATE transactions
                            SET is_owned = ?
                            WHERE symbol = ?
                            AND user_id = ?;""",
                   True, symbol, session["user_id"])

        # Create history entry WITH THE NUMBER OF SHARES
        # THAT WERE BOUGHT JUST NOW
        db.execute("""
                   INSERT INTO history
                   (symbol, shares, transaction_id, user_id, is_owned, price)
                   SELECT transactions.symbol, ?,
                   transactions.id, users.id, transactions.is_owned, ?
                   FROM transactions, users
                   WHERE transactions.symbol = ?
                   AND users.id = ?
                   AND transactions.user_id = ? ;
                   """,
                   shares, total, stock["symbol"], session["user_id"], session["user_id"]
                   )

        return redirect("/")


@app.route("/history", methods=["GET"])
@login_required
def history():
    getstock = db.execute("""
                       SELECT symbol
                       FROM history
                       WHERE user_id = ?;
                       """,
                          session["user_id"])

    getshares = db.execute("""
                        SELECT shares
                        FROM history
                        WHERE user_id = ?;
                        """,
                           session["user_id"])

    gettime = db.execute("""
                      SELECT time
                      FROM history
                      WHERE user_id = ?;
                      """,
                         session["user_id"])

    getstatus = db.execute("""
                        SELECT is_owned
                        FROM history
                        WHERE user_id = ?;
                        """,
                           session["user_id"])
    getprices = db.execute("""
                        SELECT price
                        FROM history
                        WHERE user_id = ?;
                        """,
                           session["user_id"])

    prices = []
    for i in range(len(getprices)):
        prices.append(getprices[i]["price"])

    shares = []
    for i in range(len(getshares)):
        shares.append(getshares[i]["shares"])

    times = []
    for i in range(len(gettime)):
        times.append(gettime[i]["time"])

    stocks = []
    for i in range(len(getstock)):
        stocks.append(getstock[i]["symbol"])

    status = []
    for i in range(len(getstatus)):
        status.append(getstatus[i]["is_owned"])

    combined = []
    for i in range(len(stocks)):
        combined.append({"stock": stocks[i], "times": times[i], "shares": shares[i], "status": status[i], "prices": prices[i]})

    return render_template("history.html", combined=combined)


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
        rows = db.execute(
            """SELECT *
            FROM users
            WHERE username = ?
            """,
            request.form.get("username")
        )

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(
            rows[0]["hash"], request.form.get("password")
        ):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

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
    if request.method == "GET":
        return render_template("quote.html")

    if request.method == "POST":
        symbol = request.form.get("symbol")
        stock = lookup(symbol)
        if stock is None:
            return apology("Symbol not found")
        return render_template("quoted.html", stock=stock)


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("register.html")

    if request.method == "POST":
        # Acess data
        username = request.form.get("username")
        password = request.form.get("password")
        password_verification = request.form.get("confirmation")

        # If blank field, apology
        if username == "" or password == "":
            return apology("User must provide a username and a password")

        # If passwords don't match, apology
        if password != password_verification:
            return apology("Passwords do not match")

        # INSERT new user checking for duplicates and password hash into users table
        hash = generate_password_hash(password)
        try:
            db.execute("INSERT INTO users (username, hash) VALUES (?, ?);", username, hash)
        except ValueError:
            return apology("Username already exists")
        id = db.execute("SELECT id FROM users WHERE username = ?;", username)
        session["user_id"] = id[0]["id"]
        return redirect("/")


@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    if request.method == "GET":
        stocks = db.execute("""
                            SELECT symbol
                            FROM transactions
                            WHERE user_id = ?
                            GROUP BY symbol;
                            """,
                            session["user_id"])

        return render_template("sell.html", stocks=stocks)

    if request.method == "POST":
        symbol = request.form.get("symbol").upper()
        shares = request.form.get("shares")
        shares = int(shares)

        if shares < 1:
            return apology("Invalid number of shares")

        previous_shares = db.execute("""
                            SELECT shares
                            FROM transactions
                            WHERE user_id = ?
                            AND symbol = ?;
                            """,
                                     session["user_id"], symbol)

        if not symbol:
            return apology("Invalid input")
        if previous_shares is None:
            return apology("No shares to sell")

        previous_shares = int(previous_shares[0]["shares"])
        if shares > previous_shares:
            return apology("Not enough shares to sell")

        current_value = lookup(symbol)
        total_value = shares * current_value["price"]

        # Update cash_balance
        db.execute("""
                    UPDATE users
                    SET cash = cash + ?
                    WHERE id = ?;
                    """,
                   total_value, session["user_id"])

        # Create history entry
        db.execute("""
                   INSERT INTO history
                   (symbol, shares, user_id, is_owned, price)
                   SELECT transactions.symbol, ? ,
                   users.id, ?, ?
                   FROM transactions, users
                   WHERE transactions.symbol = ?
                   AND users.id = ?
                   GROUP BY symbol;
                   """,
                   shares, False, total_value, symbol, session["user_id"]
                   )

        # Update share numbers to 0
        actualized_shares = previous_shares - shares
        db.execute("""
                   UPDATE transactions
                   SET shares = ?
                   WHERE user_id = ?
                   AND symbol = ?
                   """,
                   actualized_shares, session["user_id"], symbol)

        return redirect("/")
