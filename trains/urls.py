from django.urls import path
from .import views
urlpatterns = [
   path('search_train/', views.Trains.as_view(), name='search_trains'),
   path('train_details/<int:pk>', views.TrainDetails.as_view(), name='details'),
   path('train_details/booking/<int:pk>', views.BookSeatView.as_view(), name='booking'),
]
