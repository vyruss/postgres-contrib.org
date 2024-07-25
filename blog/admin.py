from django.contrib import admin

# Register your models here.
# blog/admin.py


from django.contrib import admin
from blog.models import Category, Post

class CategoryAdmin(admin.ModelAdmin):
    pass

class PostAdmin(admin.ModelAdmin):
    pass

admin.site.register(Category, CategoryAdmin)
admin.site.register(Post, PostAdmin)

