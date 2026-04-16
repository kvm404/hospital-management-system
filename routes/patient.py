from datetime import date, timedelta, datetime
from flask import Blueprint, render_template, request, url_for, redirect, flash, abort
from flask_login import login_required, current_user
from models import db, User, Doctor, Department, Slot, Appointment, Treatment

patient_bp = Blueprint('patient', __name__)

# PATIENT DASHBOARD
@patient_bp.route('/patient_dashboard')
@login_required
def patient_dashboard():
    departments = Department.query.all()
    appointments = (
        Appointment.query
        .join(Slot) 
        .filter(Appointment.patient_id == current_user.id,
                Slot.date >= date.today())
        .order_by(Slot.date.asc(), Slot.time.desc()) 
        .all())
    
    return render_template('patient/patient_dash.html', departments=departments, appointments=appointments)

# PATIENT SEARCH
@patient_bp.route('/patient_search')
@login_required
def patient_search():
    q = request.args.get('q')
    search_term = f"%{q}%"
    doctors = (Doctor.query
               .join(User)
               .join(Department)
               .filter((User.name.ilike(search_term)) | 
                       (Department.name.ilike(search_term)))
               .all())

    return render_template('patient/search_results.html', doctors=doctors, q=q)

# DEPARTMENT DETAILS
@patient_bp.route('/department_details/<int:dept_id>')
@login_required
def department_details(dept_id):
    dept = Department.query.get_or_404(dept_id)
    return render_template('patient/dept_details.html', dept=dept)


# CANCEL APPOINTMENT  (patient/doctor)
@patient_bp.route('/cancel_appointment/<int:id>', methods=['POST'])
@login_required
def cancel_appointment(id):
    ap = Appointment.query.get_or_404(id)
    if (ap.patient_id != current_user.id) and (current_user.role not in ['admin', 'doctor']):
        abort(403)
    ap.status = 'cancelled'
    db.session.commit()
    flash('Appointment cancelled', 'success')
    return redirect(request.referrer)

# DOCTOR DETAILS
@patient_bp.route('/doctor_details/<int:doct_id>')
@login_required
def doctor_details(doct_id):
    doctor = Doctor.query.get_or_404(doct_id)
    return render_template('patient/doctor_details.html', doctor=doctor)


# DOCTOR AVAILABILITY & SLOT BOOKING
@patient_bp.route('/check_availability/<int:doctor_id>', methods=['GET', 'POST'])
@login_required
def check_availability(doctor_id):
    if current_user.role != 'patient':
        abort(403)
        
    doctor = Doctor.query.get_or_404(doctor_id)

    if request.method == 'POST':
        slot_id = request.form.get('slot_id')
        slot = Slot.query.get(slot_id)
        if not slot:
            flash("Slot not found!", "danger")
            return redirect(url_for('patient.check_availability', doctor_id=doctor_id))
        
        existing_booking = (Appointment.query
                            .join(Slot)
                            .filter(Appointment.patient_id == current_user.id,
                                    Appointment.status == 'booked',
                                    Slot.date == slot.date,
                                    Slot.time == slot.time)
                            .first())

        if existing_booking:
            flash(f"You already have a booking on {slot.date} in the {slot.time}!", "warning")
            return redirect(url_for('patient.check_availability', doctor_id=doctor_id))

        if slot.appointments:
            last_appt = slot.appointments[-1]
            if last_appt.status == 'booked':
                flash("Someone just booked this slot!", "danger")
                return redirect(url_for('patient.check_availability', doctor_id=doctor_id))
        
        
        # New Appointment
        new_appointment = Appointment(
            patient_id=current_user.id,
            doctor_id=doctor_id,
            slot_id=slot.id,
            status='booked'
        )
        
        db.session.add(new_appointment)
        db.session.commit()
        
        flash("Appointment booked successfully!", "success")
        return redirect(url_for('patient.patient_dashboard'))

    today = date.today()
    dates = [today + timedelta(days=i) for i in range(7)]

    # existing slots
    slots = Slot.query.filter(
        Slot.doctor_id == doctor_id, 
        Slot.date >= today,
        Slot.date <= dates[-1]
    ).all()

    # slot map
    slot_map = {}

    for s in slots:
        status = 'NotAvailable'
        if s.appointments:
            apt = s.appointments[-1] 
            if apt.patient_id == current_user.id:
                if apt.status == 'cancelled':
                    status = 'CANCELLED'
                elif apt.status == 'completed':
                    status = 'COMPLETED'
                elif apt.status == 'booked':
                    status = 'BOOKED'
            else:
                if apt.status == 'cancelled':
                    status = 'OPEN'
                else:
                    status = 'NotAvailable' 
        else:
            status = 'OPEN'
        
        slot_map[(s.date, s.time)] = {'status': status, 'id': s.id}
            
    return render_template('patient/doctor_availability.html', 
                           doctor=doctor, 
                           dates=dates, 
                           slot_map=slot_map)


# PATIENT HISTORY
@patient_bp.route('/history/<int:id>')
@login_required
def history(id):
    if current_user.role != 'admin' and current_user.id != id:
        abort(403)

    patient = User.query.get_or_404(id)

    appointments = (Appointment.query
                    .join(Slot)
                    .filter(Appointment.patient_id == patient.id,
                            Appointment.status == 'completed')
                    .order_by(Slot.date.desc(), Slot.time.desc())
                    .all())
    
    return render_template('patient/history.html', appointments=appointments, patient=patient)


# PATIENT : EDIT PROFILE
@patient_bp.route('/edit_profile/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_profile(id):
    if current_user.role != 'admin' and current_user.id != id:
        abort(403)

    patient = User.query.get_or_404(id)

    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        new_password = request.form.get('new_password') 

        # Checking if email id already exists
        existing_user = User.query.filter_by(email=email).first()
        if existing_user and existing_user.id != patient.id:
            flash("Email already in use by another account!", "warning")
            return redirect(url_for('patient.edit_profile', id=patient.id))

        # Updating 
        patient.name = name
        patient.email = email
        patient.phone = phone

        if new_password and new_password.strip():
            patient.set_password(new_password)

        db.session.commit()
        flash("Profile updated successfully!", "success")
        if current_user.role == 'admin':
            return redirect(url_for('admin.admin_dashboard'))
        elif current_user.role == 'patient':
            return redirect(url_for('patient.patient_dashboard'))

    return render_template('patient/edit_profile.html', patient=patient)
