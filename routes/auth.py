from flask import Blueprint, render_template, request, url_for, redirect, flash
from flask_login import login_required, current_user, logout_user, login_user
from models import db, User

auth_bp = Blueprint('auth', __name__)

# REGISTER 
@auth_bp.route('/register', methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for(f"{current_user.role}.{current_user.role}_dashboard"))

    if request.method == "POST":
        name = (request.form.get("username") or "").strip()
        email = (request.form.get("email") or "").strip().lower()
        phone = (request.form.get("phone") or "").strip() or None
        password = request.form.get("pass") or ""
        cpass = request.form.get("cpass") or ""

        # Validation
        if not name or not email or not password:
            flash("Name, email and password required!", "warning")
            return redirect(url_for("auth.register"))
        if password != cpass:
            flash("Passwords do not match!", "warning")
            return redirect(url_for("auth.register"))
        if User.query.filter_by(email=email).first():
            flash("Email already registered!", "warning")
            return redirect(url_for("auth.register"))

        # New Patient
        patient = User(name=name, email=email, phone=phone)
        patient.set_password(password)
        db.session.add(patient)
        db.session.commit()
        flash("Registration successful. Please log in!", "success")
        return redirect(url_for("auth.login"))
    
    return render_template('auth/register.html')

# LOGIN
@auth_bp.route('/login', methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = (request.form.get("email") or "").strip().lower()
        password = request.form.get("pass") or ""
        role = request.form.get("role") or ""
        user = User.query.filter_by(email=email).first()

        if not (user and password):
            flash("Invalid email or password!", "danger")
            return redirect(url_for("auth.login"))
        
        if not user.check_password(password):
            flash("Invalid email or password!", "danger")
            return redirect(url_for("auth.login"))
            
        if user.role != role:
            flash(f"You are not registered with {role} role!", "warning")
            return redirect(url_for("auth.login"))
        if user.is_blocked:
            flash("Account is blocked. Please contact admin!", "danger")
            return redirect(url_for("auth.login"))
        
        login_user(user)
        flash("Logged in successfully!", "success")

        # redirecting based on role 
        if user.role == "patient": 
            return redirect(url_for("patient.patient_dashboard"))
        elif user.role == "doctor":
            return redirect(url_for("doctor.doctor_dashboard"))
        elif user.role == "admin":
            return redirect(url_for("admin.admin_dashboard"))

    return render_template('auth/login.html')

# LOGOUT
@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash("Logged out!", "info")
    return redirect(url_for("auth.login"))
