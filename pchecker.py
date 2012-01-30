# -- coding: utf-8 --
import sqlite3
from flask import Flask, request, session, g, redirect, url_for, \
    abort, render_template, flash
from contextlib import closing
from flask import jsonify

DEBUG = True

app = Flask(__name__)
app.config.from_object(__name__)

app.config.from_envvar('FLASKR_SETTINGS', silent=True)

def is_spec_char(char):
    return ord(char) not in range(ord('a'), ord('a') + 26) \
        and ord(char) not in range(ord('A'), ord('A') + 26) \
        and ord(char) not in range(ord('0'), ord('0') + 10)

def rating_function_alpha(username, password):
    code = rating_function_code(username, password)
    if code == 1:
        return '1 - TooShortPassword'
    elif code == 2:
        return '2 - BadPassword'
    elif code == 3:
        return '3 - GoodPassword'
    else:
        return '4 - StrongPassword'

def rating_function_code(username, password):
    score = rating_function_score(username, password)
    if score == -100:
        return 1
    elif 0 < score <= 34:
        return 2
    elif 34 < score <= 68:
        return 3
    else:
        return 4

def rating_function_score(username, password):
    score = 0
    if len(password) < 4:
        #-100 es TooShortPassword
        return -100
    elif password == username:
        #0 asegura TooShortPassword
        return 0
    
    score += len(password) * 4
    
    checked = []
    #Por cada char le resta al puntaje el número de veces que se repite
    #más de una vez
    for char in password:
        if char not in checked:
            score -= password.count(char) - 1
            checked.append(char)

    #SI hay 3 números, +5 ptos.
    num_count = 0
    added = False
    for char in password:
        try:
            if int(char) in range(10):
                num_count += 1
        except ValueError:
            pass
        if num_count == 3 and not added:
            score += 5
            added = True

    #Si hay 2 caracteres especiales, +5
    specchar_count = 0
    added = False
    for char in password:
        if is_spec_char(char):
            specchar_count += 1
        if specchar_count == 2 and not added:
            score += 5
            added = True

    #Hay mayúsculas y minúsculas
    if not password.lower() == password \
    and not password.upper() == password:
        score += 10

    #Hay números y letras
    if num_count > 0 and not num_count + specchar_count == len(password):
        score += 15

    #Hay caracteres especiales y números
    if specchar_count > 0 and num_count > 0:
        score += 15

    #Hay caracteres normales y especiales
    if specchar_count > 0 and not num_count + specchar_count == len(password):
        score += 15

    #Si sólo es caracteres
    if password.isalpha():
        score -= 10

    #Si sólo es números
    if password.isdigit():
        score -= 10

    if score > 100:
        score = 100

    return score

RATING_FUNCTIONS = {'alpha': rating_function_alpha,
                    'code': rating_function_code,
                    'score': rating_function_score}

@app.route('/')
def show_start():
    return render_template('input_password.html')

@app.route('/rate', methods=['GET', 'POST'])
def rate_password():
    score = (RATING_FUNCTIONS[request.form['mode']](
        request.form['username'], request.form['password']),
             rating_function_code(request.form['username'],
                                  request.form['password']))

    print request.form['mode']
    return jsonify(score=score[0])
#    return render_template('show_score.html', score=score)

if __name__ == '__main__':
    app.run()
