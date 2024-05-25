from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from . import views
import markdown2
from . import util
import random
from .forms import SearchForm, TitleForm, NewPageForm

# In settings.py I have inserted the path to the following context processor.
# This way, when generating the "random page" link in every page,
# I won't have to copy paste the context every time.
def random_title(request):
    return {'random_title': random.choice(util.list_entries())}


def searchform(request):
    return {'form': SearchForm()}


def index(request):
    if request.method == "GET":
        return render(request, "encyclopedia/index.html", {
            "entries": util.list_entries()
        })
    

# Markdown to HTML conversion
def entry(request, title):
    entry = util.get_entry(title)
    if entry is not None:
        entry = markdown2.markdown(entry)
        return render(request, "encyclopedia/entry.html",{
            "entry":entry,
            "title":title,
        })
    else:
        return render(request, "encyclopedia/error404.html")


def search(request):
    form = SearchForm(request.GET)
    if form.is_valid():
        query = form.cleaned_data['q']
        entry = util.get_entry(query)
        if entry is not None:
            return redirect(views.entry, title=query)
        else:
            entries = util.list_entries()
            results = []
            for item in entries:
                if query.lower() in item.lower():
                    results.append(item)

            return render(request,"encyclopedia/results.html", {
                "query": query,
                "results": results
        })
    else:
        return render(request, "encyclopedia/index.html")


def new_page(request):
    if request.method == "GET":
        return render(request, "encyclopedia/new_page.html",{
            "titleform":TitleForm,
            "newpageform":NewPageForm,
        })
    
    if request.method == "POST":
        titleform = TitleForm(request.POST)
        newpageform = NewPageForm(request.POST)
        if titleform.is_valid() and newpageform.is_valid():
            title = titleform.cleaned_data["title"]
            # If the entry already exists, return the form:
            if util.get_entry(title):
                return render(request, "encyclopedia/new_page.html",{
                "titleform":titleform,
                "newpageform":newpageform
            })
            else:
                content =  newpageform.cleaned_data["content"]
                # Here, I manually create a title in the content based on the
                # user input in the title form
                content = f"#{title}\n{content}"
                util.save_entry(title, content)
                return HttpResponseRedirect(reverse('entry', args=[title]))

        else:
            return render(request, "encyclopedia/new_page.html",{
                "titleform":titleform,
                "newpageform":newpageform
            })
           
# Open a page for editing, then redirect to the entry to check if it looks good
def edit(request, title):
    if request.method == "GET":
        entry = util.get_entry(title)
        if entry is not None:
            return render(request, "encyclopedia/edit.html",{
                # Setting the default values, copying the preexisting data in the form fields
                "title":title,
                # Not forgetting to pass the is_edit hidden value in my form(see TitleForm)
                "titleform":TitleForm(initial={'title': title, 'is_edit':True}),
                "newpageform":NewPageForm(initial={'content': entry}),
            })
        
    if request.method == "POST":
        titleform = TitleForm(request.POST)
        newpageform = NewPageForm(request.POST)
        if titleform.is_valid() and newpageform.is_valid():
            title = titleform.cleaned_data["title"]
            content =  newpageform.cleaned_data["content"]
            util.save_entry(title, content)
            return HttpResponseRedirect(reverse('entry', args=[title]))
        else:
            return render(request, "encyclopedia/edit.html",{
                "title":title,
                "titleform":titleform,
                "newpageform":newpageform
            })