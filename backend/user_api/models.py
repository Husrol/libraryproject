from django.db import models
from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from datetime import timedelta


class AppUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('An email is required.')
        if not password:
            raise ValueError('A password is required.')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('An email is required.')
        if not password:
            raise ValueError('A password is required.')

        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        # Ensure that the extra_fields contains 'is_staff' and 'is_superuser'
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, password, **extra_fields)


class AppUser(AbstractBaseUser, PermissionsMixin):
    user_id = models.AutoField(primary_key=True)
    email = models.EmailField(max_length=50, unique=True)
    username = models.CharField(max_length=50)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    
    objects = AppUserManager()
    
    def __str__(self):
        return self.username

    
class Book(models.Model):
    title = models.CharField(max_length=50)
    author = models.CharField(max_length=50)
    relase_year = models.IntegerField()
    loan_date = models.DateTimeField(null=True, blank=True)
    return_date = models.DateField(null=True, blank=True)
    receivable = models.BooleanField(default=True)
    borrower = models.CharField(max_length=50, null=True, blank=True)

    def save(self, *args, **kwargs):
        # Eğer borrower doluysa receivable False olmalı
        if self.receivable == True:
            self.borrower = None
            self.return_date= None
            self.loan_date = None


        if self.borrower:
            self.receivable = False

        # Loan date boş değilse işlem yap
        if self.loan_date:
            # Loan_date'e göre return_date hesapla (örn. 14 gün sonra)
            if not self.return_date:
                self.return_date = self.loan_date + timedelta(days=14)

            # Return_date geçmişteyse receivable'ı False yap
            if self.return_date and self.return_date < self.loan_date.date():
                self.receivable = False
        else:
            # Loan_date boşsa ve borrower yoksa, receivable True olabilir
            if not self.borrower:
                self.receivable = True
            self.return_date = None

        super(Book, self).save(*args, **kwargs)