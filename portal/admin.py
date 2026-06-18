from io import BytesIO
from zipfile import ZipFile

from django.contrib import admin
from django.urls import path
from django.shortcuts import render, redirect
from django.utils.html import format_html
from django.http import HttpResponse
from django.contrib import messages as django_messages
from .models import Profile, TeamMember


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    change_list_template = 'admin/profile_changelist.html'
    list_display = ('profile_name', 'student_id', 'phone', 'department', 'batch', 'is_member', 'has_qr')
    list_filter = ('is_member', 'department', 'batch')
    search_fields = ('user__username', 'user__email', 'student_id')
    readonly_fields = ('member_uuid', 'qr_preview')
    fieldsets = (
        (None, {
            'fields': ('user', 'student_id', 'email', 'phone', 'department', 'batch', 'is_member')
        }),
        ('Membership', {
            'fields': ('member_uuid', 'qr_preview')
        }),
    )

    def profile_name(self, obj):
        if obj.user:
            return obj.user.get_full_name() or obj.user.username
        return f'Unclaimed ({obj.student_id or str(obj.member_uuid)[:8]})'
    profile_name.short_description = 'Name'

    def has_qr(self, obj):
        return bool(obj.qr_png)
    has_qr.short_description = 'QR'
    has_qr.boolean = True

    def qr_preview(self, obj):
        if obj.qr_png:
            return format_html('<img src="{}" width="100" height="100" />', f'/member/{obj.member_uuid}/qr/')
        return 'No QR code'
    qr_preview.short_description = 'QR Code'

    actions = ['download_qr_zip']

    def download_qr_zip(self, request, queryset):
        buf = BytesIO()
        with ZipFile(buf, 'w') as zf:
            for profile in queryset:
                if profile.qr_png:
                    zf.writestr(f'{profile.student_id or profile.member_uuid}.png', profile.qr_png)
        buf.seek(0)
        resp = HttpResponse(buf, content_type='application/zip')
        resp['Content-Disposition'] = 'attachment; filename="bcc_qr_codes.zip"'
        return resp
    download_qr_zip.short_description = 'Download QR codes as ZIP'

    def get_urls(self):
        urls = super().get_urls()
        custom = [
            path('generate-profiles/', self.generate_profiles_view, name='generate_profiles'),
            path('download-unclaimed-qrs/', self.download_unclaimed_qrs_view, name='download_unclaimed_qrs'),
        ]
        return custom + urls

    def download_unclaimed_qrs_view(self, request):
        unclaimed = Profile.objects.filter(is_member=True, user__isnull=True)
        buf = BytesIO()
        with ZipFile(buf, 'w') as zf:
            for profile in unclaimed:
                if profile.qr_png:
                    zf.writestr(f'{profile.student_id or profile.member_uuid}.png', profile.qr_png)
        buf.seek(0)
        resp = HttpResponse(buf, content_type='application/zip')
        resp['Content-Disposition'] = 'attachment; filename="bcc_unclaimed_qr_codes.zip"'
        return resp

    def generate_profiles_view(self, request):
        if request.method == 'POST':
            try:
                count = int(request.POST.get('count', 0))
            except (ValueError, TypeError):
                count = 0
            if count < 1:
                django_messages.error(request, 'Enter a valid number (minimum 1).')
                return redirect('..')
            existing = Profile.objects.filter(is_member=True, user__isnull=True).count()
            if existing > 0:
                django_messages.warning(request, f'There are {existing} unclaimed profiles already. Generating more anyway.')
            created = 0
            max_id = Profile.objects.filter(
                student_id__startswith='BCC-'
            ).values_list('student_id', flat=True).order_by('student_id').last()
            start_num = 1
            if max_id:
                try:
                    start_num = int(max_id.split('-')[1]) + 1
                except (IndexError, ValueError):
                    start_num = Profile.objects.filter(is_member=True, user__isnull=True).count() + 1
            for i in range(count):
                sid = f'BCC-{start_num + i:04d}'
                profile = Profile.objects.create(
                    student_id=sid,
                    is_member=True,
                )
                profile.generate_qr_code()
                profile.save(update_fields=['qr_png'])
                created += 1
            django_messages.success(request, f'Created {created} new member profile(s) with QR codes.')
            return redirect('..')
        return render(request, 'admin/generate_profiles.html')


@admin.register(TeamMember)
class TeamMemberAdmin(admin.ModelAdmin):
    list_display = ('name', 'role', 'panel', 'order', 'is_active', 'image_preview')
    list_filter = ('panel', 'is_active')
    search_fields = ('name', 'role', 'department')
    list_editable = ('order', 'is_active')
    readonly_fields = ('image_preview',)
    fieldsets = (
        (None, {
            'fields': ('name', 'role', 'department', 'panel')
        }),
        ('Details', {
            'fields': ('bio', 'tags', 'badge', 'avatar_letter', 'image', 'image_preview')
        }),
        ('Links', {
            'fields': ('email', 'github', 'linkedin')
        }),
        ('Settings', {
            'fields': ('order', 'is_active')
        }),
    )

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="60" height="60" style="border-radius:8px;object-fit:cover;" />', obj.image.url)
        return format_html('<div style="width:60px;height:60px;border-radius:8px;background:#eee;display:flex;align-items:center;justify-content:center;font-weight:bold">{}</div>', obj.avatar_letter or '?')
    image_preview.short_description = 'Photo'
