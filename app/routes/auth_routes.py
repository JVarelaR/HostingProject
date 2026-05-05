from flask import Blueprint, app, render_template, request, redirect, session, flash
import requests, os
from services.auth_services import t_api_get, t_api_post, t_api_put, t_api_delete, refresh_token
from services.db_services import insert_user
import psycopg2
from psycopg2.extras import RealDictCursor

auth_bp = Blueprint('auth', __name__)
AUTH_URL = os.getenv('AUTH_URL')


@auth_bp.route('/register', methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template('register.html')

    email = request.form["email"]
    password = request.form["password"]
    username = request.form["username"]
    jso = {"email": email, "name": username, "password":password}
    res = requests.post(
        f"{AUTH_URL}/signup-direct",
        json=jso
    )


    if not res.ok:
        print(res.json())
        flash(res.json()["message"], "error")
        return render_template("register.html", emailForm=email, usernameForm=username)


    # Login automático
    login_res = requests.post(
        f"{AUTH_URL}/login",
        json={"email": email, "password": password}
    )

    data = login_res.json()

    session["access_token"] = data["accessToken"]
    session["refresh_token"] = data["refreshToken"]
    session["email"] = email
    session["username"] = username


    # Insertar datos en la base de datos
    insert_user(username, email)

    return redirect("/projects")




@auth_bp.route('/login', methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        res = requests.post(
            f"{AUTH_URL}/login",
            json={"email": email, "password": password}
        )

        if not res.ok:
            print(res.json())
            flash(res.json()["message"], "error")
            return render_template("login.html", emailForm=email)

        data = res.json()
        session["access_token"] = data["accessToken"]
        session["refresh_token"] = data["refreshToken"]
        session["email"] = email
        session["username"] = "username" #TODO Obtener username real del usuario desde la base de datos

        return redirect("/projects")

    return render_template("login.html")


@auth_bp.route('/logout')
def logout():
    res = t_api_post(f"{AUTH_URL}/logout")
    session.clear() 

    return render_template("login.html")