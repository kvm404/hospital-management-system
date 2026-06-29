"""Presentation seed data for the Hospital Management System.

This script resets all HMS tables and loads a richer Indian demo dataset for
presentations. It is intentionally deterministic and uses only fields that the
current Flask/Jinja app renders.

Run:
    python seed_presentation.py
    # or
    python seed.py
"""

from datetime import date, datetime, time, timedelta

from sqlalchemy import func

from app import app
from models import Appointment, Department, Doctor, Slot, Treatment, User, db


ADMIN_PASSWORD = "admin123"
DOCTOR_PASSWORD = "doctor123"
PATIENT_PASSWORD = "patient123"

SHIFTS = ("morning", "evening")


DEPARTMENTS = [
    {
        "key": "general",
        "name": "General Medicine",
        "description": "Primary care for fever, infections, diabetes, hypertension, preventive screening, and long-term adult health.",
    },
    {
        "key": "cardiology",
        "name": "Cardiology",
        "description": "Heart care including ECG review, hypertension control, chest pain evaluation, and post-procedure follow-ups.",
    },
    {
        "key": "neurology",
        "name": "Neurology",
        "description": "Care for migraine, seizures, stroke recovery, neuropathy, dizziness, and other nervous system conditions.",
    },
    {
        "key": "dermatology",
        "name": "Dermatology",
        "description": "Skin, hair, and nail care for acne, eczema, psoriasis, allergies, infections, and cosmetic concerns.",
    },
    {
        "key": "orthopaedics",
        "name": "Orthopaedics",
        "description": "Bone, joint, ligament, sports injury, fracture follow-up, spine, and rehabilitation care.",
    },
    {
        "key": "pediatrics",
        "name": "Pediatrics",
        "description": "Child health, vaccination review, nutrition, fever care, asthma, allergies, and growth monitoring.",
    },
    {
        "key": "gynecology",
        "name": "Obstetrics and Gynecology",
        "description": "Women's health, pregnancy visits, PCOS, menstrual concerns, fertility counselling, and postnatal care.",
    },
    {
        "key": "ent",
        "name": "ENT",
        "description": "Ear, nose, and throat care for sinusitis, hearing concerns, vertigo, tonsillitis, and voice issues.",
    },
    {
        "key": "gastro",
        "name": "Gastroenterology",
        "description": "Digestive care for acidity, IBS, liver health, abdominal pain, ulcers, and endoscopy follow-up.",
    },
    {
        "key": "endocrine",
        "name": "Endocrinology",
        "description": "Hormone and metabolism care for diabetes, thyroid disease, PCOS, obesity, and calcium disorders.",
    },
    {
        "key": "psychiatry",
        "name": "Psychiatry",
        "description": "Confidential mental health care for anxiety, depression, sleep concerns, stress, and medication reviews.",
    },
]


DOCTORS = [
    {
        "key": "asha",
        "name": "Asha Nair",
        "email": "asha.nair@hms.com",
        "phone": "9000010101",
        "department": "general",
        "description": "MBBS, MD Internal Medicine. Handles fever clinics, diabetes, hypertension, thyroid screening, and preventive health plans for adults.",
    },
    {
        "key": "vikram",
        "name": "Vikram Menon",
        "email": "vikram.menon@hms.com",
        "phone": "9000010102",
        "department": "cardiology",
        "description": "MBBS, DM Cardiology. Focuses on hypertension, ECG interpretation, lipid control, chest pain evaluation, and cardiac rehabilitation.",
    },
    {
        "key": "meera",
        "name": "Meera Kulkarni",
        "email": "meera.kulkarni@hms.com",
        "phone": "9000010103",
        "department": "neurology",
        "description": "MBBS, DM Neurology. Treats migraine, vertigo, neuropathy, stroke recovery, seizure disorders, and chronic headache care.",
    },
    {
        "key": "rohan",
        "name": "Rohan Bansal",
        "email": "rohan.bansal@hms.com",
        "phone": "9000010104",
        "department": "dermatology",
        "description": "MBBS, MD Dermatology. Specializes in acne, eczema, psoriasis, urticaria, hair fall, fungal infections, and skin allergy plans.",
    },
    {
        "key": "farah",
        "name": "Farah Khan",
        "email": "farah.khan@hms.com",
        "phone": "9000010105",
        "department": "orthopaedics",
        "description": "MBBS, MS Orthopaedics. Manages sports injuries, back pain, arthritis, fracture follow-up, shoulder pain, and rehabilitation plans.",
    },
    {
        "key": "kavita",
        "name": "Kavita Rao",
        "email": "kavita.rao@hms.com",
        "phone": "9000010106",
        "department": "pediatrics",
        "description": "MBBS, MD Pediatrics. Provides child fever care, vaccination review, asthma plans, growth checks, and nutrition counselling.",
    },
    {
        "key": "nandini",
        "name": "Nandini Iyer",
        "email": "nandini.iyer@hms.com",
        "phone": "9000010107",
        "department": "gynecology",
        "description": "MBBS, MS Obstetrics and Gynecology. Focuses on antenatal care, PCOS, menstrual health, fertility counselling, and postnatal recovery.",
    },
    {
        "key": "arjun",
        "name": "Arjun Sen",
        "email": "arjun.sen@hms.com",
        "phone": "9000010108",
        "department": "ent",
        "description": "MBBS, MS ENT. Treats sinusitis, ear pain, vertigo, tonsillitis, allergic rhinitis, hearing concerns, and voice strain.",
    },
    {
        "key": "siddharth",
        "name": "Siddharth Joshi",
        "email": "siddharth.joshi@hms.com",
        "phone": "9000010109",
        "department": "gastro",
        "description": "MBBS, DM Gastroenterology. Handles acidity, IBS, fatty liver, abdominal pain, ulcer follow-up, and digestive health plans.",
    },
    {
        "key": "neha",
        "name": "Neha Sinha",
        "email": "neha.sinha@hms.com",
        "phone": "9000010110",
        "department": "endocrine",
        "description": "MBBS, DM Endocrinology. Treats diabetes, thyroid disease, obesity, PCOS-related metabolic issues, and vitamin D deficiency.",
    },
    {
        "key": "riya",
        "name": "Riya Thomas",
        "email": "riya.thomas@hms.com",
        "phone": "9000010111",
        "department": "psychiatry",
        "description": "MBBS, MD Psychiatry. Provides structured care for anxiety, depression, sleep concerns, stress, panic symptoms, and medication reviews.",
    },
]


PATIENTS = [
    {"key": "aarav", "name": "Aarav Patel", "email": "aarav.patel@hms.com", "phone": "9810011101"},
    {"key": "diya", "name": "Diya Gupta", "email": "diya.gupta@hms.com", "phone": "9810011102"},
    {"key": "rohanp", "name": "Rohan Singh", "email": "rohan.singh@hms.com", "phone": "9810011103"},
    {"key": "kavya", "name": "Kavya Nair", "email": "kavya.nair@hms.com", "phone": "9810011104"},
    {"key": "arjunp", "name": "Arjun Reddy", "email": "arjun.reddy@hms.com", "phone": "9810011105"},
    {"key": "meerasha", "name": "Meera Shah", "email": "meera.shah@hms.com", "phone": "9810011106"},
    {"key": "vihaan", "name": "Vihaan Kapoor", "email": "vihaan.kapoor@hms.com", "phone": "9810011107"},
    {"key": "ananya", "name": "Ananya Sharma", "email": "ananya.sharma@hms.com", "phone": "9810011108"},
    {"key": "kabir", "name": "Kabir Malhotra", "email": "kabir.malhotra@hms.com", "phone": "9810011109"},
    {"key": "pooja", "name": "Pooja Menon", "email": "pooja.menon@hms.com", "phone": "9810011110"},
    {"key": "nikhil", "name": "Nikhil Jain", "email": "nikhil.jain@hms.com", "phone": "9810011111", "is_blocked": True},
    {"key": "sana", "name": "Sana Ali", "email": "sana.ali@hms.com", "phone": "9810011112"},
    {"key": "vivek", "name": "Vivek Rao", "email": "vivek.rao@hms.com", "phone": "9810011113"},
    {"key": "tanvi", "name": "Tanvi Desai", "email": "tanvi.desai@hms.com", "phone": "9810011114"},
    {"key": "aditya", "name": "Aditya Banerjee", "email": "aditya.banerjee@hms.com", "phone": "9810011115"},
    {"key": "priyanka", "name": "Priyanka Chawla", "email": "priyanka.chawla@hms.com", "phone": "9810011116"},
    {"key": "myra", "name": "Myra Thomas", "email": "myra.thomas@hms.com", "phone": "9810011117"},
    {"key": "harshita", "name": "Harshita Agarwal", "email": "harshita.agarwal@hms.com", "phone": "9810011118"},
]


COMPLETED_CASES = [
    {
        "patient": "aarav",
        "doctor": "asha",
        "days_ago": 52,
        "shift": "morning",
        "visit_type": "Follow-up",
        "tests_done": "CBC, platelet count, liver function test",
        "diagnosis": "Post dengue recovery with improving platelet count",
        "prescription": "Hydration, repeat CBC only if fever returns, avoid strenuous exercise for one week.",
        "medicines": "Paracetamol 500 mg SOS, oral rehydration salts, vitamin C",
    },
    {
        "patient": "aarav",
        "doctor": "vikram",
        "days_ago": 49,
        "shift": "evening",
        "visit_type": "Consultation",
        "tests_done": "ECG, lipid profile, blood pressure log review",
        "diagnosis": "Stage 1 hypertension with borderline LDL cholesterol",
        "prescription": "Low salt diet, 30 minutes walking daily, home BP log for 2 weeks.",
        "medicines": "Telmisartan 20 mg once daily",
    },
    {
        "patient": "aarav",
        "doctor": "rohan",
        "days_ago": 43,
        "shift": "morning",
        "visit_type": "First Visit",
        "tests_done": "Skin examination, allergy trigger review",
        "diagnosis": "Atopic dermatitis flare on forearms",
        "prescription": "Use fragrance-free moisturiser twice daily, avoid harsh soaps, review in 3 weeks.",
        "medicines": "Mometasone cream for 5 days, cetirizine 10 mg at night",
    },
    {
        "patient": "diya",
        "doctor": "nandini",
        "days_ago": 38,
        "shift": "evening",
        "visit_type": "Consultation",
        "tests_done": "Pelvic ultrasound, TSH, fasting insulin",
        "diagnosis": "PCOS with irregular menstrual cycles",
        "prescription": "Cycle tracking, weight training twice weekly, review hormone profile in 8 weeks.",
        "medicines": "Myo-inositol supplement, vitamin D3 weekly",
    },
    {
        "patient": "diya",
        "doctor": "neha",
        "days_ago": 34,
        "shift": "morning",
        "visit_type": "Follow-up",
        "tests_done": "TSH, free T4, anti-TPO antibody",
        "diagnosis": "Subclinical hypothyroidism under observation",
        "prescription": "Repeat thyroid profile after 6 weeks, take tablets on empty stomach if started.",
        "medicines": "No daily medicine started; vitamin D3 60000 IU weekly",
    },
    {
        "patient": "diya",
        "doctor": "rohan",
        "days_ago": 29,
        "shift": "evening",
        "visit_type": "Follow-up",
        "tests_done": "Clinical skin grading",
        "diagnosis": "Moderate inflammatory acne with post-acne marks",
        "prescription": "Use sunscreen daily, avoid picking lesions, review after 4 weeks.",
        "medicines": "Adapalene gel at night, benzoyl peroxide wash, doxycycline 100 mg",
    },
    {
        "patient": "rohanp",
        "doctor": "farah",
        "days_ago": 45,
        "shift": "morning",
        "visit_type": "Injury Review",
        "tests_done": "Ankle X-ray AP/lateral, physical stability test",
        "diagnosis": "Grade I lateral ankle sprain",
        "prescription": "RICE protocol, ankle brace for 10 days, physiotherapy if swelling persists.",
        "medicines": "Aceclofenac 100 mg after food, topical diclofenac gel",
    },
    {
        "patient": "rohanp",
        "doctor": "arjun",
        "days_ago": 31,
        "shift": "evening",
        "visit_type": "Consultation",
        "tests_done": "Nasal endoscopy, allergy history",
        "diagnosis": "Chronic allergic rhinitis with sinus congestion",
        "prescription": "Steam inhalation, saline nasal rinse, avoid dust exposure, review in 2 weeks.",
        "medicines": "Mometasone nasal spray, levocetirizine 5 mg at night",
    },
    {
        "patient": "rohanp",
        "doctor": "siddharth",
        "days_ago": 20,
        "shift": "morning",
        "visit_type": "Follow-up",
        "tests_done": "H. pylori stool antigen, liver function test",
        "diagnosis": "GERD with suspected H. pylori gastritis",
        "prescription": "Avoid late dinners, reduce tea and spicy food, complete eradication course.",
        "medicines": "Pantoprazole 40 mg, amoxicillin, clarithromycin",
    },
    {
        "patient": "kavya",
        "doctor": "meera",
        "days_ago": 44,
        "shift": "evening",
        "visit_type": "Consultation",
        "tests_done": "Neurological exam, MRI brain screening reviewed",
        "diagnosis": "Migraine without aura",
        "prescription": "Sleep schedule, hydration, headache diary, avoid skipped meals.",
        "medicines": "Sumatriptan 50 mg SOS, propranolol 20 mg at night",
    },
    {
        "patient": "kavya",
        "doctor": "asha",
        "days_ago": 25,
        "shift": "morning",
        "visit_type": "Follow-up",
        "tests_done": "CBC, serum ferritin, B12",
        "diagnosis": "Iron deficiency anemia causing fatigue",
        "prescription": "Iron-rich diet, repeat CBC after 6 weeks, avoid tea with meals.",
        "medicines": "Ferrous ascorbate, folic acid, vitamin B12",
    },
    {
        "patient": "kavya",
        "doctor": "vikram",
        "days_ago": 12,
        "shift": "evening",
        "visit_type": "Review",
        "tests_done": "ECG, thyroid profile, electrolyte panel",
        "diagnosis": "Palpitations likely related to stress and caffeine intake",
        "prescription": "Reduce caffeine, breathing exercises, return if fainting or chest pain occurs.",
        "medicines": "No cardiac medicine required",
    },
    {
        "patient": "arjunp",
        "doctor": "neha",
        "days_ago": 40,
        "shift": "morning",
        "visit_type": "Diabetes Review",
        "tests_done": "HbA1c, fasting glucose, urine microalbumin",
        "diagnosis": "Type 2 diabetes mellitus with HbA1c 8.1 percent",
        "prescription": "Carbohydrate control, daily walking, glucose log before breakfast.",
        "medicines": "Metformin 500 mg twice daily, sitagliptin 50 mg once daily",
    },
    {
        "patient": "arjunp",
        "doctor": "asha",
        "days_ago": 18,
        "shift": "evening",
        "visit_type": "Annual Checkup",
        "tests_done": "CBC, renal function, lipid profile, urine routine",
        "diagnosis": "Metabolic syndrome with central obesity",
        "prescription": "Weight loss goal 4 kg in 3 months, dietician referral, continue diabetes care.",
        "medicines": "Continue current diabetes medication",
    },
    {
        "patient": "arjunp",
        "doctor": "farah",
        "days_ago": 9,
        "shift": "morning",
        "visit_type": "Consultation",
        "tests_done": "Shoulder X-ray, range of motion exam",
        "diagnosis": "Right shoulder impingement syndrome",
        "prescription": "Physiotherapy, avoid overhead lifting, posture correction.",
        "medicines": "Etodolac 400 mg after food for 5 days",
    },
    {
        "patient": "meerasha",
        "doctor": "vikram",
        "days_ago": 35,
        "shift": "morning",
        "visit_type": "Chest Pain Evaluation",
        "tests_done": "ECG, troponin I, treadmill test",
        "diagnosis": "Atypical chest pain, cardiac markers negative",
        "prescription": "Continue observation, manage acidity, return urgently if pain changes.",
        "medicines": "Pantoprazole 40 mg for 14 days",
    },
    {
        "patient": "meerasha",
        "doctor": "siddharth",
        "days_ago": 16,
        "shift": "evening",
        "visit_type": "Follow-up",
        "tests_done": "Upper GI endoscopy report reviewed",
        "diagnosis": "Mild erosive gastritis",
        "prescription": "Avoid NSAIDs, reduce coffee, early dinner, complete PPI course.",
        "medicines": "Pantoprazole 40 mg, sucralfate syrup",
    },
    {
        "patient": "vihaan",
        "doctor": "kavita",
        "days_ago": 28,
        "shift": "morning",
        "visit_type": "Pediatric Visit",
        "tests_done": "CBC, throat examination",
        "diagnosis": "Viral fever with throat irritation",
        "prescription": "Fluids, tepid sponging if fever rises, return if breathing difficulty.",
        "medicines": "Paracetamol syrup as per weight, saline gargle",
    },
    {
        "patient": "vihaan",
        "doctor": "kavita",
        "days_ago": 10,
        "shift": "evening",
        "visit_type": "Asthma Review",
        "tests_done": "Peak flow reading, inhaler technique check",
        "diagnosis": "Mild intermittent childhood asthma",
        "prescription": "Use spacer correctly, avoid smoke exposure, action plan explained to parent.",
        "medicines": "Levosalbutamol inhaler SOS, budesonide inhaler for 2 weeks",
    },
    {
        "patient": "ananya",
        "doctor": "arjun",
        "days_ago": 23,
        "shift": "morning",
        "visit_type": "ENT Review",
        "tests_done": "Anterior rhinoscopy, allergy questionnaire",
        "diagnosis": "Seasonal allergic rhinitis",
        "prescription": "Nasal saline rinse, keep windows closed during dust exposure, follow up if wheeze appears.",
        "medicines": "Fluticasone nasal spray, fexofenadine 120 mg",
    },
    {
        "patient": "ananya",
        "doctor": "riya",
        "days_ago": 15,
        "shift": "evening",
        "visit_type": "Counselling Review",
        "tests_done": "GAD-7 screening, sleep diary review",
        "diagnosis": "Generalized anxiety with sleep disturbance",
        "prescription": "Sleep routine, breathing exercises, weekly counselling, reduce late-night screen time.",
        "medicines": "Melatonin 3 mg for short-term sleep support",
    },
    {
        "patient": "kabir",
        "doctor": "vikram",
        "days_ago": 27,
        "shift": "evening",
        "visit_type": "Risk Assessment",
        "tests_done": "Lipid profile, ECG, family history review",
        "diagnosis": "Dyslipidemia with family history of early heart disease",
        "prescription": "Mediterranean-style diet, exercise plan, repeat lipids after 3 months.",
        "medicines": "Rosuvastatin 10 mg at night",
    },
    {
        "patient": "kabir",
        "doctor": "farah",
        "days_ago": 14,
        "shift": "morning",
        "visit_type": "Back Pain Review",
        "tests_done": "Lumbar spine X-ray, straight leg raise test",
        "diagnosis": "Mechanical low back pain without radiculopathy",
        "prescription": "Core strengthening, ergonomic chair setup, avoid prolonged sitting.",
        "medicines": "Thiocolchicoside, topical analgesic gel",
    },
    {
        "patient": "pooja",
        "doctor": "nandini",
        "days_ago": 22,
        "shift": "morning",
        "visit_type": "Antenatal Visit",
        "tests_done": "Obstetric ultrasound, CBC, urine routine",
        "diagnosis": "Normal second trimester antenatal review",
        "prescription": "Fetal movement awareness, iron-rich diet, next scan as scheduled.",
        "medicines": "Iron, folic acid, calcium with vitamin D",
    },
    {
        "patient": "pooja",
        "doctor": "siddharth",
        "days_ago": 8,
        "shift": "evening",
        "visit_type": "Consultation",
        "tests_done": "Stool routine, abdominal ultrasound reviewed",
        "diagnosis": "Irritable bowel syndrome with bloating",
        "prescription": "Low FODMAP trial, meal timing regularity, stress tracking.",
        "medicines": "Probiotic capsule, mebeverine 135 mg before meals",
    },
    {
        "patient": "vivek",
        "doctor": "asha",
        "days_ago": 13,
        "shift": "morning",
        "visit_type": "Hypertension Follow-up",
        "tests_done": "Blood pressure log, renal function, potassium",
        "diagnosis": "Hypertension improving on medication",
        "prescription": "Continue BP log twice weekly, salt restriction, review after 1 month.",
        "medicines": "Amlodipine 5 mg once daily",
    },
    {
        "patient": "tanvi",
        "doctor": "neha",
        "days_ago": 7,
        "shift": "evening",
        "visit_type": "Thyroid Review",
        "tests_done": "TSH, free T3, free T4",
        "diagnosis": "Hashimoto thyroiditis with elevated TSH",
        "prescription": "Take thyroid medicine before breakfast, repeat TSH in 8 weeks.",
        "medicines": "Levothyroxine 50 mcg once daily",
    },
    {
        "patient": "aditya",
        "doctor": "meera",
        "days_ago": 6,
        "shift": "morning",
        "visit_type": "Neurology Review",
        "tests_done": "Neurological exam, vitamin B12, fasting glucose",
        "diagnosis": "Peripheral neuropathy symptoms likely related to B12 deficiency",
        "prescription": "Foot care advice, B12 replacement, review if numbness worsens.",
        "medicines": "Methylcobalamin 1500 mcg, pregabalin 75 mg at night",
    },
    {
        "patient": "priyanka",
        "doctor": "arjun",
        "days_ago": 5,
        "shift": "evening",
        "visit_type": "ENT Consultation",
        "tests_done": "Throat swab, tonsil examination",
        "diagnosis": "Acute tonsillitis",
        "prescription": "Warm saline gargle, hydration, return if fever persists beyond 72 hours.",
        "medicines": "Amoxicillin-clavulanate, paracetamol 500 mg SOS",
    },
    {
        "patient": "myra",
        "doctor": "kavita",
        "days_ago": 4,
        "shift": "morning",
        "visit_type": "Vaccination Visit",
        "tests_done": "Growth chart review, vaccine schedule check",
        "diagnosis": "Routine immunisation visit, growth appropriate for age",
        "prescription": "Observe for fever after vaccine, next vaccination date noted.",
        "medicines": "Paracetamol syrup SOS for post-vaccine fever",
    },
    {
        "patient": "sana",
        "doctor": "riya",
        "days_ago": 3,
        "shift": "evening",
        "visit_type": "Mental Health Review",
        "tests_done": "Panic symptom checklist, sleep and caffeine review",
        "diagnosis": "Panic attacks with work-related stress",
        "prescription": "Grounding exercises, therapy referral, caffeine reduction, follow-up in 2 weeks.",
        "medicines": "Clonazepam 0.25 mg only if severe panic, short-term use",
    },
    {
        "patient": "harshita",
        "doctor": "siddharth",
        "days_ago": 2,
        "shift": "morning",
        "visit_type": "Liver Review",
        "tests_done": "Liver function test, abdominal ultrasound, fasting insulin",
        "diagnosis": "Non-alcoholic fatty liver disease grade I",
        "prescription": "Weight loss target 5 percent, reduce sugary drinks, repeat LFT in 3 months.",
        "medicines": "Vitamin E after physician review, omega-3 supplement",
    },
    {
        "patient": "tanvi",
        "doctor": "nandini",
        "days_ago": 1,
        "shift": "evening",
        "visit_type": "Gynecology Review",
        "tests_done": "Pelvic ultrasound, CBC",
        "diagnosis": "Primary dysmenorrhea with normal ultrasound",
        "prescription": "Heat therapy, exercise, track cycles for 3 months.",
        "medicines": "Mefenamic acid during painful days",
    },
]


BOOKED_APPOINTMENTS = [
    {"patient": "ananya", "doctor": "asha", "days_ahead": 0, "shift": "morning"},
    {"patient": "aarav", "doctor": "vikram", "days_ahead": 0, "shift": "evening"},
    {"patient": "vihaan", "doctor": "kavita", "days_ahead": 0, "shift": "morning"},
    {"patient": "sana", "doctor": "riya", "days_ahead": 0, "shift": "evening"},
    {"patient": "meerasha", "doctor": "siddharth", "days_ahead": 1, "shift": "morning"},
    {"patient": "rohanp", "doctor": "farah", "days_ahead": 1, "shift": "evening"},
    {"patient": "diya", "doctor": "nandini", "days_ahead": 1, "shift": "morning"},
    {"patient": "arjunp", "doctor": "neha", "days_ahead": 2, "shift": "morning"},
    {"patient": "kabir", "doctor": "vikram", "days_ahead": 2, "shift": "evening"},
    {"patient": "pooja", "doctor": "meera", "days_ahead": 2, "shift": "morning"},
    {"patient": "tanvi", "doctor": "rohan", "days_ahead": 3, "shift": "evening"},
    {"patient": "vivek", "doctor": "asha", "days_ahead": 3, "shift": "morning"},
    {"patient": "myra", "doctor": "kavita", "days_ahead": 4, "shift": "evening"},
    {"patient": "aditya", "doctor": "arjun", "days_ahead": 4, "shift": "morning"},
    {"patient": "priyanka", "doctor": "siddharth", "days_ahead": 5, "shift": "evening"},
    {"patient": "harshita", "doctor": "nandini", "days_ahead": 6, "shift": "morning"},
]


CANCELLED_APPOINTMENTS = [
    {"patient": "nikhil", "doctor": "asha", "days_ahead": 2, "shift": "evening"},
    {"patient": "rohanp", "doctor": "vikram", "days_ahead": 4, "shift": "morning"},
    {"patient": "diya", "doctor": "rohan", "days_ahead": 5, "shift": "morning"},
    {"patient": "kabir", "doctor": "arjun", "days_ahead": 6, "shift": "evening"},
    {"patient": "sana", "doctor": "riya", "days_ahead": 3, "shift": "morning"},
]


def at(day, hour=10, minute=0):
    return datetime.combine(day, time(hour=hour, minute=minute))


def create_user(name, email, phone, role, password, is_blocked=False):
    user = User(
        name=name,
        email=email,
        phone=phone,
        role=role,
        is_blocked=is_blocked,
    )
    user.set_password(password)
    db.session.add(user)
    db.session.flush()
    return user


def create_slot(doctor, slot_date, shift, created_at=None):
    slot = Slot(
        doctor_id=doctor.user_id,
        date=slot_date,
        time=shift,
        created_at=created_at or at(slot_date, 7),
    )
    db.session.add(slot)
    db.session.flush()
    return slot


def add_appointment(patient, doctor, slot, status, created_at):
    appointment = Appointment(
        patient_id=patient.id,
        doctor_id=doctor.user_id,
        slot_id=slot.id,
        status=status,
        created_at=created_at,
    )
    db.session.add(appointment)
    db.session.flush()
    return appointment


def seed():
    today = date.today()

    with app.app_context():
        print("Resetting HMS database...")
        db.drop_all()
        db.create_all()

        print("Creating admin account...")
        create_user(
            name="Mr. Admin",
            email="admin@hms.com",
            phone="9800000000",
            role="admin",
            password=ADMIN_PASSWORD,
        )

        print("Creating departments...")
        departments = {}
        for data in DEPARTMENTS:
            department = Department(name=data["name"], description=data["description"])
            db.session.add(department)
            db.session.flush()
            departments[data["key"]] = department

        print("Creating doctors...")
        doctors = {}
        for data in DOCTORS:
            user = create_user(
                name=data["name"],
                email=data["email"],
                phone=data["phone"],
                role="doctor",
                password=DOCTOR_PASSWORD,
            )
            doctor = Doctor(
                user_id=user.id,
                dept_id=departments[data["department"]].id,
                description=data["description"],
            )
            db.session.add(doctor)
            db.session.flush()
            doctors[data["key"]] = doctor

        print("Creating patients...")
        patients = {}
        for data in PATIENTS:
            patients[data["key"]] = create_user(
                name=data["name"],
                email=data["email"],
                phone=data["phone"],
                role="patient",
                password=PATIENT_PASSWORD,
                is_blocked=data.get("is_blocked", False),
            )

        print("Creating the next 7 days of doctor availability...")
        future_slots = {}
        for doctor_key, doctor in doctors.items():
            for offset in range(7):
                slot_date = today + timedelta(days=offset)
                for shift in SHIFTS:
                    future_slots[(doctor_key, slot_date, shift)] = create_slot(
                        doctor=doctor,
                        slot_date=slot_date,
                        shift=shift,
                        created_at=at(today - timedelta(days=3), 9),
                    )

        print("Creating completed appointment history...")
        for case in COMPLETED_CASES:
            visit_date = today - timedelta(days=case["days_ago"])
            doctor = doctors[case["doctor"]]
            patient = patients[case["patient"]]
            slot = create_slot(
                doctor=doctor,
                slot_date=visit_date,
                shift=case["shift"],
                created_at=at(visit_date - timedelta(days=7), 9),
            )
            appointment = add_appointment(
                patient=patient,
                doctor=doctor,
                slot=slot,
                status="completed",
                created_at=at(visit_date - timedelta(days=4), 11),
            )
            db.session.add(
                Treatment(
                    appointment_id=appointment.id,
                    visit_type=case["visit_type"],
                    tests_done=case["tests_done"],
                    diagnosis=case["diagnosis"],
                    prescription=case["prescription"],
                    medicines=case["medicines"],
                    created_at=at(visit_date, 12 if case["shift"] == "morning" else 18),
                )
            )

        print("Creating upcoming booked appointments...")
        for case in BOOKED_APPOINTMENTS:
            visit_date = today + timedelta(days=case["days_ahead"])
            doctor = doctors[case["doctor"]]
            patient = patients[case["patient"]]
            slot = future_slots[(case["doctor"], visit_date, case["shift"])]
            add_appointment(
                patient=patient,
                doctor=doctor,
                slot=slot,
                status="booked",
                created_at=at(today - timedelta(days=2), 14),
            )

        print("Creating cancelled appointment examples...")
        for case in CANCELLED_APPOINTMENTS:
            visit_date = today + timedelta(days=case["days_ahead"])
            doctor = doctors[case["doctor"]]
            patient = patients[case["patient"]]
            slot = future_slots[(case["doctor"], visit_date, case["shift"])]
            add_appointment(
                patient=patient,
                doctor=doctor,
                slot=slot,
                status="cancelled",
                created_at=at(today - timedelta(days=1), 16),
            )

        db.session.commit()

        print("\nPresentation seed complete.")
        print(f"Departments: {Department.query.count()}")
        print(f"Doctors: {Doctor.query.count()}")
        print(f"Patients: {User.query.filter_by(role='patient').count()}")
        print(f"Slots: {Slot.query.count()}")
        print(f"Treatments: {Treatment.query.count()}")
        for status, count in (
            db.session.query(Appointment.status, func.count(Appointment.id))
            .group_by(Appointment.status)
            .order_by(Appointment.status)
            .all()
        ):
            print(f"Appointments {status}: {count}")

        print("\nDemo logins:")
        print(f"Admin: admin@hms.com / {ADMIN_PASSWORD}")
        print(f"Doctor: asha.nair@hms.com / {DOCTOR_PASSWORD}")
        print(f"Patient: ananya.sharma@hms.com / {PATIENT_PASSWORD}")


if __name__ == "__main__":
    seed()
