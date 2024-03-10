from django.urls import path
from .import views
urlpatterns = [
   path('search_train/', views.Trains.as_view(), name='search_trains'),
   path('train_details/<int:pk>', views.TrainDetails.as_view(), name='details'),
   path('train_details/booking/<int:pk>', views.BookSeatView.as_view(), name='booking'),
   path('train_details/cancel_booking/<int:pk>', views.CancelBookingView.as_view(), name='cancel_booking'),
   path('train_details/download_ticket/<int:pk>', views.download_ticket, name='download_ticket'),
]
