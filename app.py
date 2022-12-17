from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
import requests
from flask import (
   Flask,
   redirect,
   render_template,
   request,
   url_for,
)

from flask_login import (
    LoginManager,
    current_user,
    login_user,
    login_required,
    login_manager,
    logout_user,
    UserMixin,
)



app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'
app.config['SECRET_KEY'] = 'very secret key'

db = SQLAlchemy(app)

login_manager = LoginManager(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))


class Project(db.Model):
    #db.Integer, db.String(x) itp - jaki typ danych w kolumnie; x - ile znaków maks. 
    id = db.Column(db.Integer, primary_key=True) #pirmary_key = True --> nie może być 2 takich samych elementów w tej kolumnie
    title = db.Column(db.String(100), nullable=False) #nullable = False --> trzeba coś wpisać
    categories = db.Column(db.String(100), nullable=False)
    link = db.Column(db.String(100), nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now) #wpisać datę trzeba; nic nie wpisane = obecna data
    finished = db.Column(db.Boolean) 

    def __repr__(self):
        return '<Project %r>' % self.title

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(50))

@app.route("/")
def home():
    my_projects = Project.query.all()
    weather_mood = get_weather_mood()
    return render_template('index.html', user=current_user, my_projects=my_projects, weather_mood=weather_mood) #uruchamia stronę

#========================================= Funkcja dodania projektu =========================================#
# @app.route("/projects", methods=["POST"])
# def add_project():
#     title = request.form.get("title")
#     categories = request.form.get("categories")
#     link = request.form.get("link")

#     new_project = Project(
#         title=title,
#         categories=categories,
#         link=link,
#     )

#     db.session.add(new_project)
#     db.session.commit()
#     db.session.close()
#     return redirect(url_for('home'))

# #======================================== Funkcja usuwania projektu ========================================#
# @app.route("/projects/<int:id>/delete")
# def delete_project(id):
#      project = Project.query.get_or_404(id)
#      db.session.delete(project)
#      db.session.commit()
#      return redirect(url_for('home'))

# #================================ Funkcja zmieniania statusu(nie/ukońsczony) ================================#
# @app.route("/projects/<int:id>/change_status")
# def change_status(id):
#      project = Project.query.get_or_404(id)
#      project.finished = not project.finished
#      db.session.commit()
#      return redirect(url_for('home'))

# #======================================== Funkcja edytowania projektu ========================================#
# @app.route("/projects/<int:id>/edit", methods=["GET", "POST"])
# def edit_project(id):
#    project = Project.query.get_or_404(id)

#    if request.method == "GET":
#        return render_template('edit_project.html', project=project)

#    project.title = request.form.get("title")
#    project.categories = request.form.get("categories")
#    project.link = request.form.get("link")
#    db.session.commit()
#    return redirect(url_for('home'))

#================================================= Pogoda =================================================#

def get_weather_data():
   weather_data = requests.get(
       url='https://danepubliczne.imgw.pl/api/data/synop/station/warszawa'      #pobiera dane ze strony
   ).json()
   temperature = float(weather_data['temperatura'])     #zapisywanie danych
   pressure = float(weather_data['cisnienie'])
   rainfall = float(weather_data['suma_opadu'])
   wind = float(weather_data['predkosc_wiatru'])
   return temperature, pressure, rainfall, wind     #zwraca temperaturę, ciśnienie i opady

def get_weather_mood():
    temperature, pressure, rainfall, wind = get_weather_data()       #pobiera dane z funkcji powyżej
    work_mood = 'sprzyja'       # 0 danych = pogoda sprzyja
    comment = 'więc prawdopodobnie pracuję nad którymś z projektów'    
    if pressure < 1010:  # niekorzystne cisnienie
        work_mood = 'nie sprzyja'
        comment = 'ciśnienie jest za niskie'
    elif  pressure > 1020:
        work_mood = 'nie sprzyja'
        comment = 'ciśnienie jest za wysokie'
    else: # cisnienie sprzyja
        if rainfall < 10:  # deszcz nie pada
            if temperature > 20:  # jest ciepło
                work_mood = 'nie sprzyja'
                comment = 'jest ciepło i nie pada, więc zapewnie jestem offline :)'
            elif temperature <20 and temperature>10:
                work_mood = 'sprzyja'
                comment = 'ale sprzyja również spacerom'
            else:  # temperatura nie za wysoka
                work_mood = 'sprzyja'
                comment = 'jest zimno, więc pewnie siedzę przed komputerem :D'
            
    if rainfall < 1:
        rain_info = 'Dziś nie pada'
    elif rainfall < 10:
        rain_info = 'Może lekko popadać'
    else:
        rain_info = 'Weź parasol!'

    if rainfall <10:
        if wind > 5:
            wind_info = 'ale lepiej nie wychodź z domu, bo cię przewieje!'
        else:
            wind_info = 'i wiatr nie jest silny :)'

    return f'Pogoda {work_mood} programowaniu, {comment}. PS. {rain_info}, {wind_info}'

#================================================================== LOGOWANIE ==================================================================#
    
@app.route("/projects", methods=["POST"])
@login_required
def add_project():
    title = request.form.get("title")
    categories = request.form.get("categories")
    link = request.form.get("link")

    new_project = Project(
        title=title, 
        categories=categories,
        link=link,
    )

    db.session.add(new_project)
    db.session.commit()
    db.session.close()
    return redirect(url_for('home'))


@app.route("/projects/<int:id>/change_status")
@login_required
def change_status(id):
    project = Project.query.get_or_404(id)
    project.finished = not project.finished
    db.session.commit()
    return redirect(url_for('home'))

@app.route("/projects/<int:id>/delete")
@login_required
def delete_project(id):
    project = Project.query.get_or_404(id)
    db.session.delete(project)
    db.session.commit()
    return redirect(url_for('home'))

@app.route("/projects/<int:id>/edit", methods=["GET", "POST"])
@login_required
def edit_project(id):
    project = Project.query.get_or_404(id)

    if request.method == "GET":
        return render_template('edit_project.html', project=project)

    project.title = request.form.get("title")
    project.categories = request.form.get("categories")
    project.link = request.form.get("link")
    db.session.commit()
    return redirect(url_for('home'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user = User.query.filter_by(username=username).first()
        if user:
            if user.password == password:
                login_user(user, remember=True)
                return redirect(url_for('home'))

    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))