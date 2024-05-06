from django.urls import path
from django.contrib.auth import views as auth_views
from django.contrib.sitemaps.views import sitemap
from .sitemaps import PostSitemap
from . import views
from .feeds import LatestPostsFeed

app_name = "blog"
sitemaps = {"post": PostSitemap}


urlpatterns = [
    path("", views.post_list, name="post_list"),
    path("search", views.search, name="search"),
    path("tag/<slug:tag_slug>/", views.post_list, name="post_list_by_tag"),
    path(
        "sitemap.xml",
        sitemap,
        {"sitemaps": sitemaps},
        name="django.contrib.sitemaps.views.sitemap",
    ),
    path("feed/", LatestPostsFeed(), name="post_feed"),
    # path("", views.PostListView.as_view(), name="post_list"),
    path(
        "<int:year>/<int:month>/<int:day>/<slug:slug>/",
        views.post_detail,
        name="post_detail",
    ),
    path("<int:pk>/share/", views.share_post, name="post_share"),
    path("<int:pk>/comment/", views.post_comment, name="post_comment"),

]
