from django import forms

from .models import StudentRegistration

MIN_AGE = 16
MAX_AGE = 100
# exercise 2: the course is chosen from a list instead of typed freely
COURSE_CHOICES = [
    ("", "Select a course"),
    ("BCA", "BCA"),
    ("BTech CSE", "BTech CSE"),
    ("MCA", "MCA"),
    ("BBA", "BBA"),
]


class StudentRegistrationForm(forms.ModelForm):
    course = forms.ChoiceField(choices=COURSE_CHOICES)
    # exercise 3: a confirmation checkbox that is not stored in the database
    agree_to_rules = forms.BooleanField(
        label="I agree to the college rules",
        error_messages={"required": "You must agree to the rules to register."},
    )

    class Meta:
        model = StudentRegistration
        fields = ["name", "email", "age", "phone", "course"]
        widgets = {
            "name": forms.TextInput(attrs={"placeholder": "Enter your full name"}),
            "email": forms.EmailInput(attrs={"placeholder": "student@example.com"}),
            "age": forms.NumberInput(attrs={"min": MIN_AGE, "max": MAX_AGE}),
            "phone": forms.TextInput(attrs={"placeholder": "10 digits (optional)"}),
        }

    # Server-side rules. The min/max attributes above are only a convenience for the browser
    # and can be bypassed, so the real checks are here.
    def clean_age(self):
        age = self.cleaned_data["age"]
        if age < MIN_AGE:
            raise forms.ValidationError(f"The student must be at least {MIN_AGE} years old.")
        if age > MAX_AGE:
            raise forms.ValidationError(f"Age must not be more than {MAX_AGE}.")
        return age

    def clean_name(self):
        name = " ".join(self.cleaned_data["name"].split())          # trim and collapse spaces
        if len(name) < 2:
            raise forms.ValidationError("Please enter your full name.")
        return name

    def clean_email(self):
        return self.cleaned_data["email"].strip().lower()           # so A@x.com and a@x.com are one student

    def clean_phone(self):
        phone = self.cleaned_data["phone"].strip()
        if phone and not (phone.isdigit() and len(phone) == 10):
            raise forms.ValidationError("Phone number must be exactly 10 digits.")
        return phone
