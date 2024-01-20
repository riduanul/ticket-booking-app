from django import forms
from .models import Schedule, Comment



class SearchForm(forms.ModelForm):
    class Meta:
        model= Schedule
        fields = ['departure_station', 'arrival_station', 'date_of_journey']
        widgets = {
            'date_of_journey': forms.DateInput(attrs={'type': 'date'}),
        }

class BookingForm(forms.Form):
     seat_number = forms.IntegerField()

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['name', 'comment']
       


