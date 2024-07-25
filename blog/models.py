from django.conf import settings
from django.db import models
from django.utils import timezone

class Category(models.Model):
    name = models.TextField()

    class Meta:
        verbose_name_plural = "categories"

    def __str__(self):
        return self.name


class Post(models.Model):
    title = models.TextField()
    body = models.TextField()
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    created_at = models.DateTimeField(default=timezone.now)
    last_modified = models.DateTimeField(auto_now=True)
    category = models.ForeignKey("Category", related_name="posts", on_delete=models.PROTECT)

    def __str__(self):
        return self.title


class BlogUser(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    www_url = models.TextField()
