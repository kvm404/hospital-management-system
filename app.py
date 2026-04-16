from flask import Flask
from flask_login import LoginManager
from models import db, User, Department

# Import Blueprints
from routes.auth import auth_bp
from routes.patient import patient_bp
from routes.doctor import doctor_bp
from routes.admin import admin_bp

# Initializaton
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'hospitalsystem'
db.init_app(app)

# login manager setup
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Register Blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(patient_bp)
app.register_blueprint(doctor_bp)
app.register_blueprint(admin_bp)

# run
if __name__ == '__main__':
    with app.app_context():
        db.create_all()

    # Creating a Admin if not exist 
        if not User.query.filter_by(role='admin').first():
            new_admin = User(
                name='Mr. Admin',
                email='admin@hms.com',
                role='admin',
            )
            new_admin.set_password('admin123')
            db.session.add(new_admin)
            db.session.commit()
            print('Admin user created!!')

    # Creating some default Departments
        if not Department.query.first():
            depts = [
                Department(name='General', description='General Physician'),
                Department(name='Cardiology', description='Heart Specialist'),
                Department(name='Dermatology', description='Skin Specialist'),
                Department(name='Neurology', description='Brain Specialist')
            ]
            db.session.add_all(depts)
            db.session.commit()
            print("Default Departments Created!!")

    app.run(debug=True)