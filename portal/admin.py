from django.contrib import admin
from django.utils import timezone
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Profile, MembershipApplication

@receiver(post_save, sender=MembershipApplication)
def update_membership_status(sender, instance, created, **kwargs):
    if instance.status == 'approved':
        Profile.objects.filter(user=instance.user).update(is_member=True)
    elif instance.status == 'rejected':
        Profile.objects.filter(user=instance.user).update(is_member=False)

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'student_id', 'phone', 'department', 'batch', 'is_member')
    list_filter = ('is_member', 'department', 'batch')
    search_fields = ('user__username', 'user__email', 'student_id')

@admin.register(MembershipApplication)
class MembershipApplicationAdmin(admin.ModelAdmin):
    list_display = ('user', 'status', 'applied_at', 'reviewed_at', 'reviewed_by')
    list_filter = ('status',)
    search_fields = ('user__username', 'user__email')
    readonly_fields = ('user', 'applied_at', 'reviewed_at', 'reviewed_by')
    
    actions = ['approve_applications', 'reject_applications']
    
    def save_model(self, request, obj, form, change):
        if change and obj.status == 'approved':
            obj.reviewed_at = timezone.now()
            obj.reviewed_by = request.user
        super().save_model(request, obj, form, change)
    
    def approve_applications(self, request, queryset):
        count = 0
        for app in queryset:
            if app.status == 'pending':
                app.status = 'approved'
                app.reviewed_at = timezone.now()
                app.reviewed_by = request.user
                app.save()
                count += 1
        self.message_user(request, f'{count} application(s) approved.')
    approve_applications.short_description = 'Approve selected applications'
    
    def reject_applications(self, request, queryset):
        count = 0
        for app in queryset:
            if app.status == 'pending':
                app.status = 'rejected'
                app.reviewed_at = timezone.now()
                app.reviewed_by = request.user
                app.save()
                count += 1
        self.message_user(request, f'{count} application(s) rejected.')
    reject_applications.short_description = 'Reject selected applications'
