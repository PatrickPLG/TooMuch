from flask import Flask, render_template, request, redirect, session, url_for, escape, g
import sqlite3
import os

app = Flask(__name__)
app.secret_key = 'BAD_SECRET_KEY'

@app.route('/')
def index():
    with sqlite3.connect("db.db") as db:
        try:
            cursor = db.cursor()
            cursor.execute("SELECT * FROM Varer")
            all_items = cursor.fetchall()

            for row in all_items:
                print(row[0])
                print(row[1])
                print(row[2])
                print(row[3])
        except sqlite3.Error:
            message = "There was a problem executing the SQL statement"
            return render_template("index.html")
    return render_template('index.html')

@app.route('/create', methods=['GET', 'POST'])
def create():
    with sqlite3.connect("db.db") as db:
        try:
            if request.method == 'POST':
                beskrivelse = request.form.get('beskrivelse')
                udløbsdato = request.form.get('udløbsdato')
                lokation = request.form.get('lokation')

                file = request.files["file"]
                file.save(os.path.join("uploads", file.filename))

                cursor = db.cursor()
                cursor.execute("INSERT INTO Varer (beskrivelse, udløbsdato, lokation, datastore) VALUES (?, ?, ?, ?)", (beskrivelse, udløbsdato, lokation, file.filename))


        except sqlite3.Error:
            message = "There was a problem executing the SQL statement"
            return render_template("create.html")
    return render_template("create.html")
app.run(host='0.0.0.0', port=81, debug=True)