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
        return -100
    elif password == username:
        return 0
    
    score += len(password) * 4
    checked = []
    for char in password:
        if char not in checked:
            score -= password.count(char) - 1
            checked.append(char)

    num_count = 0
    for char in password:
        try:
            if int(char) in range(10):
                num_count += 1
        except ValueError:
            pass
        if num_count == 3:
            score += 5
            break

    specchar_count = 0
    for char in password:
        if is_spec_char(char):
            specchar_count += 1
        if specchar_count == 2:
            score += 5
            break

    if not password.islower() and not password.isupper():
        score += 10

    if not password.isdigit() and not password.isalpha():
        score += 15

    if specchar_count > 0 and num_count > 0:
        score += 15

    has_normal_char = False
    for char in password:
        if not is_spec_char(char):
            has_normal_char = True
            break

    if has_normal_char and specchar_count > 0:
        score += 15

    if password.isalpha():
        score -= 10

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
