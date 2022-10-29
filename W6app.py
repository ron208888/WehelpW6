from flask import Flask
from flask import request
from flask import redirect
from flask import url_for
from flask import render_template
from flask import session
from flask import jsonify

import re
import mysql.connector
from mysql.connector import Error

connection = mysql.connector.connect(
     host = "localhost",
     database = "W6member",
     user = "root",
     passwd = "",
     charset = "utf8mb3"
)

app = Flask(
    __name__,
)
app.secret_key = "test"

@app.route("/", methods = ["GET","POST"])
def index():
    return render_template("W6.html")

@app.route("/signup", methods = ["POST"])
def signup():
    Rname = request.form["Rname"]
    account = request.form["account"]
    passwords = request.form["passwords"]
    cursor = connection.cursor()
    command = "insert into member(name, account, password) values(%s, %s, %s);"
    # setId = "ALTER TABLE member AUTO_INCREMENT = 1;"
    
    try:
        # cursor.execute(setId)
        cursor.execute(command, (Rname, account, passwords))
        connection.commit()
        print("更新成功")
        # messagebox.showinfo("註冊成功",f"歡迎{account}加入!")
        return redirect("http://127.0.0.1:3000/")

    except Error as ex:
        print(ex)
        if Rname == "" or account == "" or passwords == "":
            message = "請輸入完整資料"
            return redirect(url_for("error", message = message))
        else:
            message="帳號已被註冊"
            return redirect(url_for("error", message = message))

@app.route("/signin", methods = ["POST"])
def signin():
    name = request.form["name"]
    password = request.form["password"]
    passwd = (f"{password}",)
    session["username"] = name
    cursor = connection.cursor()
    matchAccount = "Select password from member where account = %s"
    userNum = "select id from member where account = %s"
    
    try:
        cursor.execute(matchAccount, (name,))
        result = cursor.fetchall()
        print(result)
        
        if result[0] == passwd:
            cursor.execute(userNum, (name,))
            userId = cursor.fetchall()
            print(userId[0][0])
            session["userID"] = userId[0][0]
            session.permanent = True
            return redirect("http://127.0.0.1:3000/member")
        
        elif result[0] == () or result[0] != passwd:
            message = "帳號、或密碼輸入錯誤"
            return redirect(url_for("error", message = message))
            
    except Error as ex:
        print(ex)
        message = "請輸入帳號密碼"
        return redirect(url_for("error", message = message))


@app.route("/member")
def member():
    name = session["username"]
    getMessage = "select account,message from message"
    cursor = connection.cursor()
    
    if session.permanent == False:
            return redirect("http://127.0.0.1:3000/")
        
    try:
        cursor.execute(getMessage)
        result = list(reversed(cursor.fetchall()))
        message = "".join(map(str, result))
        removeStr = "('"
        message = "".join(x for x in message if x not in removeStr)
        message = message.replace(")", "\n")
        message = message.replace(",", ":")
        print(result)
        print(message)
        return render_template("member.html", name = name , message = message)
            
    except Error as ex:
        print(ex)
    

@app.route("/error")
def error():
    message = request.args.get("message")
    return render_template("error.html", errortype = message)
    
@app.route("/signout")
def signout():
    session.permanent = False
    return redirect("http://127.0.0.1:3000/")

@app.route("/message")
def message():
    message = request.args.get("message")
    name = session["username"]
    userID = session["userID"]
    cursor = connection.cursor()
    writeMessage = "insert into message(id, account, message)values(%s, %s, %s)"
    
    try:
        cursor.execute(writeMessage, (userID, name, message))
        print(message)
        connection.commit()
        return redirect("http://127.0.0.1:3000/member")
    
    except Error as ex:
        print(ex)
        message = "請輸入留言"
        return redirect(url_for("error", message = message))

app.run(port = 3000)
