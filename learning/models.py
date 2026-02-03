from django.db import models
from django.contrib.auth import get_user_model
User = get_user_model()
from django.utils import timezone
import json
from django.db.models import UniqueConstraint

class Course(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class Lesson(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='lessons')
    name = models.CharField(max_length=100)
    slug = models.SlugField()  # e.g., 'drawing', 'sculpture', 'textile'
    max_score = models.IntegerField(default=100)
    difficulty_level = models.IntegerField(default=1)  # 1-5 scale
    created_at = models.DateTimeField(auto_now_add=True) # "drawing-activity"
    
    class Meta:
        unique_together = ['course', 'slug']  
    
    def __str__(self):
       return "{}/{}".format(self.course.slug, self.name)

class StudentProfile(models.Model):
    """Extended user profile for learners"""
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    age = models.IntegerField(null=True, blank=True)
    grade_level = models.CharField(max_length=20, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
      if self.user:
         return "{}'s Profile".format(self.user.email)  # or self.user.full_name
      return "Profile (No User)"


class Assessment(models.Model):
    """Model to represent quizzes within lessons"""
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='assessments')
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='assessments', null=True, blank=True)  # Add this
    title = models.CharField(max_length=200)
    total_questions = models.IntegerField()
    passing_score = models.IntegerField(default=70)  # Percentage
    
    def __str__(self):
      return self.title 


class AssessmentAttempt(models.Model):
    """Model to track individual quiz attempts"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    assessment = models.ForeignKey(Assessment, on_delete=models.CASCADE)
    score = models.IntegerField()  # Number of correct answers
    percentage = models.FloatField()  # Percentage score
    time_taken = models.DurationField(null=True, blank=True)
    answers = models.JSONField(default=dict)  # Store user's answers
    completed_at = models.DateTimeField(auto_now_add=True)
    passed = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-completed_at']
    
    def save(self, *args, **kwargs):
        # Calculate percentage and pass status
        self.percentage = (self.score / self.assessment.total_questions) * 100
        self.passed = self.percentage >= self.assessment.passing_score
        super().save(*args, **kwargs)
    
    def __str__(self):
      return "{} - {} - {}/{}".format(
        self.user.email,
        self.assessment.title,
        self.score,
        self.assessment.total_questions
    )


class StudentProgress(models.Model):
    # Fixed: Use consistent field names
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE)
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE)  # Changed from lesson to activity
    status = models.CharField(max_length=20, choices=[
        ('not_started', 'Not Started'),
        ('in_progress', 'In Progress'), 
        ('completed', 'Completed')
    ], default='not_started')
    score = models.IntegerField(default=0)
    attempts = models.IntegerField(default=0)  # Added this field since it's used in views
    time_spent = models.DurationField(null=True, blank=True)  # Added this field
    started_at = models.DateTimeField(null=True, blank=True)  # Changed from auto_now_add
    completed_at = models.DateTimeField(null=True, blank=True)
    last_accessed = models.DateTimeField(null=True, blank=True)  # Added this field

    class Meta:
        constraints = [
            UniqueConstraint(fields=['student', 'lesson'], name='unique_student_lesson')
        ]

    @property
    def completion_percentage(self):
        if self.lesson.max_score > 0:
            return min(100, (self.score / self.lesson.max_score) * 100)
        return 0

    def __str__(self):
        user_email = getattr(self.student.user, 'email', 'Unknown Email')
        lesson_name = getattr(self.lesson, 'name', 'Unknown Lesson')
        return "{} - {} - {}".format(user_email, lesson_name, self.status)



class CourseProgress(models.Model):
    """Overall progress tracking for a subject"""
    STATUS_CHOICES = [
        ('not_started', 'Not Started'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('mastered', 'Mastered'),
    ]
    
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    total_lessons_completed = models.IntegerField(default=0)
    total_score = models.IntegerField(default=0)
    average_score = models.FloatField(default=0.0)
    level = models.IntegerField(default=1)  # Achievement level
    badges_earned = models.JSONField(default=list)  # Store earned badges
    last_lesson_date = models.DateTimeField(null=True, blank=True)
    
    # Additional fields if you need them
    best_assessment_score = models.FloatField(default=0.0)
    attempts_count = models.IntegerField(default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='not_started')
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        unique_together = ['student', 'course']
    
    def update_progress(self):
        """Update progress based on completed activities and quiz attempts"""
        # Update activity-based progress
        lessons = StudentProgress.objects.filter(
            student=self.student,
            lesson__course=self.course,
            status='completed'
        )
        
        self.total_lessons_completed = lessons.count()
        self.total_score = sum(lesson.score for lesson in lessons)
        if self.total_lessons_completed > 0:
            self.average_score = self.total_score / self.total_lessons_completed
        else:
            self.average_score = 0.0
        
        # Update quiz-based progress
        assessment_attempts = AssessmentAttempt.objects.filter(
            user=self.student.user,
            assessment__course=self.course
        )
        
        if assessment_attempts.exists():
            self.best_assessment_score = assessment_attempts.aggregate(
                models.Max('percentage')
            )['percentage__max'] or 0.0
            self.attempts_count = assessment_attempts.count()
            
            # Check if any attempt passed
            if assessment_attempts.filter(passed=True).exists():
                self.status = 'completed'
                if not self.completed_at:
                    self.completed_at = timezone.now()
            else:
                self.status = 'in_progress'
                
            if not self.started_at:
                self.started_at = assessment_attempts.order_by('completed_at').first().completed_at
        
        # Update level based on progress
        if self.average_score >= 90:
            self.level = 3
        elif self.average_score >= 70:
            self.level = 2
        else:
            self.level = 1
        
        self.save()
    
    def __str__(self):
      return "{} - {} - {}".format(
        self.student.user.email,
        self.course.name,
        self.status
    )
  