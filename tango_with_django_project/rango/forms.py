from django import forms
from rango.models import Page, Category, UserProfile
from django.contrib.auth.models import User


class CategoryForm(forms.ModelForm):
    name = forms.CharField(max_length=128, help_text="Please enter the category name.")
    views = forms.IntegerField(widget=forms.HiddenInput, initial=0)  # Hiding these fields from the user; we change them
    likes = forms.IntegerField(widget=forms.HiddenInput, initial=0)
    slug = forms.CharField(widget=forms.HiddenInput, required=False)

    # Inline class to provide additional information for the form
    class Meta:
        # Provide association between this ModelForm and a model
        model = Category
        fields = ('name', )


class PageForm(forms.ModelForm):
    title = forms.CharField(max_length=128, help_text="Please enter the title of the page.")
    # http://stackoverflow.com/questions/21923838/django-1-6-automatically-remove-or-add-http-from-urlfield-from-form-data
    # needed 'widget=forms.widgets.TextInput'
    url = forms.URLField(max_length=200, help_text="Please enter the URL of the page.", widget=forms.widgets.TextInput)
    views = forms.IntegerField(widget=forms.HiddenInput, initial=0)

    # Handle malformed urls; chapter 8.2.7
    def clean(self):
        cleaned_data = self.cleaned_data
        url = cleaned_data.get('url')

        # If URL is not empty or does not start with http://, prepend http://
        if url and not url.startswith('http://'):
            url = 'http://' + url
            cleaned_data['url'] = url

        return cleaned_data

    # Another inline class for additional information
    class Meta:
        # Association between model and form
        model = Page

        # We can decide what fields we want to incldue in the form;
        # In this case -> hide foreign key; some fields my allow null values so do not include them
        # We can either exclude the category field
        exclude = ('category',)
        # or specify the fields to include (i.e. not include the category field)
        # fields = ('title', 'url', 'views')


class UserForm(forms.ModelForm):
    # Need this since the regular password field in the django User model will not hide
    # the password; need to override it with widget=forms.PasswordInput
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ('username', 'email', 'password')


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ('website', 'picture')


# This is needed since this form does not change the password
class EditUserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('username', 'email')
