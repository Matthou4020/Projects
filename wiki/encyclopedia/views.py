from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django import forms
from . import views
import markdown2
from . import util
import random

# In settings.py I have inserted the path to the following context processor.
# This way, when generating the "random page" link in every page,
# I won't have to copy paste the context every time.
def random_title(request):
    return {'random_title': random.choice(util.list_entries())}

# I did the same for the search form
def searchform(request):
    return {'form': SearchForm()}


class SearchForm(forms.Form):
    q = forms.CharField(
        widget=forms.TextInput(attrs={
            'placeholder': 'Search Encyclopedia'
            })
        , label=''
    )

# Here is my title form when editing or creating a new page.
# When editing, the is_edit value will be set to True by the edit view. 
# This way, I can set different outcomes whether the form is submitted via a
# create page or an edit page.
class TitleForm(forms.Form):
    title = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={
            'placeholder': 'Title of your page'
        }), label=''
    )
    is_edit = forms.BooleanField(
        widget=forms.HiddenInput(), 
        required=False)
    
# I chose to override the title form's clean function, 
# because it wasn't working properly for my purposes
    def clean(self):
        cleaned_data = super().clean()
        title = cleaned_data.get('title')
        is_edit = cleaned_data.get('is_edit')
        if not is_edit and title in util.list_entries():
            raise forms.ValidationError("This title already exists.")

        elif is_edit:
            if title in util.list_entries():
                return cleaned_data


class NewPageForm(forms.Form):
    content = forms.CharField(
        widget=forms.Textarea(attrs={
            'id': 'page_text',
            'placeholder': 'Text',
            'rows': 4,
            'cols': 50
        }), label=''
    )


def index(request):
    if request.method == "GET":
        return render(request, "encyclopedia/index.html", {
            "entries": util.list_entries()
        })
    
# Here we do the mardown to HTML conversion so the content
# is formatted in the viewport
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