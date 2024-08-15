from django.contrib.auth import get_user_model, login, logout
from rest_framework.decorators import api_view
from rest_framework.authentication import SessionAuthentication
from rest_framework.views import APIView
from datetime import datetime
from django.views.decorators.http import require_http_methods
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from datetime import datetime, timedelta
from django.contrib.auth.models import User
from .models import Book, AppUser
from django.utils.decorators import method_decorator
from rest_framework.parsers import JSONParser
from django.http import Http404
from rest_framework.permissions import AllowAny
import json
from rest_framework import generics
from django.http import JsonResponse
from rest_framework.response import Response
from .serializers import UserRegisterSerializer, UserLoginSerializer, UserSerializer, BookSerializer, AppUserSerializer
from rest_framework import permissions, status
from .validations import custom_validation, validate_email, validate_password
from django.utils.dateparse import parse_datetime


class UserRegister(APIView):
	permission_classes = (permissions.AllowAny,)
	def post(self, request):
		clean_data = custom_validation(request.data)
		serializer = UserRegisterSerializer(data=clean_data)
		if serializer.is_valid(raise_exception=True):
			user = serializer.create(clean_data)
			if user:
				return Response(serializer.data, status=status.HTTP_201_CREATED)
		return Response(status=status.HTTP_400_BAD_REQUEST)


class UserLogin(APIView):
    permission_classes = (permissions.AllowAny,)
    authentication_classes = (SessionAuthentication,)

    def post(self, request):
        data = request.data
        print(data)
        assert validate_email(data)
        assert validate_password(data)
        serializer = UserLoginSerializer(data=data)
        print(serializer)
        if serializer.is_valid(raise_exception=True):
            user = serializer.check_user(data)  # Kullanıcıyı burada alın
            login(request, user)  # login fonksiyonuna kullanıcı nesnesini gönderin
            response_data = serializer.validated_data
            return Response(response_data, status=status.HTTP_200_OK)
    


class UserLogout(APIView):
	permission_classes = (permissions.AllowAny,)
	authentication_classes = ()
	def post(self, request):
		logout(request)
		return Response(status=status.HTTP_200_OK)


class UserView(APIView):
	permission_classes = (permissions.IsAuthenticated,)
	authentication_classes = (SessionAuthentication,)
	##
	def get(self, request):
		serializer = UserSerializer(request.user)
		return Response({'user': serializer.data}, status=status.HTTP_200_OK)
     
class UserListView(APIView):
    def get(self, request):
        users = AppUser.objects.all()
        serializer = AppUserSerializer(users, many=True)
        return Response(serializer.data)

class UserDetailView(APIView):
    permission_classes = [AllowAny]

    def get_object(self, pk):
        try:
            return AppUser.objects.get(pk=pk)
        except AppUser.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        user = self.get_object(pk)
        serializer = AppUserSerializer(user)
        return Response(serializer.data)

    def put(self, request, pk, format=None):
        user = self.get_object(pk)
        serializer = AppUserSerializer(user, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        user = self.get_object(pk)
        user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def patch(self, request, pk, format=None):
        user = self.get_object(pk)
        serializer = AppUserSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET"])
def get_books(request):
    books = Book.objects.all()
    serializedbook = BookSerializer(books, many=True).data
    return Response(serializedbook)


@csrf_exempt
def create_book(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            title = data.get('title')
            author = data.get('author')
            release_year = data.get('release_year')

            # Yeni bir Book objesi oluştur
            book = Book(title=title, author=author, relase_year=release_year)

            # Diğer alanları isteğe bağlı olarak ekle
            loan_date = data.get('loan_date')
            if loan_date:
                book.loan_date = loan_date
            
            borrower = data.get('borrower')
            if borrower:
                book.borrower = borrower
            
            # Kitap objesini kaydet
            book.save()
            
            return JsonResponse({'message': 'Book created successfully'}, status=201)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
    return JsonResponse({'error': 'Invalid method'}, status=405)

@csrf_exempt
def book_detail(request, pk):
    try:
        book = Book.objects.get(pk=pk)
    except Book.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    
    if request.method == "DELETE":
        book.delete()
        return Response({"message": "Book deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
    elif request.method == "PUT":
        data=request.data
        serializer = BookSerializer(book, data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@csrf_exempt
def loan_book(request, pk):
    if request.method == 'PUT':
        try:
            data = json.loads(request.body)
            book = get_object_or_404(Book, pk=pk)
            
            # Günün tarihini ayarla
            loan_date = datetime.now()

            book.borrower = data.get('borrower', book.borrower)
            book.loan_date = loan_date
            book.receivable = data.get('receivable', book.receivable)
            
            # loan_date'e göre return_date hesapla
            if book.loan_date:
                book.return_date = (book.loan_date + timedelta(days=14)).date()
            
            book.save()
            return JsonResponse({'message': 'Book loaned successfully'}, status=200)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
    return JsonResponse({'error': 'Invalid method'}, status=405)


@csrf_exempt
def update_book(request, book_id):
    try:
        book = Book.objects.get(pk=book_id)
    except Book.DoesNotExist:
        return JsonResponse({'error': 'Book not found'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'PUT':
        try:
            # Load JSON data from request.body
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=status.HTTP_400_BAD_REQUEST)

        serializer = BookSerializer(book, data=data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse(serializer.data, status=status.HTTP_200_OK)
        return JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@csrf_exempt    
def return_book(request, book_id):
    try:
        book = Book.objects.get(pk=book_id)
    except Book.DoesNotExist:
        return JsonResponse({'error': 'Book not found'}, status=status.HTTP_404_NOT_FOUND)
    
    if request.method == 'PUT':
        try:
            # Load JSON data from request.body
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=status.HTTP_400_BAD_REQUEST)

        serializer = BookSerializer(book, data=data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse(serializer.data, status=status.HTTP_200_OK)
        return JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)