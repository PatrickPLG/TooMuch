from flask import Flask, render_template, request, redirect, session, url_for, escape, g
import sqlite3
import os
import bisect

app = Flask(__name__)
app.secret_key = 'BAD_SECRET_KEY'
goods = {}
leaderboard_list = {}

@app.route('/', methods=['GET', 'POST'])
def index():
    with sqlite3.connect("db.db") as db:
        try:
            if session.get('username') == None:
                return render_template("login.html")
            cursor = db.cursor()
            cursor.execute("SELECT * FROM Varer WHERE buyer = ''")
            all_items = cursor.fetchall()

            for row in all_items:
                goods[str(row[0])] = [row[1],row[2],row[3],row[4], row[0]]

        except sqlite3.Error:
            message = "There was a problem executing the SQL statement"
            return render_template("index.html")
    return render_template('index.html', goods = goods)

@app.route('/get', methods=['GET', 'POST'])
def get_item():
    with sqlite3.connect("db.db") as db:
        try:
            global goods
            if request.method == 'POST':
                val = request.get_json().get('val')
                print(val)
                for key in goods.items():
                    print(key[0])
                    if key[0] == val:
                        del goods[key[0]]
                        cursor = db.cursor()
                        cursor.execute("UPDATE Varer SET buyer = ? WHERE id = ?", (session['username'], val))
                        cursor.execute("UPDATE Person_information SET points = points + 10 WHERE username = '" + session['username'] + "'")
                        cursor.execute("UPDATE Person_information SET points_overall = points_overall + 10 WHERE username = '" + session['username'] + "'")
                        return redirect("/")
            return redirect("/")
        except sqlite3.Error:
            message = "There was a problem executing the SQL statement"
            return redirect("/")
    return redirect("/")

@app.route('/create', methods=['GET', 'POST'])
def create():
    with sqlite3.connect("db.db") as db:
        try:
            cur = db.cursor()
            cur.execute("select * from Person_information where username = '" + session['username'] + "'")
            personalInformation = cur.fetchall()

            points_to_give = 5+(int(personalInformation[0][6])*0.7)
            print(points_to_give)
            if session.get('username') == None:
                return render_template("login.html")
            if request.method == 'POST':
                beskrivelse = request.form.get('beskrivelse')
                udløbsdato = request.form.get('udløbsdato')
                lokation = request.form.get('lokation')

                file = request.files["file"]
                file.save(os.path.join("static/images", file.filename))

                cursor = db.cursor()
                cursor.execute("INSERT INTO Varer (beskrivelse, udløbsdato, lokation, datastore, seller, buyer) VALUES (?, ?, ?, ?, ?, '')", (beskrivelse, udløbsdato, lokation, file.filename, session['username']))
                cursor.execute("UPDATE Person_information SET points = points + ? WHERE username = ?", (points_to_give, session['username']))
                cursor.execute("UPDATE Person_information SET points_overall = points_overall + ? WHERE username = ?", (points_to_give, session['username']))
        except sqlite3.Error:
            message = "There was a problem executing the SQL statement"
            return render_template("create.html")
    return render_template("create.html", points=points_to_give)

@app.route('/profile', methods=['GET', 'POST'])
def profile():
    with sqlite3.connect('db.db') as db:
        try:
            if session.get('username') == None:
                return render_template("login.html")
            cur = db.cursor()
            cur.execute("select * from Person_information where username = '" + session['username'] + "'")
            personalInformation = cur.fetchall()

            exp_level = [10,30,60,100,150,210,270,340,420,510,600]
            level = bisect.bisect(exp_level, int(personalInformation[0][5]))

            cur.execute("UPDATE Person_information SET level = ? WHERE username = ?", (level, session['username']))


            if request.method == 'POST':
                name = request.form.get('navn')
                adress = request.form.get('adresse')
                number = request.form.get('nummer')
                print(name)
                print(adress)
                print(number)
                cur.execute("UPDATE Person_information SET name = ?, adress = ?, number = ? WHERE username = ?", (name, adress, number, session['username']))
                return redirect("/profile")

            return render_template("profile.html", personalInformation=personalInformation, level=level)
        except sqlite3.Error:
            message = "There was a problem executing the SQL statement"
            return render_template("profile.html")
    return render_template("profile.html", personalInformation=personalInformation)

@app.route('/leaderboard', methods=['GET', 'POST'])
def leaderboard():
    with sqlite3.connect('db.db') as db:
        try:
            if session.get('username') == None:
                return render_template("login.html")
            cursor = db.cursor()
            cursor.execute("SELECT name,points FROM Person_information ORDER BY points DESC")
            leaderboard = cursor.fetchall()

            for row in leaderboard:
                print(row[0])
                print(row[1])
                leaderboard_list[str(row[0])] = [row[0],row[1]]
            return render_template("leaderboard.html", leaderboard_list=leaderboard_list)
        except sqlite3.Error:
            message = "There was a problem executing the SQL statement"
            return render_template("leaderboard.html")
    return render_template("leaderboard.html", leaderboard_list=leaderboard_list)

@app.route('/shop', methods=['GET', 'POST'])
def shop():
    with sqlite3.connect('db.db') as db:
        try:
            if session.get('username') == None:
                return render_template("login.html")
            return render_template("shop.html")
        except sqlite3.Error:
            message = "There was a problem executing the SQL statement"
            return render_template("shop.html")
    return render_template("shop.html")


def log_the_user_in(username):
    return redirect("/")
    

@app.route('/login', methods=['POST', 'GET'])
def login():
    with sqlite3.connect("db.db") as db:
        try:
            error = None
            if request.method == 'POST':
                username = request.form.get('username')
                password = request.form.get('password')

                cursor = db.cursor()
                cursor.execute('select * from User where username = ? and password = ?', (username,password))
                valid_login = cursor.fetchall()

                if valid_login != []:
                    session['username'] = request.form['username']
                    
                    return log_the_user_in(request.form['username'])
                else:
                    error = 'Invalid username/password'
        except sqlite3.Error:
            message = "There was a problem executing the SQL statement"
            return render_template("login.html", error=message)

    return render_template('login.html', error=error)

@app.route('/register', methods=['POST', 'GET'])
def register():
    with sqlite3.connect("db.db") as db:
        try:
            error = None
            if request.method == 'POST':
                username = request.form.get('username')
                password = request.form.get('password')
                name = request.form.get('name')
                adress = request.form.get('adress')
                number = request.form.get('number')

                cursor = db.cursor()
                cursor.execute('select * from User where username = ? and password = ?', (username,password))
                print(cursor.fetchall())
                valid_login = cursor.fetchall()
                
                if valid_login == []:
                    cur = db.cursor()
                    cur.execute("INSERT INTO User(username, password) values (?,?)", (username,password))
                    cur.execute("INSERT INTO Person_information VALUES (?, ?, ?, ?, 0, 0, 1)", (username, name, adress, number))
                    
                    render_template('login.html', error=error)
                else:
                    error = 'Kontoen eksisterer allerede'
        except sqlite3.Error:
            return render_template("register.html", error=error)
    return render_template('register.html', error=error)

@app.route('/logout')
def logout():
    session.pop('username', default=None)
    return render_template('login.html')

@app.route('/info')
def info():
    return render_template('info.html')


app.run(host='0.0.0.0', port=81, debug=True)