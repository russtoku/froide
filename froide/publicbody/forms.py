import floppyforms.__future__ as forms

from django.utils.translation import ugettext_lazy as _


class PublicBodyForm(forms.Form):
    name = forms.CharField(label=_("Name of Public Body"))
    description = forms.CharField(label=_("Short description"),
        widget=forms.Textarea, required=False)
    email = forms.EmailField(widget=forms.EmailInput,
        label=_("Email Address for Freedom of Information Requests"))
    url = forms.URLField(label=_("Homepage URL of Public Body"))
