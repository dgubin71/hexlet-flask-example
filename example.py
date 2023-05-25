import json, os
from user_agents import parse
from flask import Flask, render_template, request, redirect, url_for, flash, get_flashed_messages, session
from werkzeug.utils import secure_filename
from pathlib import Path

# Это callable WSGI-приложение
app = Flask(__name__, template_folder='templates')
UPLOAD_FOLDER = 'static/images/'
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}


@app.route('/')
def index():
    if session.get('user'):
        if check_login(session['user']):
            flash('You connect as' + session['user'] + ' succes', 'success')
            return redirect(url_for("find_users"))
    else:
        session['user'] = ""
        user = {"name": "", "email":""}
        placeholder = {"name": "LOGIN", "email":"PASSWORD"}
        errors = ""
        header = "Enter LOGIN & PASSWORD"
         #   получаем   user agent для определения типа браузера
        ua_string = request.headers.get('User-Agent')  # получаем строку user agent
        user_agent = parse(ua_string)
        if user_agent.is_mobile:
              template_for_login = 'users/login_mobile.html'  # используем шаблон для мобильного
        else:
               template_for_login = 'users/login.html'  # используем шаблон для десктопа
        return render_template(
        template_for_login,    #'users/login.html',
        user=user,
        header=header,
        placeholder = placeholder,
        errors=errors
    )

@app.post('/login')
def login_user():
     session.clear()
     errors = ""
     user = {}
     login = request.form.get('password')
     if check_login(login):
         session['user']=login
         #flash('login as '+ session['user'] +'  is succes', 'success')  # 'success')#
         return redirect(url_for('find_users'), code=302)
     else:
          session['user'] = ""
          user = {"name": "", "email": ""}
          placeholder = {"name": "LOGIN", "email": "PASSWORD"}
          errors = "Can't find login or password"
          header = "Enter LOGIN & PASSWORD"

        #   получаем   user agent для определения типа браузера
     ua_string = request.headers.get('User-Agent')  # получаем строку user agent
     user_agent = parse(ua_string)
     if user_agent.is_mobile:
            template_for_login = 'users/login_mobile.html'  # используем шаблон для мобильного
     else:
            template_for_login = 'users/login.html'  # используем шаблон для десктопа

     return render_template(
            template_for_login,  # 'users/login.html',
            user=user,
            header=header,
            placeholder=placeholder,
            errors=errors)


@app.route('/courses/<id>')
def courses(id):
    return f'Course id: {id}'

@app.route('/users/<id>')
def users(id):
    user = {}
    errors = {}

    users = json.load(open('templates/users/users.json'))
    user = next(filter(lambda s: s['id'] == int(id), users))
    ua_string = request.headers.get('User-Agent')  # получаем строку user agent
    user_agent = parse(ua_string)
    if user_agent.is_mobile:
        template_for_show_user = 'users/show_customer_mobile.html'  # используем шаблон для мобильного
    else:
        template_for_show_user = 'users/show.html'  # используем шаблон для десктопа


    return render_template(
        template_for_show_user, #'users/show.html',
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
    ua_string = request.headers.get('User-Agent')  # получаем строку user agent
    user_agent = parse(ua_string)
    if user_agent.is_mobile:
        template_for_find_user = 'users/customers_row_mobile.html'  # используем шаблон для мобильного
    else:
        template_for_find_user = 'users/index.html'  # используем шаблон для десктопа

    return render_template(
         template_for_find_user, #'users/index.html', #'users/show_mobile.html',
         names=filtered_users,
         messages=messages,
         search=term,

    )

@app.route('/users/new')
def users_new():
    #   получаем   user agent для определения типа браузера
    ua_string = request.headers.get('User-Agent')  # получаем строку user agent
    user_agent = parse(ua_string)
    if user_agent.is_mobile:
        template_for_new = 'users/new_customer_mobile.html'
    else:
        template_for_new = 'users/new.html'  # используем шаблон для десктопа

    user = {'id': 0,
            'name': '',
            'email': '',
            'birthday': '',
            'phone': '',
            'address': '',
            'photo':''
            }
    errors = {}
    header = "NEW CUSTOMER"
    placeholder = {'name': 'NAME',
                   'email': 'EMAIL for@example.com'}
    return render_template(
        template_for_new,    #'users/new.html',
        user=user,
        header=header,
        placeholder=placeholder,
        errors=errors
    )

@app.post('/users')
def users_post():
    filename = ""
    file = request.files['file']
    # Если файл не выбран, то браузер может
    # отправить пустой файл без имени.
    if file.filename != '':

        if file and allowed_file(file.filename):
            # безопасно извлекаем оригинальное имя файла
            filename = secure_filename(file.filename)
            # сохраняем файл
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        else:
            flash("Can't save  insecure file")
            return redirect(url_for('find_users'), code=302)
    new_user_id = next_id()
    user = {'id': '',
            'name': '',
            'email': '',
            'birthday': '',
            'phone': '',
            'address': '',
            'photo':''
            }
    user['id'] = new_user_id
    user['name'] = request.form.get('name')
    user['email'] = request.form.get('email')
    user['birthday'] = request.form.get('birthday')
    user['phone'] = request.form.get('phone')
    user['address'] = request.form.get('address')
    user['photo'] = filename

    errors = validate(user)

    if errors:
        ua_string = request.headers.get('User-Agent')  # получаем строку user agent
        user_agent = parse(ua_string)
        header = "NEW CUSTOMER"
        placeholder = {'name': 'NAME',
                       'email': 'EMAIL for@example.com'}
        if user_agent.is_mobile:
            template_for_new = 'users/new_customer_mobile.html', #'users/new_mobile.html'  # используем шаблон для мобильного
        else:
            template_for_new = 'users/new.html'  # используем шаблон для десктопа
        return render_template(
          template_for_new,  #'users/new.html',
          user=user,
          errors=errors,
          header=header,
          placeholder=placeholder,
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
    ua_string = request.headers.get('User-Agent')  # получаем строку user agent
    user_agent = parse(ua_string)
    header = "NEW CUSTOMER"
    placeholder = {'name': 'NAME',
                   'email': 'EMAIL for@example.com'}
    if user_agent.is_mobile:
        template_for_update= 'users/update_customer_mobile.html'  # используем шаблон для мобильного
    else:
        template_for_update = 'users/update.html'  # используем шаблон для десктопа
    return render_template(
        template_for_update , #'users/update.html',
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
    filename = ""
    file = request.files['file']
    # Если файл не выбран, то браузер может
    # отправить пустой файл без имени.
    if file.filename != '':

       if file and allowed_file(file.filename):
           # безопасно извлекаем оригинальное имя файла
           filename = secure_filename(file.filename)
           # сохраняем файл
           file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
       else:
           flash("Can't save  insecure file")
           return redirect(url_for('find_users'), code=302)

    user = {'id': '',
            'name': '',
            'email': '',
            'birthday': '',
            'phone': '',
            'address': ''
            }

    user['id'] = id
    user['name'] = request.form.get('name')
    user['email'] = request.form.get('email')
    user['birthday'] = request.form.get('birthday')
    user['phone'] = request.form.get('phone')
    user['address'] = request.form.get('address')
    if  filename != "":
        user.setdefault('photo',filename)
    flash(user)  # 'success')#
    errors = validate(user)

    if errors:
        return render_template(
          'users/update_customer_mobile.html',
          user=user,
          errors=errors,
       ), 422
    edit_user(user)
    return redirect(url_for('find_users'), code=302)



def validate(user):
    errors = {}
    if not user['name']:
       errors['name'] = "Name can't be blank"
    if len(user['email'])<11:
       errors['email'] = "Email must have more 10 simbols"
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
            if item_user['photo'] != "":
                file_photo = os.path.join(app.config['UPLOAD_FOLDER'], item_user['photo'])
                if os.path.exists(file_photo):
                     os.remove(file_photo)
                else:
                    flash("The photo file does not exist")
            users.pop(users.index(user))
            break
    users_file = open('templates/users/users.json', 'w')
    json.dump(users, users_file)

def check_login(login):

    logins_file = open('templates/users/logins.json', 'r')
    users = json.load(logins_file)
    for item_user in users:
        if item_user['password'] == login:
            return True
    return False

def allowed_file(filename):
    """ Функция проверки расширения файла """
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
