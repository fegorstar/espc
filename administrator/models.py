from accounts.models import User
from django.db import models
from django.db.models.signals import post_migrate
from django.dispatch import receiver

# Model to represent symptoms
class Symptom(models.Model):
    name = models.CharField(max_length=100)  # Name of the symptom
    description = models.TextField()  # Description of the symptom
    created_at = models.DateTimeField(auto_now_add=True)  # Timestamp for when the symptom was created
    updated_at = models.DateTimeField(auto_now=True)  # Timestamp for the last update of the symptom

    def __str__(self):
        return self.name  # String representation of the symptom

# Model to represent diagnoses
class Diagnosis(models.Model):
    name = models.CharField(max_length=100)  # Name of the diagnosis
    description = models.TextField()  # Description of the diagnosis
    symptoms = models.ManyToManyField(Symptom, related_name='diagnoses')  # Symptoms associated with the diagnosis
    created_at = models.DateTimeField(auto_now_add=True)  # Timestamp for when the diagnosis was created
    updated_at = models.DateTimeField(auto_now=True)  # Timestamp for the last update of the diagnosis

    def __str__(self):
        return self.name  # String representation of the diagnosis
    
    class Meta:
        verbose_name = "Diagnosis"
        verbose_name_plural = "Diagnoses"

# Model to represent drugs
class Drug(models.Model):
    name = models.CharField(max_length=255)  # Name of the drug
    description = models.TextField()  # Description of the drug
    ADR_History = models.TextField(blank=True, null=True)  # Adverse drug reactions history
    symptoms = models.ManyToManyField(Symptom, related_name='drugs', blank=True)  # Symptoms treated by the drug
    created_at = models.DateTimeField(auto_now_add=True)  # Timestamp for when the drug was created
    updated_at = models.DateTimeField(auto_now=True)  # Timestamp for the last update of the drug

    def __str__(self):
        return self.name  # String representation of the drug

# Model to represent patient reports
class PatientReport(models.Model):
    patient = models.ForeignKey(User, on_delete=models.CASCADE)  # Patient associated with the report
    age = models.PositiveIntegerField()  # Age of the patient
    sex = models.CharField(max_length=10)  # Gender of the patient (e.g., 'Male', 'Female', 'Other')
    symptoms = models.ManyToManyField(Symptom)  # Symptoms reported by the patient
    diagnosis = models.ForeignKey(Diagnosis, on_delete=models.SET_NULL, null=True)  # Diagnosis made for the patient
    drugs_recommended = models.ManyToManyField(Drug, blank=True)  # Drugs recommended for the patient
    created_at = models.DateTimeField(auto_now_add=True)  # Timestamp for when the report was created
    updated_at = models.DateTimeField(auto_now=True)  # Timestamp for the last update of the report

    def __str__(self):
        return f'Report by {self.patient.email} - Age: {self.age}, Sex: {self.sex}'  # String representation of the patient report

# Signal to load sample data after migrations
@receiver(post_migrate)
def load_sample_data(sender, **kwargs):
    if sender.name == 'administrator':  # Replace with your app name
        load_symptoms()  # Load sample symptoms
        load_diagnoses()  # Load sample diagnoses
        load_drugs()  # Load sample drugs

# Function to load sample symptoms
def load_symptoms():
    if not Symptom.objects.exists():  # Check if symptoms already exist
        symptoms_data = [
            {"name": "Fever", "description": "Increased body temperature."},
            {"name": "Cough", "description": "Persistent dry cough."},
            {"name": "Headache", "description": "Pain in the head or upper neck."},
            {"name": "Fatigue", "description": "Feeling overly tired with low energy."},
            {"name": "Nausea", "description": "A sensation of unease in the stomach."},
            {"name": "Vomiting", "description": "Forcibly emptying the stomach."},
            {"name": "Dizziness", "description": "A sensation of spinning."},
            {"name": "Shortness of Breath", "description": "Difficulty breathing."},
            {"name": "Chest Pain", "description": "Pain in the chest."},
            {"name": "Sore Throat", "description": "Pain or irritation in the throat."},
            {"name": "Diarrhea", "description": "Frequent loose or watery stools."},
            {"name": "Abdominal Pain", "description": "Pain in the stomach area."},
        ]
        symptom_instances = [Symptom(name=symptom["name"], description=symptom["description"]) for symptom in symptoms_data]
        Symptom.objects.bulk_create(symptom_instances)  # Bulk create symptom instances

# Function to load sample diagnoses
def load_diagnoses():
    if not Diagnosis.objects.exists():  # Check if diagnoses already exist
        diagnoses_data = [
            {
                "name": "Flu",
                "description": "A common viral infection.",
                "symptoms": ["Fever", "Cough", "Fatigue", "Headache"]
            },
            {
                "name": "Common Cold",
                "description": "A viral infection of the upper respiratory tract.",
                "symptoms": ["Cough", "Sore Throat", "Fatigue", "Headache"]
            },
            {
                "name": "Gastroenteritis",
                "description": "Inflammation of the stomach and intestines.",
                "symptoms": ["Nausea", "Vomiting", "Diarrhea", "Abdominal Pain"]
            },
            {
                "name": "Pneumonia",
                "description": "Infection that inflames the air sacs in one or both lungs.",
                "symptoms": ["Cough", "Chest Pain", "Shortness of Breath", "Fever"]
            },
            {
                "name": "Allergic Reaction",
                "description": "An immune response to allergens.",
                "symptoms": ["Nausea", "Dizziness", "Fatigue"]
            },
        ]
        
        for diagnosis in diagnoses_data:
            diag = Diagnosis.objects.create(name=diagnosis["name"], description=diagnosis["description"])
            # Link the specific symptoms to the diagnosis
            for symptom_name in diagnosis["symptoms"]:
                symptom = Symptom.objects.filter(name=symptom_name).first()
                if symptom:
                    diag.symptoms.add(symptom)  # Add symptom to diagnosis

# Function to load sample drugs
def load_drugs():
    if not Drug.objects.exists():  # Check if drugs already exist
        drugs_data = [
            {
                "name": "Paracetamol",
                "description": "Pain reliever and a fever reducer.",
                "ADR_History": "Nausea, Rash",
                "symptoms": ["Fever", "Headache"]
            },
            {
                "name": "Ibuprofen",
                "description": "Nonsteroidal anti-inflammatory drug.",
                "ADR_History": "Stomach upset, Dizziness",
                "symptoms": ["Pain", "Fever"]
            },
            {
                "name": "Aspirin",
                "description": "Used to reduce pain, fever, or inflammation.",
                "ADR_History": "Gastrointestinal bleeding, Allergic reactions",
                "symptoms": ["Pain", "Fever"]
            },
            {
                "name": "Amoxicillin",
                "description": "Antibiotic used to treat bacterial infections.",
                "ADR_History": "Diarrhea, Allergic reactions",
                "symptoms": ["Cough", "Chest Pain"]
            },
            {
                "name": "Cough Syrup",
                "description": "Used to relieve cough.",
                "ADR_History": "Drowsiness, Dizziness",
                "symptoms": ["Cough"]
            },
            {
                "name": "Dextromethorphan",
                "description": "Cough suppressant.",
                "ADR_History": "Dizziness, Drowsiness",
                "symptoms": ["Cough", "Shortness of Breath"]
            },
            {
                "name": "Diphenhydramine",
                "description": "Antihistamine used to relieve symptoms of allergy.",
                "ADR_History": "Drowsiness, Dry mouth",
                "symptoms": ["Nausea", "Dizziness"]
            },
            {
                "name": "Loratadine",
                "description": "Antihistamine that relieves allergy symptoms.",
                "ADR_History": "Headache, Fatigue",
                "symptoms": ["Nausea"]
            },
            {
                "name": "Guaifenesin",
                "description": "Expectorant used to relieve chest congestion.",
                "ADR_History": "Nausea, Vomiting",
                "symptoms": ["Cough", "Chest Pain"]
            },
            {
                "name": "Omeprazole",
                "description": "Proton pump inhibitor used to treat acid reflux.",
                "ADR_History": "Nausea, Headache",
                "symptoms": ["Nausea"]
            },
        ]

        for drug_data in drugs_data:
            drug = Drug.objects.create(
                name=drug_data["name"],
                description=drug_data["description"],
                ADR_History=drug_data["ADR_History"]
            )
            # Link symptoms to the drug
            for symptom_name in drug_data["symptoms"]:
                symptom = Symptom.objects.filter(name=symptom_name).first()
                if symptom:
                    drug.symptoms.add(symptom)  # Add symptom to drug

# Note: The dataset for patient symptoms and diagnoses can be found at the following sources:
# - Global Health Data Exchange (GHDx): https://ghdx.healthdata.org/
# - Global Burden of Disease Study 2019 (GBD 2019): https://ghdx.healthdata.org/gbd-2019
# - Disease Symptoms and Patient Profile Dataset on Kaggle: https://www.kaggle.com/datasets/uom190346a/disease-symptoms-and-patient-profile-dataset