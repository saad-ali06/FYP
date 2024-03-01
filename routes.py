from flask import Flask, render_template, url_for, flash, redirect, session, request
from forms import RegistrationForm, LoginForm
from func import  port, check_password_email, registration_checker, add_post_to_db, get_post_db
from func import delete_post_from_db, edit_post_form_db
from datetime import timedelta
import secrets


app = Flask(__name__)
app.config['SECRET_KEY'] = secrets.token_hex(16)
# session lifetime is only 1min
# session logout after 1min
app.permanent_session_lifetime = timedelta(minutes=3)

posts = []
# Route for home page
@app.route("/")
@app.route("/home")
def home():
    if 'user_name' in session:
        posts =  get_post_db(session['email'])
    else:
        posts = []
    return render_template('home.html', session=session,posts=posts)

# Route for about page
@app.route("/about")
def about():
    return render_template('about.html', title='About')

# Route for user registration
@app.route("/register", methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    
    # Check if user is already logged in
    if 'user_name' in session:
        return redirect(url_for('home'))
    else:
        if form.validate_on_submit():
            # Collect user data from registration form
            user_data = registration_checker(form.username.data,form.email.data,form.password.data)
            
            if user_data:
                session['user_name'] = user_data['user_name']
                session['email'] = user_data['email']
                session['password'] = user_data['password']
                session['c_time'] = user_data['c_time']
                session['posts'] = user_data['posts']
                
                user_data = dict(session)
                # Insert user data into the database
                # user_table.insert_one(user_data)
                flash(f'Account created for {form.username.data}!', 'success')
                return redirect(url_for('home'))
            else:
                flash('Username or Email exists','danger')
            
    return render_template('register.html', title='Register', form=form)


# Route for user login
@app.route("/login", methods=['GET', 'POST'])
def login():
    form = LoginForm()
    
    # Check if user is already logged in
    if 'user_name' in session:
        return redirect(url_for('home'))
    else:
        if form.validate_on_submit():
            # Assuming u is the user retrieved from the database
            # Check if login credentials are valid
            user_data = check_password_email(form.email.data,form.password.data)
            if user_data:
                # Set session data for the logged-in user
                session['user_name'] = user_data['user_name']
                session['email'] = user_data['email']
                session['password'] = user_data['password']
                session['c_time'] = user_data['c_time']
                flash('You have been logged in!', 'success')
                
                return redirect(url_for('home'))
            else:
                flash('Login Unsuccessful. Please check username and password', 'danger')

    return render_template('login.html', title='Login', form=form)


# session pop/logout route 
@app.route('/logout/')
def clear_session_key():
    # Replace 'key_to_pop' with the key you want to remove from the session
    session.pop('user_name', None)
    return redirect(url_for('home'))

@app.route('/add_post/', methods=['GET', 'POST'])
def add_post():
    if request.method == 'POST':
        post_title = request.form['title']
        post_content = request.form['content']
        if add_post_to_db(post_title,post_content,session['email'] ,session['user_name']):
            flash('Post Added','success')
            return redirect(url_for('home'))
        else:
            flash('Post not Added','danger')
    return render_template('add_post.html',title='Add Post')

@app.route('/delete_post/<int:index>', methods=['GET', 'POST'])
def delete_post(index):
    delete_post_from_db(index, session['email'])
    flash('Post Deleted ','success')
    return redirect(url_for('home'))

@app.route('/edit_post/<int:index>', methods=['GET', 'POST'])
def edit_post(index):
    if request.method == "POST":
        print('--------------',index,type(index),'---------------')
        new_title= request.form['new_title']
        new_content = request.form['new_content']
        # print(post,type(post))
        edit_post_form_db(index,new_title,new_content,session['email'])
        flash("Post Updated ","success")
        return redirect(url_for('home'))
    else:
        return render_template('edit_post.html',index=index,title="Update Post")
    
        

# Run the application
if __name__ == '__main__':
    app.run(debug=True, port=port)

