from data.models import *
from data.auth import login_manager, AuthUser

from flask_login import current_user, login_user
from flask import Flask, render_template, request, redirect, flash
from secrets import token_urlsafe


app = Flask(__name__)
login_manager.init_app(app)
app.config['SECRET_KEY'] = token_urlsafe(16)


@app.route("/", methods=["GET"])
def index():
    user = current_user
    if user.is_authenticated:
        clients = Client.get_by_user(user.id)
        return render_template("index.html", user=user, clients=clients)
    return render_template("index.html", user=None, clients=[])


@app.route("/profile/login", methods=["POST", "GET"])
def profile_login():
    if request.method == "GET":
        if current_user.is_authenticated:
            return render_template(
                "login.html", current_user_name=f"Вы авторизированны, {current_user.id}"
            )
        return render_template("login.html", )

    password = request.form.get("password")
    login = request.form.get("login")

    user_pk = User.exists(login=login, password=password)
    if user_pk:
        login_user( AuthUser(user_pk) )
        return redirect( "/" )

    flash("Неверный логин или пароль")
    return redirect("/profile/login")


@app.route("/profile/register", methods=["POST", "GET"])
def profile_register():
    if request.method == "GET":
        return render_template("register.html", )

    password = request.form.get("password")
    login = request.form.get("login")

    fio = ' '.join([
        request.form.get("name_1"),
        request.form.get("name_2"),
        request.form.get("name_3")
    ])
    if len(password) < 6:
        flash("Пароль должен состоять минимум из 6 символов")
        return redirect("/profile/register")

    user = User.check_login(login)
    if user:
        flash("Логин занят")
        return redirect("/profile/register")

    User.create(True, fio=fio, password=password, login=login,)
    flash("Аккаунт создан!")
    return redirect("/profile/login")


@app.route("/clients/new", methods=["POST"])
def new_client():
    if not current_user.is_authenticated:
        return redirect('/')
    user = User.get_by_pk( current_user.id )
    Client.create(
        True,
        fio_user=user[0],
        status=0
    )
    return redirect('/')


@app.route("/clients/update", methods=["POST"])
def update_client():
    if not current_user.is_authenticated:
        return redirect('/')

    user = User.get_by_pk( current_user.id )
    data = request.form.to_dict()

    if not Client.check_user(data["id"], user[0]):
        return redirect('/')

    for key, value in data.items():
        if not data[key]:
            data[key] = "NULL"
        elif key not in ('status', ):
            data[key] = f'"{data[key].strip()}"'

    Client.update(
        data["id"],
        sql_code=f"""
        "firstname"={data["firstname"]},
        "lastname"={data["lastname"]},
        "fathername"={data["fathername"]},
        "account_number"={data["account_number"]},
        "inn_number"={data["inn_number"]},
        "birth_date"={data["birth_date"]},
        "status"={data["status"]} """)

    return redirect('/')


if __name__ == '__main__':
    app.run(debug=True)
