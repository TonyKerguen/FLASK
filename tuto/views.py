from .app import app
from flask import flash, render_template
from .models import Book, get_sample, get_author
from flask_wtf import FlaskForm
from wtforms import FloatField, StringField, HiddenField, SubmitField
from wtforms.validators import DataRequired
from flask import url_for, redirect
from .app import db
from wtforms import PasswordField
from .models import User, Author
from hashlib import sha256
from flask_login import login_user, current_user
from flask import request
from flask_login import logout_user
from flask_login import login_required

class loginForm(FlaskForm):
    username = StringField('Username')
    password = PasswordField('Password')
    next = HiddenField()
    def get_authenticated_user(self):
        user = User.query.get(self.username.data)
        if user is None:
            return None
        m = sha256()
        m.update(self.password.data.encode())
        passwd = m.hexdigest()
        return user if passwd == user.password else None

class BookForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    price = FloatField('Price', validators=[DataRequired()])
    image = StringField('Image URL', validators=[DataRequired()])
    submit = SubmitField('Save Changes')

class AuthorForm(FlaskForm):
    id = HiddenField('id')
    name = StringField('Nom', validators=[DataRequired()])

@app.route ("/")
def home():
    return render_template(
        "home.html",
        title="Hello World",
        books=get_sample())
    
    
@app.route ("/name")
def show_name():
    return render_template(
        "home.html",
        title="name",
        names=["Pierre", "Jean", "Axel"])
    
    
@app.route ("/sample")
def sample():
    return render_template(
        "home.html",
        title="My Books !",
        books=get_sample())
    
    
@app.route("/detail/<id>")
def detail(id):
    books = get_sample()
    book = books[int(id)]
    return render_template(
    "detail.html",
    b=book)
    
@app.route("/edit-author/<int:id>")
@login_required
def edit_author(id):
    a = get_author(id)
    f = AuthorForm(id=a.id, name=a.name)
    return render_template(
        "edit-author.html",
        author=a, form = f)
    
@app.route("/save/author/", methods =("POST" ,))
def save_author():
        a = None
        f = AuthorForm()
        if f.validate_on_submit():
            id = int(f.id.data)
            a = get_author(id)
            a.name = f.name.data
            db.session.commit()
            return redirect(url_for('sample', id=a.id))
        a = get_author(int(f.id.data))
        return render_template(
            "edit-author.html",
            author =a, form=f)

@app.route("/login/",methods=("GET","POST" ,))
def login():
    f = loginForm()
    if not f.is_submitted():
        f.next.data = request.args.get("next")
    elif f.validate_on_submit():
        user = f.get_authenticated_user()
        if user:
            login_user(user)
            next = f.next.data or url_for("home")
            return redirect(next)
    return render_template("login.html", form=f)

@app.route("/logout/")
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route("/search/", methods=["GET"])
def search_books_by_author():
    author_name = request.args.get('author_name', '')
    if author_name:
        # on cherche dans la bd tout les autheurs qui contiennent "author_name"
        authors = Author.query.filter(Author.name.ilike(f"%{author_name}%")).all()
        books = []
        for author in authors:
            books.extend(author.books.all()) 

        return render_template(
            "home.html",
            title="Books by Author",
            books=books
        )
    else:
        #si on clic sur shearch sans rien ecrire
        return render_template(
            "home.html",
            title="No Author Specified",
            books=[]
        )
    
@app.route("/edit-book/<int:id>", methods=["GET", "POST"])
@login_required
def edit_book(id):
    book = Book.query.get_or_404(id)
    form = BookForm(obj=book)

    # on verifit si le formulaire est valide
    if form.validate_on_submit():
        book.title = form.title.data
        book.price = form.price.data
        book.image = form.image.data
        db.session.commit()
        return redirect(url_for('detail', id=book.id-1))

    return render_template('edit_book.html', form=form, book=book)