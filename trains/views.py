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
from django.http import HttpResponse
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from django.core.mail import EmailMessage, EmailMultiAlternatives
from django.template.loader import render_to_string 
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
        total_seats = range(1, 30 + 1)
        booked_seats = Booking.objects.filter(train=train)
        booked_seat_numbers = [booking.booked_seat for booking in booked_seats]
        comments = train.comments.all()
        comment_form = CommentForm()
        
        context.update({
            
            'total_seats': total_seats,
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
        
        booking = Booking.objects.create(user=user_instance, train=train, booked_seat=seat_number)

        # message = render_to_string('email.html', {
        #     'user':request.user.user_account,
        #     'train': booking.train.train,
        #     'from': booking.train.departure_station,
        #     'to':booking.train.arrival_station,
        #     'date': booking.train.date_of_journey,
        #     'time': booking.train.departure_time,
        #     'seat': booking.booked_seat,
        #     'price': booking.train.ticket_price,
        # })
        # send_email = EmailMultiAlternatives('Ticket Booking Confirmation', '', to=[request.user.email])
        # send_email.attach_alternative(message, 'text/html')
        # send_email.send()
        messages.success(request, "Successfully ticket has been booked! ")
        train.available_seats -= 1
        train.save()
    
        return redirect('details', pk=train.pk)


class CancelBookingView(LoginRequiredMixin, View):
    def post(self, request, pk):
        booking  = get_object_or_404(Booking, pk =pk)
        train_pk = booking.train.pk
        booking.cancel_booking()
        user = request.user.user_account
        user.balance += booking.train.ticket_price
        user.save()
        train = booking.train
        train.available_seats += 1
        train.save()

        messages.success(request, "Booking canceled successfully !")
        return redirect('details', pk=train_pk)


def generate_pdf(booking):
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="ticket_{booking.id}.pdf"'
    
    # Create a PDF
    p = canvas.Canvas(response, pagesize=letter)
    y_coordinate = 750  # Initial Y-coordinate

    # Write Booking ID
    p.setTitle("Train Ticket")
    p.drawString(100, y_coordinate, f"Booking ID: XX000114500{booking.id}")
    y_coordinate -= 20  # Move to the next line

    # Write User Name
     # Write Date and Time
    p.drawString(100, y_coordinate, f"Date: {booking.train.date_of_journey}")
    y_coordinate -= 20  # Move to the next line
    p.drawString(100, y_coordinate, f"{booking.train.train}")
    y_coordinate -= 20  # Move to the next line
    p.drawString(100, y_coordinate, f"Name Of Passenger:")
    y_coordinate -= 20  # Move to the next line
    p.drawString(100, y_coordinate, f"Mr./Ms: {booking.user.user.first_name} {booking.user.user.last_name}")
    y_coordinate -= 20  # Move to the next line

    # Write From and To Stations
    p.drawString(100, y_coordinate, f"From: {booking.train.departure_station} To: {booking.train.arrival_station}")
   
    y_coordinate -= 20  # Move to the next line

   
    p.drawString(100, y_coordinate, f"Time: {booking.train.departure_time}")
    y_coordinate -= 20  # Move to the next line

    # Write Seat Number
    p.drawString(100, y_coordinate, f"Seat Number: {booking.booked_seat}")
    y_coordinate -= 20  # Move to the next line
    # Add more details as needed

    p.showPage()
    p.save()
    return response

def download_ticket(self, pk):
    booking = get_object_or_404(Booking, pk=pk)
   
    pdf = generate_pdf(booking)
    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] =  f'attachment; filename="ticket_{booking.id}.pdf"'
    return response


