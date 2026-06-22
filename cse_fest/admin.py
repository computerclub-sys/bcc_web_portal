from django.contrib import admin
from .models import Fest, FestEvent, FestSchedule, Notice, CommitteeMember, Faq, Sponsor, FestRegistration


class FestEventInline(admin.TabularInline):
    model = FestEvent
    extra = 1
    fields = ('title', 'slug', 'category', 'date', 'order', 'registration_open')


class FestScheduleInline(admin.TabularInline):
    model = FestSchedule
    extra = 1
    fields = ('title', 'date', 'time', 'order')


class NoticeInline(admin.TabularInline):
    model = Notice
    extra = 1


@admin.register(Fest)
class FestAdmin(admin.ModelAdmin):
    list_display = ('title', 'year', 'is_active', 'target_date', 'created_at')
    list_filter = ('is_active',)
    inlines = [FestEventInline, FestScheduleInline, NoticeInline]


@admin.register(FestEvent)
class FestEventAdmin(admin.ModelAdmin):
    list_display = ('title', 'fest', 'category', 'date', 'registration_open', 'order')
    list_filter = ('category', 'registration_open', 'fest')
    search_fields = ('title', 'description')
    prepopulated_fields = {'slug': ('title',)}
    fieldsets = (
        ('Fest', {'fields': ('fest', 'category')}),
        ('Event Info', {'fields': ('title', 'slug', 'short_description', 'description', 'poster')}),
        ('Date & Time', {'fields': ('date', 'time')}),
        ('Registration', {'fields': ('registration_open', 'requires_team', 'team_size', 'requires_payment')}),
        ('Files', {'fields': ('rule_book_pdf',)}),
        ('Ordering', {'fields': ('order',)}),
    )


@admin.register(FestSchedule)
class FestScheduleAdmin(admin.ModelAdmin):
    list_display = ('title', 'fest', 'date', 'time')
    list_filter = ('fest',)


@admin.register(Notice)
class NoticeAdmin(admin.ModelAdmin):
    list_display = ('title', 'fest', 'is_new', 'is_active', 'created_at')
    list_filter = ('is_new', 'is_active', 'fest')
    actions = ['mark_active', 'mark_inactive']

    def mark_active(self, request, queryset):
        queryset.update(is_active=True)
        self.message_user(request, f'{queryset.count()} notice(s) activated.')
    mark_active.short_description = 'Mark selected as Active'

    def mark_inactive(self, request, queryset):
        queryset.update(is_active=False)
        self.message_user(request, f'{queryset.count()} notice(s) deactivated.')
    mark_inactive.short_description = 'Mark selected as Inactive'


@admin.register(CommitteeMember)
class CommitteeMemberAdmin(admin.ModelAdmin):
    list_display = ('name', 'position', 'role', 'fest')
    list_filter = ('role', 'fest')
    search_fields = ('name',)


@admin.register(Faq)
class FaqAdmin(admin.ModelAdmin):
    list_display = ('question', 'fest', 'is_active', 'order')
    list_filter = ('is_active', 'fest')


@admin.register(Sponsor)
class SponsorAdmin(admin.ModelAdmin):
    list_display = ('name', 'sponsor_type', 'fest', 'order')
    list_filter = ('sponsor_type', 'fest')


@admin.register(FestRegistration)
class FestRegistrationAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'email', 'event', 'phone', 'created_at')
    list_filter = ('event__fest', 'event')
    search_fields = ('full_name', 'email', 'phone', 'student_id')
    readonly_fields = ('created_at',)
