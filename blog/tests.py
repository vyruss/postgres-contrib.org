import json
import re

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from blog.models import Category, Contribution, Post

SUBMISSION = {
    "body": "Ada Lovelace organised **twelve** Brighton meetups, and found a speaker for every one.",
    "submitter": "Ada Lovelace <ada@example.org>",
}


class ContributionFormTests(TestCase):
    def test_guest_sees_the_form(self):
        response = self.client.get(reverse("contribute"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "<form")

    def test_guest_submission_is_stored_unreviewed(self):
        response = self.client.post(reverse("contribute"), SUBMISSION)
        self.assertRedirects(response, reverse("contribute_thanks"))
        contribution = Contribution.objects.get()
        self.assertEqual(contribution.body, SUBMISSION["body"])
        self.assertFalse(contribution.reviewed)
        self.assertIsNone(contribution.reviewed_at)

    def test_submitter_is_optional(self):
        self.client.post(reverse("contribute"), dict(SUBMISSION, submitter=""))
        self.assertEqual(Contribution.objects.count(), 1)

    def test_empty_submission_is_rejected(self):
        response = self.client.post(reverse("contribute"), dict(SUBMISSION, body=""))
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Contribution.objects.exists())

    def test_filled_spam_trap_stores_nothing(self):
        response = self.client.post(reverse("contribute"), dict(SUBMISSION, website="http://spam.example"))
        self.assertRedirects(response, reverse("contribute_thanks"))
        self.assertFalse(Contribution.objects.exists())


class ContributionReviewTests(TestCase):
    def setUp(self):
        self.contribution = Contribution.objects.create(**SUBMISSION)

    def log_in_as_staff(self):
        User.objects.create_superuser("editor", "editor@example.org", "s3cret-for-tests")
        self.client.login(username="editor", password="s3cret-for-tests")

    def test_marking_reviewed_records_the_time(self):
        self.contribution.reviewed = True
        self.contribution.save()
        self.assertIsNotNone(self.contribution.reviewed_at)

    def test_unmarking_clears_the_time(self):
        self.contribution.reviewed = True
        self.contribution.save()
        self.contribution.reviewed = False
        self.contribution.save()
        self.assertIsNone(self.contribution.reviewed_at)

    def test_dashboard_lists_submissions_for_staff(self):
        self.log_in_as_staff()
        response = self.client.get("/admin/blog/contribution/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Brighton")

    def test_dashboard_is_closed_to_guests(self):
        response = self.client.get("/admin/blog/contribution/")
        self.assertEqual(response.status_code, 302)

    def test_review_page_offers_the_submitted_text_for_copying(self):
        self.log_in_as_staff()
        response = self.client.get(f"/admin/blog/contribution/{self.contribution.pk}/change/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "twelve")

    def test_bulk_action_marks_submissions_reviewed(self):
        self.log_in_as_staff()
        self.client.post("/admin/blog/contribution/", {
            "action": "mark_reviewed",
            "index": 0,
            "_selected_action": [self.contribution.pk],
        })
        self.contribution.refresh_from_db()
        self.assertTrue(self.contribution.reviewed)
        self.assertIsNotNone(self.contribution.reviewed_at)


class SeoTests(TestCase):
    def setUp(self):
        author = User.objects.create_user("ada", first_name="Ada", last_name="Lovelace")
        self.post = Post.objects.create(
            title="A talk in Brighton",
            body="Ada spoke about **indexes**.",
            author=author,
            category=Category.objects.create(name="news"),
        )

    def title_of(self, url):
        html = self.client.get(url).content.decode()
        return re.search(r"<title>(.*?)</title>", html).group(1)

    def test_every_page_has_its_own_title(self):
        urls = ["/", self.post.get_absolute_url(), "/about/", "/contribute/"]
        titles = [self.title_of(url) for url in urls]
        self.assertEqual(len(set(titles)), len(urls))
        self.assertIn("A talk in Brighton", self.title_of(self.post.get_absolute_url()))

    def test_canonical_is_absolute_and_points_at_the_page_itself(self):
        path = self.post.get_absolute_url()
        response = self.client.get(path)
        self.assertContains(response, f'<link rel="canonical" href="https://postgres-contrib.org{path}">')

    def test_paginated_listing_canonicals_to_its_own_page(self):
        response = self.client.get("/", {"page": 1})
        self.assertContains(response, '<link rel="canonical" href="https://postgres-contrib.org/">')

    def test_post_page_carries_structured_data(self):
        path = self.post.get_absolute_url()
        html = self.client.get(path).content.decode()
        block = re.search(r'<script type="application/ld\+json">(.*?)</script>', html, re.S).group(1)
        data = json.loads(block)
        self.assertEqual(data["headline"], "A talk in Brighton")
        self.assertEqual(data["author"]["name"], "Ada Lovelace")
        self.assertEqual(data["mainEntityOfPage"], f"https://postgres-contrib.org{path}")

    def test_sitemap_lists_posts_and_pages(self):
        response = self.client.get("/sitemap.xml")
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "<loc>http://")
        self.assertContains(response, self.post.get_absolute_url())
        self.assertContains(response, "/about/")
        self.assertContains(response, "/contribute/")

    def test_robots_points_at_the_sitemap(self):
        response = self.client.get("/robots.txt")
        self.assertEqual(response["Content-Type"], "text/plain")
        self.assertContains(response, "Sitemap: https://testserver/sitemap.xml")
        self.assertContains(response, "Disallow: /admin/")

    def test_thanks_page_is_not_indexed(self):
        response = self.client.get(reverse("contribute_thanks"))
        self.assertContains(response, '<meta name="robots" content="noindex">')


class NavigationTests(TestCase):
    def header_of(self, url):
        html = self.client.get(url).content.decode()
        return html[html.index("<header>"):html.index("</header>")]

    def test_navigation_sits_in_the_header(self):
        header = self.header_of("/")
        for link in ["/about/", "/contribute/", "/rss/", "https://postgresql.org/", "https://postgresql.life/"]:
            self.assertIn(link, header)

    def test_footer_no_longer_carries_the_links(self):
        html = self.client.get("/").content.decode()
        self.assertNotIn("/about/", html[html.index("<footer>"):])

    def test_hamburger_toggle_is_present_for_mobile(self):
        header = self.header_of("/")
        self.assertIn('id="nav-toggle"', header)
        self.assertIn('for="nav-toggle"', header)
