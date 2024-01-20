from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.contrib.auth.forms import PasswordChangeForm
from .models import Passenger, Transaction
from trains.models import Booking
from .forms import RegistrationForm, DepositForm, ChangeUserDataForm
from django.views.generic import  FormView, CreateView, ListView
from django.contrib.auth.views import LoginView, LogoutView
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
#for token generate
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
#for sending email
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.http import Http404
# Create your views here.
class SignupView(FormView):
    form_class = RegistrationForm
    template_name = 'registration.html'
    success_url = reverse_lazy('home')

    def form_valid(self, form):
        user = form.save()
        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        current_site = get_current_site(self.request)
        confirm_link = f"http://127.0.0.1:8000/accounts/active/{uid}/{token}/"
        email_subject = 'Email Confirmation'
        email_body = render_to_string('confirmation_email.html', {'confirm_link': confirm_link})
        email = EmailMultiAlternatives(email_subject, '', to=[user.email])
        email.attach_alternative(email_body, 'text/html')
        email.send()
        messages.success(self.request, "Check Your Email To Confirm Email ")
       
        return super().form_valid(form)
    
def userActivation(request, uidb64, token ):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Passenger._default_manager.get(pk=uid)
        print(uid,user)
    except(Passenger.DoesNotExist):
        user = None
        raise Http404("Invalid Activation Link")

    if user is not None and default_token_generator.check_token(user, token):
        user.save()
        return redirect('login')
    else:
        return redirect('signup')

class LoginView(LoginView):
    template_name = 'login.html'
    def get_success_url(self):
       return reverse_lazy('home')

def userLogout(request):
    logout(request)
    return redirect('home')


class ProfileView(ListView):
    model = Booking
    template_name = 'profile.html'
    context_object_name = 'booking'

    
    def get_object(self, queryset=None):
        return self.request.user.user_account  

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        bookings = Booking.objects.filter(user=self.request.user.user_account)
        context['bookings'] = bookings
        return context

@login_required
def update_profile(request):
    if request.user.is_authenticated:
        if request.method == 'POST':
            profile_form = ChangeUserDataForm(request.POST, instance= request.user )
            if profile_form.is_valid():
                profile_form.save()
                messages.success(request, 'Profile Updated Successfully')
                return redirect('profile')
        else:
            profile_form = ChangeUserDataForm(instance = request.user)
        return render(request, 'update_profile.html',{'form': profile_form, 'user': request.user})
    else:
        return redirect('login')


@login_required
def password_change(request):
        if request.method == 'POST':
            form = PasswordChangeForm(request.user, request.POST )
            if form.is_valid():
                form.save()
                messages.success(request, 'Password Updated Successfully ')
                update_session_auth_hash(request, form.user)
                return redirect('profile')
        else:
            form = PasswordChangeForm(request.user)

        return render(request, 'password_change.html', {'form': form})


class DepositMoneyView(LoginRequiredMixin, CreateView):
    model = Transaction
    form_class = DepositForm
    template_name = 'deposit.html'
    success_url = reverse_lazy('deposit')
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['account'] = self.request.user.user_account
        return kwargs
        
    def form_valid(self, form):
        amount = form.cleaned_data.get('amount')
        account = self.request.user.user_account
        account.balance += amount
        account.save(update_fields = ['balance'])
        return super().form_valid(form)