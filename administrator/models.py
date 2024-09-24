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
    description = models.TextField()  # Detailed description of the drug
    ADR_History = models.TextField(blank=True, null=True)  # Comprehensive adverse drug reactions history
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


# Model to represent questions associated with drugs
class DrugQuestion(models.Model):
    drug = models.ForeignKey(Drug, on_delete=models.CASCADE)  # Drug associated with the question
    question_text = models.CharField(max_length=255)  # The question about the drug

    def __str__(self):
        return f'Question for {self.drug.name}'


# Model to represent options for drug questions (side effects)
class DrugQuestionOption(models.Model):
    question = models.ForeignKey(DrugQuestion, on_delete=models.CASCADE)  # Question associated with the option
    option_text = models.CharField(max_length=100)  # Text of the option (side effect)

    def __str__(self):
        return f'Option for {self.question.question_text}'


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
            {"name": "Fever", "description": "A temporary increase in body temperature, typically above 100.4°F (38°C)."},
            {"name": "Cough", "description": "A sudden, forceful expulsion of air from the lungs, often caused by infections."},
            {"name": "Headache", "description": "Pain or discomfort in the head, scalp, or neck."},
            {"name": "Fatigue", "description": "A state of persistent tiredness or lack of energy."},
            {"name": "Nausea", "description": "An uncomfortable sensation in the stomach that may lead to vomiting."},
            {"name": "Vomiting", "description": "The forceful expulsion of stomach contents through the mouth."},
            {"name": "Dizziness", "description": "A sensation of lightheadedness or unsteadiness."},
            {"name": "Shortness of Breath", "description": "A feeling of not being able to breathe well or difficulty breathing."},
            {"name": "Chest Pain", "description": "Discomfort or pain in the chest area."},
            {"name": "Sore Throat", "description": "Pain, scratchiness, or irritation in the throat."},
            {"name": "Diarrhea", "description": "Frequent loose or watery bowel movements."},
            {"name": "Abdominal Pain", "description": "Pain located in the stomach area."},
        ]
        symptom_instances = [Symptom(name=symptom["name"], description=symptom["description"]) for symptom in symptoms_data]
        Symptom.objects.bulk_create(symptom_instances)  # Bulk create symptom instances


# Function to load sample diagnoses
def load_diagnoses():
    if not Diagnosis.objects.exists():  # Check if diagnoses already exist
        diagnoses_data = [
            {
                "name": "Flu",
                "description": "A common viral infection characterized by fever, cough, body aches, and fatigue.",
                "symptoms": ["Fever", "Cough", "Fatigue", "Headache"]
            },
            {
                "name": "Common Cold",
                "description": "A viral infection of the upper respiratory tract, causing sneezing, sore throat, and fatigue.",
                "symptoms": ["Cough", "Sore Throat", "Fatigue", "Headache"]
            },
            {
                "name": "Migraine",
                "description": "A type of headache characterized by intense, debilitating pain, often accompanied by nausea and sensitivity to light.",
                "symptoms": ["Headache", "Nausea", "Dizziness"]
            },
            {
                "name": "Gastroenteritis",
                "description": "Inflammation of the stomach and intestines, often leading to diarrhea and vomiting.",
                "symptoms": ["Diarrhea", "Vomiting", "Abdominal Pain"]
            },
            {
                "name": "Pneumonia",
                "description": "An infection that inflames the air sacs in one or both lungs, causing cough, fever, and difficulty breathing.",
                "symptoms": ["Cough", "Fever", "Shortness of Breath", "Chest Pain"]
            }
        ]
        for diagnosis_data in diagnoses_data:
            diagnosis = Diagnosis.objects.create(
                name=diagnosis_data["name"],
                description=diagnosis_data["description"]
            )
            for symptom_name in diagnosis_data["symptoms"]:
                symptom = Symptom.objects.filter(name=symptom_name).first()
                if symptom:
                    diagnosis.symptoms.add(symptom)


# Function to load sample drugs, their questions, and options
def load_drugs():
    if not Drug.objects.exists():  # Check if drugs already exist
        drugs_data = [
            {
                "name": "Paracetamol",
                "description": "An analgesic and antipyretic medication.",
                "ADR_History": "Common adverse effects include nausea.",
                "symptoms": ["Fever", "Headache"],
                "side_effects": [
                    "Nausea", "Dizziness", "Skin Rash", "None of the Above"
                ]
            },
            {
                "name": "Ibuprofen",
                "description": "A nonsteroidal anti-inflammatory drug (NSAID) used for pain relief, fever reduction, and inflammation.",
                "ADR_History": "Common adverse effects include stomach upset and dizziness.",
                "symptoms": ["Fever", "Pain", "Inflammation"],
                "side_effects": [
                    "Stomach Upset", "Dizziness", "Headache", "None of the Above"
                ]
            },
            {
                "name": "Amoxicillin",
                "description": "An antibiotic used to treat bacterial infections.",
                "ADR_History": "Common adverse effects include diarrhea and nausea.",
                "symptoms": ["Fever", "Fatigue"],
                "side_effects": [
                    "Diarrhea", "Nausea", "Rash", "None of the Above"
                ]
            },
            {
                "name": "Lisinopril",
                "description": "An ACE inhibitor used to treat high blood pressure and heart failure.",
                "ADR_History": "Common adverse effects include cough and dizziness.",
                "symptoms": ["High Blood Pressure", "Chest Pain"],
                "side_effects": [
                    "Cough", "Dizziness", "Fatigue", "None of the Above"
                ]
            },
            {
                "name": "Cetirizine",
                "description": "An antihistamine used to relieve allergy symptoms.",
                "ADR_History": "Common adverse effects include drowsiness and dry mouth.",
                "symptoms": ["Itching", "Sneezing"],
                "side_effects": [
                    "Drowsiness", "Dry Mouth", "Nausea", "None of the Above"
                ]
            }
        ]

        for drug_data in drugs_data:
            drug = Drug.objects.create(
                name=drug_data["name"],
                description=drug_data["description"],
                ADR_History=drug_data["ADR_History"]
            )
            for symptom_name in drug_data["symptoms"]:
                symptom = Symptom.objects.filter(name=symptom_name).first()
                if symptom:
                    drug.symptoms.add(symptom)

            question = DrugQuestion.objects.create(drug=drug, question_text=f"Have you experienced any of the following side effects from {drug.name}?")
            for side_effect in drug_data["side_effects"]:
                DrugQuestionOption.objects.create(question=question, option_text=side_effect)

