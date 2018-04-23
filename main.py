from flask import Flask, request, redirect, render_template, session
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:blogz@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
app.secret_key = '420'
db = SQLAlchemy(app)

class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), unique=True)
    body = db.Column(db.String(200))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, entry, owner):
        self.title = title
        self.body = entry
        self.owner = owner

    def __repr__(self):
        return '<Blog %r>' % self.id
      

class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120))
    password = db.Column(db.String(200))
    blogs = db.relationship('Blog', backref="owner")

    def __init__(self, username, password):
        self.username = username
        self.password = password

    def __repr__(self):
        return '<Blog %r>' % self.id


def get_users():
    return User.query.all()   

def get_blogs():
    return Blog.query.all()

@app.route("/login", methods=['POST', 'GET'])
def login():  
    if request.method == 'POST':
        error_msg = ""
        username_in = request.form['username']
        password_in = request.form['password']

        if not (username_in and password_in):
            error_msg = "Username/Password Required"
        
        else:
            existing_user = User.query.filter_by(username=username_in).first()

            if not existing_user:
                error_msg = "Username not found"
            else:
                if password_in != existing_user.password:
                    error_msg = "Invalid Password"
        if error_msg:
            return render_template('login.html', err_p=error_msg, username_p=username_in)

        else:
            session['username'] = username_in
            print(session)
            return redirect ("/newpost")

    return render_template('login.html')

@app.route("/signup", methods=['GET', 'POST'])
def signup():  
    if request.method == 'POST':
        namein = request.form['username']
        pwin = request.form['password']
        vpwin = request.form['verify']
        namein_error = ""
        pwin_error = ""
        vpwin_error = ""

        if namein:
            if " " in namein:
                namein_error = "Username cannot contain spaces"    
            else:
                if len(namein) < 3 or len(namein) > 20:
                    namein_error = "Username must be between 3 and 20 characters in length"
        else:
            namein_error = "Username cannot be empty"

        if pwin:
            if " " in pwin:
                pwin_error = "Password cannot contain spaces"    
            else:
                if len(pwin) < 3 or len(pwin) > 20:
                    pwin_error = "Password must be between 3 and 20 characters in length"
        else:
            pwin_error = "Password cannot be empty"

        if vpwin:
            if vpwin != pwin:
                vpwin_error = "Passowrds do not match, Please re-enter matching passwords"

        else:
            vpwin_error = "Verification password cannot be empty"

        if namein_error or pwin_error or vpwin_error:
            return render_template("signup.html", un_1=namein, un_p=namein_error,
            pw_p=pwin_error, vpw_p=vpwin_error)
        else:
            existing_user = User.query.filter_by(username=namein).first()

            if existing_user:
                namein_error = "Username Currently In Use"
                return render_template("signup.html", un_1=namein, un_p=namein_error,
                pw_p=pwin_error, vpw_p=vpwin_error)
            
            else:
                new_user = User(namein, pwin)
                db.session.add(new_user)
                db.session.commit()
                session['username'] = namein

                return redirect('/blog')
 
    return render_template('signup.html')

@app.route("/")
def index():
    return render_template('index.html', users=get_users())

@app.before_request
def require_login():
    allowed_routes = ['login', 'signup', 'all_posts', 'index']

    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect("/login")

@app.route("/logout")
def logout():
    del session['username']
    return redirect("/blog")

@app.route("/blog")
def all_posts():
    id_scrin = request.args.get('blog_id')

    user_id = request.args.get('user_id')

    if user_id:
        user_blogs = Blog.query.filter_by(owner_id=user_id).all()
        return render_template("blog_guts.html", blogs=user_blogs)
    
    if id_scrin:
        blog_get = Blog.query.filter_by(id=id_scrin).first()
        return render_template("blog_guts.html", blogs=blog_get)
        
    return render_template('blog_guts.html', blogs=get_blogs())

@app.route("/newpost", methods=['POST', 'GET'])
def newpost():
    if request.method == 'POST':

        title_blog = (request.form['title_in'])
        entry_blog = (request.form['entry_in'])
        print("entry=", entry_blog)
    
        if not title_blog:
            error_title = "Please enter a title"
        else:
            error_title=""

        if not entry_blog:
            error_entry = "Please enter blog content"
        else:
            error_entry = ""

        if error_title or error_entry:
            return render_template("blog_add.html", error_title=error_title, 
                error_content=error_entry, title_in=title_blog, entry_in=entry_blog)
        else:
    # create new blog object to add to db
            owner = User.query.filter_by(username=session['username']).first()
            blog_object = Blog(title_blog, entry_blog, owner)
            print("blog_object value", blog_object)

    
            
            db.session.add(blog_object)
            db.session.commit()
            return redirect('/blog?blog_id=' + str(blog_object.id))

    else:
        return render_template('blog_add.html')


if __name__ == '__main__':
    app.run()