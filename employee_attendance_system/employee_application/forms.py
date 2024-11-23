from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Employee

class EmployeeCreationForm(UserCreationForm):
    first_name = forms.CharField(required=True, label="First Name", max_length=45)
    last_name = forms.CharField(required=True, label="Last Name", max_length=45)
    contact_number = forms.CharField(required=True, label="Contact Number", max_length=12)
    email = forms.EmailField(required=True, label="Email Address")
    street_address_1 = forms.CharField(required=True, label="Address Line 1", max_length=120)
    street_address_2 = forms.CharField(required=False, label="Address Line 2", max_length=120)
    city = forms.CharField(required=True, label="City", max_length=50)
    state = forms.CharField(required=True, label="State", max_length=20)
    zip_code = forms.CharField(required=True, label="Postal Code", max_length=10)
    employee_identifier = forms.CharField(required=True, label="Identifier Number", max_length=20)

    class Meta:
        model = Employee
        fields = [
            'first_name', 'last_name', 'contact_number', 'email',
            'street_address_1', 'street_address_2', 'city', 'state',
            'zip_code', 'identification_number', 'password1', 'password2'
        ]

    def save(self, commit=True):
        user = super(EmployeeCreationForm, self).save(commit=False)
        user.phone_number = self.cleaned_data['contact_number']
        user.username = self.cleaned_data['contact_number']  # Set the username as the phone number
        if commit:
            user.save()
        return user



class AdminRegistrationForm(UserCreationForm):
    first_name = forms.CharField(required=True, label="First Name", max_length=45)
    last_name = forms.CharField(required=True, label="Last Name", max_length=45)
    phone_number = forms.CharField(required=True, label="Contact Number", max_length=12)
    email = forms.EmailField(required=True, label="Email Address")

    class Meta:
        model = Employee
        fields = (
        'first_name', 'last_name', 'phone_number', 'email','password1', 'password2')

    def save(self, commit=True):
        admin = super(AdminRegistrationForm, self).save(commit=False)
        admin.contact_number = self.cleaned_data['phone_number']
        admin.username = self.cleaned_data['phone_number']
        if commit:
            admin.save()
        return admin



class AdminUpdateForm(forms.ModelForm):

    class Meta:
        model = Employee
        fields = ['first_name', 'last_name', 'contact_number', 'email']
    def __init__(self, *args, **kwargs):
        super(AdminUpdateForm, self).__init__(*args, **kwargs)
        # If work_experience_info is optional at the model level, this is not necessary

class EmployeeAddressUpdateForm(forms.ModelForm):

    class Meta:
        model = Employee
        fields = ['first_name', 'last_name', 'contact_number', 'email','street_address_1', 'street_address_2', 'city', 'state', 'zip_code','identification_number']
        labels = {
            'street_address_1': 'Address Line 1',
            'street_address_2': 'Address Line 2',
            # Other labels as before
        }

    def __init__(self, *args, **kwargs):
        super(EmployeeAddressUpdateForm, self).__init__(*args, **kwargs)
        # If work_experience_info is optional at the model level, this is not necessary


