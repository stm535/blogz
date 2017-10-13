from flask import Flask, request, redirect, render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:build-a-blog@localhost:8889/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)


class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(2000))

    def __init__(self, title, body):
        self.title = title
        self.body = body


@app.route('/blog', methods=["POST", "GET"])
def index():
    blogs = Blog.query.all()
    
    return render_template('blogs.html', title='All of the Blogs', blogs=blogs)

@app.route('/newpost')
def new_post():
    return render_template('newpost.html', title='Creative Space')

@app.route('/newpost', methods=["POST"])
def validate_post():
    blog_title = request.form['blog_title']
    body = request.form['body']

    blog_title_error = ''
    body_error = ''

    if blog_title == '':
        blog_title_error = "Please enter a title"

    if body == '':
        body_error = "Please enter some cool text!"

    if not blog_title_error and not body_error:
        blog_title=request.form['blog_title']
        body=request.form['body']
        add_post = Blog(blog_title, body)
        db.session.add(add_post)
        db.session.commit()
        blog_id = str(add_post.id)
        return redirect('/display_blog?id='+blog_id)     
    
    else:
        return render_template('newpost.html', blog_title_error=blog_title_error, body_error=body_error, blog_title=blog_title, body=body)

@app.route('/display_blog', methods=['POST', 'GET'])
def display_post():
   
    blog_id = request.args.get('id')
    blog = Blog.query.get(blog_id)

    return render_template('display_blog.html', blog=blog)


if __name__ == '__main__':
    app.run()