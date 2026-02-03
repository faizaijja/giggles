from django.shortcuts import render, redirect
from django.contrib.auth import logout
from django.contrib import messages
from django.template.loader import get_template
from django.http import HttpResponse
from weasyprint import HTML
from io import BytesIO
from django.http import HttpResponse
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from django.utils.timezone import localtime
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_protect

from learning.models import StudentProfile, StudentProgress
from .models import CustomUser



@csrf_protect
def signup_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        full_name = request.POST.get('full_name')
        user_type = request.POST.get('user_type')

        if not all([email, password, full_name, user_type]):
            messages.error(request, 'All fields are required.')
            return render(request, 'accounts/signup.html')

        if len(password) < 6:
            messages.error(request, 'Password must be at least 6 characters long.')
            return render(request, 'accounts/signup.html')

        if CustomUser.objects.filter(email=email).exists():
            messages.error(request, 'An account with this email already exists.')
            return render(request, 'accounts/signup.html')

        try:
            user = CustomUser.objects.create_user(
                email=email,
                password=password,
                full_name=full_name,
                user_type=user_type
            )
            login(request, user)
            messages.success(request, 'Account created successfully!')
            return redirect('index')  # Changed from 'login' to 'index'

        except Exception as e:
            messages.error(request, f'Error: {str(e)}')
            return render(request, 'accounts/signup.html')

    return render(request, 'accounts/signup.html')


@csrf_protect
def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('username')  
        password = request.POST.get('password')

        user = authenticate(request, email=email, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, 'Login successful!')
            return redirect('index') 
        else:
            messages.error(request, 'Invalid email or password.')

    return render(request, 'accounts/login_page.html')


def landing_view(request):
    print("Landing view called!")  
    print("Rendering giggles.html") 
    return render(request, 'accounts/giggles.html')


@login_required(login_url = 'login')  # Added login protection
def index_view(request):
   
    return render(request, 'accounts/index.html')

def socials_view(request):
    return render(request, 'accounts/socials.html')


def progress_view(request):
    user = request.user

    try:
        student_profile = user.studentprofile
    except StudentProfile.DoesNotExist:
        return render(request, 'accounts/progress.html', {
            'user': user,
            'error': "No student profile found."
        })

    progress_qs = StudentProgress.objects.filter(student=student_profile).select_related('lesson')

    return render(request, 'accounts/progress.html', {
        'user': user,
        'progress_list': progress_qs,
    })

@login_required
def download_progress_pdf(request):
    user = request.user
    progress_qs = user.studentprofile.studentprogress_set.select_related('lesson')

    context = {
        'user': user,
        'progress_list': progress_qs,
    }

    html_string = get_template('accounts/progress_pdf.html').render(context)
    pdf_file = HTML(string=html_string, base_url=request.build_absolute_uri()).write_pdf()

    response = HttpResponse(pdf_file, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{user.username}_progress_report.pdf"'
    return response


def settings_view(request):
    return render(request, 'accounts/settings.html')

def custom_logout(request):
    logout(request)
    return redirect('landing')