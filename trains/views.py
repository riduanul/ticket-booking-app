from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.db.models import Q
from .models import Schedule, Booking
from passengers.models import Passenger
from django.views import View
from django.views.generic import FormView, DetailView
from .forms import SearchForm, CommentForm
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
# Create your views here.


class Trains(LoginRequiredMixin, FormView):
    template_name = 'train.html'
    form_class = SearchForm
    success_url = reverse_lazy('filtered_train')


    def form_valid(self, form):
        departure_station =form.cleaned_data['departure_station']
        arrival_station = form.cleaned_data['arrival_station']
        date_of_journey = form.cleaned_data['date_of_journey']

        trains = Schedule.objects.filter(
            Q(departure_station=departure_station) &
            Q(arrival_station=arrival_station) &
            Q(date_of_journey=date_of_journey)
        )

        return render(self.request, 'filtered_train.html', {'trains': trains})


class TrainDetails(LoginRequiredMixin, DetailView):
    model = Schedule
    template_name = 'train_details.html'
    context_object_name = 'train'

    def post(self, request, *args, **kwargs):
        comment_form = CommentForm(data=self.request.POST)
        train = self.get_object()

        if self.user_has_booking(request.user, train):
            if comment_form.is_valid():
                new_comment = comment_form.save(commit=False)
                new_comment.train = train
                new_comment.save()
                return redirect('details', pk=train.pk)
            else:
                messages.error(request, "Invalid comment")
        else:
            messages.error(request, "You can only comment if you have booked a ticket.")

        return self.get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        train = self.object
        available_seats = range(1, train.available_seats + 1)
        booked_seats = Booking.objects.filter(train=train)
        booked_seat_numbers = [booking.booked_seat for booking in booked_seats]
        comments = train.comments.all()
        comment_form = CommentForm()

        context.update({
            'available_seats': available_seats,
            'booked_seat_numbers': booked_seat_numbers,
            'comments': comments,
            'comment_form': comment_form
        })

        return context

    def user_has_booking(self, user, train):
        return Booking.objects.filter(user__user=user, train=train).exists()

class BookSeatView(LoginRequiredMixin, View):
    
    def post(self, request, pk):
        train = get_object_or_404(Schedule, pk=pk)
        seat_number = request.POST.get('seat_number')

        comment_form = CommentForm(data = self.request.POST)        
        user_instance = Passenger.objects.get(user=request.user)
        
        
        if not seat_number:
           
            messages.warning(request, "Please enter a seat number.")
            return redirect('details', pk=train.pk)

        if not seat_number.isdigit() or int(seat_number) not in range(1, train.available_seats + 1):
            messages.warning(request, "Invalid Seat Number")
            return redirect('details', pk=train.pk)

        if Booking.objects.filter( train=train, booked_seat=seat_number).exists():
            messages.warning(request, "Sorry Seat Already Booked")
            return redirect('details', pk=train.pk)
        
        if train.ticket_price > user_instance.balance:
            messages.warning(request, "Insufficient Balance")
            return redirect('details', pk=train.pk)

        user_instance.balance -= train.ticket_price
        user_instance.save()
        
        Booking.objects.create(user=user_instance, train=train, booked_seat=seat_number)
        messages.success(request, "Successfully ticket has been booked!")
        train.available_seats -= 1
        train.save()
    
        return redirect('details', pk=train.pk)
   

