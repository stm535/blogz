from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:blogz@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'oihofhasjlkdfnlajs'


class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(2000))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, body, owner):
        self.title = title
        self.body = body
        self.owner = owner

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(25), unique=True)
    password = db.Column(db.String(25))
    blogs = db.relationship('Blog', backref='owner')

    def __init__(self, username, password):
        self.username = username
        self.password = password

@app.before_request
def require_login():
    allowed_routes = ['login', 'signup', 'list_blogs', 'index']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')

@app.route('/', methods=['POST', 'GET'])
def index():
    usernames = User.query.all()

    return render_template('index.html', title='Usernames', usernames=usernames)

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.form['username'] 
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            session['username'] = username
            return redirect ('/newpost')
        else:
            flash('User password incorrect, or user does not exist', 'error')
    
    return render_template('login.html')


@app.route('/signup', methods=['POST', 'GET'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify']

        username_error = ''
        password_error = ''
        verify_password_error = ''
        
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            username_error = 'Username already exists, please select a new one'
        
        if username == '':
            username_error = 'Please enter a valid username!'
            
        if password == '':
            password_error = 'Please enter a valid password!'
        
        for char in (username):
            if char ==' ':
                username_error = "Username must not contain a space and must be between 3 and 20 characters"
            else:
                if 3>len(username) or len(username)>20:
                    username_error = "Username must not contain a space and must be between 3 and 20 characters"
        
        for char in password:
            if char == ' ':
                password_error = "Password must not contain a space and must be between 3 and 20 characters"
            else:
                if 3>len(password) or len(password)>20:
                    password_error = "Password must not contain a space and must be between 3 and 20 characters"

        if password != verify:
            verify_password_error = 'Passwords do not match!'

        if not username_error and not password_error and not verify_password_error:
            new_user = User(username, password)
            db.session.add(new_user)
            db.session.commit()
            session['username'] = username
            return redirect ('/newpost')
            flash('Logged In')
        else:
            return render_template('signup.html',
            username_error=username_error,
            password_error=password_error,
            verify_password_error=verify_password_error,
            username=username) 
    return render_template('signup.html')

@app.route('/logout')
def logout():
    del session['username']
    return redirect ('/blog')
            
@app.route('/blog', methods=["POST", "GET"])
def list_blogs():
    if request.args.get('id'):
        blog_id = request.args.get('id')
        blog = Blog.query.get(blog_id)

        return render_template('display_blog.html', blog=blog)

    if request.args.get('user'):
        user_id = request.args.get('user')
        blogs = Blog.query.filter_by(owner_id=user_id).all()

        return render_template('author_posts.html', blogs=blogs)
    
    #if request.method == 'GET':
    blogs = Blog.query.all()
    users = User.query.all()
    return render_template('blogs.html', title='All of the Blogs', blogs=blogs)

@app.route('/newpost')
def new_post():
    return render_template('newpost.html', title='Creative Space')

@app.route('/newpost', methods=["POST"])
def validate_post():
    blog_title = request.form['blog_title']
    body = request.form['body']
    owner = User.query.filter_by(username=session['username']).first()

    blog_title_error = ''
    body_error = ''

    if blog_title == '':
        blog_title_error = "Please enter a title"

    if body == '':
        body_error = "Please enter some cool text!"

    if not blog_title_error and not body_error:
        blog_title=request.form['blog_title']
        body=request.form['body']
        add_post = Blog(blog_title, body, owner)
        db.session.add(add_post)
        db.session.commit()
        blog_id = str(add_post.id)
        return redirect('/blog?id='+blog_id)     
    
    return render_template('newpost.html', blog_title_error=blog_title_error, body_error=body_error, blog_title=blog_title, body=body)


if __name__ == '__main__':
    app.run()