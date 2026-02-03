from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from .models import StudentProfile, StudentProgress, CourseProgress, AssessmentAttempt

User = get_user_model()

@receiver(post_save, sender=User)
def create_student_profile(sender, instance, created, **kwargs):
    """Automatically create a StudentProfile when a new User is created"""
    if created:
        StudentProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_student_profile(sender, instance, **kwargs):
    """Save the StudentProfile when the User is saved"""
    if hasattr(instance, 'studentprofile'):
        instance.studentprofile.save()

@receiver(post_save, sender=StudentProgress)
def update_course_progress_on_lesson_completion(sender, instance, created, **kwargs):
    """Update CourseProgress when a lesson is completed"""
    if instance.status == 'completed':
        course_progress, created = CourseProgress.objects.get_or_create(
            student=instance.student,
            course=instance.lesson.course
        )
        course_progress.update_progress()

@receiver(post_save, sender=AssessmentAttempt)
def update_course_progress_on_assessment(sender, instance, created, **kwargs):
    """Update CourseProgress when an assessment is completed"""
    if created:
        student_profile, created = StudentProfile.objects.get_or_create(
            user=instance.user
        )
        course_progress, created = CourseProgress.objects.get_or_create(
            student=student_profile,
            course=instance.assessment.course
        )
        course_progress.update_progress()

@receiver(post_delete, sender=StudentProgress)
def update_course_progress_on_lesson_deletion(sender, instance, **kwargs):
    """Update CourseProgress when a lesson progress is deleted"""
    try:
        course_progress = CourseProgress.objects.get(
            student=instance.student,
            course=instance.lesson.course
        )
        course_progress.update_progress()
    except CourseProgress.DoesNotExist:
        pass