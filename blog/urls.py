from django.contrib.sitemaps.views import sitemap
from django.urls import path
from . import views
from blog.feeds import PostFeed, AuthorPostFeed
from blog.sitemaps import CategorySitemap, PostSitemap, StaticViewSitemap

sitemaps = {
    "posts": PostSitemap(),
    "categories": CategorySitemap(),
    "pages": StaticViewSitemap(),
}

urlpatterns = [
    path("", views.blog_index, name="blog_index"),
    path("post/<int:pk>/", views.blog_detail, name="blog_detail"),
    path("category/<category>/", views.blog_category, name="blog_category"),
    path("about/", views.about, name="about"),
    path("contribute/", views.contribute, name="contribute"),
    path("contribute/thanks/", views.contribute_thanks, name="contribute_thanks"),
    path("rss/", PostFeed()),
#    path("rss/<int:author_id>/", AuthorPostFeed()),
    path("rss/<str:author_name>/", AuthorPostFeed()),
    path("sitemap.xml", sitemap, {"sitemaps": sitemaps}, name="django.contrib.sitemaps.views.sitemap"),
    path("robots.txt", views.robots_txt, name="robots_txt"),
]
