from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.utils.text import Truncator
from blog.models import Post
import markdown

POSTS_PER_PAGE = 20
TRUNCATE_CHARS = 500
MD_EXTENSIONS = ["fenced_code"]


def _render_md(text):
    return markdown.markdown(text, extensions=MD_EXTENSIONS)


def _teaser(post):
    full = _render_md(post.body)
    link = f'<a href="{reverse("blog_detail", args=[post.pk])}" class="read-more"><strong>&hellip;</strong></a>'
    return Truncator(full).chars(TRUNCATE_CHARS, html=True, truncate=link)


def _paginated_context(request, posts_qs, **extra):
    paginator = Paginator(posts_qs.order_by("-created_at"), POSTS_PER_PAGE)
    page_obj = paginator.get_page(request.GET.get("page"))
    for post in page_obj.object_list:
        post.body = _teaser(post)
    return {"posts": page_obj.object_list, "page_obj": page_obj, **extra}


def blog_index(request):
    return render(request, "blog/index.html",
                  _paginated_context(request, Post.objects.all()))


def blog_category(request, category):
    posts = Post.objects.filter(category__name__contains=category)
    return render(request, "blog/category.html",
                  _paginated_context(request, posts, category=category))


def blog_detail(request, pk):
    post = get_object_or_404(Post, pk=pk)
    post.body = _render_md(post.body)
    return render(request, "blog/detail.html", {"post": post})


def about(request):
    return render(request, "blog/about.html")
