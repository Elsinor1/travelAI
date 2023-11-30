from django import forms

class NewPostForm(forms.Form):
    text = forms.CharField(max_length=400, label="Post text", widget=forms.Textarea(attrs={'rows': 3}))
