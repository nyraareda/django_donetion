import pytz
from django.core.mail import send_mail
from django.urls import reverse
from datetime import datetime, timedelta
import uuid
from django.shortcuts import render, redirect,get_object_or_404
from django.http import HttpResponse, JsonResponse,HttpResponseRedirect
from django.contrib import messages
from django.urls import reverse
from django.core.mail import send_mail
from .forms import UserForm, AdditionalInfoForm,LoginForm
from Home.models import User
from django.contrib.auth.hashers import make_password
from django.utils import timezone
from django.contrib.auth import authenticate, login,logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import make_password
from django.shortcuts import render
from django.contrib.auth.views import LoginView
from .forms import LoginForm,PasswordResetForm
import logging
from django import forms



class CustomLoginView(LoginView):
    form_class = LoginForm
    template_name = 'registration/login.html'

def verify(request, key):
    user = User.objects.filter(activation_key=key).first()
    if user:
        timestamp = int(key.split('_')[-1])
        activation_time = datetime.fromtimestamp(timestamp).replace(tzinfo=pytz.utc)
        now = datetime.now(pytz.utc)
        if now - activation_time > timedelta(hours=24):
            return render(request, 'accounts/activation_expired.html')
        user.is_activated = True
        user.save()
        return render(request, 'accounts/account_activated.html', {'user': user})
    else:
        return HttpResponse("Invalid activation key.")

def activateEmail(request, user):
    timestamp = int(timezone.now().timestamp())
    activation_key = str(uuid.uuid4()) + '_' + str(timestamp)
    user.activation_key = activation_key
    user.save()
    activation_link = request.build_absolute_uri(reverse('verify', kwargs={'key': activation_key}))
    send_mail(
        'Activate Your Account',
        f'Dear {user.first_name}, please click the following link to activate your account: {activation_link}',
        'sender@example.com',
        [user.email],
        fail_silently=False,
    )
    messages.success(request, f"An activation email has been sent to {user.email}.")

def user_create_form(request):
    if request.method == 'POST':
        form = UserForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save(commit=False)
            user.password = make_password(form.cleaned_data['password'])
            user.confirm_password = make_password(form.cleaned_data['confirm_password'])
            user.is_activated = False
            image = request.FILES.get("profile_picture")
            if image:
                user.profile_picture = image
            else:
                user.profile_picture = "users/images/1_.jpg"
            user.save()
            activateEmail(request, user)
            return render(request, 'accounts/activation_email_sent.html', {'email': user.email})
    else:
        form = UserForm()
    return render(request, 'accounts/register.html', {'form': form})

logger = logging.getLogger(__name__)

def add_additional_info(request):
    if request.method == 'POST':
        form = AdditionalInfoForm(request.POST)
        if form.is_valid():
            user_id = request.POST.get('user_id')
            if user_id:
                user = get_object_or_404(User, pk=user_id)
                user.birth_date = form.cleaned_data['birth_date']
                user.country = form.cleaned_data['country']
                user.facebook_profile = form.cleaned_data['facebook_profile']
                user.save()
                return redirect('profile', user_id=user.id)
            else:
                return HttpResponse("User ID is missing.")
    else:
        form = AdditionalInfoForm()
    return render(request, 'accounts/additional_info_form.html', {'form': form})

def delete_account(request):
    if request.method == 'POST':
        try:
            user_id = request.POST.get('user_id')
            user = User.objects.get(pk=user_id)
            user.delete()
            return render(request, 'accounts/register.html')
        except User.DoesNotExist:
            return HttpResponse("User does not exist.")
    return HttpResponse("Invalid request.")



def edit_profile(request, user_id):
    user = get_object_or_404(User, pk=user_id)
    if request.method == 'POST':
        form = UserForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            profile_picture = request.FILES.get('profile_picture')
            if profile_picture:
                user.profile_picture = profile_picture
            form.save()
            messages.success(request, "Profile updated successfully.")
    else:
        form = UserForm(instance=user)
    
    return render(request, 'accounts/edit.html', {'form': form, 'user': user})


def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            user = form.user
            user.is_active = True
            user.save() 

            if user.is_activated:
                login(request, user)
                if user.is_superuser :  # Check if the user is staff
                    return redirect('admin_view', user_id=user.id)
                else:
                    return redirect('home_profile', user_id=user.id)
            else:
                return render(request, 'accounts/not_activated.html', {'email': user.email})
    else:
        form = LoginForm()
    
    # If the form is invalid, render the login page with the form containing the errors
    return render(request, 'registration/login.html', {'form': form})

def custom_logout(request, user_id):
    user = get_object_or_404(User, pk=user_id)
    user.is_active= False
    user.save()
    return redirect('login')


def profile(request, user_id):
    if request.user.is_authenticated:
        return redirect('profile', user_id=request.user.id)

    user = get_object_or_404(User, pk=user_id)

    if user.is_active:
        if user.is_activated:
            form = AdditionalInfoForm(instance=user)
            return render(request, 'accounts/profile.html', {'form': form, 'user': user})
        else:
            return render(request, 'accounts/not_activated.html')
    else:
        return redirect('login')


def generate_reset_token(user):
    timestamp = int(timezone.now().timestamp())
    reset_token = str(uuid.uuid4()) + '_' + str(timestamp)
    user.reset_token = reset_token
    user.save()
    return reset_token

class CustomPasswordResetForm(PasswordResetForm):
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email:
            # Check if user exists
            user = User.objects.filter(email=email).first()
            if user:
                if user.is_active:
                    self.user = user
                else:
                    raise forms.ValidationError("This account is not activated.")
            else:
                raise forms.ValidationError("User with this email does not exist.")
        return email

def request_password_reset(request):
    if request.method == 'POST':
        form = CustomPasswordResetForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('email')
            user = form.user
            reset_token = generate_reset_token(user)
            reset_link = request.build_absolute_uri(reverse('password_reset_confirm', kwargs={'token': reset_token}))
            send_mail(
                'Password Reset',
                f'Click the following link to reset your password: {reset_link}',
                'sender@example.com',
                [user.email],
                fail_silently=False,
            )
            messages.success(request, "Password reset link sent to your email.")
            return render(request, 'reset_pass_sent.html', {'email': user.email})
    else:
        form = CustomPasswordResetForm()
    
    return render(request, 'registration/password_reset_request.html', {'form': form})

def password_reset_confirm(request, token):
    user = User.objects.filter(reset_token=token).first()
    if user:
        timestamp = int(token.split('_')[-1])
        reset_time = datetime.fromtimestamp(timestamp).replace(tzinfo=pytz.utc)
        now = datetime.now(pytz.utc)
        if now - reset_time > timedelta(hours=24):
            messages.error(request, "Password reset link has expired.")
            return redirect('login')
        else:
            if request.method == 'POST':
                new_password = request.POST.get('new_password')
                confirm_password = request.POST.get('confirm_password')
                if new_password == confirm_password:
                    user.set_password(new_password)
                    user.reset_token = None
                    user.save()
                    messages.success(request, "Password reset successfully. You can now login with your new password.")
                    return redirect('login')
                else:
                    messages.error(request, "Passwords do not match.")
                    return render(request, 'registration/password_reset_confirm.html', {'token': token})
    else:
        messages.error(request, "Invalid or expired reset link.")
    return render(request, 'registration/password_reset_confirm.html', {'token': token})

def reset_pass_sent(request):
    # You can customize this function to include any additional logic if needed
    # For now, let's simply render the template with the provided email context
    email = request.GET.get('email')  # Assuming the email is passed as a query parameter
    return render(request, 'accounts/reset_pass_sent.html', {'email': email})