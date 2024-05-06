from django import forms
from .models import Comment


class EmailForm(forms.Form):
    subject = forms.CharField(max_length=100)
    to = forms.EmailField(label="Your recepient address")
    comment = forms.CharField(required=False, label="Additional comments")


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ["author", "email", "body"]


class SearchForm(forms.Form):
    query = forms.CharField(max_length=250)
