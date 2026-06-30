from django.contrib import admin
from django.http import HttpResponse
from openpyxl import Workbook
from .models import Fest, FestEvent, FestPrize, FestSchedule, Notice, CommitteeMember, Faq, Sponsor, FestRegistration, FestTeamMember


class FestEventInline(admin.TabularInline):
    model = FestEvent
    extra = 1
    fields = ('title', 'slug', 'category', 'date', 'order', 'registration_open')


class FestPrizeInline(admin.TabularInline):
    model = FestPrize
    extra = 1
    fields = ('position', 'amount', 'order')


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
    fieldsets = (
        ('Fest', {'fields': ('title', 'year', 'is_active', 'poster', 'target_date', 'bkash_number')}),
    )
    inlines = [FestEventInline, FestScheduleInline, NoticeInline]


@admin.register(FestEvent)
class FestEventAdmin(admin.ModelAdmin):
    list_display = ('title', 'fest', 'category', 'date', 'registration_open', 'registration_fee', 'prize_pool', 'order')
    list_filter = ('category', 'registration_open', 'fest')
    search_fields = ('title', 'description')
    prepopulated_fields = {'slug': ('title',)}
    fieldsets = (
        ('Fest', {'fields': ('fest', 'category')}),
        ('Event Info', {'fields': ('title', 'slug', 'short_description', 'description', 'poster')}),
        ('Date & Time', {'fields': ('date', 'time', 'last_registration_date')}),
        ('Registration', {'fields': ('registration_open', 'requires_team', 'min_team_size', 'max_team_size', 'requires_payment', 'registration_fee', 'hackathon_fee_3', 'hackathon_fee_4')}),
        ('Prizes & Kit', {'fields': ('prize_pool', 'provided_kit')}),
        ('Files', {'fields': ('rule_book_pdf',)}),
        ('Ordering', {'fields': ('order',)}),
    )
    inlines = [FestPrizeInline]


@admin.register(FestSchedule)
class FestScheduleAdmin(admin.ModelAdmin):
    list_display = ('title', 'event', 'fest', 'date', 'time')
    list_filter = ('fest', 'event')


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


class FestTeamMemberInline(admin.TabularInline):
    model = FestTeamMember
    extra = 0
    fields = ('name', 'email', 'phone', 'student_id', 'department', 'semester', 'section', 'group', 't_shirt_size')
    readonly_fields = ('name', 'email', 'phone', 'student_id', 'department', 'semester', 'section', 'group', 't_shirt_size')
    can_delete = False
    max_num = 0


@admin.register(FestRegistration)
class FestRegistrationAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'email', 'event', 'phone', 'payment_method', 'status', 'created_at')
    list_filter = ('event__fest', 'event', 'payment_method', 'status')
    search_fields = ('full_name', 'email', 'phone', 'student_id', 'application_id', 'transaction_id')
    readonly_fields = ('application_id', 'created_at',)
    inlines = [FestTeamMemberInline]
    actions = ['export_approved_excel']
    fieldsets = (
        ('Application', {'fields': ('application_id', 'event', 'status', 'created_at')}),
        ('Personal Info', {'fields': ('full_name', 'email', 'phone', 'gender', 'section', 'group')}),
        ('Academic', {'fields': ('university', 'department', 'student_id')}),
        ('Team', {'fields': ('team_name', 'hackathon_category')}),
        ('Payment', {'fields': ('payment_method', 'transaction_id')}),
        ('eFootball', {'fields': ('in_game_name_id', 'device_name', 'self_photo')}),
        ('Other', {'fields': ('notes',)}),
    )

    @admin.action(description='Export selected (approved) as Excel')
    def export_approved_excel(self, request, queryset):
        registrations = queryset.filter(status='confirmed').order_by('event', 'full_name')
        if not registrations.exists():
            self.message_user(request, 'No approved registrations selected.', level='WARNING')
            return

        wb = Workbook()
        ws = wb.active
        ws.title = 'Approved Registrations'
        ws.append(['App ID', 'Event', 'Name', 'Email', 'Phone', 'Dept', 'Student ID', 'Semester', 'Section', 'Group', 'Team Name', 'Status', 'Registered At'])

        for r in registrations:
            ws.append([
                r.application_id, r.event.title, r.full_name, r.email, r.phone,
                r.department, r.student_id, '', '', '',
                r.team_name, r.status, r.created_at.strftime('%Y-%m-%d %H:%M')
            ])
            for m in r.team_members.all():
                ws.append([
                    '', '', m.name, m.email, m.phone,
                    m.department, m.student_id, m.semester, m.section, m.group,
                    '', '', ''
                ])

        response = HttpResponse(
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = 'attachment; filename="approved_registrations.xlsx"'
        wb.save(response)
        return response
