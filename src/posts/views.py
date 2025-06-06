from django.shortcuts import render
from .models import Post, Photo
from django.http import JsonResponse, HttpResponse
from .forms import PostForm
from profiles.models import Profile
from .utils import action_permission
from django.contrib.auth.decorators import login_required
# Create your views here.

@login_required
def post_list_and_create(request):
    form = PostForm(request.POST or None)
    # qs = Post.objects.all()

# Author is using there "request.js_ajax()" to check for AJAX requests. 
# but this method is used in the older version of the Django.
# while i have installed the latest version.
# So i am replaced it with "request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest'".
# this is the source where i find it: Django >= 3.1 and is_ajax. (n.d.). Stack Overflow. https://stackoverflow.com/questions/63629935/django-3-1-and-is-ajax  
    if request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':
        if form.is_valid():
            author = Profile.objects.get(user=request.user)
            instance = form.save(commit=False)
            instance.author = author
            instance.save()
            return JsonResponse({
                'title': instance.title,
                'body': instance.body,
                'author': instance.author.user.username,
                'id': instance.id,
            })
            
    context = {
        'form': form,
    }

    return render(request, 'posts/main.html', context)

@login_required
def post_detail(request, pk):
    obj = Post.objects.get(pk=pk)
    form = PostForm()

    context = {
        'obj': obj,
        'form': form,
    }

    return render(request, 'posts/detail.html', context)

@login_required
def load_post_data_view(request, num_posts):
    if request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':
        visible = 3
        upper = num_posts
        lower = upper - visible 
        size = Post.objects.all().count()

        qs = Post.objects.all()
        data = []
        for obj in qs:
            item = {
                'id': obj.id,
                'title': obj.title,
                'body': obj.body,
                'liked': True if request.user in obj.liked.all() else False,
                'count': obj.like_count,
                'author': obj.author.user.username
            }
            data.append(item)
        return JsonResponse({'data':data[lower:upper], 'size': size})

@login_required
def post_detail_data_view(request, pk):
    if request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':
        obj = Post.objects.get(pk=pk)
        data = {
            'id': obj.id,
            'title': obj.title,
            'body': obj.body,
            'author': obj.author.user.username,
            'avatar': obj.author.avatar.url,
            'logged_in': request.user.username,
        }
        return JsonResponse({'data': data})
    return redirect('posts:main-board')

@login_required
def like_unlike_post(request):
    if request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':
        pk = request.POST.get('pk')
        obj = Post.objects.get(pk=pk)
        if request.user in obj.liked.all():
            liked = False
            obj.liked.remove(request.user)
        else:
            liked = True
            obj.liked.add(request.user)
        return JsonResponse({'liked': liked, 'count': obj.like_count})
    return redirect('posts:main-board')

@login_required
@action_permission
def update_post(request, pk):
    obj = Post.objects.get(pk=pk)
    if request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':
        new_title = request.POST.get('title')
        new_body = request.POST.get('body')
        obj.title = new_title
        obj.body = new_body
        obj.save()
        return JsonResponse({
            'title': new_title,
            'body': new_body,
        })
    return redirect('posts:main-board')

@login_required
@action_permission
def delete_post(request, pk):
    obj = Post.objects.get(pk=pk)
    if request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':
        obj.delete()
        return JsonResponse({'msg':'some message'})
    # return JsonResponse({'msg': 'access denied - ajax only'})
    return redirect('posts:main-board')

@login_required
def image_upload_view(request):
    # print(request.FILES)
    if request.method == 'POST':
        img = request.FILES.get('file')
        new_post_id = request.POST.get('new_post_id')
        post = Post.objects.get(id=new_post_id)
        Photo.objects.create(image=img, post=post)
    return HttpResponse()
