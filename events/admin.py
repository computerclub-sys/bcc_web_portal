from django.contrib import admin
from django.utils import timezone
from django.utils.html import format_html, mark_safe
from .models import Event, EventImage, EventRegistration

class EventImageInline(admin.TabularInline):
    model = EventImage
    extra = 1

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('title', 'date', 'status', 'registration_open', 'requires_registration', 'requires_payment', 'created_at')
    list_filter = ('status', 'registration_open', 'requires_registration', 'requires_payment')
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
    list_display = ('user_info', 'event', 'payment_method_display', 'status', 'applied_at')
    list_filter = ('status', 'payment_method', 'event')
    search_fields = ('user__username', 'user__email', 'event__title', 'transaction_id')
    readonly_fields = ('user', 'event', 'applied_at', 'reviewed_at', 'reviewed_by', 'applicant_details', 'payment_details')
    
    fieldsets = (
        ('Applicant Details', {
            'fields': ('applicant_details',)
        }),
        ('Payment Info', {
            'fields': ('payment_details', 'payment_method', 'transaction_id')
        }),
        ('Approval', {
            'fields': ('status', 'notes', 'reviewed_at', 'reviewed_by')
        }),
    )
    
    actions = ['approve_registrations', 'reject_registrations']

    def user_info(self, obj):
        return f"{obj.user.get_full_name() or obj.user.username} ({obj.user.email})"
    user_info.short_description = 'Applicant'

    def payment_method_display(self, obj):
        return obj.get_payment_method_display()
    payment_method_display.short_description = 'Payment'

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

    def payment_details(self, obj):
        if obj.payment_method == 'bkash':
            return format_html(
                '<div style="background:#f9fafb; padding:15px; border-radius:8px; font-family:monospace; line-height:2;">'
                '<strong>Payment Method:</strong> bKash<br>'
                '<strong>bKash Number:</strong> 12345678<br>'
                '<strong>Transaction ID:</strong> {}<br>'
                '</div>',
                obj.transaction_id or 'Not provided'
            )
        return mark_safe(
            '<div style="background:#f9fafb; padding:15px; border-radius:8px; font-family:monospace; line-height:2;">'
            '<strong>Payment Method:</strong> Offline/Physical<br>'
            '<strong>Note:</strong> Collect payment at event venue<br>'
            '</div>'
        )
    payment_details.short_description = 'Payment Details'

    def save_model(self, request, obj, form, change):
        if change:
            if obj.status in ('approved', 'rejected'):
                obj.reviewed_at = timezone.now()
                obj.reviewed_by = request.user
                obj.payment_status = obj.status
                obj.payment_reviewed_at = timezone.now()
                obj.payment_reviewed_by = request.user
        super().save_model(request, obj, form, change)

    def _bulk_update(self, request, queryset, new_status, label):
        qs = queryset.filter(status='pending')
        now = timezone.now()
        count = 0
        for obj in qs:
            obj.status = new_status
            obj.reviewed_at = now
            obj.reviewed_by = request.user
            obj.payment_status = new_status
            obj.payment_reviewed_at = now
            obj.payment_reviewed_by = request.user
            obj.save()
            count += 1
        self.message_user(request, f'{count} {label}.')

    def approve_registrations(self, request, queryset):
        self._bulk_update(request, queryset,
            new_status='approved', label='registration(s) approved')
    approve_registrations.short_description = 'Approve selected registrations'

    def reject_registrations(self, request, queryset):
        self._bulk_update(request, queryset,
            new_status='rejected', label='registration(s) rejected')
    reject_registrations.short_description = 'Reject selected registrations'
