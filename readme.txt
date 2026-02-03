# Learning Management System (Django App)

A comprehensive Django application for managing courses, lessons, assessments, and student progress.

## Models

The app includes the following renamed models:

- **Course** (formerly Subject) - Main course/subject entity
- **Lesson** (formerly Activity) - Individual lessons within courses  
- **StudentProfile** (formerly LearnerProfile) - Extended user profiles for students
- **Assessment** (formerly Quiz) - Assessments/quizzes within courses
- **AssessmentAttempt** (formerly QuizAttempt) - Individual assessment attempts
- **StudentProgress** (formerly LearnerProgress) - Progress tracking for lessons
- **CourseProgress** (formerly SubjectProgress) - Overall course progress tracking

## Features

- **Course Management**: Create and organize courses with lessons and assessments
- **Progress Tracking**: Monitor student progress across courses and lessons
- **Assessment System**: Create assessments with automatic grading and pass/fail logic
- **Dashboard**: Student dashboard showing progress, recent attempts, and statistics
- **Admin Interface**: Comprehensive admin interface for managing all entities
- **API Support**: Django REST Framework serializers included
- **Signals**: Automatic profile creation and progress updates
- **Sample Data**: Management command to create sample data for testing

## Installation

1. Add 'learning' to your INSTALLED_APPS in settings.py:

```python
INSTALLED_APPS = [
    # ... other apps
    'learning',
]
```

2. Include the learning URLs in your main urls.py:

```python
from django.urls import path, include

urlpatterns = [
    # ... other patterns
    path('learning/', include('learning.urls')),
]
```

3. Run migrations:

```bash
python manage.py makemigrations learning
python manage.py migrate
```

4. Create sample data (optional):

```