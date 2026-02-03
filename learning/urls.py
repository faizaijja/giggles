from django.urls import path
from . import views
from django.http import JsonResponse
from django.core.serializers.json import DjangoJSONEncoder

app_name = 'learning'

urlpatterns = [
    # Dashboard
    path('', views.dashboard, name='lessons'),
    # urls.py
    path('edit-profile/', views.edit_profile, name='edit_profile'),

    
    # Course URLs
    path('courses/<slug:slug>/', views.CourseDetailView.as_view(), name='course_detail'),
    
    # Lesson URLs
    path('courses/<slug:course_slug>/lessons/<slug:lesson_slug>/', 
         views.LessonDetailView.as_view(), name='lesson_detail'),
    path('courses/<slug:course_slug>/lessons/<slug:lesson_slug>/start/', 
         views.start_lesson, name='start_lesson'),
    path('courses/<slug:course_slug>/lessons/<slug:lesson_slug>/complete/', 
         views.complete_lesson, name='complete_lesson'),
    
    # Assessment URLs
    path('courses/<slug:course_slug>/assessments/<int:assessment_id>/', 
         views.AssessmentDetailView.as_view(), name='assessment_detail'),
    path('courses/<slug:course_slug>/assessments/<int:assessment_id>/take/', 
         views.take_assessment, name='take_assessment'),
    path('courses/<slug:course_slug>/assessment-results/<int:attempt_id>/', 
         views.assessment_result, name='assessment_result'),
    
   # Progress URLs
     path('accounts/progress/', views.student_progress, name='progress'),
     path('progress/courses/<slug:course_slug>/', views.course_progress_detail, name='course_progress_detail'),
    
     path(
    'courses/<slug:course_slug>/lessons/<slug:lesson_slug>/assessments/<int:assessment_id>/submit/',
    views.submit_quiz_score,
    name='submit_quiz_score'
),


]

