import json
from django.views.decorators.http import require_POST
from django.db.models.signals import post_save
from django.contrib.auth import get_user_model
from django.dispatch import receiver
from django.utils.timezone import localtime
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from django.http import JsonResponse
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q, Avg, Count
from django.utils import timezone
from .forms import StudentProfileForm
from .models import (
    Course, Lesson, StudentProfile, Assessment, 
    AssessmentAttempt, StudentProgress, CourseProgress
)
from django.core.paginator import Paginator
from django.core.serializers.json import DjangoJSONEncoder


User = get_user_model()
# Dashboard Views
@login_required
def dashboard(request):
    """Main dashboard view for students"""
    student_profile, created = StudentProfile.objects.get_or_create(user=request.user)
    
    # Get student's course progress
    course_progress = CourseProgress.objects.filter(student=student_profile)
    recent_attempts = AssessmentAttempt.objects.filter(user=request.user)[:5]
    
    context = {
        'student_profile': student_profile,
        'course_progress': course_progress,
        'recent_attempts': recent_attempts,
    }
    return render(request, 'accounts/index.html', context)

# Course Views
class CourseListView(ListView):
    model = Course
    template_name = 'lessons/lessons.html'
    context_object_name = 'courses'
    paginate_by = 12

    def get_queryset(self):
        queryset = Course.objects.all()
        search_query = self.request.GET.get('search')
        if search_query:
            queryset = queryset.filter(
                Q(name__icontains=search_query) | 
                Q(description__icontains=search_query)
            )
        return queryset.order_by('-created_at')

class CourseDetailView(DetailView):
    model = Course
    context_object_name = 'course'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'

    def get_template_names(self):
        # Example: for 'literacy' slug, looks for 'learning/literacy.html'
        slug = self.kwargs.get(self.slug_url_kwarg)
        return [f'learning/{slug}.html']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        course = self.get_object()
        
        if self.request.user.is_authenticated:
            student_profile, created = StudentProfile.objects.get_or_create(user=self.request.user)
            try:
                course_progress = CourseProgress.objects.get(student=student_profile, course=course)
                context['course_progress'] = course_progress
            except CourseProgress.DoesNotExist:
                context['course_progress'] = None
                
        context['lessons'] = course.lessons.all().order_by('created_at')
        context['assessments'] = course.assessments.all()
        return context

# Lesson Views
class LessonDetailView(LoginRequiredMixin, DetailView):
    model = Lesson
    template_name = 'learning/lesson_detail.html'
    context_object_name = 'lesson'

    def get_object(self):
        course_slug = self.kwargs.get('course_slug')
        lesson_slug = self.kwargs.get('lesson_slug')
        return get_object_or_404(
            Lesson, 
            course__slug=course_slug, 
            slug=lesson_slug
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        lesson = self.get_object()
        student_profile, created = StudentProfile.objects.get_or_create(user=self.request.user)
        
        # Get or create student progress for this lesson
        progress, created = StudentProgress.objects.get_or_create(
            student=student_profile,
            lesson=lesson,
            defaults={'started_at': timezone.now()}
        )
        
        context['progress'] = progress
        context['assessments'] = lesson.assessments.all()
        return context

@login_required
@require_POST
def start_lesson(request, course_slug, lesson_slug):
    """Start or continue a lesson"""
    if request.method == 'POST':
        lesson = get_object_or_404(Lesson, course__slug=course_slug, slug=lesson_slug)
        student_profile, _ = StudentProfile.objects.get_or_create(user=request.user)

        progress, created = StudentProgress.objects.get_or_create(
            student=student_profile,
            lesson=lesson,
            defaults={
                'started_at': timezone.now(),
                'status': 'in_progress',
                'last_accessed': timezone.now()
            }
        )

        if not created:
            if progress.status == 'not_started':
                progress.status = 'in_progress'
                progress.started_at = timezone.now()
            progress.last_accessed = timezone.now()
            progress.save()

        # AJAX request
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
          print(f"Started lesson: {lesson.slug} for {student_profile.user.username}")
          return JsonResponse({'success': True})


    # Fallback: regular page redirect
    return redirect('learning:lesson_detail', course_slug=course_slug, lesson_slug=lesson_slug)

@login_required
def complete_lesson(request, course_slug, lesson_slug):
    """Mark a lesson as completed"""
    if request.method != 'POST':
        return JsonResponse({'error': 'POST method required'}, status=405)
    
    lesson = get_object_or_404(
        Lesson, 
        course__slug=course_slug, 
        slug=lesson_slug
    )
    student_profile, created = StudentProfile.objects.get_or_create(user=request.user)
    
    progress, created = StudentProgress.objects.get_or_create(
        student=student_profile,
        lesson=lesson
    )
    
    progress.status = 'completed'
    progress.completed_at = timezone.now()
    progress.score = lesson.max_score  # You might want to modify this logic
    progress.save()
    
    # Update course progress
    course_progress, created = CourseProgress.objects.get_or_create(
        student=student_profile,
        course=lesson.course
    )
    course_progress.update_progress()
    
    messages.success(request, f'Lesson "{lesson.name}" completed successfully!')
    return JsonResponse({'success': True, 'message': 'Lesson completed!'})

# Assessment Views
class AssessmentDetailView(LoginRequiredMixin, DetailView):
    model = Assessment
    template_name = 'learning/assessment_detail.html'
    context_object_name = 'assessment'

    def get_object(self):
        course_slug = self.kwargs.get('course_slug')
        assessment_id = self.kwargs.get('assessment_id')
        return get_object_or_404(
            Assessment, 
            course__slug=course_slug, 
            id=assessment_id
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        assessment = self.get_object()
        
        # Get user's previous attempts
        attempts = AssessmentAttempt.objects.filter(
            user=self.request.user,
            assessment=assessment
        ).order_by('-completed_at')
        
        context['attempts'] = attempts
        context['best_attempt'] = attempts.filter(passed=True).first() or attempts.first()
        return context

@login_required
def take_assessment(request, course_slug, assessment_id):
    """Take an assessment"""
    assessment = get_object_or_404(
        Assessment, 
        course__slug=course_slug, 
        id=assessment_id
    )
    
    if request.method == 'POST':
        # Process assessment submission
        score = int(request.POST.get('score', 0))
        answers = request.POST.get('answers', '{}')
        time_taken = request.POST.get('time_taken')
        
        # Create assessment attempt
        attempt = AssessmentAttempt.objects.create(
            user=request.user,
            assessment=assessment,
            score=score,
            answers=answers,
        )
        
        # Update course progress
        student_profile, created = StudentProfile.objects.get_or_create(user=request.user)
        course_progress, created = CourseProgress.objects.get_or_create(
            student=student_profile,
            course=assessment.course
        )
        course_progress.update_progress()
        
        if attempt.passed:
            messages.success(request, f'Congratulations! You passed with {attempt.percentage:.1f}%')
        else:
            messages.warning(request, f'You scored {attempt.percentage:.1f}%. Keep practicing!')
        
        return redirect('learning:assessment_result', course_slug=course_slug, attempt_id=attempt.id)
    
    return render(request, 'learning/take_assessment.html', {'assessment': assessment})

@csrf_exempt
def submit_quiz_score(request, course_slug, lesson_slug, assessment_id):
    if request.method == 'POST':
        data = json.loads(request.body)
        score = int(data.get('score'))

        assessment = get_object_or_404(Assessment, id=assessment_id, course__slug=course_slug)
        user = request.user

        passed = False
        if assessment.total_questions > 0:
            percentage = (score / assessment.total_questions) * 100
            passed = percentage >= assessment.passing_score

        attempt = AssessmentAttempt.objects.create(
            user=user,
            assessment=assessment,
            score=score,
            passed=passed
        )
        if assessment.lesson:
            profile, _ = StudentProfile.objects.get_or_create(user=user)
            progress, _ = StudentProgress.objects.get_or_create(
                student=profile,
                lesson=assessment.lesson,
                defaults={
                    'status': 'in_progress',
                    'started_at': timezone.now()
                }
            )
            progress.score = score
            progress.status = 'completed'
            progress.completed_at = timezone.now()
            progress.save()

        return JsonResponse({'success': True, 'attempt_id': attempt.id})
    
    return JsonResponse({'success': False, 'error': 'Invalid request'})


@login_required
def assessment_result(request, course_slug, attempt_id):
    """Show assessment results"""
    attempt = get_object_or_404(
        AssessmentAttempt,
        id=attempt_id,
        user=request.user,
        assessment__course__slug=course_slug
    )
    
    context = {
        'attempt': attempt,
        'assessment': attempt.assessment,
        'course': attempt.assessment.course,
    }
    return render(request, 'learning/assessment_result.html', context)

@receiver(post_save, sender=AssessmentAttempt)
def update_student_progress(sender, instance, created, **kwargs):
    if not created or not instance.assessment.lesson:
        return

    profile, _ = StudentProfile.objects.get_or_create(user=instance.user)
    progress, _ = StudentProgress.objects.get_or_create(
        student=profile,
        lesson=instance.assessment.lesson,
        defaults={
            'status': 'in_progress',
            'started_at': timezone.now()
        }
    )

    progress.score = instance.score
    progress.status = 'completed'
    progress.completed_at = timezone.now()
    progress.save()

@login_required
def student_progress_json(request):
    student_profile = request.user.studentprofile
    print("Student profile:", student_profile)

    progress_qs = StudentProgress.objects.filter(student=student_profile).select_related('lesson')
    print("Progress count:", progress_qs.count())
    
    progress_list = []
    for p in progress_qs:
        progress_list.append({
            'lesson_title': p.lesson.name,
            'status': p.status,
            'score': p.score,
            'attempts': p.attempts,
            'time_spent': str(p.time_spent) if p.time_spent else None,
            'started_at': localtime(p.started_at).strftime('%Y-%m-%d %H:%M') if p.started_at else None,
            'completed_at': localtime(p.completed_at).strftime('%Y-%m-%d %H:%M') if p.completed_at else None,
            'last_accessed': localtime(p.last_accessed).strftime('%Y-%m-%d %H:%M') if p.last_accessed else None,
        })
    
    return JsonResponse({'progress': progress_list})


@login_required
def student_progress(request):
    """Show student's overall progress"""
    student_profile, created = StudentProfile.objects.get_or_create(user=request.user)
    
    course_progress = CourseProgress.objects.filter(student=student_profile)
    lesson_progress = StudentProgress.objects.filter(student=student_profile)
    recent_lessons = lesson_progress.order_by('-updated_at')[:5]  # assuming 'updated_at' exists
    recent_assessments = AssessmentAttempt.objects.filter(user=request.user).order_by('-completed_at')[:5]

    # Dummy badges for now
    badges = []  # or Badge.objects.filter(user=request.user)

    # Summary dictionary to match template
    progress_summary = {
        'completed_lessons': lesson_progress.filter(status='completed').count(),
        'in_progress_lessons': lesson_progress.filter(status='in_progress').count(),
        'total_assessments': recent_assessments.count(),
        'completion_rate': (lesson_progress.filter(status='completed').count() / lesson_progress.count() * 100) if lesson_progress.exists() else 0,
    }

    course_progress_data = []
    for cp in course_progress:
        course_progress_data.append({
            'lesson_name': cp.lesson.name,
            'subject': cp.lesson.subject.name,
            'status': cp.get_status_display(),
            'score': cp.score,
            'attempts': cp.attempts,
            'completion_percentage': cp.completion_percentage,
            'time_spent': str(cp.time_spent) if cp.time_spent else "N/A",
            'started_at': cp.started_at.strftime('%Y-%m-%d %H:%M') if cp.started_at else "N/A",
            'completed_at': cp.completed_at.strftime('%Y-%m-%d %H:%M') if cp.completed_at else "N/A",
        })

    return JsonResponse({
        'user': {
            'username': request.user.full_name,
            'email': request.user.email,
        },
        'progress_summary': progress_summary,
        'course_progress': course_progress_data,
        'badges': [],  # Replace with real badge data if available
    }, encoder=DjangoJSONEncoder)


@login_required
def course_progress_detail(request, course_slug):
    """Detailed progress for a specific course"""
    course = get_object_or_404(Course, slug=course_slug)
    student_profile, created = StudentProfile.objects.get_or_create(user=request.user)
    
    course_progress, created = CourseProgress.objects.get_or_create(
        student=student_profile,
        course=course
    )
    
    lesson_progress = StudentProgress.objects.filter(
        student=student_profile,
        lesson__course=course
    )
    
    assessment_attempts = AssessmentAttempt.objects.filter(
        user=request.user,
        assessment__course=course
    )
    
    context = {
        'course': course,
        'course_progress': course_progress,
        'lesson_progress': lesson_progress,
        'assessment_attempts': assessment_attempts,
    }
    return render(request, 'accounts/progress.html', context)

@login_required
def edit_profile(request):
    profile = request.user.studentprofile
    if request.method == 'POST':
        form = StudentProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('settings')  # or wherever you want to go
    else:
        form = StudentProfileForm(instance=profile)
    
    return render(request, 'edit_profile.html', {'form': form})