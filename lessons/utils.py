from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django import models
from .models import QuizAttempt, LearnerProgress
import logging

logger = logging.getLogger('lessons')

def send_progress_notification(user, quiz_attempt):
    """Send email notification for quiz completion"""
    if not hasattr(settings, 'EMAIL_HOST_USER'):
        return
    
    subject = f"Quiz Completed: {quiz_attempt.quiz.title}"
    
    context = {
        'user': user,
        'attempt': quiz_attempt,
        'passed': quiz_attempt.passed,
    }
    
    message = render_to_string('emails/quiz_completion.html', context)
    
    try:
        send_mail(
            subject,
            message,
            settings.EMAIL_HOST_USER,
            [user.email],
            html_message=message,
            fail_silently=False,
        )
        logger.info(f"Progress notification sent to {user.email}")
    except Exception as e:
        logger.error(f"Failed to send notification: {str(e)}")

def generate_progress_summary(user):
    """Generate a comprehensive progress summary for a user"""
    progress_records = LearnerProgress.objects.filter(user=user)
    quiz_attempts = QuizAttempt.objects.filter(user=user)
    
    summary = {
        'total_lessons': progress_records.count(),
        'completed_lessons': progress_records.filter(status='completed').count(),
        'in_progress_lessons': progress_records.filter(status='in_progress').count(),
        'total_attempts': quiz_attempts.count(),
        'passed_attempts': quiz_attempts.filter(passed=True).count(),
        'average_score': quiz_attempts.aggregate(
            avg_score=models.Avg('percentage')
        )['avg_score'] or 0,
        'best_score': quiz_attempts.aggregate(
            max_score=models.Max('percentage')
        )['max_score'] or 0,
        'recent_attempts': quiz_attempts.order_by('-completed_at')[:5],
    }
    
    return summary

def export_progress_to_csv(queryset):
    """Export progress data to CSV format"""
    import csv
    from django.http import HttpResponse
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="learner_progress.csv"'
    
    writer = csv.writer(response)
    writer.writerow([
        'Username', 'Full Name', 'Email', 'Lesson', 'Status',
        'Best Score', 'Attempts', 'Started', 'Completed'
    ])
    
    for progress in queryset.select_related('user', 'lesson'):
        writer.writerow([
            progress.user.username,
            progress.user.get_full_name(),
            progress.user.email,
            progress.lesson.title,
            progress.get_status_display(),
            f"{progress.best_quiz_score:.1f}%" if progress.best_quiz_score else "N/A",
            progress.attempts_count,
            progress.started_at.strftime('%Y-%m-%d') if progress.started_at else "N/A",
            progress.completed_at.strftime('%Y-%m-%d') if progress.completed_at else "N/A",
        ])
    
    return response