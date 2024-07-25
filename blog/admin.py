from django.contrib import admin

# Register your models here.
# blog/admin.py


from django.contrib import admin
from blog.models import Category, Post, BlogUser
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User

class CategoryAdmin(admin.ModelAdmin):
    pass

class PostAdmin(admin.ModelAdmin):
    pass


class BlogUserInline(admin.StackedInline):
    model = BlogUser
    can_delete = False

# Define a new User admin
class UserAdmin(BaseUserAdmin):
    inlines = [BlogUserInline]


admin.site.register(Category, CategoryAdmin)
admin.site.register(Post, PostAdmin)

# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)
