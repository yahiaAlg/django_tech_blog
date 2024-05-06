from django import template
from django.utils.safestring import mark_safe
from markdown import markdown
from ..models import Post
from django.db.models import Count
from taggit.models import Tag


register = template.Library()


@register.simple_tag()
def total_posts():
    return Post.published.count()


@register.simple_tag()
def get_most_commented(count=3):
    return Post.published.annotate(comments_count=Count("comments")).order_by(
        "-comments_count"
    )[:count]


@register.inclusion_tag("blog/partials/sidebar_listings.html")
def sidebar_listings(count=2):
    recent_posts = Post.published.order_by("-publish")[:count]
    tags = Tag.objects.all()
    return {"recent_posts": recent_posts, "tags": tags}


@register.inclusion_tag("blog/partials/searchbar.html")
def searchbar(search_form=None):
    from ..forms import SearchForm

    return {
        "search_form": search_form if search_form else SearchForm(),
    }


@register.filter(name="format_markdown")
def markdown_format(value):
    return mark_safe(markdown(value))
