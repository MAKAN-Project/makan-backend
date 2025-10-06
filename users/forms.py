from django import forms

# Reserve Consulting Session Form
class ReserveConsultingSessionForm(forms.Form):
	session_date = forms.DateTimeField(label="Date & Time", widget=forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}))
	engineer_type = forms.ChoiceField(label="Engineer Type", choices=[], widget=forms.Select(attrs={'class': 'form-select'}))
	engineer_id = forms.ChoiceField(label="Select Engineer", choices=[], widget=forms.Select(attrs={'class': 'form-select'}))

# Upload Room Photo Form
class UploadRoomPhotoForm(forms.Form):
	room_photo = forms.ImageField(label="Room Photo", widget=forms.ClearableFileInput(attrs={'class': 'form-control'}))
	furniture_style = forms.CharField(label="Furniture Style", max_length=100, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Modern, Classic'}))

# Create Building Project Form
class CreateBuildingProjectForm(forms.Form):
	project_name = forms.CharField(label="Project Name", max_length=200, widget=forms.TextInput(attrs={'class': 'form-control'}))
	project_details = forms.CharField(label="Project Details", widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3}))
