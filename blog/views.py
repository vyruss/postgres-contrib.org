from django.core.paginator import Paginator
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils.html import strip_tags
from django.utils.text import Truncator
from blog.forms import ContributionForm
from blog.models import Post
import markdown

POSTS_PER_PAGE = 10
TRUNCATE_CHARS = 500
DESCRIPTION_CHARS = 160
MD_EXTENSIONS = ["fenced_code"]
SITE_NAME = "postgres-contrib.org"
INDEX_TITLE = "postgres-contrib.org | Contributions to the PostgreSQL Project"


def _render_md(text):
    return markdown.markdown(text, extensions=MD_EXTENSIONS)


def _teaser(post):
    full = _render_md(post.body)
    link = f'<a href="{reverse("blog_detail", args=[post.pk])}" class="read-more"><strong>&hellip;</strong></a>'
    return Truncator(full).chars(TRUNCATE_CHARS, html=True, truncate=link)


def _summarise(html):
    return Truncator(" ".join(strip_tags(html).split())).chars(DESCRIPTION_CHARS)


def _paginated_context(request, posts_qs, meta_title=INDEX_TITLE, **extra):
    paginator = Paginator(posts_qs.order_by("-created_at"), POSTS_PER_PAGE)
    page_obj = paginator.get_page(request.GET.get("page"))
    for post in page_obj.object_list:
        post.body = _teaser(post)
    if page_obj.number > 1:
        meta_title = f"{meta_title} | page {page_obj.number}"
        meta_path = f"{request.path}?page={page_obj.number}"
    else:
        meta_path = request.path
    return {
        "posts": page_obj.object_list,
        "page_obj": page_obj,
        "meta_title": meta_title,
        "meta_path": meta_path,
        **extra,
    }


def blog_index(request):
    return render(request, "blog/index.html",
                  _paginated_context(request, Post.objects.all()))


def blog_category(request, category):
    posts = Post.objects.filter(category__name__contains=category)
    return render(request, "blog/category.html",
                  _paginated_context(
                      request, posts,
                      meta_title=f"{category} | {SITE_NAME}",
                      meta_description=f"PostgreSQL contributions listed under {category} on {SITE_NAME}.",
                      category=category,
                  ))


def blog_detail(request, pk):
    post = get_object_or_404(Post, pk=pk)
    post.body = _render_md(post.body)
    return render(request, "blog/detail.html", {
        "post": post,
        "meta_title": f"{post.title} | {SITE_NAME}",
        "meta_description": _summarise(post.body),
        "meta_type": "article",
    })


def about(request):
    return render(request, "blog/about.html", {
        "meta_title": f"About | {SITE_NAME}",
        "meta_description": f"{SITE_NAME} is a volunteer website by members of the PostgreSQL community, "
                            "highlighting the contributions that keep the project going.",
    })


def contribute(request):
    if request.method == "POST":
        form = ContributionForm(request.POST)
        if form.is_valid():
            if not form.is_spam():
                form.save()
            return redirect("contribute_thanks")
    else:
        form = ContributionForm()
    return render(request, "blog/contribute.html", {
        "form": form,
        "meta_title": f"Submit a contribution | {SITE_NAME}",
        "meta_description": "Tell us about a contribution to the PostgreSQL project, and we will add it to the list.",
    })


def contribute_thanks(request):
    return render(request, "blog/contribute_thanks.html", {
        "meta_title": f"Thank you | {SITE_NAME}",
    })


def robots_txt(request):
    lines = [
        "User-agent: *",
        "Disallow: /admin/",
        "Disallow: /contribute/thanks/",
        "",
        f"Sitemap: https://{request.get_host()}/sitemap.xml",
    ]
    return HttpResponse("\n".join(lines), content_type="text/plain")
