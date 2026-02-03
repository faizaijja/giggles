from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import (
    Course, Lesson, StudentProfile, Assessment,
    AssessmentAttempt, StudentProgress, CourseProgress
)

User = get_user_model()

class CourseSerializer(serializers.ModelSerializer):
    lesson_count = serializers.IntegerField(source='lessons.count', read_only=True)
    assessment_count = serializers.IntegerField(source='assessments.count', read_only=True)
    
    class Meta:
        model = Course
        fields = ['id', 'name', 'slug', 'description', 'created_at', 
                 'lesson_count', 'assessment_count']
        read_only_fields = ['created_at']

class LessonSerializer(serializers.ModelSerializer):
    course_name = serializers.CharField(source='course.name', read_only=True)
    assessment_count = serializers.IntegerField(source='assessments.count', read_only=True)
    
    class Meta:
        model = Lesson
        fields = ['id', 'course', 'course_name', 'name', 'slug', 
                 'max_score', 'difficulty_level', 'created_at', 'assessment_count']
        read_only_fields = ['created_at']

class StudentProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    email = serializers.CharField(source='user.email', read_only=True)
    
    class Meta:
        model = StudentProfile
        fields = ['id', 'user', 'username', 'email', 'age', 'grade_level', 'created_at']
        read_only_fields = ['user', 'created_at']

class AssessmentSerializer(serializers.ModelSerializer):
    course_name = serializers.CharField(source='course.name', read_only=True)
    lesson_name = serializers.CharField(source='lesson.name', read_only=True)
    attempt_count = serializers.IntegerField(source='assessmentattempt_set.count', read_only=True)
    
    class Meta:
        model = Assessment
        fields = ['id', 'course', 'course_name', 'lesson', 'lesson_name', 
                 'title', 'total_questions', 'passing_score', 'attempt_count']

class AssessmentAttemptSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    assessment_title = serializers.CharField(source='assessment.title', read_only=True)
    
    class Meta:
        model = AssessmentAttempt
        fields = ['id', 'user', 'username', 'assessment', 'assessment_title',
                 'score', 'percentage', 'time_taken', 'answers', 
                 'completed_at', 'passed']
        read_only_fields = ['percentage', 'passed', 'completed_at']

class StudentProgressSerializer(serializers.ModelSerializer):
    student_username = serializers.CharField(source='student.user.username', read_only=True)
    lesson_name = serializers.CharField(source='lesson.name', read_only=True)
    course_name = serializers.CharField(source='lesson.course.name', read_only=True)
    completion_percentage = serializers.ReadOnlyField()
    
    class Meta:
        model = StudentProgress
        fields = ['id', 'student', 'student_username', 'lesson', 'lesson_name', 
                 'course_name', 'status', 'score', 'attempts', 'completion_percentage',
                 'time_spent', 'started_at', 'completed_at', 'last_accessed']
        read_only_fields = ['completion_percentage']

class CourseProgressSerializer(serializers.ModelSerializer):
    student_username = serializers.CharField(source='student.user.username', read_only=True)
    course_name = serializers.CharField(source='course.name', read_only=True)
    
    class Meta:
        model = CourseProgress
        fields = ['id', 'student', 'student_username', 'course', 'course_name',
                 'total_lessons_completed', 'total_score', 'average_score', 
                 'level', 'badges_earned', 'last_lesson_date', 
                 'best_assessment_score', 'attempts_count', 'status',
                 'started_at', 'completed_at']
        read_only_fields = ['total_lessons_completed', 'total_score', 'average_score',
                           'best_assessment_score', 'attempts_count']

class CourseDetailSerializer(CourseSerializer):
    lessons = LessonSerializer(many=True, read_only=True)
    assessments = AssessmentSerializer(many=True, read_only=True)
    
    class Meta(CourseSerializer.Meta):
        fields = CourseSerializer.Meta.fields + ['lessons', 'assessments']

class StudentDashboardSerializer(serializers.Serializer):
    """Serializer for student dashboard data"""
    student_profile = StudentProfileSerializer(read_only=True)
    enrolled_courses = serializers.IntegerField(read_only=True)
    completed_courses = serializers.IntegerField(read_only=True)
    total_lessons_completed = serializers.IntegerField(read_only=True)
    recent_attempts = AssessmentAttemptSerializer(many=True, read_only=True)
    course_progress = CourseProgressSerializer(many=True, read_only=True)
    
class ProgressStatsSerializer(serializers.Serializer):
    """Serializer for progress statistics"""
    total_courses = serializers.IntegerField()
    completed_courses = serializers.IntegerField()
    total_lessons = serializers.IntegerField()
    completed_lessons = serializers.IntegerField()
    total_assessments_taken = serializers.IntegerField()
    passed_assessments = serializers.IntegerField()
    average_score = serializers.FloatField()
    current_streak = serializers.IntegerField()