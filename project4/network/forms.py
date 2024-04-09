from django import forms

class PostForm(forms.Form):
    title = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control mb-2'}),
                            max_length=60)
    content = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control mb-2'}), 
                            max_length= 500)

    def __str__(self):
        return f"{self.title}... posted by {self.user}"