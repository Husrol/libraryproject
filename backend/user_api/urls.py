from django.urls import path
from . import views
from django.views.decorators.csrf import csrf_exempt

urlpatterns = [
	path('register/', views.UserRegister.as_view(), name='register'),
	path('login/', views.UserLogin.as_view(), name='login'),
	path('logout/', views.UserLogout.as_view(), name='logout'),
	path('user/', views.UserView.as_view(), name='user'),
    path("books/", views.get_books, name="get_books"),
    path("books/create/", csrf_exempt(views.create_book), name="create_book"),
    path("books/<int:pk>/", views.book_detail, name="book_detail"),
    path("loan_book/<int:pk>/", views.loan_book, name="loan_book"),
    path('books/update/<int:book_id>/', csrf_exempt(views.update_book), name='book-update'),
    path("return_book/<int:book_id>/", views.return_book, name="return_book"),
    path('users/', views.UserListView.as_view(), name='user-list'),
    path('users/<int:pk>/', views.UserDetailView.as_view(), name='user-delete'),
]
