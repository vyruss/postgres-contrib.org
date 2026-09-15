from django import forms
from blog.models import Contribution


class ContributionForm(forms.ModelForm):
    # Spam trap: people never see this field, so anything in it came from a bot.
    website = forms.CharField(required=False, widget=forms.HiddenInput())

    class Meta:
        model = Contribution
        fields = ["body", "submitter"]
        labels = {
            "body": "The contribution",
            "submitter": "Your name and email address",
        }
        help_texts = {
            "body": "Plain text is fine and Markdown is better. Names, dates and links are all welcome.",
            "submitter": "This is optional, and we will only use it if we need to ask you about your submission.",
        }
        widgets = {
            "body": forms.Textarea(attrs={"rows": 16}),
            "submitter": forms.TextInput(),
        }

    def is_spam(self):
        return bool(self.cleaned_data.get("website"))
