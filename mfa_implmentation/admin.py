from django.contrib import admin
from .models import UserInformation,UserAccountBalance,UserMfaSecret,User3MfaCodes,UserLogs

# Register your models here.
class UserInformationAdmin(admin.ModelAdmin):
    list_display = ("username","accountNumber")

class UserAccountBalanceAdmin(admin.ModelAdmin):
    list_display = ("accountNumber","balance")

class UserMfaSecretAdmin(admin.ModelAdmin):
    list_display = ("username","secret")

class User3MfaCodesAdmin(admin.ModelAdmin):
    list_display = ("username","otp")

admin.site.register(UserInformation,UserInformationAdmin)
admin.site.register(UserAccountBalance,UserAccountBalanceAdmin)
admin.site.register(UserMfaSecret,UserMfaSecretAdmin)
admin.site.register(User3MfaCodes,User3MfaCodesAdmin)

class UserLogsAdmin(admin.ModelAdmin):
    list_display = ("username","transactionAmount","transactionType")
admin.site.register(UserLogs,UserLogsAdmin)