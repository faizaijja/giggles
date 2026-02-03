from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import (
    Course, Lesson, StudentProfile, Assessment, 
    AssessmentAttempt, StudentProgress, CourseProgress
)

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'lesson_count', 'created_at']
    list_filter = ['created_at']
    search_fields = ['name', 'slug', 'description']
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ['created_at']
    
    def lesson_count(self, obj):
        return obj.lessons.count()
    lesson_count.short_description = 'Number of Lessons'

@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ['name', 'course', 'slug', 'difficulty_level', 'max_score', 'created_at']
    list_filter = ['course', 'difficulty_level', 'created_at']
    search_fields = ['name', 'slug', 'course__name']
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ['created_at']
    list_select_related = ['course']
    
    fieldsets = (
        (None, {
            'fields': ('course', 'name', 'slug')
        }),
        ('Settings', {
            'fields': ('max_score', 'difficulty_level')
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )

@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'get_username', 'age', 'grade_level', 'created_at']
    list_filter = ['grade_level', 'age', 'created_at']
    search_fields = ['user__username', 'user__email', 'user__first_name', 'user__last_name']
    readonly_fields = ['created_at']
    raw_id_fields = ['user']
    
    def get_username(self, obj):
        return obj.user.username
    get_username.short_description = 'Username'
    get_username.admin_order_field = 'user__username'

@admin.register(Assessment)
class AssessmentAdmin(admin.ModelAdmin):
    list_display = ['title', 'course', 'lesson', 'total_questions', 'passing_score', 'attempt_count']
    list_filter = ['course', 'lesson', 'passing_score']
    search_fields = ['title', 'course__name', 'lesson__name']
    list_select_related = ['course', 'lesson']
    
    fieldsets = (
        (None, {
            'fields': ('course', 'lesson', 'title')
        }),
        ('Assessment Settings', {
            'fields': ('total_questions', 'passing_score')
        }),
    )
    
    def attempt_count(self, obj):
        return obj.assessmentattempt_set.count()
    attempt_count.short_description = 'Total Attempts'

@admin.register(AssessmentAttempt)
class AssessmentAttemptAdmin(admin.ModelAdmin):
    list_display = ['user', 'assessment', 'score', 'percentage', 'passed', 'completed_at']
    list_filter = ['passed', 'completed_at', 'assessment__course']
    search_fields = ['user__username', 'assessment__title']
    readonly_fields = ['percentage', 'passed', 'completed_at']
    list_select_related = ['user', 'assessment']
    date_hierarchy = 'completed_at'
    
    fieldsets = (
        (None, {
            'fields': ('user', 'assessment')
        }),
        ('Results', {
            'fields': ('score', 'percentage', 'passed', 'time_taken')
        }),
        ('Details', {
            'fields': ('answers', 'completed_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_readonly_fields(self, request, obj=None):
        if obj:  # editing an existing object
            return self.readonly_fields + ['user', 'assessment', 'score']
        return self.readonly_fields

class StudentProgressInline(admin.TabularInline):
    model = StudentProgress
    extra = 0
    readonly_fields = ['completion_percentage', 'started_at', 'completed_at', 'last_accessed']
    fields = ['lesson', 'status', 'score', 'attempts', 'completion_percentage', 'last_accessed']

@admin.register(StudentProgress)
class StudentProgressAdmin(admin.ModelAdmin):
    list_display = ['student', 'lesson', 'status', 'score', 'completion_percentage', 'attempts', 'last_accessed']
    list_filter = ['status', 'lesson__course', 'lesson__difficulty_level', 'completed_at']
    search_fields = ['student__user__username', 'lesson__name', 'lesson__course__name']
    readonly_fields = ['completion_percentage', 'started_at', 'completed_at', 'last_accessed']
    list_select_related = ['student__user', 'lesson__course']
    date_hierarchy = 'last_accessed'
    
    fieldsets = (
        (None, {
            'fields': ('student', 'lesson', 'status')
        }),
        ('Progress', {
            'fields': ('score', 'attempts', 'completion_percentage', 'time_spent')
        }),
        ('Timestamps', {
            'fields': ('started_at', 'completed_at', 'last_accessed'),
            'classes': ('collapse',)
        }),
    )
    
    def completion_percentage_display(self, obj):
        try:
            percentage = obj.completion_percentage
            return f"{percentage:.1f}%" if percentage is not None else "N/A"
        except Exception:
            return "N/A"

    completion_percentage_display.short_description = 'Completion %'
 

@admin.register(CourseProgress)
class CourseProgressAdmin(admin.ModelAdmin):
    list_display = ['student', 'course', 'status', 'total_lessons_completed', 
                   'average_score', 'level', 'best_assessment_score', 'last_lesson_date']
    list_filter = ['status', 'level', 'course', 'completed_at']
    search_fields = ['student__user__username', 'course__name']
    readonly_fields = ['total_lessons_completed', 'total_score', 'average_score', 
                      'best_assessment_score', 'attempts_count', 'started_at', 'completed_at']
    list_select_related = ['student__user', 'course']
    date_hierarchy = 'last_lesson_date'
    
    fieldsets = (
        (None, {
            'fields': ('student', 'course', 'status')
        }),
        ('Progress Statistics', {
            'fields': ('total_lessons_completed', 'total_score', 'average_score', 
                      'best_assessment_score', 'attempts_count')
        }),
        ('Achievement', {
            'fields': ('level', 'badges_earned')
        }),
        ('Timestamps', {
            'fields': ('started_at', 'completed_at', 'last_lesson_date'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['update_progress']
    
    def update_progress(self, request, queryset):
        """Action to manually update progress for selected course progress records"""
        updated = 0
        for progress in queryset:
            progress.update_progress()
            updated += 1
        
        self.message_user(
            request,
            f'Successfully updated progress for {updated} course progress records.'
        )
    update_progress.short_description = 'Update selected progress records'

# Custom admin site configuration
admin.site.site_header = 'Learning Management System'
admin.site.site_title = 'Learning Admin'
admin.site.index_title = 'Learning Administration'