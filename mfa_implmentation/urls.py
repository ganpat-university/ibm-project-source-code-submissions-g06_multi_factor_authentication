from unicodedata import name
from django.urls import path
from . import views


urlpatterns = [
    path('',views.HomeView.as_view(),name="home"),
    path('register/',views.RegisterView.as_view(),name="register"),
    path('login/',views.LoginView.as_view(),name="login"),
    path('mfa-verification',views.MfaVerificationView.as_view(),name="mfaverification"),
    path('user-profile/',views.LoginSuccessView.as_view(),name="profile"),
    path('backup-codes/',views.BackupCodeView.as_view() ,name="backupcodes"),
    path('otpverification/',views.OtpVerificationView.as_view(),name="otpverification"),
    path('pnumberVerification/',views.pnumberVerificationView.as_view(),name="pnumberVerification"),
    path('user-profile/FixedDeposit',views.FixedDepositView.as_view(),name="fixeddeposit"),
    path('user-profile/AddMoney',views.AddMoneyView.as_view(),name="addmoney"),
    path('user-profile/Stocks',views.StocksView.as_view(),name="stocks"),
    path('backupcodeverification',views.BackupCodeVerification.as_view(),name="backupcodeverification"),
    path('ssverification',views.ssverification.as_view(),name="ssverification"),
    path('user-profile/CryptoCurrency', views.CryptoCurrencyView.as_view(),name="cryptocurrency"),
    path("logout/",views.LogoutView.as_view(),name="logout"),
]