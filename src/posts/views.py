from django.shortcuts import render
from .models import Post
from django.http import JsonResponse
from .forms import PostForm
from profiles.models import Profile
# Create your views here.

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


def hello_world_view(request):
    return JsonResponse({'text': 'hello world x2'})