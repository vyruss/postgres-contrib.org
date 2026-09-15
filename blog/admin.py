from django.contrib import admin

# Register your models here.
# blog/admin.py


from django import forms
from django.contrib import admin
from blog.models import Category, Contribution, Post, BlogUser
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User

class CategoryAdmin(admin.ModelAdmin):
    pass

class PostAdmin(admin.ModelAdmin):
    pass


class ContributionAdminForm(forms.ModelForm):
    class Meta:
        model = Contribution
        fields = "__all__"
        widgets = {
            "body": forms.Textarea(attrs={"rows": 30, "cols": 100}),
            "submitter": forms.TextInput(attrs={"size": 60}),
        }


class ContributionAdmin(admin.ModelAdmin):
    form = ContributionAdminForm
    list_display = ("__str__", "submitter", "submitted_at", "reviewed")
    list_editable = ("reviewed",)
    list_filter = ("reviewed", "submitted_at")
    search_fields = ("body", "submitter")
    date_hierarchy = "submitted_at"
    readonly_fields = ("submitted_at", "reviewed_at")
    actions = ["mark_reviewed", "mark_not_reviewed"]

    def _set_reviewed(self, request, queryset, reviewed):
        updated = 0
        for contribution in queryset:
            contribution.reviewed = reviewed
            contribution.save()
            updated += 1
        self.message_user(request, f"{updated} submission(s) updated.")

    @admin.action(description="Mark selected submissions as reviewed")
    def mark_reviewed(self, request, queryset):
        self._set_reviewed(request, queryset, True)

    @admin.action(description="Mark selected submissions as not reviewed")
    def mark_not_reviewed(self, request, queryset):
        self._set_reviewed(request, queryset, False)


class BlogUserInline(admin.StackedInline):
    model = BlogUser
    can_delete = False

# Define a new User admin
class UserAdmin(BaseUserAdmin):
    inlines = [BlogUserInline]


admin.site.register(Category, CategoryAdmin)
admin.site.register(Post, PostAdmin)
admin.site.register(Contribution, ContributionAdmin)

# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)
