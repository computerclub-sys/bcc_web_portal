from django.contrib import admin
from django.utils import timezone
from .models import Event, EventImage, EventRegistration

class EventImageInline(admin.TabularInline):
    model = EventImage
    extra = 1

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('title', 'date', 'status', 'registration_open', 'created_at')
    list_filter = ('status', 'registration_open')
    search_fields = ('title', 'description')
    inlines = [EventImageInline]
    actions = ['mark_active', 'mark_running', 'mark_completed']

    def mark_active(self, request, queryset):
        queryset.update(status='active')
        self.message_user(request, f'{queryset.count()} event(s) marked as Active.')
    mark_active.short_description = 'Mark selected as Active'

    def mark_running(self, request, queryset):
        queryset.update(status='running')
        self.message_user(request, f'{queryset.count()} event(s) marked as Running.')
    mark_running.short_description = 'Mark selected as Running'

    def mark_completed(self, request, queryset):
        queryset.update(status='completed')
        self.message_user(request, f'{queryset.count()} event(s) marked as Completed.')
    mark_completed.short_description = 'Mark selected as Completed'

@admin.register(EventRegistration)
class EventRegistrationAdmin(admin.ModelAdmin):
    list_display = ('user_info', 'event', 'status', 'applied_at')
    list_filter = ('status', 'event')
    search_fields = ('user__username', 'user__email', 'event__title')
    readonly_fields = ('user', 'event', 'applied_at', 'reviewed_at', 'reviewed_by', 'applicant_details')
    
    fieldsets = (
        ('Applicant Details', {
            'fields': ('applicant_details',)
        }),
        ('Registration Info', {
            'fields': ('user', 'event', 'status', 'notes', 'applied_at', 'reviewed_at', 'reviewed_by')
        }),
    )
    
    actions = ['approve_registrations', 'reject_registrations']

    def user_info(self, obj):
        return f"{obj.user.get_full_name() or obj.user.username} ({obj.user.email})"
    user_info.short_description = 'Applicant'

    def applicant_details(self, obj):
        return (
            f"Name: {obj.user.get_full_name() or obj.user.username}\n"
            f"Email: {obj.user.email}\n"
            f"Student ID: {obj.user.profile.student_id or 'N/A'}\n"
            f"Phone: {obj.user.profile.phone or 'N/A'}\n"
            f"Department: {obj.user.profile.department or 'N/A'}\n"
            f"Batch: {obj.user.profile.batch or 'N/A'}"
        )
    applicant_details.short_description = 'Full Applicant Info'

    def save_model(self, request, obj, form, change):
        if change and obj.status in ('approved', 'rejected'):
            obj.reviewed_at = timezone.now()
            obj.reviewed_by = request.user
        super().save_model(request, obj, form, change)

    def approve_registrations(self, request, queryset):
        count = 0
        for reg in queryset.filter(status='pending'):
            reg.status = 'approved'
            reg.reviewed_at = timezone.now()
            reg.reviewed_by = request.user
            reg.save()
            count += 1
        self.message_user(request, f'{count} registration(s) approved.')
    approve_registrations.short_description = 'Approve selected registrations'

    def reject_registrations(self, request, queryset):
        count = 0
        for reg in queryset.filter(status='pending'):
            reg.status = 'rejected'
            reg.reviewed_at = timezone.now()
            reg.reviewed_by = request.user
            reg.save()
            count += 1
        self.message_user(request, f'{count} registration(s) rejected.')
    reject_registrations.short_description = 'Reject selected registrations'
