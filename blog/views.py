from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from .models import Post
from .forms import PostForm
from django.shortcuts import redirect
import json
from watson_developer_cloud import ToneAnalyzerV3
from watson_developer_cloud import LanguageTranslatorV2 as LanguageTranslator


def post_list(request):
    posts = Post.objects.filter(published_date__lte=timezone.now()).order_by('published_date')
    tone_analyzer = ToneAnalyzerV3(
        username='0096ff27-be5a-4135-9cc6-fad697ce3897',
        password='ONS18fjX0Es6',
        version='2018-04-02 ')

    language_translator = LanguageTranslator(
        username='b4cd42f1-ebbb-48d2-8053-254e729804b3',
        password='8EBLgw2dgpmL')

    # print(json.dumps(translation, indent=2, ensure_ascii=False))

    for post in posts:
        posting = post.text
        toneObj= json.dumps(tone_analyzer.tone(tone_input=posting,
                                   content_type="text/plain"), indent=2)
        post.toneObj2 = json.loads(toneObj)
        print (post.toneObj2)
        #The IBM WATSON RESPONSE HAS BEEN UPDATED OVER TIME SO THE code has changed since the tutorial was written
        try:
            post.angerScore = post.toneObj2['document_tone']['tones'][0]['score']
            post.disgustScore = post.toneObj2['document_tone']['tones'][1]['score']
            post.fearScore = post.toneObj2['document_tone']['tones'][2]['score']
            # post.joyScore = post.toneObj2['sentence_tone']['tones'][4]['score']
            # post.sadScore = post.toneObj2['document_tone']['tones'][4]['score']
        except:
            pass
        translation = language_translator.translate(
            text=post.text,
            source='en',
            target='fr')
        obj= json.dumps(translation, indent=2, ensure_ascii=False)
        post.obj2 = json.loads(obj)
        print (post.obj2)
        post.objtxt = post.obj2['translations'][0]['translation']
        post.objword = post.obj2['word_count']
        post.objchar = post.obj2['character_count']


    return render(request, 'blog/post_list.html', {'posts': posts})


def post_detail(request, pk):
    post = get_object_or_404(Post, pk=pk)
    # Post.objects.get(pk=pk)
    return render(request, 'blog/post_detail.html', {'post': post})


def post_new(request):
    if request.method == "POST":
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.published_date = timezone.now()
            post.save()
            return redirect('post_detail', pk=post.pk)
    else:
        form = PostForm()
    return render(request, 'blog/post_edit.html', {'form': form})


def post_edit(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if request.method == "POST":
        form = PostForm(request.POST, instance=post)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.published_date = timezone.now()
            post.save()
            return redirect('post_detail', pk=post.pk)
    else:
        form = PostForm(instance=post)
    return render(request, 'blog/post_edit.html', {'form': form})
