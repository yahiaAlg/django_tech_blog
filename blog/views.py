from pprint import pprint
from django.http import Http404
from django.views.generic import ListView
from django.shortcuts import redirect, render, get_object_or_404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.mail import send_mail
from django.conf import settings
from django.contrib import messages
from .forms import CommentForm, EmailForm, SearchForm
from .models import Post, Comment
from django.db.models import Count
from taggit.models import Tag
from django.views.decorators.http import require_POST
from django.contrib.postgres.search import (
    SearchVector,
    SearchQuery,
    SearchRank,
    TrigramSimilarity,
)
from django.contrib.auth.decorators import login_required

# Create your views here.
# class PostListView(ListView):
#     queryset = Post.published.all()
#     context_object_name = "posts"
#     paginate_by = 3
#     template_name = "blog/post/list.html"


@login_required
def post_list(request, tag_slug=None):
    pprint(tag_slug)
    tag = None

    post_list = Post.published.all()
    if tag_slug:
        tag = get_object_or_404(Tag, slug=tag_slug)
        post_list = Post.published.filter(tags__in=[tag])
        pprint(tag)
        pprint(post_list)
    paginator = Paginator(post_list, 3)  # type: ignore
    page_number = request.GET.get("page", 1)

    try:
        posts = paginator.get_page(page_number)
    except EmptyPage:
        posts = paginator.get_page(paginator.num_pages)
    except PageNotAnInteger:
        posts = paginator.get_page(1)

    return render(request, "blog/post/list.html", {"posts": posts, "tag": tag})


def post_detail(request, year, month, day, slug):
    # try:
    #     post = Post.published.get(pk=pk)
    # except Post.DoesNotExist:
    #     raise Http404("Post does not exist")

    # post = get_object_or_404(Post, pk=pk, status=Post.Status.PUBLISHED) #not SEO-FRIENDLY
    post = get_object_or_404(
        Post, publish__year=year, publish__month=month, publish__day=day, slug=slug
    )

    post_tags_ids = post.tags.values_list("id", flat=True)
    similar_posts = Post.published.filter(tags__in=post_tags_ids).exclude(id=post.id)  # type: ignore
    similar_posts = similar_posts.annotate(same_tags=Count("tags")).order_by(
        "-same_tags", "-publish"
    )[:3]
    comments = Comment.objects.filter(post=post, active=True).order_by("created")

    pprint(comments)
    pprint(similar_posts)
    form = CommentForm()
    return render(
        request,
        "blog/post/detail.html",
        {
            "post": post,
            "similar_posts": similar_posts,
            "comments": comments,
            "form": form,
        },
    )


def share_post(request, pk):
    post = get_object_or_404(Post, pk=pk, status=Post.Status.PUBLISHED)
    sent = False
    if request.method == "POST":
        form = EmailForm(request.POST)
        if form.is_valid():
            comment = request.POST.get("comment", "")
            if comment:
                subject = '%s recommends you reading "%s"' % (
                    request.user.username,
                    request.POST["subject"],
                )
                message = "%s thinks you might be interested in this:\n\n%s" % (
                    request.user.username,
                    comment,
                )
                send_mail(
                    subject, message, settings.DEFAULT_FROM_EMAIL, [request.POST["to"]]
                )
            else:
                send_mail(subject, comment, settings.DEFAULT_FROM_EMAIL, [request.POST["to"]])  # type: ignore
                return redirect("post_list")
            sent = True
        else:
            messages.error(request, "Incorrect Data")
    else:
        form = EmailForm()
    return render(
        request, "blog/post/share_form.html", {"form": form, "post": post, "sent": sent}
    )


@require_POST
def post_comment(request, pk):
    post = get_object_or_404(Post, pk=pk, status=Post.Status.PUBLISHED)
    comment = None
    form = CommentForm(request.POST)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.post = post
        comment.save()
    return render(
        request,
        "blog/post/comment.html",
        {"form": form, "post": post, "comment": comment},
    )


from django.db.models import Q


def search(request):
    query = None
    results = []
    if "query" in request.GET:
        query = request.GET["query"]
        print("searching for post with : ", query)  # type: ignore
        form = SearchForm(request.GET)
        if form.is_valid():
            query = form.cleaned_data["query"]
            # query_vector = SearchQuery(query)
            # content_vector = SearchVector("title", "body", "author__username")
            # results = Post.published.annotate(
            #     search=content_vector, rank=SearchRank(content_vector, query_vector)
            # ).filter(search=query_vector).order_by("-rank")

            # TRIGRAM SIMILARITY
            # results = Post.published.annotate(
            #     similarity=TrigramSimilarity("body", query)
            # ).filter(similarity__gt=0.1).order_by("-similarity")

            # SEARCH VECTOR
            q_objects = Q()

            # Search in title, body, and author
            for field in ["title", "body", "author__username"]:
                q_objects |= Q(**{f"{field}__icontains": query})

            # Search in tags
            for tag in Post.tags.all():
                if query.lower() in tag.name.lower():
                    q_objects |= Q(tags__name=tag.name)

            for post in Post.published.all():
                for comment in post.comments.all():
                    if query.lower() in comment.body.lower():
                        q_objects |= Q(comments__body=comment.body)
            # Get distinct results
            results = Post.published.filter(q_objects).distinct()

            print("results:", results)
            return render(
                request,
                "blog/post/list.html",
                {"search_form": form, "posts": results, "tag": None},
            )

    return render(request, "blog/post/list.html", {"posts": results, "tag": None})


from django.contrib.postgres.search import TrigramSimilarity
from django.db.models import F
from .documents import PostDocument

# def search(request):
#     query = None
#     results = []
#     if "query" in request.GET:
#         query = request.GET["query"]
#         print("Searching for post with :", query)  # type: ignore
#         form = SearchForm(request.GET)
#         if form.is_valid():
#             query = form.cleaned_data["query"]

#             # TRIGRAM SIMILARITY
#             results = (
#                 Post.published.annotate(
#                     similarity_title=TrigramSimilarity("title", query),
#                     similarity_author=TrigramSimilarity("author__username", query),
#                     similarity_body=TrigramSimilarity("body", query),
#                     total_similarity=F("similarity_title")
#                     + F("similarity_author")
#                     + F("similarity_body"),
#                 )
#                 .filter(total_similarity__gt=0.1)
#                 .order_by("-total_similarity")
#             )

#             #ELASTIC SEARCH
#             # results = PostDocument.search().query("multi_match", query=query, fields=["title", "body", "author"]).to_queryset()
#             print("Results:", results)
#             return render(
#                 request,
#                 "blog/post/list.html",
#                 {"search_form": form, "posts": results, "tag": None},
#             )

#     return render(request, "blog/post/list.html", {"posts": results, "tag": None})
