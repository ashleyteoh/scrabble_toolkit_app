import os

from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime
import sqlite3

from helpers import apology, login_required

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Connect SQLite database
def connectDB():
    conn = sqlite3.connect("scores.db")
    cur = conn.cursor()

    return conn, cur
            

@app.route("/", methods=["GET", "POST"])
def index():

    # Submit button clicked
    if request.method == "POST":

        # User login validation
        if "loginusername" in request.form:

            username = request.form.get("loginusername")

            # Query database for username
            conn, cur = connectDB()
            cur.execute("SELECT * FROM users WHERE username = ?", [username])
            rows = cur.fetchone()
            
            # Ensure username exists and password is correct
            if not rows or not check_password_hash(rows[2], request.form.get("loginpassword")):
                flash("Invalid username and/or password", "danger")
                return redirect("/")

            # Remember which user has logged in
            session["user_id"] = rows[0]

            # Close db
            conn.close()

            flash("Logged in", "success")
            return render_template("index.html", username=username)

        # User registration
        elif "regusername" in request.form:

            # Ensure password confirmation matches
            if request.form.get("confirmation") != request.form.get("regpassword"):
                flash("Passwords do not match", "danger")
                return redirect("/")
            
            # Ensure password is 8 chars
            if len(request.form.get("regpassword")) < 8:
                flash("Password must be at least 8 characters long", "danger")
                return redirect("/")

            # connect db
            conn, cur = connectDB()
            cur.execute("SELECT * FROM users WHERE username = ?", [request.form.get("regusername")])
            user = cur.fetchall()
            
            # Ensure username isn't taken and login
            if len(user) == 0:

                # Insert new user info into database
                username = request.form.get("regusername")
                password = generate_password_hash(request.form.get("regpassword"))
                cur.execute("INSERT INTO users (username, hash) VALUES (?, ?)", (username, password))
                conn.commit()

                cur.execute("SELECT id FROM users WHERE username = ?", [username])
                id = cur.fetchone()

                # Remember which user has logged in
                session["user_id"] = id[0]
                
                conn.close()

                # Redirect user to home page
                flash("Registered!", "success")
                return render_template("index.html", username=username)

            else:
                flash("Username taken", "danger")
                return redirect("/")

        # Save game into db
        elif "save_names" in request.form:

            total_scores = request.form.get("save_total")
            total_scores = total_scores.replace(",", ", ")

            player_names = request.form.get("save_names")
            player_names = player_names.replace(",", ", ")

            start_time = request.form.get("start_time")
            moves = request.form.get("moves")
            winner = request.form.get("winner")
            tie = request.form.get("tie")


            # print(total_scores[2])

            # get date and end time of game
            date, end_time = find_now()

            # duration of game
            duration = game_duration(start_time, end_time)

            # print("id: ", session['user_id'])
            # print("date: ", date, type(date))
            # print("duration: ", duration, type(duration))
            # print("names: ", player_names, type(player_names))
            # print("scores: ", total_scores, type(total_scores))
            # print("winner: ", winner, type(winner))
            # print("tie: ", tie)

            if winner == None:
                winner = tie

            conn, cur = connectDB()
            cur.execute("INSERT INTO games (user_id, date, time, moves, players, scores, winner) VALUES (?, ?, ?, ?, ?, ?, ?)", (session['user_id'], date, str(duration), moves, player_names, total_scores, winner))
            conn.commit()
            conn.close()

        return render_template("index.html")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        if session.get("user_id") is not None:
            username = profilename()
            return render_template("index.html", username=username)
    return render_template("index.html")



@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to main page
    flash("Logged out", "success")
    return redirect("/")


@app.route("/history", methods=["GET"])
def history():
    if session.get("user_id") is not None:

        username = profilename()

        conn, cur = connectDB()
        cur.execute("SELECT date, time, moves, players, scores, winner FROM games WHERE user_id = ?", [session["user_id"]])
        rows = cur.fetchall()
        # print(rows)

        conn.close

        return render_template("history.html", username=username, rows=rows)

    else:
        if session.get("user_id") is not None:
            username = profilename()
            return render_template("history.html", username=username)
        return render_template("history.html")


@app.route("/checker", methods=["GET", "POST"])
def checker():
    if request.method == "POST":
        word = request.form.get("word").upper()
        # print(word)
        if word == "":
            return render_template("checker.html", msg="emp")

        # read dictionary line by line
        with open("collins.txt", "r") as dictionary:
            for line in dictionary:
                # if word is found in dict
                if word == line.strip():
                    print("Yes!", line)
                    # return valid word and username if logged in
                    if session.get("user_id") is not None:
                        username = profilename()
                        return render_template("checker.html", msg="Yes", word=word, username=username)
                    # return just valid word if not logged in
                    return render_template("checker.html", msg="Yes", word=word)

            # word is not in dict, return invalid word and username
            if session.get("user_id") is not None:
                username = profilename()
                return render_template("checker.html", msg="No", word=word, username=username)
            # return invalid word
            return render_template("checker.html", msg="No", word=word)

    else:
        if session.get("user_id") is not None:
            username = profilename()
            return render_template("checker.html", msg=None, username=username)
        return render_template("checker.html", msg=None)
    

@app.route("/changepassword", methods=["GET", "POST"])
def change():
    if request.method == "POST":
        # get form info
        old = request.form.get("oldpassword")
        new = request.form.get("password")
        confirm = request.form.get("confirmpassword")

        # get current user password from db
        conn, cur = connectDB()
        cur.execute("SELECT hash FROM users WHERE id = ?", [session["user_id"]])
        hash = cur.fetchone()
        # print(hash)

        conn.close()

        # current password validation
        if not check_password_hash(hash[0], old):
            flash("Incorrect current password entered", "danger")
            return redirect("/changepassword")

        # new and confirmed password match validation
        elif new != confirm:
            flash("New passwords do not match", "danger")
            return redirect("/changepassword")

        # new password is not old password
        elif new == old:
            flash("New password cannot be the same as current password", "danger")
            return redirect("/changepassword")
        
        # pass all check, change password in db
        else:
            new = generate_password_hash(new)
            conn, cur = connectDB()
            cur.execute("UPDATE users SET hash = ? WHERE id = ?", (new, session["user_id"]))
            conn.commit()
            conn.close()

            flash("Password changed!", "success")
            return redirect("/changepassword")

    else:
        if session.get("user_id") is not None:
                username = profilename()
                return render_template("change.html", username=username)
        return render_template("change.html")



@app.route("/about", methods=["GET"])
def about():
    if session.get("user_id") is not None:
        username = profilename()
        return render_template("about.html", username=username)
    return render_template("about.html")


def profilename():
    conn, cur = connectDB()
    cur.execute("SELECT username FROM users WHERE id = ?", [session['user_id']])
    user = cur.fetchone()
    username = user[0]
    conn.close()

    return username

def find_now():
    now = datetime.now()
    date = now.strftime("%d/%m/%Y")
    end_time = now.strftime("%H:%M:%S")

    return date, end_time


def game_duration(start, end):
    FMT = '%H:%M:%S'
    tdelta = datetime.strptime(end, FMT) - datetime.strptime(start, FMT)

    return tdelta


def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)
