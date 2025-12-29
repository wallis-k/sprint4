from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from .models import Post, Comment

User = get_user_model()


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('title', 'text', 'pub_date', 'location', 'category', 'image')
        widgets = {
            'pub_date': forms.DateTimeInput(
                format='%Y-%m-%dT%H:%M',
                attrs={'type': 'datetime-local'}
            ),
        }


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('text',)


class UserRegistrationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email')


class UserEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'username', 'email')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Делаем поля обязательными
        self.fields['username'].required = True
        self.fields['email'].required = True

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if (username and User.objects.filter(username=username)
                .exclude(pk=self.instance.pk).exists()):
            raise forms.ValidationError(
                'Пользователь с таким именем уже существует.'
            )
        return username

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if (email and User.objects.filter(email=email)
                .exclude(pk=self.instance.pk).exists()):
            raise forms.ValidationError(
                'Пользователь с таким email уже существует.'
            )
        return email

