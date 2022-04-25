from django.db import models
from django.contrib.auth.models import User


class UserInformation(models.Model):
    username = models.ForeignKey(User, on_delete=models.SET_NULL,null=True, related_name="user")
    accountNumber = models.CharField(max_length=11)
    favourite_dish = models.CharField(max_length=200)
    middle_name = models.CharField(max_length=200)
    city = models.CharField(max_length=200)
    pnumber = models.CharField(max_length=12)

class UserAccountBalance(models.Model):
    username = models.ForeignKey(User, on_delete=models.SET_NULL,null=True, related_name="userName")
    accountNumber = models.ForeignKey(UserInformation, on_delete=models.SET_NULL,null=True,related_name="accountnumber")
    balance = models.CharField(max_length=12)

class UserMfaSecret(models.Model):
    username = models.ForeignKey(User, on_delete=models.SET_NULL,null=True, related_name="user_name")
    secret = models.CharField(max_length=50)

class User3MfaCodes(models.Model):
    username = models.ForeignKey(User, on_delete=models.SET_NULL,null=True, related_name="User_Name")
    backupCode1 = models.CharField(max_length=7)
    backupCode2 = models.CharField(max_length=7)
    backupCode3 = models.CharField(max_length=7)
    otp = models.CharField(max_length=6,null=True)
    potp = models.CharField(max_length=6,null=True)

class UserLogs(models.Model):
    username = models.CharField(max_length=100)
    accountNumber = models.CharField(max_length=11)
    transactionAmount = models.CharField(max_length=10)
    transactionType = models.CharField(max_length=100)