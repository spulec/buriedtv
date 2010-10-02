from django import forms
from django.forms import Form, ModelForm, ValidationError
from django.forms.models import BaseInlineFormSet
from django.contrib.auth.models import User
from demTvDjango.demTV.models import UserProfile, Show, TimeSlot

class ContactForm(Form):
    your_email = forms.EmailField("Your email(so we can respond)")
    subject = forms.CharField(max_length=100)
    message = forms.CharField(widget=forms.Textarea)


class UserForm(ModelForm):
    class Meta:
        model = User
        fields = ('first_name', 'last_name')

class UserProfileForm(ModelForm):
    class Meta:
        model = UserProfile
        fields = ('bio', 'display_email', 'email_lineup')

class BaseShowFormSet(BaseInlineFormSet):
    def __init__(self, *args, **kwargs):
        super(BaseShowFormSet, self).__init__(*args, **kwargs)
        # Only display enabled timeslots
        for form in self.forms:        
            form.fields['time_slot'].queryset = TimeSlot.objects.filter(enabled=True).order_by('day', 'military_time')
        self.user = None

    def clean(self):
        if any(self.errors):
            return
        for form in self.forms:
            changedShow = form.save(commit=False)
            name = changedShow.name
            if not name:
                continue

            # Remove whitespace
            name = name.replace(' ', "")

            if not name.isalnum():
                raise ValidationError, "Show names must only be letter, numbers, and spaces."

