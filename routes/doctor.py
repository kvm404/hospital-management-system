from datetime import date, timedelta, datetime
from sqlalchemy.exc import IntegrityError
from flask import Blueprint, render_template, request, url_for, redirect, flash, abort
from flask_login import login_required, current_user
from models import db, User, Doctor, Slot, Appointment, Treatment

doctor_bp = Blueprint('doctor', __name__)

# DOCTOR DASHBOARD
@doctor_bp.route('/doctor_dashboard')
@login_required
def doctor_dashboard():
    appointments = (
        Appointment.query
        .join(Slot) 
        .filter(Appointment.doctor_id == current_user.id,
                Appointment.status == "booked",
                Slot.date >= date.today())
        .order_by(Slot.date.asc(), Slot.time.desc())
        .all())
    
    treatments = (
        Treatment.query
        .join(Appointment) 
        .filter(Appointment.doctor_id == current_user.id,
                Appointment.status == "completed")
        .order_by(Treatment.created_at.desc())
        .all())
    return render_template('doctor/doctor_dash.html', appointments=appointments, treatments=treatments)


# MARK APPOINTMENT
@doctor_bp.route('/mark_appointment/<int:id>', methods=['POST'])
@login_required
def mark_appointment(id):
    ap = Appointment.query.get_or_404(id)
    if (ap.doctor_id != current_user.id):
        abort(403)
    ap.status = 'completed'
    db.session.commit()
    return redirect(request.referrer)


# PATIENT HISTORY
@doctor_bp.route('/patient_history/<int:id>')
@login_required
def patient_history(id):
    patient = User.query.get_or_404(id)
    treatments = (
        Treatment.query
        .join(Appointment) 
        .filter(Appointment.doctor_id == current_user.id,
                Appointment.patient_id == id,
                Appointment.status == "completed")
        .order_by(Treatment.created_at.desc())
        .all())
    return render_template('doctor/patient_history.html', treatments=treatments, patient=patient)


# ADD TREATMENT DETAILS
@doctor_bp.route('/add_treatment_details/<int:id>', methods=['GET', 'POST'])
@login_required
def add_treatment_details(id):
    appointment = Appointment.query.get_or_404(id)

    if appointment.doctor_id != current_user.id:
        abort(403)

    if appointment.slot.date != date.today():
        flash('You cannot add Treatment details of future appointments!', 'danger')
        return redirect(url_for('doctor.doctor_dashboard'))

    if request.method == 'POST':
        visit_type = request.form.get('visit')
        tests = request.form.get('test')
        diagnosis = request.form.get('diagnosis')
        medicines = request.form.get('medicines')
        prescription = request.form.get('prescription')

        # New Treatment
        treatment = Treatment(
            appointment_id=appointment.id,
            visit_type=visit_type,
            tests_done=tests,
            diagnosis=diagnosis,
            medicines=medicines,
            prescription=prescription
        )

        db.session.add(treatment)
        db.session.commit()
        
        flash('Treatment details added successfully!', 'success')
        return redirect(url_for('doctor.doctor_dashboard'))

    return render_template('doctor/treatment_form.html', appointment=appointment)


# UPDATE AVAILABILITY (doctor/admin)
@doctor_bp.route('/update_availability/<int:user_id>', methods=['GET', 'POST'])
@login_required
def update_availability(user_id):
    doctor = Doctor.query.get_or_404(user_id)

    # Authorization Check
    if current_user.role not in ['admin', 'doctor']:
        abort(403)
    if current_user.role == 'doctor' and current_user.id != user_id:
        abort(403)

    if request.method == 'POST':
        date_str = request.form.get('date') 
        time_slot = request.form.get('time') 
        
        slot_date = datetime.strptime(date_str, '%Y-%m-%d').date()

        # Validation
        if slot_date < date.today():
            flash("You cannot add availability for past dates!", "warning")
            return redirect(url_for('doctor.update_availability', user_id=user_id))
        
        if slot_date >= (date.today() + timedelta(days=7)):
            flash("You can only add availability for upcoming 7 days!", "warning")
            return redirect(url_for('doctor.update_availability', user_id=user_id))

        try:
            new_slot = Slot(doctor_id=user_id, date=slot_date, time=time_slot)
            db.session.add(new_slot)
            db.session.commit()
            flash("Slot added successfully!", "success")
        except IntegrityError:
            db.session.rollback()
            flash("You have already added this slot!", "danger")
        
        return redirect(url_for('doctor.update_availability', user_id=user_id))

    # Existing slots
    slots = Slot.query.filter(
        Slot.doctor_id == user_id, 
        Slot.date >= date.today()
    ).order_by(Slot.date).all()
    
    return render_template('doctor/update_availability.html', slots=slots, today=date.today(), doctor=doctor)


# DELETE SLOT
@doctor_bp.route('/delete_slot/<int:id>', methods=['POST'])
@login_required
def delete_slot(id):
    slot = Slot.query.get_or_404(id)

    if current_user.role != 'admin' and current_user.id != slot.doctor_id:
        abort(403)

    if slot.appointments and slot.appointments[-1].status != 'cancelled':
        flash("Cannot delete this slot because it is booked!", "danger")
    else:
        db.session.delete(slot)
        db.session.commit()
        flash("Slot removed successfully", "success")

    return redirect(url_for('doctor.update_availability', user_id=slot.doctor_id))
