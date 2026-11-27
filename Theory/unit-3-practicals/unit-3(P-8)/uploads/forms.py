from django import forms

from .models import StudentDocument, StudentPhoto
from .validators import validate_document, validate_pdf_upload, validate_photo


class StudentDocumentForm(forms.ModelForm):
    class Meta:
        model = StudentDocument
        fields = ["student_name", "document"]

    # The HTML `accept` attribute is a convenience only; this server-side check is the real one.
    def clean_document(self):
        return validate_document(self.cleaned_data["document"])


class StudentPhotoForm(forms.ModelForm):
    class Meta:
        model = StudentPhoto
        fields = ["photo"]

    def clean_photo(self):
        return validate_photo(self.cleaned_data["photo"])


class PortalDocumentForm(forms.Form):
    file = forms.FileField(label="PDF assignment", validators=[validate_pdf_upload],
                           widget=forms.ClearableFileInput(attrs={"accept": "application/pdf,.pdf"}))
