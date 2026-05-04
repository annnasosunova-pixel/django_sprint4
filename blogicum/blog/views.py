from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.core.paginator import Paginator
from django.utils import timezone
from django.http import Http404  
from .models import Post, Category, Comment
from .forms import PostForm, CommentForm

User = get_user_model()


def post_detail(request, id):
    template = 'blog/detail.html'
    post = get_object_or_404(Post, id=id)
    
    if request.user != post.author:
        current_datetime = timezone.now()  
        if not (post.is_published and 
                post.category.is_published and 
                post.pub_date <= current_datetime):
            raise Http404("Пост не найден")
    
    comment_form = CommentForm()
    
    context = {
        'post': post,
        'comment_form': comment_form,
        'comments': post.comments.all(),
    }
    return render(request, template, context)



def index(request):
    template = 'blog/index.html'
    current_datetime = timezone.now()  
    post_list = Post.objects.filter(
        pub_date__lte=current_datetime,
        is_published=True,
        category__is_published=True
    ).order_by('-pub_date')
    
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {'page_obj': page_obj}
    return render(request, template, context)

def category_posts(request, category_slug):
    template = 'blog/category.html'
    current_datetime = timezone.now()    
    category = get_object_or_404(
        Category,
        slug=category_slug,
        is_published=True
    )
    
    post_list = category.posts.filter(
        pub_date__lte=current_datetime,
        is_published=True
    ).order_by('-pub_date')
    
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'category': category,
        'page_obj': page_obj,
    }
    return render(request, template, context)


def profile_view(request, username):
    """Страница профиля пользователя"""
    author = get_object_or_404(User, username=username)
    
    if request.user == author:
        posts = author.posts.all()
    else:
        posts = author.posts.filter(
            is_published=True,
            pub_date__lte=timezone.now(),
            category__is_published=True
        )
    
    posts = posts.order_by('-pub_date')
    
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'profile': author, 
        'page_obj': page_obj,
    }
    return render(request, 'blog/profile.html', context)


@login_required
def profile_edit(request, username):
    """Редактирование профиля"""
    if request.user.username != username:
        return redirect('blog:profile', username=username)
    
    from .forms import UserChangeForm  
    
    if request.method == 'POST':
        form = UserChangeForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('blog:profile', username=username)
    else:
        form = UserChangeForm(instance=request.user)
    
    context = {'form': form}
    return render(request, 'blog/user.html', context)


@login_required
def create_post(request):
    """Создание нового поста"""
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect('blog:profile', username=request.user.username)
    else:
        form = PostForm()
    
    return render(request, 'blog/create.html', {'form': form})


@login_required
def edit_post(request, post_id):
    """Редактирование поста"""
    post = get_object_or_404(Post, id=post_id)
    
    if request.user != post.author:
        return redirect('blog:post_detail', id=post_id)
    
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            form.save()
            return redirect('blog:post_detail', id=post_id)
    else:
        form = PostForm(instance=post)
    
    return render(request, 'blog/create.html', {'form': form, 'post': post})


@login_required
def delete_post(request, post_id):
    """Удаление поста"""
    post = get_object_or_404(Post, id=post_id)
    
    if request.user != post.author:
        return redirect('blog:post_detail', id=post_id)
    
    if request.method == 'POST':
        post.delete()
        return redirect('blog:profile', username=request.user.username)
    
    return render(request, 'blog/create.html', {'form': post})


@login_required
def add_comment(request, post_id):
    """Добавление комментария"""
    post = get_object_or_404(Post, id=post_id)
    form = CommentForm(request.POST or None)
    
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    
    return redirect('blog:post_detail', id=post_id)


@login_required
def edit_comment(request, post_id, comment_id):
    """Редактирование комментария"""
    comment = get_object_or_404(Comment, id=comment_id, post_id=post_id)
    
    if request.user != comment.author:
        return redirect('blog:post_detail', id=post_id)
    
    if request.method == 'POST':
        form = CommentForm(request.POST, instance=comment)
        if form.is_valid():
            form.save()
            return redirect('blog:post_detail', id=post_id)
    else:
        form = CommentForm(instance=comment)
    
    context = {
        'form': form, 
        'comment': comment,
        'post_id': post_id,  
    }
    return render(request, 'blog/comment.html', context)


@login_required
def delete_comment(request, post_id, comment_id):
    """Удаление комментария"""
    comment = get_object_or_404(Comment, id=comment_id, post_id=post_id)
    
    if request.user != comment.author:
        return redirect('blog:post_detail', id=post_id)
    
    if request.method == 'POST':
        comment.delete()
        return redirect('blog:post_detail', id=post_id)
    
    context = {
        'comment': comment,
        'post_id': post_id, 
    }
    return render(request, 'blog/comment.html', context)