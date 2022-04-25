from django.http.response import HttpResponseRedirect
from django.shortcuts import render
from django.views import View
from django.contrib.auth.models import User
from django.urls import reverse
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.hashers import make_password
from .models import UserInformation,UserAccountBalance,UserMfaSecret,User3MfaCodes,UserLogs
import boto3
import random
import string
import requests
from datetime import date,timedelta
import pyotp
from django.conf import settings
from django.core.mail import send_mail
from twilio.rest import Client
import messagebird


today = date.today()
yesterday = today - timedelta(days = 3)

queue_url = 'https://sqs.ap-south-1.amazonaws.com/552470016854/myqueue'
stock_url = ['https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol=RELIANCE.BSE&outputsize=full&apikey=BVL5MGAAMSINNX3K','https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol=TATACHEM.BSE&outputsize=full&apikey=BVL5MGAAMSINNX3K','https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol=ADANIENT.BSE&outputsize=full&apikey=BVL5MGAAMSINNX3K','https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol=ONGC.BSE&outputsize=full&apikey=BVL5MGAAMSINNX3K','https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol=TITAN.BSE&outputsize=full&apikey=BVL5MGAAMSINNX3K']
crypto_url = ['https://www.alphavantage.co/query?function=DIGITAL_CURRENCY_DAILY&symbol=BTC&market=USD&apikey=BVL5MGAAMSINNX3K','https://www.alphavantage.co/query?function=DIGITAL_CURRENCY_DAILY&symbol=ETH&market=USD&apikey=BVL5MGAAMSINNX3K','https://www.alphavantage.co/query?function=DIGITAL_CURRENCY_DAILY&symbol=THETA&market=USD&apikey=BVL5MGAAMSINNX3K','https://www.alphavantage.co/query?function=DIGITAL_CURRENCY_DAILY&symbol=DOT&market=USD&apikey=BVL5MGAAMSINNX3K','https://www.alphavantage.co/query?function=DIGITAL_CURRENCY_DAILY&symbol=BNB&market=USD&apikey=BVL5MGAAMSINNX3K']

def getAuthenticateEmail(email):
	sqs = boto3.client('sqs',region_name='ap-south-1')
	
	# Send message to SQS queue
	response = sqs.send_message(
		QueueUrl=queue_url,
		DelaySeconds=10,
		MessageAttributes={
			'email': {
				'DataType': 'String',
				'StringValue': email
			},
			'is_secret': {
				'DataType': 'String',
				'StringValue': "no"
			}					
		},
		MessageBody=(
			'sgnons'
		)
	)
	print("\n\n\n\n\n")
	print(response['MessageId'])


def callSQS(Secret,email):
	sqs = boto3.client('sqs',region_name='ap-south-1')

	response = sqs.send_message(
		QueueUrl=queue_url,
		DelaySeconds=10,
		MessageAttributes={
			'Secret': {
				'DataType': 'String',
				'StringValue': Secret
			},
			'email': {
				'DataType': 'String',
				'StringValue': email
			},
			'is_secret': {
				'DataType': 'String',
				'StringValue': "yes"
			}		
		},
		MessageBody=(
			'sgnons'
		)
	)

	print(response['MessageId'])

def GetSecret():
	return ''.join(random.choices(string.ascii_uppercase + string.digits, k = 11))


def BackupCodes():
	return ''.join(random.choices(string.digits, k = 7))

def OtpGenration():
    return ''.join(random.choices(string.digits, k = 6))

class HomeView(View):
    def get(self , request):
        return render(request,"Homepage/Home.html")

class RegisterView(View):
    def get(self , request):
        return render(request,"Register.html")
    
    def post(self, request):
        context = {}
        if request.method == "POST":
            username = request.POST['username']
            email = request.POST['email']
            password = request.POST['password']
            symbols = ['!', '@', '#', '$', '%', '^', '&', '*', '(', ')', '.']
            
            if len(password) < 8: 
                context["error"] = "Password does meet the minimum length requirements of 8 characters. Password criteria not satisfied, please enter valid password!"
                return render(request, "Register.html",context)
                
            if len(password) > 15: 
                context["error"] = "Password should not exceed 15 characters. Password criteria not satisfied, please enter valid password!"
                return render(request, "Register.html",context)

            if not any(char.islower() for char in password): 
                context["error"] = "Password should have at least one lowercase letter. Password criteria not satisfied, please enter valid password!"
                return render(request, "Register.html",context)
                
            if not any(char.isupper() for char in password): 
                context["error"] = "Password should have at least one uppercase letter. Password criteria not satisfied, please enter valid password!"
                return render(request, "Register.html",context)

            if not any(char.isdigit() for char in password): 
                context["error"] = "Password should have at least one number. Password criteria not satisfied, please enter valid password!"
                return render(request, "Register.html",context)
                
            if not any(char in symbols for char in password): 
                context["error"] = "Password should have at least one of the symbols: .!@#$%^&*(). Password criteria not satisfied, please enter valid password!"
                return render(request, "Register.html",context)
        
            print("Password is valid")
            confirm_password = request.POST['confirm_password']

            if(password==confirm_password):
                userprofile = User(
                    username = username,
                    email = email,
                    password = make_password(password)
                )
                userprofile.save()
                getAuthenticateEmail(email)
                context["success"] = "You have Registered Successfully! Please Check Your Email for Authentication:)"
                return render(request, "Register.html",context)
            else:
                context["error"] = "Please Enter Same password and Confirm password!!"
                return render(request, "Register.html",context)
        else:
            context["error"] = "Some Error Occured Please Try Again:("
            return render(request, "Register.html",context)

class LoginView(View):
    def get(self , request):
        return render(request,"Login.html")

    def post(self , request):
        context = {}
        if request.method == "POST":
            username = request.POST['username']
            password = request.POST['password']
            user = authenticate(request,username=username,password=password)
            if user:
                login(request,user)
                return HttpResponseRedirect(reverse("mfaverification"))
            else:
                context["error"] = "Enter Valid Credentials!!"
                return render(request , "Login.html",context)

class MfaVerificationView(View):
    def get(self,request):
        name = request.user
        context = {}
        if UserMfaSecret.objects.filter(username=name).exists():  
            context["secret"] = UserMfaSecret.objects.filter(username=name).values_list('secret', flat=True)[0]
            return render(request,"MfaVerification.html",context)
        else:
            context["secret"] = pyotp.random_base32()
            return render(request,"MfaVerification.html",context)
    
    def post(self,request):
        context = {}
        name = request.user
        if request.method == "POST":
            secret = request.POST['secret']
            otp = request.POST['otp']
            otp = int(otp)
            if UserMfaSecret.objects.filter(username=name).exists():
                if pyotp.TOTP(secret).verify(otp):
                    return HttpResponseRedirect(reverse("profile"))
                else:
                    context["error"] = "Wrong OTP, Try Again !!"
                    return render(request,"MfaVerification.html",context)
            else:
                userMfa = UserMfaSecret(
                    username=name,
                    secret=secret,
                )
                userMfa.save()
                if pyotp.TOTP(secret).verify(otp):
                    return HttpResponseRedirect(reverse("profile"))
                else:
                    context["error"] = "Wrong OTP, Try Again !!"
                    return render(request,"MfaVerification.html",context)
            
class LoginSuccessView(View):
    def get(self , request):
        name = request.user
        context = {}
        if UserInformation.objects.filter(username=name).exists(): 
            context["accountnumber"] = UserInformation.objects.filter(username=name).values_list('accountNumber', flat=True)[0]
            context["date"] = today.strftime("%b %d %Y")
            if UserAccountBalance.objects.filter(username=name).exists():
                context["accountbalance"] = UserAccountBalance.objects.filter(username=name).values_list('balance', flat=True)[0]
                context["userlogs"] = UserLogs.objects.all()
                return render(request , "Profile.html",context)
            else:
                return render(request , "Profile.html",context)
        else:
            return render(request , "PersonalQuestions.html")

    def post(self,request):
        context = {}
        if request.method == "POST":
            user = request.user
            Account = GetSecret()
            email = User.objects.filter(username=user).values_list('email', flat=True)[0]
            dish = request.POST['dish']
            middlename = request.POST['middlename']
            city = request.POST['city']
            pnumber = request.POST['pnumber']
            userdetails = UserInformation(
                username = user,
                accountNumber = Account,
                favourite_dish = dish,
                middle_name = middlename,
                city = city,
                pnumber = pnumber 
            )
            userdetails.save()
            callSQS(Account,email)
            context["success"] = "Please Verify Your Account Number with the Email also!"
            return HttpResponseRedirect(reverse("profile"))

class FixedDepositView(View):
    def get(self , request):
        context = {}
        name = request.user
        context["accountnumber"] = UserInformation.objects.filter(username=name).values_list('accountNumber', flat=True)[0]
        context["date"] = today.strftime("%b %d %Y")
        if UserAccountBalance.objects.filter(username=name).exists():
            context["accountbalance"] = UserAccountBalance.objects.filter(username=name).values_list('balance', flat=True)[0]
        return render(request,"FixedDeposit.html",context)
    
    def post(self,request):
        name = request.user
        context = {}
        amount = request.POST['amount']
        context["amount"] = amount
        context["accountnumber"] = UserInformation.objects.filter(username=name).values_list('accountNumber', flat=True)[0]
        pnumber = UserInformation.objects.filter(username=name).values_list('pnumber', flat=True)[0]
        Genrated_Otp = OtpGenration()
        User3MfaCodes.objects.filter(username=name).update(potp=Genrated_Otp)
        message = f'Hi {name},\nYour OTP is {Genrated_Otp}, Please Enter it Correctly and Complete Your Transaction for Rupees {amount}'
        frm = '+919978655186'
        to = '+919978855186'
        client = messagebird.Client('worBdUgn2oZIaDhTfWCjdSmjj')
        message = client.message_create(
          'TestMessage',
          [pnumber],
          message
        )
        return render(request,"pnumberVerification.html",context)

class pnumberVerificationView(View):
    def post(self,request):
        context ={}
        name = request.user
        if request.method == "POST":
            potp = request.POST['potp']
            account = request.POST['accountNo']
            amount = request.POST['amount']
            userOtp = User3MfaCodes.objects.filter(username=name).values_list('potp', flat=True)[0]
            if(potp==userOtp):
                if UserAccountBalance.objects.filter(username=name).exists():
                    oldbalance = UserAccountBalance.objects.filter(username=name).values_list('balance', flat=True)[0]
                    newbalance = int(oldbalance) - int(amount)
                    UserAccountBalance.objects.filter(username=name).update(balance=newbalance)
                    userlog = UserLogs(
                        username = name,
                        accountNumber = account,
                        transactionAmount = amount,
                        transactionType = "Fixed Deposit"
                    )   
                    userlog.save()
                    return HttpResponseRedirect(reverse("fixeddeposit"))
                else:
                    if request.method == "POST":
                        account = request.POST['accountNo']
                        Accountnumber = UserInformation.objects.get(accountNumber=account)
                        balance = request.POST['amount']
                        userbalance = UserAccountBalance(
                            username = name,
                            accountNumber = Accountnumber,
                            balance = balance,
                        )
                        userbalance.save()
                        userlog = UserLogs(
                        username = name,
                        accountNumber = account,
                        transactionAmount = amount,
                        transactionType = "Fixed Deposit"
                    )   
                    userlog.save()
                    return HttpResponseRedirect(reverse("fixeddeposit")) 
            else:
                context["Error"] = "Your Transaction Failed please enter valid OTP for Transaction!"
                return render(request,"FixedDeposit.html",context)

class AddMoneyView(View):
    def get(self,request):
        context = {}
        name = request.user
        context["accountnumber"] = UserInformation.objects.filter(username=name).values_list('accountNumber', flat=True)[0]
        context["date"] = today.strftime("%b %d %Y")
        if UserAccountBalance.objects.filter(username=name).exists():
            context["accountbalance"] = UserAccountBalance.objects.filter(username=name).values_list('balance', flat=True)[0]
        return render(request,"AddMoney.html",context)
    
    def post(self,request):
        name = request.user
        context = {}
        amount = request.POST['amount']
        context["amount"] = amount
        context["accountnumber"] = UserInformation.objects.filter(username=name).values_list('accountNumber', flat=True)[0]
        email = User.objects.filter(username=name).values_list('email', flat=True)[0]
        Genrated_Otp = OtpGenration()
        User3MfaCodes.objects.filter(username=name).update(otp=Genrated_Otp)
        subject = 'OTP Verification by Fintrans'
        message = f'Hi {name},\nYour OTP is {Genrated_Otp}, Please Enter it Correctly and Complete Your Transaction for Rupees {amount}'
        email_from = settings.EMAIL_HOST_USER
        recipient_list = [email]
        send_mail( subject, message, email_from, recipient_list )
        return render(request,"otpVerfication.html",context)


class OtpVerificationView(View):
    def post(self,request):
        context ={}
        name = request.user
        if request.method == "POST":
            otp = request.POST['otp']
            account = request.POST['accountNo']
            amount = request.POST['amount']
            userOtp = User3MfaCodes.objects.filter(username=name).values_list('otp', flat=True)[0]
            if(otp==userOtp):
                if UserAccountBalance.objects.filter(username=name).exists():
                    oldbalance = UserAccountBalance.objects.filter(username=name).values_list('balance', flat=True)[0]
                    newbalance = int(oldbalance) + int(amount)
                    UserAccountBalance.objects.filter(username=name).update(balance=newbalance)
                    userlog = UserLogs(
                        username = name,
                        accountNumber = account,
                        transactionAmount = amount,
                        transactionType = "Add Money"
                    )   
                    userlog.save()
                    return HttpResponseRedirect(reverse("addmoney"))
                else:
                    if request.method == "POST":
                        account = request.POST['accountNo']
                        Accountnumber = UserInformation.objects.get(accountNumber=account)
                        balance = request.POST['amount']
                        userbalance = UserAccountBalance(
                            username = name,
                            accountNumber = Accountnumber,
                            balance = balance,
                        )
                        userbalance.save()
                        userlog = UserLogs(
                        username = name,
                        accountNumber = account,
                        transactionAmount = amount,
                        transactionType = "Add Money"
                    )   
                    userlog.save()
                    return HttpResponseRedirect(reverse("addmoney")) 
            else:
                context["Error"] = "Your Transaction Failed Please Enter Valid OTP for Transaction!"
                return render(request,"AddMoney.html",context)

class StocksView(View):
    def get(self , request):
        context = {}
        name = request.user
        stock = []
        price = []
        context["accountnumber"] = UserInformation.objects.filter(username=name).values_list('accountNumber', flat=True)[0]
        for i in range(len(stock_url)):
            r = requests.get(stock_url[i])
            data = r.json()
            stock.append(data['Meta Data']['2. Symbol'])
            price.append(data["Time Series (Daily)"][str(yesterday)]["4. close"])
        context["stock"] = stock
        context["price"] = price   
        context["date"] = today.strftime("%b %d %Y")
        return render(request,"Stocks.html",context)

    def post(self,request):
        name = request.user
        context = {}
        quantity = request.POST['quantity']
        amount = request.POST['price']
        context["amount"] = float(amount)*int(quantity)
        context["quantity"] = quantity
        context["accountnumber"] = UserInformation.objects.filter(username=name).values_list('accountNumber', flat=True)[0]
        return render(request,"VerifyBackupCodes.html",context)

class BackupCodeVerification(View):
    def post(self,request):
        name = request.user
        context = {}
        if request.method == "POST":
            amount = request.POST['amount']
            account = request.POST['accountNo']
            code1 = request.POST['code1']
            code3 = request.POST['code3']
            backup1 = User3MfaCodes.objects.filter(username=name).values_list('backupCode1', flat=True)[0]
            backup3 = User3MfaCodes.objects.filter(username=name).values_list('backupCode3', flat=True)[0]
            if(code1==backup1 and code3==backup3):
                balance = UserAccountBalance.objects.filter(username=name).values_list('balance', flat=True)[0]
                if(float(amount)<=int(balance)):
                    newbalance = int(balance)-float(amount)
                    newbalance = int(newbalance)
                    UserAccountBalance.objects.filter(username=name).update(balance=newbalance)
                    userlog = UserLogs(
                        username = name,
                        accountNumber = account,
                        transactionAmount = amount,
                        transactionType = "Stocks"
                    )   
                    userlog.save()
                    context["Success"] = "Your Transaction is Completed!!"
                    return render(request,"VerifyBackupCodes.html",context)
                else:
                    context["Error"] = "Your Account Doesn't have Enough Money, So Your Trancation Failed!"
                    return render(request,"VerifyBackupCodes.html",context)
            else:
                context["Error"] = "Your Transaction Failed Please Enter Valid BackupCodes for Tranaction!"
                return render(request,"VerifyBackupCodes.html",context)

class ssverification(View):
    def post(self,request):
        name = request.user
        context = {}
        if request.method == "POST":
            amount = request.POST['amount']
            account = request.POST['accountnumber']
            #context["accountnumber"] = UserInformation.objects.filter(username=name).values_list('accountNumber', flat=True)[0]
            ans1 = request.POST['ans1']
            ans2 = request.POST['ans2']
            ss1 = UserInformation.objects.filter(username=name).values_list('favourite_dish', flat=True)[0]
            ss2 = UserInformation.objects.filter(username=name).values_list('middle_name', flat=True)[0]
            if(ans1==ss1 and ans2==ss2):
                balance = UserAccountBalance.objects.filter(username=name).values_list('balance', flat=True)[0]
                if(float(amount)<=int(balance)):
                    newbalance = int(balance)-float(amount)
                    newbalance = int(newbalance)
                    UserAccountBalance.objects.filter(username=name).update(balance=newbalance)
                    userlog = UserLogs(
                        username = name,
                        accountNumber = account,
                        transactionAmount = amount,
                        transactionType = "Cryptocurrency"
                    )   
                    userlog.save()
                    context["Success"] = "Your Transaction is Completed!!"
                    return render(request,"SSVerification.html",context)
                else:
                    context["Error"] = "Your Account Doesnt have Enough Money, So Your Trancation Failed!"
                    return render(request,"SSVerification.html",context)
            else:
                context["Error"] = "Your transaction failed please answer correct security questions for Tranaction!"
                return render(request,"SSverification.html",context)            


class CryptoCurrencyView(View):
    def get(self , request):
        context = {}
        name = request.user
        crypto = []
        price = []
        context["accountnumber"] = UserInformation.objects.filter(username=name).values_list('accountNumber', flat=True)[0]
        for i in range(len(crypto_url)):
            r = requests.get(crypto_url[i])
            data = r.json()
            crypto.append(data['Meta Data']['3. Digital Currency Name'])
            price.append(int(float(data['Time Series (Digital Currency Daily)'][str(yesterday)]["4b. close (USD)"]))*75.08)
        context["crypto"] = crypto
        context["price"] = price
        context["date"] = today.strftime("%b %d %Y")
        return render(request,"CryptoCurrency.html",context)

    def post(self,request):
        name = request.user
        context = {}
        quantity = request.POST['quantity']
        amount = request.POST['price']
        context["amount"] = float(amount)*int(quantity)
        context["quantity"] = quantity
        context["accountnumber"] = UserInformation.objects.filter(username=name).values_list('accountNumber', flat=True)[0]
        return render(request,"SSVerification.html",context)

class BackupCodeView(View):
    def get(self,request):
        context = {}
        name = request.user
        context["accountnumber"] = UserInformation.objects.filter(username=name).values_list('accountNumber', flat=True)[0]
        if User3MfaCodes.objects.filter(username=name).exists():
            context["backup1"] = User3MfaCodes.objects.filter(username=name).values_list('backupCode1', flat=True)[0]
            context["backup2"] = User3MfaCodes.objects.filter(username=name).values_list('backupCode2', flat=True)[0]
            context["backup3"] = User3MfaCodes.objects.filter(username=name).values_list('backupCode3', flat=True)[0]
            return render(request,"BackupCodes.html",context)
        else:
            backup1 = BackupCodes()
            backup2 = BackupCodes()
            backup3 = BackupCodes()
            backupCode = User3MfaCodes(
                username = name,
                backupCode1 = backup1,
                backupCode2 = backup2,
                backupCode3 = backup3,
                otp = 123456,
            )
            backupCode.save()
            context["backup1"] = backup1
            context["backup2"] = backup2
            context["backup3"] = backup3
            return render(request,"BackupCodes.html",context)

class LogoutView(View):
    def post(self, request):
        if request.method == "POST":
            logout(request)
            return HttpResponseRedirect(reverse("login"))