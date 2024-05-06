from django_elasticsearch_dsl import Document, fields
from django_elasticsearch_dsl.registries import registry
from .models import Post


@registry.register_document
class PostDocument(Document):
    author = fields.ObjectField(
        properties={
            "username": fields.TextField(),
            "email": fields.TextField(),
        }
    )

    class Index:
        name = "posts"
        settings = {"number_of_shards": 1, "number_of_replicas": 0}

    class Django:
        model = Post
        fields = ["title", "body"]

    def get_instances_from_related(self, related_instance):
        if isinstance(related_instance, Post.author.field.related_model): # type: ignore
            return related_instance.post_set.all()
