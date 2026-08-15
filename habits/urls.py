
from django.urls import path
from .views import UserHabitList, PublicHabitList, HabitDetail

urlpatterns = [
    path('my-habits/', UserHabitList.as_view(), name='my-habits'),
    path('public-habits/', PublicHabitList.as_view(), name='public-habits'),
    path('<int:pk>/', HabitDetail.as_view(), name='habit-detail'),
]