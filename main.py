from flask import Flask, render_template, request, session, redirect, url_for, abort, flash
import sqlite3
from model import img_analytics
import os
from werkzeug.utils import secure_filename

listed = os.listdir("static/img_analytics_users")
print(sorted(listed))
#names, path = analitic(img_path="path/img_users/0301.png")
#print(names, path)

path_upload = f'{os.path.dirname(__file__)}/static/img_users'
allowed_file_img = ['jpg', 'png', 'jpeg']

#path_analytics = "path/img_analytics_users"
#print(os.listdir(path_analytics))

app = Flask(__name__)
app.config.from_object(__name__)
app.config.update(dict(
    DEBUG=True,
    SECRET_KEY="r{A[A't_E)F_]Q^<u.6j1)+yI$6n13'W0*v]ABOBAr{A[A't_EF$)]Q^<u.6j)+yI$6n'W0*v]"

))
app.config['UPLOAD_FOLDER'] = path_upload



# --- функции для работы---#

def start_db():
    connect = sqlite3.connect("server.db")
    cursor = connect.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users(
    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
    fio TEXT NOT NULL,
    date_birth DATE NOT NULL,
    number_phone TEXT NOT NULL,
    email TEXT NOT NULL,
    country TEXT NOT NULL,
    city TEXT NOT NULL,
    password TEXT NOT NULL,
    date_reg TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status INTEGER NOT NULL,
    role TEXT NOT NULL)
    """)
    connect.commit()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS image_user(
    img_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    path TEXT NOT NULL,
    status INTEGER NOT NULL)
    """)
    connect.commit()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS result(
        result_id INTEGER PRIMARY KEY AUTOINCREMENT,
        img_id INTEGER NOT NULL,
        user_id INTEGER NOT NULL,
        analysis TEXT NOT NULL,
        path TEXT NOT NULL,
        status INTEGER NOT NULL)
        """)
    connect.commit()
    cursor.close()


def allowed_file(filename):
    return "." in filename and \
        filename.rsplit('.', 1)[1].lower() in allowed_file_img


@app.route("/")
def main():
    return render_template("main.html")


@app.route("/register", methods=['GET', 'POST'])
def register():
    error = None
    if request.method == "POST":
        connect = sqlite3.connect("server.db")
        cursor = connect.cursor()
        # парсим данные с запроса
        user_req = [request.form["fio"], request.form["date"], request.form["phone"], request.form["email"], "Россия",
                    request.form["town"], request.form["password"], 1, "user"]

        # проверяем есть ли запись с этими данными
        cursor.execute(f'SELECT * FROM users WHERE email = ? OR number_phone = ?', (user_req[3], user_req[2]))

        if cursor.fetchone() is None:
            print("true-0")
            # записываем данные в бд
            cursor.execute(
                'INSERT INTO users (fio, date_birth, number_phone, email, country, city, password, status, role) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)',
                user_req)

            connect.commit()
            # получаем user_id пользователя
            user_inf = cursor.execute("SELECT * FROM users WHERE email = ?", (user_req[3],)).fetchone()
            connect.close()
            session['logged_in'] = True
            session['user'] = user_req[3]
            session['user_id'] = user_inf[0]
            return redirect(url_for(f"userpage"))
        else:
            errors = "Данная почта или же номер телефона уже занят"
            return render_template('register.html', error=errors)
    return render_template("register.html", error=None)


@app.route("/userpage", methods=["GET", "POST"])
def userpage():
    if session.get("user_id") != None:
        connect = sqlite3.connect("server.db")
        cursor = connect.cursor()
        user_inf = cursor.execute("SELECT * FROM users WHERE user_id = ? AND email = ?",
                                  (session.get("user_id"), session.get("user"))).fetchone()
        path_img = cursor.execute("SELECT * FROM image_user WHERE user_id = ?", (int(session.get("user_id")),)).fetchall()
        connect.close()
        return render_template("userpage.html", user_inf=user_inf, error=None, len=len(path_img), path_img=path_img)
    else:
        return render_template("userpage.html", error="Вы невошли в свой аккаунт!")

@app.route("/analysis", methods=["GET", "POST"])
def analysis():
    if session.get("user_id") != None:
        connect = sqlite3.connect("server.db")
        cursor = connect.cursor()
        user_inf = cursor.execute("SELECT * FROM users WHERE user_id = ? AND email = ?",
                                  (session.get("user_id"), session.get("user"))).fetchone()
        path_img = cursor.execute("SELECT * FROM result WHERE user_id = ?", (int(session.get("user_id")),)).fetchall()
        connect.close()

        if user_inf != None:
                return render_template("analysis.html", user_inf=user_inf, error=None, len=len(path_img)-1, path_img=path_img)
        else:
            return render_template("analysis.html", error="Вы невошли в свой аккаунт!")
    else:
        return render_template("analysis.html", error="Вы невошли в свой аккаунт!")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        connect = sqlite3.connect("server.db")
        cursor = connect.cursor()
        user_inf = cursor.execute("SELECT * FROM users WHERE email = ? AND password = ?",
                                  (request.form["email"], request.form["password"])).fetchone()
        connect.close()
        if user_inf != None:
            session['logged_in'] = True
            session['user'] = user_inf[4]
            session['user_id'] = user_inf[0]
            return redirect(url_for("userpage", error=None))
        else:
            return render_template("login.html",
                                   error="Введен не верный пароль или же данного пользователя не существует")
    else:
        return render_template("login.html", error=None)


@app.route("/upload", methods=['GET', 'POST'])
def upload():
    if request.method == "POST":
        if 'file' not in request.files:
            error = "Не могу прочитать данный файл"
            return render_template('upload.html', error=error)
        file = request.files['file']

        if file.filename == '':
            error = "Нет выбранного файла"
            return redirect(url_for('upload', error=error))

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            path = filename
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            names, path_img, analysis = model.analytics("static/img_users/" + filename)

            connect = sqlite3.connect("server.db")
            cursor = connect.cursor()
            cursor.execute(
                'INSERT INTO image_user (user_id, path, status) VALUES (?, ?, ?)',
                (session.get("user_id"), path, 1))
            img_path_load = cursor.execute("SELECT img_id FROM image_user WHERE user_id = ? AND path = ?", (int(session.get("user_id")), path, )).fetchall()
            connect.commit()
            print(img_path_load, "$$$ path_img",path_img)
            cursor.execute(
                'INSERT INTO result (img_id, user_id, analysis, path, status) VALUES (?, ?, ?, ?, ?)',
                (img_path_load[-1][0], session.get("user_id"), analysis, path_img, 1))
            connect.commit()
            connect.close()
            error = "Фото успешно загружено"
            return redirect(url_for('userpage'))
    return render_template("upload.html", error=None)


@app.route("/logout")
def logout():
    session.pop('logged_in')
    session.pop('user_id')
    session.pop('user')
    return redirect(url_for("login", error=None))


start_db()
model = img_analytics()
if __name__ == '__main__':
  	app.run(host='0.0.0.0', port=80, use_reloader=False)
