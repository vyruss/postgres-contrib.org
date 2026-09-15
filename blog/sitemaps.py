from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from blog.models import Category, Post


class HttpsSitemap(Sitemap):
    """The site is served over TLS behind a proxy, which request.is_secure() cannot see."""

    protocol = "https"


class PostSitemap(HttpsSitemap):
    changefreq = "monthly"
    priority = 0.8

    def items(self):
        return Post.objects.order_by("-created_at")

    def lastmod(self, post):
        return post.last_modified


class CategorySitemap(HttpsSitemap):
    changefreq = "weekly"
    priority = 0.5

    def items(self):
        return Category.objects.order_by("name")

    def location(self, category):
        return reverse("blog_category", args=[category.name])


class StaticViewSitemap(HttpsSitemap):
    changefreq = "monthly"
    priority = 0.6

    def items(self):
        return ["blog_index", "about", "contribute"]

    def location(self, name):
        return reverse(name)
