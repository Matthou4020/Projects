from django import forms

class PostForm(forms.Form):
    content = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control mb-2',
                                                            'cols': 10,
                                                            'rows': 2,
                                                            'placeholder' : 'Anything you would like to share?'
                                                            }), 
                            max_length= 500)

    def __str__(self):
        return f"{self.title}... posted by {self.user}"