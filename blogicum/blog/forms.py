from django import forms
from django.contrib.auth import get_user_model
from .models import Post, Comment

User = get_user_model()


class UserChangeForm(forms.ModelForm):
    """Форма для редактирования профиля пользователя"""
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email')


class PostForm(forms.ModelForm):
    """Форма для создания и редактирования поста"""
    class Meta:
        model = Post
        fields = ('title', 'text', 'pub_date', 'location', 'category', 'image', 'is_published')  
        widgets = {
            'pub_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }


class CommentForm(forms.ModelForm):
    """Форма для комментариев"""
    class Meta:
        model = Comment
        fields = ('text',)