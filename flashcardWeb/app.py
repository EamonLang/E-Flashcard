from flask import Flask, render_template,request,jsonify,redirect,session,url_for,flash
import mysql.connector
from flask_login import UserMixin, login_user, LoginManager,login_required,logout_user,current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired, Length, ValidationError
from flask_bcrypt import Bcrypt
from datetime import datetime, timedelta
from itsdangerous import URLSafeTimedSerializer
from flask_mail import Mail, Message
from zoneinfo import ZoneInfo
import os
from dotenv import load_dotenv
import agent

load_dotenv()



class User(UserMixin):
    def __init__(self,id,name,password,email):
        self.id = id
        self.name=name
        self.password = password
        self.email = email
        self.score=()
    def get_id(self):
        return str(self.id)
    def get_token(self,expires_sec=300):
        serial=URLSafeTimedSerializer(app.secret_key)
        return serial.dumps({'user_id':self.id},salt=app.config['SECURITY_PASSWORD_SALT'])
    @staticmethod
    def verify_token(token,expires_sec=300):
        serial = URLSafeTimedSerializer(app.secret_key)
        try:
            user_id=serial.loads(token,salt=app.config['SECURITY_PASSWORD_SALT'],max_age=expires_sec)['user_id']
            return manager.get_user(user_id)
            
        except:
            return None
    @property
    def is_authenticated(self):
        return True

    @property
    def is_active(self):
        return True

    @property
    def is_anonymous(self):
        return False

    


class SQLManager:
    def get_connection(self):
        try:
            connection = mysql.connector.connect(
                host=os.getenv('DB_HOST'),
                user=os.getenv('DB_USER'),
                password=os.getenv('DB_PASSWORD'),
                database=os.getenv('DB_NAME')
            )
            return connection
        except mysql.connector.Error as e:
            msg = f"Error occured in get_connection. Message: {e}"
            self.save_error(msg)
            raise
    
    def save_set(self,title):
        try:
            connection = self.get_connection()
            cursor = connection.cursor()
            
            query= "INSERT INTO flashcard_sets (user_id,set_name) VALUES (%s,%s)"
            values = (current_user.id,title)
            cursor.execute(query,values)
            connection.commit()
            cursor.execute("SELECT id FROM flashcard_sets WHERE set_name = %s", (title,))
            set_id = cursor.fetchone()
            print(f"Set ID inserted: {set_id}")
            return set_id
        except mysql.connector.Error as e:
            print(f"Erorr in save_set: {e}")
            self.save_error(e)
            raise

    def save_pair(self,question,answer,title):
        try:
            connection = self.get_connection()
            cursor = connection.cursor()
            query = "SELECT id FROM flashcard_sets WHERE set_name = %s"
            values = (title,)
            cursor.execute(query,values)
            set_id = cursor.fetchone()

            if set_id:
                set_id = set_id[0]
                insert_query = "INSERT INTO flashcards (set_id,question,answer) VALUES(%s,%s,%s)"
                values2 = (set_id,question,answer)
                cursor.execute(insert_query,values2)
                connection.commit()
            else:
                raise ValueError
        except mysql.connector.Error as e:
            msg = f"Error occured in save_pair. Message: {e}"
            self.save_error(msg)

            raise
    def load_titles(self):
        try:
            connection = self.get_connection()
            cursor = connection.cursor()
            if not current_user.is_anonymous:
                id = current_user.id
                query= "SELECT set_name FROM flashcard_sets WHERE user_id = %s"
                values = (id,)
                cursor.execute(query,values)

                sets = cursor.fetchall()
                if len(sets)>0:
                    return sets
                else:
                    return ("Create sets to begin practicing!",)
            else:
                return ("Login to create sets",)
        except mysql.connector.Error as e:
            msg = f"Error occured in load_titles. Message: {e}"
            self.save_error(msg)
            raise
    def load_cards(self,title):
        try: 
            connection = self.get_connection()
            cursor = connection.cursor()
            query="SELECT id FROM flashcard_sets WHERE set_name = %s"
            values = (title,)
            cursor.execute(query,values)
            set_id = cursor.fetchone()
            if set_id:
                set_id = set_id[0]
                query2 = "SELECT question, answer FROM flashcards WHERE set_id = %s"
                values2 = (set_id,)
                cursor.execute(query2,values2)
                results = cursor.fetchall()
                return results
            else:
                print(f"Error: No set with that title")
                return None
        except mysql.connector.Error as e:
            msg = f"Error occured in load_cards. Message: {e}"
            self.save_error(msg)
            raise
    def delete_set(self,title):
        try: 
            connection = self.get_connection()
            cursor = connection.cursor()
            get_id_query = "SELECT id FROM flashcard_sets WHERE set_name = %s"
            title_values = (title,)
            cursor.execute(get_id_query,title_values)
            set_id = cursor.fetchone()
            if set_id:
                set_id = set_id[0]
                #drops the set name from the flashcard_sets table
                set_query = "DELETE FROM flashcard_sets WHERE id = %s"
                cursor.execute(set_query,(set_id,))
                connection.commit()
                #now drops the flashcards from the flashcards table
                flashcard_query = "DELETE FROM flashcards WHERE set_id = %s"
                cursor.execute(flashcard_query,(set_id,))
                connection.commit()
                print(f"Succesfully deleted")
                return "success"
            else:
                print(f"Error: No set with that title")
                return None
        except mysql.connector.Error as e:
            msg = f"Error occured in delete_set. Message: {e}"
            self.save_error(msg)
            raise
    
    def validate_user(self,username):
        try:
            connection = self.get_connection()
            cursor = connection.cursor()
            query= "SELECT name FROM flashcard_users WHERE name=%s"
            values=(username,)
            cursor.execute(query,values)
            user = cursor.fetchone()
            return user
        except mysql.connector.Error as e:
            msg = f"Error occured in validate_user. Message: {e}"
            self.save_error(msg)
    
    def add_user(self,username,password,email):
        try:
            connection = self.get_connection()
            cursor = connection.cursor()
            query= "INSERT INTO flashcard_users(name,password,email) VALUES(%s,%s,%s)"
            values = (username,password,email)
            cursor.execute(query,values)
            connection.commit()
            user_id = cursor.lastrowid
            return user_id
        except mysql.connector.Error as e:
            msg = f"Error occured in add_user. Message: {e}"
            self.save_error(msg)
            raise
    #used to load user information based on their id
    def get_user(self,id):
        try:
            connection = self.get_connection()
            cursor = connection.cursor()
            query="SELECT * FROM flashcard_users WHERE id=%s"
            values=(id,)
            cursor.execute(query,values)
            user = cursor.fetchone()
            if user:
                user = User(user[0],user[1],user[2],user[3])
                return user
            else:
                print("No user found")
        except mysql.connector.Error as e:
            msg = f"Error occured in get_user. Message: {e}"
            self.save_error(msg)
            return "Error in get user"

    #check to see if user exists
    def check_user(self,username):
        try:
            connection = self.get_connection()
            cursor = connection.cursor()
            query= "SELECT * FROM flashcard_users WHERE name =%s"
            values = (username,)
            cursor.execute(query,values)
            user = cursor.fetchone()
            if user != None:
                real_user = User(user[0],user[1],user[2],user[3])
                return real_user
            else:
                print("no user found")
        except mysql.connector.Error as e:
            msg = f"Error occured in check_user. Message: {e}"
            self.save_error(msg)
            return "Error in check_user"
    
    def update_score(self,score,date):
        try:
            connection = self.get_connection()
            cursor = connection.cursor()
            query = "SELECT score FROM flashcard_users WHERE id=%s"
            values = (current_user.id,)
            cursor.execute(query,values)
            user_score = cursor.fetchone()
            if user_score:
                user_score = user_score[0]
                try:
                    user_score = int(user_score)
                    user_score += score
                except ValueError:
                    print("Error with inting the user_score")
            else:
                print("no use score")

            update_score = "UPDATE flashcard_users SET score = %s WHERE id=%s"
            new_values =(user_score,current_user.id)

            cursor.execute(update_score,new_values)
            connection.commit()

            update_date_query = "INSERT INTO user_practice_dates (user_id,practice_date) VALUES (%s,%s)"
            date_values = (current_user.id,date)
            cursor.execute(update_date_query,date_values)
            connection.commit()
        except mysql.connector.Error as e:
            msg = f"Error occured in update_score. Message: {e}"
            self.save_error(msg)
    def retrieve_date(self):
        try:
            connection = self.get_connection()
            cursor = connection.cursor()
            query = "SELECT practice_date FROM user_practice_dates WHERE user_id = %s AND practice_date BETWEEN %s AND %s"
            today = datetime.now()
            one_week = today-timedelta(days=7)
            if not current_user.is_anonymous:
                values = (current_user.id,one_week,today)
                cursor.execute(query,values)
                dates = cursor.fetchall()
                return dates
            else:
                return("login")
        except mysql.connector.Error as e:
            msg = f"Error occured in retrieve_date. Message: {e}"
            self.save_error(msg)
    def user_score(self):
        try:
            connection = self.get_connection()
            cursor = connection.cursor()
            query = "SELECT score,score_goal FROM flashcard_users WHERE id = %s"
            values = (current_user.id,)
            cursor.execute(query,values)
            score = cursor.fetchone()
            # retrieve the scores and the score_goal
            if score:
                user_score = score[0]
                score_goal = score[1]
                # now check if the score_goal should be updated or not
                if user_score>=score_goal:
                    # if score is greater than goal double the score and update the goal score
                    score_goal = score_goal*2
                    update = "UPDATE flashcard_users SET Score_goal =%s WHERE id=%s "
                    update_values = (score_goal,current_user.id)
                    cursor.execute(update,update_values)
                    connection.commit()
                    return (user_score,score_goal)
                # otherwise just return the score goal and user score
                return (user_score,score_goal)
            else:
                print("error retrieving score")
                return "Error retrieving score"
        except mysql.connector.Error as e:
            msg = f"Error occured in user_score. Message: {e}"
            self.save_error(msg)
            return "Failure getting score"
    def check_email(self,email):
        try:
            connection = self.get_connection()
            cursor = connection.cursor()
            query = "SELECT * FROM flashcard_users WHERE email=%s"
            values = (email,)
            cursor.execute(query,values)
            user = cursor.fetchone()
            if user:
                user= User(user[0],user[1],user[2],user[3])
                return user
            return None
        except mysql.connector.Error as e:
            msg = f"Error occured in check_mail. Message: {e}"
            self.save_error(msg)
            return "Database failure checking user email"
        
    def save_new_password(self,password,user_id):
        try:
            connection = self.get_connection()
            cursor = connection.cursor()
            query="UPDATE flashcard_users SET password = %s WHERE id=%s"
            values= (password,user_id)
            cursor.execute(query,values)
            connection.commit()
            print("Succesful update password")
        except mysql.connector.Error as e:
            msg = f"Error occured in save_new_password. Message: {e}"
            self.save_error(msg)
            return "Database error when saving password"
    
    def feedback_message(self,message):
        try:
            connection = self.get_connection()
            cursor = connection.cursor()
            if not current_user.is_anonymous:
                get_user = "SELECT name FROM flashcard_users WHERE id=%s"
                user_id = (current_user.id,)
                cursor.execute(get_user,user_id)
                user_name = cursor.fetchone()
                if user_name:
                    user_name = user_name[0]
                    update = "INSERT INTO feedback (user_id,user_name,message,time_of_msg) VALUES (%s,%s,%s,%s)"
                    time = datetime.now()
                    values = (current_user.id,user_name,message,time)
                    cursor.execute(update,values)
                    connection.commit()
                    return "submitted"
                else:
                    print("error getting user from database")
                    return None
            else:
                return None
        except mysql.connector.Error as e:
            msg = f"Error occured in feedback_message. Message: {e}"
            self.save_error(msg)
            return None
    def save_error(self,error):
        try:
            connection = self.get_connection()
            cursor = connection.cursor()
            query = "INSERT INTO errors (error,time) VALUES(%s,%s)"
            date = datetime.now()
            values = (error,date)
            cursor.execute(query,values)
            connection.commit()
            return "Succesfully commited"
        except mysql.connector.Error as e:
            print(f"error: An error occured in save_error {e}")

    def save_ai_cards(self,question,answer):
        try:
            connection = self.get_connection()
            cursor = connection.cursor()
            query="INSERT INTO ai_cards (user_id,question,answer,date_created) VALEUS (%s,%s,%s,%s)"
            date = datetime.now()
            values = (current_user.id,question,answer,date)
            cursor.execute(query,values)
            connection.commit()
            return "Succesfully added ai cards"
        except mysql.connector.Error as e:
            msg = f"An error has occured when trying to save ai cards. Error: {e}"
            self.save_error(msg)






        



manager = SQLManager()


class RegisterForm(FlaskForm):
    username = StringField(validators = [InputRequired(),Length(min=4,max=20)],render_kw={"placeholder": "Username"})
    password = PasswordField(validators = [InputRequired(),Length(min=4,max=20)],render_kw={"placeholder":"Password"})
    email = StringField(validators=[InputRequired(),Length(min=5,max=50)],render_kw={"placeholder":"E-mail"})
    submit = SubmitField("sign up")

    def validate_username(self,username):
        prev_user = manager.validate_user(username.data)
        if prev_user:
            raise ValidationError("Error: That username already exists")

class LoginForm(FlaskForm):
    username = StringField(validators = [InputRequired(),Length(min=4,max=20)],render_kw={"placeholder": "Username"})
    password = PasswordField(validators = [InputRequired(),Length(min=4,max=20)],render_kw={"placeholder":"Password"})
    submit = SubmitField("Login")

class ResetForm(FlaskForm):
    email = StringField(validators = [InputRequired(),Length(min=4,max=50)],render_kw={"placeholder": "E-mail"})
    submit = SubmitField("Reset Password")

class NewPasswordForm(FlaskForm):
    password = PasswordField(validators = [InputRequired(),Length(min=4,max=20)],render_kw={"placeholder":"Password"})
    confirm_password = PasswordField(validators = [InputRequired(),Length(min=4,max=20)],render_kw={"placeholder":"Password"})
    submit = SubmitField("Reset Password")


        


app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY')
bcrypt = Bcrypt(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"
app.config['SECURITY_PASSWORD_SALT'] = os.getenv('SECURITY_PASSWORD_SALT')


app.config['MAIL_SERVER'] =os.getenv('MAIL_SERVER')
app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT'))
app.config['MAIL_USE_TLS'] =  os.getenv('MAIL_USE_TLS') == 'True'
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')

mail = Mail(app)

@login_manager.user_loader
def load_user(user_id):
    return manager.get_user(user_id)



@app.route('/')
def home():
    # get days of the week for the past seven days || +timedelta(days=1)
    today = datetime.now(ZoneInfo("America/New_York")) 
    pastdates = [today-timedelta(days=i) for i in range(7)]
    days_of_week = [date.strftime("%a") for date in pastdates]
    days_of_week.reverse()
    days_of_week[len(days_of_week)-1]="Today"
    user = {}
    if current_user.is_authenticated:
        score = manager.user_score()
        # passes score name score_goal and progress to the html so it can be displayed
        user['name']=current_user.name
        user['score']=score[0]
        user['score_goal']=score[1]
        
        progress= ((score[0]-(score[1]/2))/(score[1]/2)) *100
            
        user['percent_completed'] = progress

    else:
        user['name']='Guest'
        user['score']='Login to start a score'
        user['percent_completed']=0
        
    return render_template('index.html',days_of_week = days_of_week,user=user)

@app.route('/create')
def create():
    return render_template("create.html")

@app.route('/delete')
def delete():
    return render_template("delete.html")


@app.route('/Self-create')
def auto_create():
    return render_template("auto_create.html")
@app.route('/set')
def set():
    return render_template('set.html')

# sends the reset password email to the user
def send_mail(user):
    token = user.get_token()

    msg = Message('Password Reset E-Flash',recipients=[user.email],sender='eamonlanglais67@gmail.com')
    msg.body = f''' To reset password. Please follow the link below

    {url_for('reset_token',token=token,_external=True)}

    If you didnt send a password reset request. Please ignore this message.

'''
    mail.send(msg)
    pass
# user enters email to which they want the reset password to be sent to. If email in database then it will send mail
@app.route('/reset',methods=['GET','POST'])
def reset():
    form = ResetForm()
    if form.validate_on_submit():
        user = manager.check_email(form.email.data)
        if user:
            send_mail(user)
            return redirect(url_for('login'))
        else:
            flash('No user with that E-mail')
    return render_template('reset_request.html',form=form)


# verifies the user and the correct token which it recieves from the url then user can enter new password
@app.route('/reset_password/<token>',methods=['GET','POST'])
def reset_token(token):


    user=User.verify_token(token)

    if user is None:
        flash("Expired Token. Please try again")
        return redirect(url_for('reset'))
    form = NewPasswordForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        manager.save_new_password(hashed_password,user.id)
        return redirect(url_for('login'))
    return render_template('change_password.html',form = form)

        
@app.route('/login',methods=['GET','POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = manager.check_user(form.username.data)
        if user:
            # if user exists checks to see if password entered is equal to the password of the user
            if bcrypt.check_password_hash(user.password, form.password.data):
                login_user(user)
                return redirect( url_for('home'))
            else:
                flash('Incorrect password or username')
        else:
            flash('Incorrect password or username')
            
    return render_template('login.html',form=form)

@app.route('/signUp',methods=['GET','POST'])
def sign_up():
    form = RegisterForm()
    if form.validate_on_submit():

        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user_id = manager.add_user(form.username.data,hashed_password,form.email.data)
        new_user = User(user_id,name=form.username.data,password = hashed_password,email=form.email.data)

        print(f"name{form.username.data}, password={hashed_password},email={form.email.data}")
        
        print(f"user_added: {new_user.name}")
        return redirect(url_for('login'))
    print("Form did not validate")
    return render_template('signUp.html',form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))


@app.route('/add_set',methods=['POST'])
def add_set():
    try:
        data = request.get_json()
        if not data:
            raise ValueError("no data recieved")

        title = data['title']
        manager.save_set(title)
        for card in data['cards']:
            manager.save_pair(card['question'],card['answer'],title)
       
        
        return jsonify({"status":"success","message":"Set added succesfully"}),200
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500
    
@app.route('/api/flashcard_title',methods=['GET'])
def get_titles():
    try:
        sets = manager.load_titles()

        return jsonify(sets)
    except Exception as e:
        print(f"Error: {e}")
        msg= f"Error in /add_set: {e}"
        manager.save_error(msg)
        return jsonify ({"status":"error","message":str(e)}),500


@app.route('/api/load_flashcards',methods = ['POST'])
def get_cards():
    
    if request.method == 'POST':#below gets the title that the user enters
        try:
            data = request.get_json()
            if not data:
                raise ValueError("Error: No data recieved")
            
            cards = manager.load_cards(data['title'])
            if cards:
                return jsonify ({"status":"success","flashcards":cards}),200
            else:
                return jsonify ({"status":"error","message":"no set with that title"})
        except Exception as e:
            msg= f"Error in /api/load_flashcards: {e}"
            manager.save_error(msg)
            return jsonify({"status":"error","message":"an error occured"}),500

@app.route('/delete_flashcards',methods = ['POST'])
def delete_flashcards():
    try:
        data = request.get_json()
        if not data:
            raise ValueError("Error: No data recieved")
        title = data['title']
        if title:
            title=title[0]
        result = manager.delete_set(title)
        if not result:
            return jsonify({"status":"error","message":"no title with that name"})
        return jsonify ({"status":"success","message":"succsesfully deleted"})

    except Exception as e:
        print(f"Error:{e}")
        msg= f"Error in /delete_flashcards: {e}"
        manager.save_error(msg)
        return jsonify({"status":"error","message":"an error has occured"})

@app.route('/update_score',methods=['POST'])
def update_score():
    try:
        data= request.get_json()
        if not data:
            raise ValueError("Error: No data recieved")
        score = data['score']
        date = data['time']
        if score and date:
            manager.update_score(score,date)
            return jsonify({"status":"success","message":"score updated succesfully"})
        else:
            return jsonify({"status":"error","message":"couldn't update score"})
    except Exception as e:
        print(f"error:{e}")
        msg= f"Error in /update_score: {e}"
        manager.save_error(msg)
        return ({"status":"error","message":"an error has occured"})
@app.route('/get_practice_dates',methods=['GET'])
def get_practice_dates():
    try:
        dates =manager.retrieve_date()
        if dates:
            return jsonify({"status":"success","dates":dates})
        else:
            return jsonify({"status":"success","dates":[]})

    except Exception as e:
        print(f"error: {e}")
        msg= f"Error in /get_practice_dates: {e}"
        manager.save_error(msg)
        return jsonify({"status":"error","message":"an error has occured"})

@app.route('/api/feedback',methods=['POST'])
def feedback():
    try:
        data = request.get_json()
        # add something to get stuff out of json
        message = data['feedback']
        save_message = manager.feedback_message(message)
        if save_message:
            return jsonify({"status":"success","message":"feedback noted succesfully"})
        else: 
            return jsonify({"status":"error","message":"issue saving message"})

    except Exception as e:
        print(f"error: {e}")
        msg= f"Error in /api/feedback: {e}"
        manager.save_error(msg)
        return jsonify({"status":"error","message":"error saving feedback"})

@app.route('/ai_flashcards',methods=['POST'])
def ai_flashcards():
    try:
        data = request.get_json()
        # get user request then create flashcards

        request = data["request"]
        flashcards = agent.find_information(request)
        
        if flashcards:
            manager.save_ai_cards(request,flashcards)
            return jsonify({"status":"success","flashcards":flashcards})
        else:
            return jsonify({"status":"error","message":"error creating flashcards"})
    except Exception as e:
        msg = "An error occured in the route ai_flashcards"
        manager.save_error(msg)
        return jsonify({"status":"error","message":"error creating flashcards"})
        
if __name__ == '__main__':
    app.run(debug=True)