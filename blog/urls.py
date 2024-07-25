from django.urls import path
from . import views
from blog.feeds import PostFeed, AuthorPostFeed

urlpatterns = [
    path("", views.blog_index, name="blog_index"),
    path("post/<int:pk>/", views.blog_detail, name="blog_detail"),
    path("category/<category>/", views.blog_category, name="blog_category"),
    path("about/", views.about, name="about"),
    path("rss/", PostFeed()),
#    path("rss/<int:author_id>/", AuthorPostFeed()),
    path("rss/<str:author_name>/", AuthorPostFeed()),
]
