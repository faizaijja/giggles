from django import forms
from django.contrib.auth import get_user_model
from .models import StudentProfile, Course, Lesson, Assessment, AssessmentAttempt
from django import forms
from .models import StudentProfile

User = get_user_model()

class StudentProfileForm(forms.ModelForm):
    class Meta:
        model = StudentProfile
        fields = ['user','age', 'grade_level']


class StudentProfileForm(forms.ModelForm):
    class Meta:
        model = StudentProfile
        fields = ['age', 'grade_level']
        widgets = {
            'age': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '5',
                'max': '100'
            }),
            'grade_level': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Grade 9, College Freshman'
            })
        }

class CourseSearchForm(forms.Form):
    search = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search courses...'
        })
    )
    
    difficulty_level = forms.ChoiceField(
        choices=[
            ('', 'All Levels'),
            ('1', 'Beginner'),
            ('2', 'Intermediate'),
            ('3', 'Advanced'),
            ('4', 'Expert'),
            ('5', 'Master')
        ],
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )

class AssessmentForm(forms.Form):
    """Base form for taking assessments - to be extended based on question types"""
    
    def __init__(self, assessment, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.assessment = assessment
        
        # This is a basic implementation - you'll need to customize based on your question types
        for i in range(assessment.total_questions):
            self.fields[f'question_{i}'] = forms.CharField(
                label=f'Question {i+1}',
                widget=forms.TextInput(attrs={'class': 'form-control'}),
                required=True
            )

class AssessmentAttemptForm(forms.ModelForm):
    class Meta:
        model = AssessmentAttempt
        fields = ['answers']
        widgets = {
            'answers': forms.HiddenInput()
        }

class LessonFeedbackForm(forms.Form):
    rating = forms.ChoiceField(
        choices=[
            (1, '1 - Poor'),
            (2, '2 - Fair'),
            (3, '3 - Good'),
            (4, '4 - Very Good'),
            (5, '5 - Excellent')
        ],
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'}),
        required=True
    )
    
    feedback = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 4,
            'placeholder': 'Share your thoughts about this lesson...'
        }),
        required=False
    )
    
    difficulty = forms.ChoiceField(
        choices=[
            ('easy', 'Too Easy'),
            ('just_right', 'Just Right'),
            ('hard', 'Too Hard')
        ],
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'}),
        required=False
    )

class BulkEnrollmentForm(forms.Form):
    """Form for bulk enrolling students in courses"""
    course = forms.ModelChoiceField(
        queryset=Course.objects.all(),
        widget=forms.Select(attrs={'class': 'form-select'}),
        empty_label="Select a course"
    )
    
    students = forms.ModelMultipleChoiceField(
        queryset=User.objects.filter(is_active=True),
        widget=forms.CheckboxSelectMultiple,
        help_text="Select students to enroll in the course"
    )

class ProgressFilterForm(forms.Form):
    """Form for filtering progress views"""
    course = forms.ModelChoiceField(
        queryset=Course.objects.all(),
        required=False,
        empty_label="All Courses",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    status = forms.ChoiceField(
        choices=[
            ('', 'All Statuses'),
            ('not_started', 'Not Started'),
            ('in_progress', 'In Progress'),
            ('completed', 'Completed'),
            ('mastered', 'Mastered')
        ],
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    date_from = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )
    
    date_to = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )