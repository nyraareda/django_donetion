from django import forms
from django.contrib.auth.hashers import make_password
from Home.models import User
from django.contrib.auth import authenticate

class UserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password', 'confirm_password', 'phone_number',
                  'profile_picture']

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password and confirm_password:
            if password != confirm_password:
                self.add_error('confirm_password', "Passwords do not match.")
            if len(password) < 5:
                self.add_error('password', "Password must be at least 5 characters long.")
        else:
            self.add_error('password', "Password field is required.")

    def save(self, commit=True):
        user = super().save(commit=False)
        password = self.cleaned_data.get('password')
        if password:
            user.password = make_password(password)  # Hash the password
        if commit:
            user.save()
        return user

    def clean_first_name(self):
        first_name = self.cleaned_data.get('first_name')
        if len(first_name) < 2:
            raise forms.ValidationError("First name must be at least 2 characters long.")
        return first_name
    
    def clean_last_name(self):
        last_name = self.cleaned_data.get('last_name')
        if len(last_name) < 2:
            raise forms.ValidationError("Last name must be at least 2 characters long.")
        return last_name
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        allowed_endings = ['.com', '.gmail', '.edu']
        if not any(email.endswith(ending) for ending in allowed_endings):
            raise forms.ValidationError("Please enter a valid email address.")
        return email
    
    def clean_profile_picture(self):
        profile_picture = self.cleaned_data.get('profile_picture')
    
        if not profile_picture:
            return "users/images/1_.jpg"  # This should be the relative path to the default image
    
        return profile_picture

    def clean_phone_number(self):
        phone_number = self.cleaned_data.get('phone_number')
    
        if phone_number is None:
            raise forms.ValidationError("Phone number is required.")
    
        phone_input = ''.join(filter(str.isdigit, phone_number))
    
        if len(phone_input) >= 10:
            if len(phone_input) == 10:
                phone_number_with_prefix = "+20" + phone_input
            else:
                phone_number_with_prefix = "+" + phone_input
        else:
            raise forms.ValidationError("Invalid phone number format.")
    
        return phone_number_with_prefix



class AdditionalInfoForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['birth_date', 'country', 'facebook_profile']

    birth_date = forms.DateField(
        label='Birth Date',
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )
    country = forms.CharField(
        label='Country',
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    facebook_profile = forms.URLField(
        label='Facebook Profile',
        required=False,
        widget=forms.URLInput(attrs={'class': 'form-control'})
    )


class LoginForm(forms.Form):
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if not email:
           
           self.add_error("Email field is required.")
        
        # Check if user exists with the provided email
        user = User.objects.filter(email=email).first()
        if not user:
            self.add_error("User with this email does not exist.")

        return email

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get("email")
        password = cleaned_data.get("password")

        if email and password:
            # Check if user exists
            user = authenticate(email=email, password=password)
            if user is not None:
                if user.is_activated:
                    self.user = user
                else:
                    self.add_error('email', "This account is not activated.")
            else:
                self.add_error('password', "Incorrect password or email")
        return cleaned_data


class PasswordResetForm(forms.Form):
    email = forms.EmailField(
        required=True,
        error_messages={'required': 'This field is required.'}
    )
    def clean_email(self):
        cleaned_data = super().clean()
        email = self.cleaned_data.get('email')
        if email:
            # Check if user exists
            user = authenticate(email=email)
            if user is not None:
                if user.is_activated:
                    self.user = user
                else:
                    self.add_error('email', "This account is not activated.")
        return cleaned_data

        