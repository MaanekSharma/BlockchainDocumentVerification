from django import forms   
from .models import User
class SignInForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'password']
        labels = {
            "username":"Username",
            "password":"Password"
        }
        widgets={ 
            'username' : forms.TextInput(attrs={"onClick":"myFn()"}),
            'password' : forms.PasswordInput(attrs={"onClick":"myFn()"})
        }

class LogInForm(forms.Form):
    
    username = forms.CharField(label="Username", max_length=150)
    password = forms.CharField(label="Password",widget=forms.PasswordInput)
    
class DocumentsForm(forms.Form):
    file = forms.FileField(label="Select a file to upload")
    
    