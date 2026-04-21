from datetime import date
from flask import Blueprint, render_template, request, url_for, redirect, flash, abort
from flask_login import login_required, current_user
from models import db, User, Doctor, Department, Slot, Appointment, Treatment

admin_bp = Blueprint('admin', __name__)

# ADMIN DASHBOARD
@admin_bp.route('/admin_dashboard')
@login_required
def admin_dashboard():
    if current_user.role != 'admin':
        abort(403)

    total_doctors = Doctor.query.count()
    total_patients = User.query.filter_by(role='patient').count()
    total_treatments = Treatment.query.count()
    todays_appointments = Appointment.query.join(Slot).filter(
        Slot.date == date.today(),
        Appointment.status == 'booked'
    ).count()

    # Doctor search
    d_query = request.args.get('d')
    doc_base = Doctor.query.join(User).join(Department) 
    if d_query:
        search_term = f"%{d_query}%"
        doctors = doc_base.filter(
            (User.name.ilike(search_term)) | 
            (Department.name.ilike(search_term))
        ).all()
    else:
        doctors = doc_base.all()

    # Patient Search
    p_query = request.args.get('p')
    pat_base = User.query.filter_by(role='patient')
    if p_query:
        search_term = f"%{p_query}%"
        patients = pat_base.filter(
            (User.name.ilike(search_term)) | 
            (User.email.ilike(search_term)) |
            (User.phone.ilike(search_term))
        ).all()
    else:
        patients = pat_base.all()

    up_appointments = (Appointment.query
                    .join(Slot)
                    .filter(Slot.date >= date.today())
                    .order_by(Slot.date.asc(), Slot.time.desc())
                    .all())
    
    past_appointments = (Appointment.query
                    .join(Slot)
                    .filter(Slot.date < date.today())
                    .order_by(Slot.date.asc(), Slot.time.desc())
                    .all())

    return render_template('admin/admin_dash.html', 
                           doctors=doctors, 
                           patients=patients, 
                           up_appointments=up_appointments,
                           past_appointments=past_appointments,
                           total_doctors=total_doctors,
                           total_patients=total_patients,
                           total_treatments=total_treatments,
                           todays_appointments=todays_appointments)


# ADD NEW DOCTOR
@admin_bp.route('/add_doctor', methods=['GET', 'POST'])
@login_required
def add_doctor():
    if current_user.role != 'admin':
        abort(403)

    departments = Department.query.all()

    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        password = request.form.get('password')
        dept_id = request.form.get('dept_id')
        description = request.form.get('description')

        # Validation
        if User.query.filter_by(email=email).first():
            flash("Email already registered!", "warning")
            return redirect(url_for('admin.add_doctor'))

        # New Doctor (Login Details)
        new_user = User(
            name=name, 
            email=email, 
            phone=phone, 
            role='doctor'
        )
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()

        # New Doctor Entry (Profile Details)
        new_doctor = Doctor(
            user_id=new_user.id,
            dept_id=dept_id,
            description=description
        )
        
        db.session.add(new_doctor)
        db.session.commit()

        flash(f"{name} added successfully!", "success")
        return redirect(url_for('admin.admin_dashboard'))

    return render_template('admin/add_doctor.html', departments=departments)


# BLOCK/UNBLOCK Patient and Doctors
@admin_bp.route('/toggle_block/<int:user_id>')
@login_required
def toggle_block(user_id):
    if current_user.role != 'admin':
        abort(403)

    user = User.query.get_or_404(user_id)
    
    user.is_blocked = not user.is_blocked
    
    db.session.commit()
    
    status = "Blocked" if user.is_blocked else "Unblocked"
    flash(f"{user.name} has been {status}!", "success")
    
    return redirect(url_for('admin.admin_dashboard'))


# ADD DEPARTMENT
@admin_bp.route('/add_department', methods=['GET', 'POST'])
@login_required
def add_department():
    if current_user.role != 'admin':
        abort(403)

    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')

        if Department.query.filter_by(name=name).first():
            flash(f"Department '{name}' already exists!", "warning")
            return redirect(url_for('admin.add_department'))

        # New Department
        new_dept = Department(name=name, description=description)
        db.session.add(new_dept)
        db.session.commit()

        flash(f"Department '{name}' added successfully!", "success")
        return redirect(url_for('admin.admin_dashboard'))

    return render_template('admin/add_department.html')


# Update Doctor's Profile
@admin_bp.route('/edit_doctor/<int:user_id>', methods=['GET', 'POST'])
@login_required
def edit_doctor(user_id):
    if current_user.role != 'admin':
        abort(403)

    doctor = Doctor.query.get_or_404(user_id)
    departments = Department.query.all()

    if request.method == 'POST':
        doctor.user.name = request.form.get('name')
        doctor.dept_id = request.form.get('dept_id')
        doctor.description = request.form.get('description')

        db.session.commit()
        
        flash(f"{doctor.user.name}'s profile updated successfully!", "success")
        return redirect(url_for('admin.admin_dashboard'))

    return render_template('admin/edit_doctor.html', doctor=doctor, departments=departments)


# DELETE USER
@admin_bp.route('/delete_user/<int:user_id>', methods=['POST'])
@login_required
def delete_user(user_id):
    if current_user.role != 'admin':
        abort(403)

    user = User.query.get_or_404(user_id)
    name = user.name
    
    db.session.delete(user)
    db.session.commit()
    
    flash(f"User '{name}' and all associated data have been deleted.", "success")
    return redirect(url_for('admin.admin_dashboard'))
