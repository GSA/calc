import os
import re
from django.contrib import admin
from django.http import HttpResponse, HttpResponseForbidden
from django.db import models, transaction
from django import forms
from django.core.urlresolvers import reverse
from django.utils.safestring import mark_safe
from django.utils.html import format_html
from django.utils.text import slugify
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserChangeForm
from django.conf.urls import url
from django.shortcuts import get_object_or_404


from frontend.upload import DEFAULT_FILE_EXTENSIONS
from .management.commands.initgroups import VIEW_ATTEMPT_PERMISSION
from . import email
from .schedules import registry
from .models import (SubmittedPriceList, SubmittedPriceListRow,
                     AttemptedPriceListSubmission)
from .templatetags.data_capture import tz_timestamp


class UniqueEmailFormMixin:
    '''
    A mixin that enforces the uniqueness, relative to the User model,
    of an 'email' field in the form it's mixed-in with.

    Taken from https://gist.github.com/gregplaysguitar/1184995.
    '''

    def clean_email(self):
        qs = User.objects.filter(email__iexact=self.cleaned_data['email'])
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.count():
            raise forms.ValidationError(
                'That email address is already in use.'
            )
        else:
            return self.cleaned_data['email']


class CustomUserCreationForm(forms.ModelForm, UniqueEmailFormMixin):
    '''
    A substitute for django.contrib.auth.forms.UserCreationForm which
    doesn't ask for information about new users that's irrelevant
    to how CALC works.
    '''

    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ('email',)

    def generate_username(self, email, max_attempts=100):
        '''
        Generate a unique username based on the given email address
        by slugifying the first several characters of the username
        part of the email. If needed, a number is added at the end
        to avoid conflicts with existing usernames.
        '''

        basename = slugify(email.split('@')[0])[:15]
        for i in range(max_attempts):
            if i == 0:
                username = basename
            else:
                username = '{}{}'.format(basename, i)
            if not User.objects.filter(username=username).exists():
                return username
        raise Exception(
            'unable to generate username for {} after {} attempts'.format(
                email,
                max_attempts
            )
        )

    def clean(self):
        email = self.cleaned_data.get('email')

        if email:
            self.cleaned_data['username'] = self.generate_username(email)

        return self.cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = self.cleaned_data['username']
        if commit:
            user.save()
        return user


class CustomUserChangeForm(UserChangeForm, UniqueEmailFormMixin):
    email = forms.EmailField(required=True)


class CustomUserAdmin(UserAdmin):
    '''
    Simplified user admin for non-superusers, which also prevents such
    users from upgrading themselves to superuser.
    '''

    form = CustomUserChangeForm

    add_form_template = 'admin/data_capture/add_user_form.html'

    add_form = CustomUserCreationForm

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email',),
        }),
    )

    non_superuser_fieldsets = (
        (None, {'fields': (
            'username',
            # Even though we don't need/use the password field, showing it
            # is apparently required to make submitting changes work.
            'password'
        )}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'groups')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )

    list_display = ('email', 'is_staff')

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if not request.user.is_superuser:
            qs = qs.filter(is_superuser=False)
        return qs

    def get_fieldsets(self, request, obj=None):
        if obj is not None and not request.user.is_superuser:
            return self.non_superuser_fieldsets
        return super().get_fieldsets(request, obj)


admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)


class SubmittedPriceListRowInline(admin.TabularInline):
    model = SubmittedPriceListRow

    can_delete = False

    fields = (
        'labor_category',
        'education_level',
        'min_years_experience',
        'base_year_rate',
        'sin',
        'is_muted',
    )

    readonly_fields = ()

    formfield_overrides = {
        models.TextField: {'widget': forms.TextInput}
    }

    def has_add_permission(self, request):
        return False

    def get_readonly_fields(self, request, obj=None):
        if obj and obj.status is SubmittedPriceList.STATUS_APPROVED:
            return self.fields
        return self.readonly_fields


@transaction.atomic
def approve(modeladmin, request, queryset):
    not_approved = queryset.exclude(status=SubmittedPriceList.STATUS_APPROVED)
    count = not_approved.count()
    for price_list in not_approved:
        price_list.approve(request.user)
        email.price_list_approved(price_list)

    messages.add_message(
        request,
        messages.INFO,
        '{} price list(s) have been approved and added to CALC.'.format(
            count
        )
    )


approve.short_description = (
    'Approve selected price lists (add their data to CALC)'
)


@transaction.atomic
def retire(modeladmin, request, queryset):
    approved = queryset.filter(status=SubmittedPriceList.STATUS_APPROVED)
    count = approved.count()
    for price_list in approved:
        price_list.retire(request.user)
        email.price_list_retired(price_list)
    messages.add_message(
        request,
        messages.INFO,
        '{} price list(s) have been retired and removed from CALC.'.format(
            count
        )
    )


retire.short_description = (
    'Retire selected price lists (remove their data from CALC)'
)


@transaction.atomic
def reject(modeladmin, request, queryset):
    unreviewed = queryset.filter(status=SubmittedPriceList.STATUS_UNREVIEWED)
    count = unreviewed.count()
    for price_list in unreviewed:
        price_list.reject(request.user)
        email.price_list_rejected(price_list)
    messages.add_message(
        request,
        messages.INFO,
        '{} price list(s) have been rejected.'.format(count)
    )


reject.short_description = (
    'Reject selected price lists'
)


class UndeletableModelAdmin(admin.ModelAdmin):
    '''
    Represents a model admin UI that offers no way of deleting
    instances. This is useful to ensure accidental data loss, especially
    when we want to keep it around for historical/data provenance purposes.
    '''

    # http://stackoverflow.com/a/25813184/2422398
    def get_actions(self, request):
        actions = super().get_actions(request)
        del actions['delete_selected']
        return actions

    def has_delete_permission(self, request, obj=None):
        return False


def short_description(desc: str):
    def decorator(func):
        func.short_description = desc
        return func

    return decorator


class BaseSubmittedPriceListAdmin(UndeletableModelAdmin):
    list_display = ('contract_number', 'vendor_name', 'submitter',
                    'tz_created_at', 'status_changed_by_email',
                    'tz_status_changed_at')

    fields = (
        'contract_number',
        'vendor_name',
        'is_small_business',
        'schedule_title',
        'contractor_site',
        'contract_start',
        'contract_end',
        'escalation_rate',
        'submitter',
        'tz_created_at',
        'tz_updated_at',
        'current_status',
        'tz_status_changed_at',
        'status_changed_by_email',
    )

    readonly_fields = (
        'schedule_title',
        'tz_created_at',
        'tz_updated_at',
        'current_status',
        'submitter',
        'tz_status_changed_at',
        'status_changed_by_email',
    )

    inlines = [
        SubmittedPriceListRowInline
    ]

    @short_description('Status changed by')
    def status_changed_by_email(self, instance):
        '''
        custom field to show the email address of the status_changed_by user
        '''
        return instance.status_changed_by.email

    def current_status(self, instance):
        content = instance.get_status_display() + "<br>"
        if instance.status is SubmittedPriceList.STATUS_APPROVED:
            content += ("<span style=\"color: green\">"
                        "This price list has been approved, so its data is "
                        "now in CALC. To retire it, you will need to use "
                        "the 'Retire selected price lists' action from the "
                        "<a href=\"..\">list view</a>. Note also that in "
                        "order to edit the fields in this price list, you "
                        "will first need to retire it.")
        else:
            content += ("<span style=\"color: red\">"
                        "This price list is not currently approved, so its "
                        "data is not in CALC. To approve it, you will need to "
                        "use the 'Approve selected price lists' action from "
                        "the <a href=\"..\">list view</a>.")

        return mark_safe(content)  # nosec

    @short_description('Created at')
    def tz_created_at(self, instance):
        return tz_timestamp(instance.created_at)

    @short_description('Updated at')
    def tz_updated_at(self, instance):
        return tz_timestamp(instance.updated_at)

    @short_description('Status changed at')
    def tz_status_changed_at(self, instance):
        return tz_timestamp(instance.status_changed_at)

    @short_description('Schedule')
    def schedule_title(self, instance):
        return registry.get_class(instance.schedule).title

    def has_add_permission(self, request):
        return False

    def get_readonly_fields(self, request, obj=None):
        if obj and obj.status is SubmittedPriceList.STATUS_APPROVED:
            return self.fields
        return self.readonly_fields


class ApprovedPriceList(SubmittedPriceList):
    class Meta:
        proxy = True


@admin.register(ApprovedPriceList)
class ApprovedPriceListAdmin(BaseSubmittedPriceListAdmin):
    actions = [retire]

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.filter(status=SubmittedPriceList.STATUS_APPROVED)


class UnreviewedPriceList(SubmittedPriceList):
    class Meta:
        proxy = True


@admin.register(UnreviewedPriceList)
class UnreviewedPriceListAdmin(BaseSubmittedPriceListAdmin):
    actions = [approve, reject]

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.filter(status=SubmittedPriceList.STATUS_UNREVIEWED)


class RejectedPriceList(SubmittedPriceList):
    class Meta:
        proxy = True


@admin.register(RejectedPriceList)
class RejectedPriceListAdmin(BaseSubmittedPriceListAdmin):
    actions = [approve]

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.filter(status=SubmittedPriceList.STATUS_REJECTED)


class RetiredPriceList(SubmittedPriceList):
    class Meta:
        proxy = True


@admin.register(RetiredPriceList)
class RetiredPriceListAdmin(BaseSubmittedPriceListAdmin):
    actions = [approve]

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.filter(status=SubmittedPriceList.STATUS_RETIRED)


@admin.register(SubmittedPriceListRow)
class SubmittedPriceListRowAdmin(UndeletableModelAdmin):
    list_display = (
        'contract_number',
        'vendor_name',
        'labor_category',
        'education_level',
        'min_years_experience',
        'base_year_rate',
        'sin',
        'is_muted',
    )

    list_editable = (
        'is_muted',
    )

    def contract_number(self, obj):
        # get status label and derive url from it
        status_display = obj.price_list.get_status_display()
        url = reverse(
            'admin:data_capture_{}pricelist_change'.format(status_display),
            args=(obj.price_list.id,))
        return format_html(
            '<a href="{}">{}</a>',
            url,
            obj.price_list.contract_number
        )

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.exclude(
            price_list__status=SubmittedPriceList.STATUS_APPROVED)

    def vendor_name(self, obj):
        return obj.price_list.vendor_name

    def has_add_permission(self, request):
        return False


def clean_filename(filename):
    '''
    Attempt to clean the filename so it doesn't contain invalid
    characters or potentially dangerous file extensions.

    Examples:

        >>> clean_filename('boop.exe')
        'boop'

        >>> clean_filename('.csv')
        'csv'

        >>> clean_filename('$.csv')
        'data.csv'

        >>> clean_filename('u$goose.xls')
        'ugoose.xls'
    '''

    basename, ext = os.path.splitext(filename)

    basename = ''.join([
        char for char in basename
        if re.match('[A-Za-z0-9_\-]', char)
    ]) or 'data'

    if ext.lower() not in DEFAULT_FILE_EXTENSIONS:
        ext = ''

    return basename + ext


@admin.register(AttemptedPriceListSubmission)
class AttemptedPriceListSubmissionAdmin(admin.ModelAdmin):
    list_display = (
        'created_at',
        'id',
        'submitter',
        'uploaded_file_name',
        'valid_row_count',
        'invalid_row_count',
    )

    change_form_template = 'admin/data_capture/view_attempted_submission.html'

    def has_add_permission(self, request):
        return False

    def send_uploaded_file(self, request, id):
        if not request.user.has_perm(VIEW_ATTEMPT_PERMISSION):
            return HttpResponseForbidden()

        id = int(id)
        obj = get_object_or_404(AttemptedPriceListSubmission, pk=id)
        response = HttpResponse(obj.uploaded_file.contents.read(),
                                content_type='application/octet-stream')
        response['Content-Disposition'] = 'attachment; filename="{}"'.format(
            clean_filename(obj.uploaded_file_name),
        )
        return response

    def get_urls(self):
        return [
            url(r'^(?P<id>\d+)/download/$',
                self.admin_site.admin_view(self.send_uploaded_file),
                name='data_capture_send_uploaded_file'),
        ] + super().get_urls()
