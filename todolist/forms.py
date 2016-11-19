from django import forms

######新しくフォームを作るぞ!!!!!!!!!!!!!!!!!!!!!(11/19)
class CreateForm(forms.Form):
    title = forms.CharField(max_length=50)
    text = forms.CharField(widget=forms.Textarea)
    finish_at = forms.DateTimeField()
