from django.contrib.syndication.views import Feed
from django.utils.feedgenerator import Rss201rev2Feed
from django.urls import reverse
from django.contrib.auth.models import User
from .models import Post
import markdown


class CorrectMimeTypeFeed(Rss201rev2Feed):
    content_type = 'application/xml; charset=utf-8'


class AuthorPostFeed(Feed):
    feed_type = CorrectMimeTypeFeed
    title = "postgres-contrib.org | PostgreSQL Contributions"
    link = "/"
    description = "Weekly PostgreSQL contribution news"

    def get_object(self, request, author_name):
        fname = author_name.split('-')[0]
        lname = author_name.split('-')[1]
        return User.objects.filter(first_name__iexact=fname, last_name__iexact=lname)[0]

    def items(self, obj):
        return Post.objects.filter(author=obj).order_by("-created_at")[:10]

    def item_title(self, item):
        return item.title

    def author_name(self, obj):
        return f"{obj.first_name} {obj.last_name}"

    def item_description(self, item):
        md = markdown.Markdown(extensions=["fenced_code"])
        description = md.convert(item.body)
        return description

    def item_pubdate(self, item):
        return item.created_at

    # item_link is only needed if item has no get_absolute_url method.
    def item_link(self, item):
        return reverse("blog_detail", args=[item.pk])


class PostFeed(Feed):
    feed_type = CorrectMimeTypeFeed
    title = "postgres-contrib.org | PostgreSQL Contributions"
    link = "/"
    description = "Weekly PostgreSQL contribution news"

    def items(self):
       return Post.objects.order_by("-created_at")[:10]

    def item_title(self, item):
        return item.title

    def author_name(self, obj):
        return "postgres-contrib.org team"

    def item_description(self, item):
        md = markdown.Markdown(extensions=["fenced_code"])
        description = md.convert(item.body)
        return description

    def item_pubdate(self, item):
        return item.created_at

    # item_link is only needed if item has no get_absolute_url method.
    def item_link(self, item):
        return reverse("blog_detail", args=[item.pk])

