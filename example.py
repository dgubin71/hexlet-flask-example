import json
from user_agents import parse
from flask import Flask, render_template, request, redirect, url_for, flash, get_flashed_messages, session


# Это callable WSGI-приложение
app = Flask(__name__, template_folder='templates')
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'


@app.route('/')
def index():
    if session.get('user'):
        if check_login(session['user']):
            flash('You connect as' + session['user'] + ' succes', 'success')
            return redirect(url_for("find_users"))
    session['user'] = ""
    user = {"name": "Login", "email": "Enter email"}
    errors = {}
    return render_template(
        'users/login.html',
         user=user,
         errors=errors
    )

@app.post('/login')
def login_user():
    session.clear()
    errors = {}
    user = {}
    login = request.form.get('email')
    if check_login(login):
         session['user']=login
         flash('login as '+ session['user'] +'  is succes', 'success')  # 'success')#
         return redirect(url_for('find_users'), code=302)
    else:
          user['name'] = "Login"
          user['email'] = ""
          errors['name'] = ""
          errors['email'] = "Enter email"
          return render_template(
                'users/login.html',
                 user = user,
                 errors = errors)

@app.route('/courses/<id>')
def courses(id):
    return f'Course id: {id}'

@app.route('/users/<id>')
def users(id):
    user = {}
    errors = {}

    users = json.load(open('templates/users/users.json'))
    user = next(filter(lambda s: s['id'] == int(id), users))

    return render_template(
        'users/show.html',
        #'users/show_mobile.html',

         user = user,
         errors=errors,
    )

@app.route('/users/')
def find_users():
    users = json.load(open('templates/users/users.json'))
    term = request.args.get('term')
    if term == None: term =''
    filtered_users = list(filter(lambda s: s['name'].startswith(term) != 0, users))
    messages = get_flashed_messages(with_categories=True)
    return render_template(
          'users/index.html',
         #'users/show_mobile.html',
         names = filtered_users,
         messages = messages,
         search=term,

    )

@app.route('/users/new')
def users_new():
#   получаем   user agent для определения типа браузера
    ua_string = request.headers.get('User-Agent')  #  получаем строку user agent
    user_agent = parse(ua_string)
    if user_agent.is_mobile:
        template_for_new = 'users/new_mobile.html'   #  используем шаблон для мобильного
    else:
        template_for_new = 'users/new.html' #  используем шаблон для десктопа

    user = {'name': '',
            'email': ''
            }
    errors = {}

    return render_template(
        template_for_new,    #'users/new.html',
        user=user,
        errors=errors
    )

@app.post('/users')
def users_post():
    new_user_id = next_id()
    user = {'id': '',
             'name': '',
            'email': ''
            }
    user['id'] = new_user_id
    user['name'] = request.form.get('name')
    user['email'] = request.form.get('email')
    errors = validate(user)

    if errors:
        return render_template(
          'users/new.html',
          user=user,
          errors=errors,
        )
    add_new_user(user)
    flash('New user '+ user['name'] + ' has been added', 'success')# 'success')#
    #return redirect('/users', code=302)
    return redirect(url_for('find_users'), code=302)

@app.route ('/users/<int:id>/update')
def users_for_update(id):
    errors = {}
    users = json.load(open('templates/users/users.json'))
    user = next(filter(lambda s: s['id'] == int(id), users))
    return render_template(
        'users/update.html',
        user=user,
        errors=errors,
    )

@app.route ('/users/<int:id>/delete')
def users_for_delete(id):
    users = json.load(open('templates/users/users.json'))
    user = next(filter(lambda s: s['id'] == int(id), users))
    delete_user(user)
    flash('User has been deleted', 'warning')# 'success')#
    return redirect(url_for('find_users'), code=302)


@app.post('/users/<int:id>')
def patch_user(id):
    user = {'id': '',
             'name': '',
            'email': ''
            }
    user['id'] = id
    user['name'] = request.form.get('name')
    user['email'] = request.form.get('email')
    errors = validate(user)

    if errors:
        return render_template(
          '/users/update.html',
          user=user,
          errors=errors,
        ), 422
    edit_user(user)
    flash('User   '+ user['name'] + ' has been updated', 'success')# 'success')#
    return redirect(url_for('find_users'), code=302)



def validate(user):
    errors = {}
    if not user['name']:
       errors['name'] = "Can't be blank"
    if len(user['email'])<11:
       errors['email'] = "email must have more 10 simbols"
    return errors

def next_id():
   id_line = []
   users = json.load(open('templates/users/users.json'))
   for item in users:
       id_line.append(item['id'])
   new_id = max(id_line)
   return new_id + 1

def add_new_user(user):
        users_file = open('templates/users/users.json', 'r')
        users = json.load(users_file)
        users.append(user)
        users_file = open('templates/users/users.json', 'w')
        json.dump(users, users_file)


def edit_user(user):
    users_file = open('templates/users/users.json', 'r')
    users = json.load(users_file)
    id = user['id']
    for item_user in users:
        if item_user['id'] == id:
            item_user.update(user)
            break
    users_file = open('templates/users/users.json', 'w')
    json.dump(users, users_file)


def delete_user(user):
    users_file = open('templates/users/users.json', 'r')
    users = json.load(users_file)
    id = user['id']
    for item_user in users:
        if item_user['id'] == id:
            users.pop(users.index(user))
            break
    users_file = open('templates/users/users.json', 'w')
    json.dump(users, users_file)

def check_login(login):
    users_file = open('templates/users/users.json', 'r')
    users = json.load(users_file)
    for item_user in users:
        if item_user['email'] == login:
            return True
    return False
