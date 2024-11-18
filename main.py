from Tools.scripts.make_ctype import method
from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap5
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Text
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, URL
from flask_ckeditor import CKEditor, CKEditorField
from datetime import date, datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
Bootstrap5(app)
ckeditor = CKEditor(app)

class PostForm(FlaskForm):
    title =StringField('The blog post title', validators=[DataRequired()])
    subtitle = StringField('The subtitle', validators=[DataRequired()])
    author = StringField('The author name', validators=[DataRequired()])
    URL = StringField('A URL for the background image', validators=[DataRequired()])
    body = CKEditorField('Blog content', validators=[DataRequired()])

# CREATE DATABASE
class Base(DeclarativeBase):
    pass
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///posts.db'
db = SQLAlchemy(model_class=Base)
db.init_app(app)


# CONFIGURE TABLE
class BlogPost(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(250), unique=True, nullable=False)
    subtitle: Mapped[str] = mapped_column(String(250), nullable=False)
    date: Mapped[str] = mapped_column(String(250), nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    author: Mapped[str] = mapped_column(String(250), nullable=False)
    img_url: Mapped[str] = mapped_column(String(250), nullable=False)


with app.app_context():
    db.create_all()


@app.route('/')
def get_all_posts():
    result = db.session.execute(db.select(BlogPost))
    posts = result.scalars().all()
    return render_template("index.html", all_posts=posts)

@app.route('/<int:post_id>')
def show_post(post_id):
    result = db.session.execute(db.select(BlogPost).where(BlogPost.id == post_id))
    requested_post = result.scalar()
    return render_template("post.html", post=requested_post)


# TODO: add_new_post() to create a new blog post
@app.route('/new-post', methods=["POST", "GET"])
def add_new_post():
    edit_form = PostForm()
    if request.method == "POST":
        new_blog = BlogPost(
            title= request.form.get("title"),
            subtitle= request.form.get("subtitle"),
            date= datetime.now(),
            body= request.form.get("ckeditor"),
            author= request.form.get("author"),
            img_url=request.form.get("URL"),
        )
        db.session.add(new_blog)
        db.session.commit()
        return redirect(url_for('get_all_posts'))

    return render_template("make-post.html", form = edit_form)


# TODO: edit_post() to change an existing blog post
@app.route('/edit-post/<int:post_id>', methods= ["GET", "POST"])
def edit_post(post_id):
    post = db.get_or_404(BlogPost, post_id)
    print(post.img_url, post.body)
    edit_form = PostForm(
        title = post.title,
        subtitle = post.subtitle,
        URL = post.img_url,
        author = post.author,
        body = post.body
    )
    return render_template("make-post.html", form=edit_form, is_edit=True)


# TODO: delete_post() to remove a blog post from the database

# Below is the code from previous lessons. No changes needed.
@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/contact")
def contact():
    return render_template("contact.html")


if __name__ == "__main__":
    app.run(debug=True, port=5003)
