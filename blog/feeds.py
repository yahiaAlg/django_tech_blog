import markdown
from django.contrib.syndication.views import Feed
from django.urls import reverse_lazy
from django.template.defaultfilters import truncatewords_html
from .models import Post


class LatestPostsFeed(Feed):
    title = "System Symphosium News"
    link = reverse_lazy("blog:post_list")
    description = "The latest news and updates from System Symphosium, focusing on Linux administration, ecommerce development and Ubuntu servers."

    def items(self):
        return Post.published.all()[:3]

    def item_title(self, item: Post):
        return item.title

    def item_description(self, item: Post):
        return truncatewords_html(markdown.markdown(item.body), 30)

    def item_pubdate(self, item: Post):
        return item.publish
