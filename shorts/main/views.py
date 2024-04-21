from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.template import loader
from django.views import View
from django.contrib.auth import login, logout, authenticate
import json
from api import views
from .forms import RegisterForm, CodeFromEmailForm, LoginForm, OnlyEmailForm, AddShortForm, NewPasswordForm


def mainView(request, page):
    content = json.loads(views.shortView(request).content)[(page-1)*20:page*20]
    template = loader.get_template("main.html")
    context = {
        "shorts": content,
    }

    return HttpResponse(template.render(context, request))


class RegisterView(View):
    @staticmethod
    def get(request):
        template = loader.get_template("register.html")
        context = {
            "form": RegisterForm(),
        }

        return HttpResponse(template.render(context, request))
    
    @staticmethod
    def post(request):
        form = RegisterForm(request.POST)

        if not form.is_valid():
            print(form.errors)
            template = loader.get_template("register.html")
            context = {
                "form": RegisterForm(),
            }

            return HttpResponse(template.render(context, request), status=400)
        
        res = views.RegisterClientView.post(request)

        match res.status_code:
            case 201:
                return HttpResponseRedirect("/auth/code/")
            case 400:
                template = loader.get_template("register.html")
                context = {
                    "form": RegisterForm(),
                }

                return HttpResponse(template.render(context, request), status=400)
            case _:
                return HttpResponseRedirect("/page/1")
            

class RegisterCodeView(View):
    @staticmethod
    def get(request):
        template = loader.get_template("registerCode.html")
        context = {
            "form": CodeFromEmailForm(),
        }

        return HttpResponse(template.render(context, request), status=200)
    
    @staticmethod
    def post(request):
        res = views.RegisterCodeView.post(request)

        match res.status_code:
            case 202:
                return HttpResponseRedirect("/page/1")
            case _:
                template = loader.get_template("registerCode.html")
                context = {
                    "form": CodeFromEmailForm(),
                }

                return HttpResponse(template.render(context, request), status=400)


class LoginView(View):
    @staticmethod
    def get(request):
        template = loader.get_template("login.html")
        context = {
            "form": LoginForm(),
        }

        return HttpResponse(template.render(context, request), status=200)
    
    @staticmethod
    def post(request):
        form = LoginForm(request.POST)

        if not form.is_valid():
            print(form.errors)
            template = loader.get_template("login.html")
            context = {
                "form": LoginForm(),
            }

            return HttpResponse(template.render(context, request), status=400)
        
        username = form.cleaned_data["username"]
        password = form.cleaned_data["password"]

        user = authenticate(username=username, password=password)
        
        if user is None:
            template = loader.get_template("login.html")
            context = {
                "form": LoginForm(),
            }

            return HttpResponse(template.render(context, request), status=400)
        
        login(request, user)

        return HttpResponseRedirect("/page/1")
    

class EditPasswordView(View):
    @staticmethod
    def get(request):
        template = loader.get_template("editPassword.html")
        context = {
            "emailForm": OnlyEmailForm(),
            "codeForm": CodeFromEmailForm(),
            "passwordForm": NewPasswordForm(),
        }

        return HttpResponse(template.render(context, request))


def logoutView(request):
    logout(request)
    return HttpResponseRedirect("/page/1")


class AddShortView(View):
    @staticmethod
    def get(request):
        if not request.user.is_authenticated:
            return HttpResponseRedirect("/page/1")

        template = loader.get_template("addShort.html")
        context = {
            "form": AddShortForm(),
        }

        return HttpResponse(template.render(context, request), status=200)
    
    @staticmethod
    def post(request):
        match views.AddShortView.post(request).status_code:
            case 400:
                template = loader.get_template("addShort.html")
                context = {
                    "form": AddShortForm(),
                }

                return HttpResponse(template.render(context, request), status=400)
            case 201:
                return HttpResponseRedirect("/page/1")
            case _:
                return HttpResponseRedirect("/page/1")


def getProfileView(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect("/page/1")
    
    template = loader.get_template("profile.html")
    context = {
        "client": json.loads(views.clientUsernameView(request).content),
        "shorts": json.loads(views.shortClientView(request).content),
    }

    return HttpResponse(template.render(context, request), status=200)
