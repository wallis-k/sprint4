from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Count
from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from django.views.decorators.http import require_http_methods

from .forms import PostForm, CommentForm, UserRegistrationForm, UserEditForm
from .models import Post, Category, Comment

User = get_user_model()


def index(request):
    post_list = Post.objects.select_related(
        'category', 'location', 'author'
    ).filter(
        is_published=True,
        pub_date__lte=timezone.now(),
        category__is_published=True
    ).annotate(
        comment_count=Count('comments')
    ).order_by('-pub_date')
    
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'blog/index.html', {'page_obj': page_obj})


def post_detail(request, id):
    post = get_object_or_404(
        Post.objects.select_related('category', 'location', 'author'),
        pk=id
    )
    
    # Проверка доступа для автора
    is_author = request.user == post.author
    
    # Для неавторов показываем только опубликованные посты
    if not is_author:
        if (not post.is_published or 
            post.pub_date > timezone.now() or
            (post.category and not post.category.is_published)):
            return redirect('blog:index')
    
    comments = post.comments.all().order_by('created_at')
    comment_form = CommentForm()
    
    context = {
        'post': post,
        'comments': comments,
        'form': comment_form,
    }
    return render(request, 'blog/detail.html', context)


def category_posts(request, category_slug):
    category = get_object_or_404(
        Category,
        slug=category_slug,
        is_published=True
    )
    post_list = category.posts.select_related(
        'category', 'location', 'author'
    ).filter(
        is_published=True,
        pub_date__lte=timezone.now()
    ).annotate(
        comment_count=Count('comments')
    ).order_by('-pub_date')
    
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'category': category,
        'page_obj': page_obj
    }
    return render(request, 'blog/category.html', context)


@login_required
def create_post(request):
    form = PostForm(request.POST or None, files=request.FILES or None)
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect('blog:profile', username=request.user.username)
    return render(request, 'blog/create.html', {'form': form})


@login_required
def edit_post(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    
    if post.author != request.user:
        return redirect('blog:post_detail', id=post_id)
    
    form = PostForm(request.POST or None, files=request.FILES or None, instance=post)
    if form.is_valid():
        form.save()
        return redirect('blog:post_detail', id=post_id)
    return render(request, 'blog/create.html', {'form': form})


@login_required
@require_http_methods(['GET', 'POST'])
def delete_post(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    
    if post.author != request.user:
        return redirect('blog:post_detail', id=post_id)
    
    if request.method == 'POST':
        post.delete()
        return redirect('blog:profile', username=request.user.username)
    
    form = PostForm(instance=post)
    return render(request, 'blog/create.html', {'form': form})


def profile(request, username):
    profile_user = get_object_or_404(User, username=username)
    
    # Автор видит все свои посты, включая отложенные и снятые с публикации
    if request.user == profile_user:
        post_list = profile_user.posts.select_related(
            'category', 'location', 'author'
        ).annotate(
            comment_count=Count('comments')
        ).order_by('-pub_date')
    else:
        # Остальные видят только опубликованные
        post_list = profile_user.posts.select_related(
            'category', 'location', 'author'
        ).filter(
            is_published=True,
            pub_date__lte=timezone.now(),
            category__is_published=True
        ).annotate(
            comment_count=Count('comments')
        ).order_by('-pub_date')
    
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'profile': profile_user,
        'page_obj': page_obj,
    }
    return render(request, 'blog/profile.html', context)


@login_required
def edit_profile(request):
    if request.method == 'POST':
        form = UserEditForm(request.POST, instance=request.user)
        if form.is_valid():
            user = form.save()
            # Обновляем пользователя в сессии после изменения username
            from django.contrib.auth import update_session_auth_hash
            update_session_auth_hash(request, user)
            from django.contrib import messages
            messages.success(request, 'Профиль успешно обновлен!')
            return redirect('blog:profile', username=user.username)
    else:
        form = UserEditForm(instance=request.user)
    return render(request, 'blog/user.html', {'form': form})


def registration(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = UserRegistrationForm()
    return render(request, 'registration/registration_form.html', {'form': form})


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    form = CommentForm(request.POST)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.post = post
        comment.author = request.user
        comment.save()
    return redirect('blog:post_detail', id=post_id)


@login_required
def edit_comment(request, post_id, comment_id):
    comment = get_object_or_404(Comment, pk=comment_id, post_id=post_id)
    
    if comment.author != request.user:
        return redirect('blog:post_detail', id=post_id)
    
    if request.method == 'POST':
        form = CommentForm(request.POST, instance=comment)
        if form.is_valid():
            form.save()
            return redirect('blog:post_detail', id=post_id)
    else:
        form = CommentForm(instance=comment)
    
    return render(request, 'blog/comment.html', {'form': form, 'comment': comment})


@login_required
@require_http_methods(['GET', 'POST'])
def delete_comment(request, post_id, comment_id):
    comment = get_object_or_404(Comment, pk=comment_id, post_id=post_id)
    
    if comment.author != request.user:
        return redirect('blog:post_detail', id=post_id)
    
    if request.method == 'POST':
        comment.delete()
        return redirect('blog:post_detail', id=post_id)
    
    return render(request, 'blog/comment.html', {'comment': comment})
