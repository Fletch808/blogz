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
    body = db.Column(db.String(200))

    def __init__(self, title, entry):
        self.title = title
        self.body = entry

    def __repr__(self):
        return '<Blog %r>' % self.id
       # return '<Blog %r>' % self.title
       # return '<Blog %r>' % self.body


    # TODO add repl code

def get_blogs():
    return Blog.query.all()

@app.route("/blog")
def index():
    id_scrin = request.args.get('id')

    if id_scrin:
        blog_get = Blog.query.filter_by(id=id_scrin).first()
        return render_template('blog_detail.html', blog_title=blog_get.title, blog_body=blog_get.body)
    return render_template('blog_guts.html', blogs=get_blogs())

@app.route("/newpost", methods=['POST', 'GET'])
def newpost():
    if request.method == 'POST':

    # get input from add screen
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
            blog_object = Blog(title_blog, entry_blog)
            print("blog_object value", blog_object)

    # add object to db
            db.session.add(blog_object)
            db.session.commit()
            return redirect('/blog?id=' + str(blog_object.id))

    else:
        return render_template('blog_add.html')


if __name__ == '__main__':
    app.run()