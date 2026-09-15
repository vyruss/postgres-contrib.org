from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.text import Truncator

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

    def get_absolute_url(self):
        return reverse("blog_detail", args=[self.pk])


class BlogUser(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    www_url = models.TextField()


class Contribution(models.Model):
    """A contribution submitted from the public form, awaiting review."""

    body = models.TextField()
    submitter = models.TextField(blank=True)
    submitted_at = models.DateTimeField(auto_now_add=True)
    reviewed = models.BooleanField(default=False)
    reviewed_at = models.DateTimeField(null=True, blank=True, editable=False)

    class Meta:
        ordering = ["reviewed", "-submitted_at"]

    def __str__(self):
        return Truncator(self.body).chars(80)

    def save(self, *args, **kwargs):
        if self.reviewed and self.reviewed_at is None:
            self.reviewed_at = timezone.now()
        elif not self.reviewed:
            self.reviewed_at = None
        super().save(*args, **kwargs)
