from django.http import HttpRequest, JsonResponse, FileResponse
from django.contrib.auth import login
from django.views import View
from django.core.cache import cache
from .serializers import ShortSerializer, ClientSerializer
from .models import Short, Client, ShortRating
from .forms import RegisterForm, CodeFromEmailForm, AddShortForm, OnlyEmailForm, NewPasswordForm
from . import tasks
import json, random


def sendCodeToEmail(REMOTE_ADDR, email):
    code = str(random.randint(100000, 999999))
    print(REMOTE_ADDR, email)
    cache.set(REMOTE_ADDR, (email, code), 60*5, 2)

    tasks.sendCodeToEmail.delay(email, code)



def testView(request):
    short = Short.objects.get(id=1)
    # short.image.name = f"http://127.0.0.1:8000/api/{short.image.name}"
    print(short)
    print(short.image.name)
    print(short.image.__dict__)

    ser = ShortSerializer(short)
    print(ser.data)

    return JsonResponse(ser.data, status=200)


def shortView(request):
    return JsonResponse(ShortSerializer(Short.objects.all().select_related().only("title", "image", "rating", "created",
            "client__rating", "client__username", "client__email"), many=True).data, safe=False, status=200)


def shortIDView(request, id):
    try:
        return JsonResponse(ShortSerializer(Short.objects.select_related().only("title", "image", "rating", "created",
                "client__rating", "client__username", "client__email").get(id=id)).data, status=200)
    except:
        return JsonResponse({"reason":"Данный short не найден."}, status=404)
    

def shortClientView(request):
    return JsonResponse(ShortSerializer(Short.objects.select_related().only("title", "image", "rating", "created", "client__username", "client__email", "client__rating") \
                                        .filter(client__username=request.user), many=True).data, safe=False, status=200)
    

def clientView(request):
    return JsonResponse(ClientSerializer(Client.objects.only("rating", "username", "email") \
                                         .filter(is_superuser=False), many=True).data, safe=False, status=200)


def clientIDView(request, id):
    try:
        return JsonResponse(ClientSerializer(Client.objects.only(
                "rating", "username", "email").get(id=id, is_superuser=False)).data, status=200)
    except:
        return JsonResponse({"reason":"Данный client не найден."}, status=404)
    

def clientUsernameView(request):
    try:
        return JsonResponse(ClientSerializer(Client.objects.only(
                "rating", "username", "email").get(username=request.user, is_superuser=False)).data, status=200)
    except:
        return JsonResponse({"reason":"Данный client не найден."}, status=404)


def imageView(request, name):
    try:
        return FileResponse(open(f"api/image/{name}", "rb"), status=200)
    except Exception as e:
        print(e)
        return FileResponse(status=404)
    

class RegisterClientView(View):
    @staticmethod
    def post(request):
        form = RegisterForm(request.POST)

        if not form.is_valid():
            print(form.errors)
            return JsonResponse({}, status=400)

        try:
            user = form.save(commit=False)
            user.is_active = False
            user.set_password(user.password)
            user.save()

            sendCodeToEmail(request.META["REMOTE_ADDR"], user.email)
        except Exception as e:
            print(e)
            return JsonResponse({}, status=400)

        return JsonResponse(ClientSerializer(user).data, status=201)
    

class RegisterCodeView(View):
    @staticmethod
    def post(request):
        form = CodeFromEmailForm(request.POST)

        if not form.is_valid():
            print(form.errors)
            return JsonResponse({}, status=400)
        
        email, code = cache.get(request.META["REMOTE_ADDR"], ("NoEmail", None), 2)
        
        if code is None:
            print("Код не найден")
            return JsonResponse({}, status=404)
        
        if code != form.cleaned_data["code"]:
            print("Неправильный код")
            return JsonResponse({}, status=400)
        
        try:
            user = Client.objects.get(email=email)
        except Exception as e:
            print(e)
            return JsonResponse({}, status=404)
        
        user.is_active = True
        user.save()

        login(request, user)

        cache.delete(request.META["REMOTE_ADDR"], 2)

        return JsonResponse({}, status=202)
    

class EditPasswordView(View):
    @staticmethod
    def post(request : HttpRequest):
        action = request.headers["action"]

        match action:
            case "email":
                form = OnlyEmailForm(request.POST)

                if not form.is_valid():
                    return JsonResponse({}, status=401)
                
                try:
                    Client.objects.get(email=form.cleaned_data["email"])
                except:
                    return JsonResponse({}, status=404)
                
                sendCodeToEmail(request.META["REMOTE_ADDR"], form.cleaned_data["email"])
                
                return JsonResponse({"email": form.cleaned_data["email"]}, status=200)
            case "code":
                form = CodeFromEmailForm(request.POST)

                if not form.is_valid():
                    return JsonResponse({}, status=401)
                
                print(request.META["REMOTE_ADDR"])
                email, code = cache.get(request.META["REMOTE_ADDR"], ("NoEmail", None), 2)

                if code is None:
                    print("Код не найден")
                    return JsonResponse({}, status=404)
                
                if code != form.cleaned_data["code"]:
                    print("Неправильный код")
                    return JsonResponse({}, status=400)
                
                cache.set(request.META["REMOTE_ADDR"], email, 60*5, 3)
                
                return JsonResponse({}, status=200)
            case "password":
                form = NewPasswordForm(request.POST)

                if not form.is_valid():
                    return JsonResponse({}, status=401)
                
                email = cache.get(request.META["REMOTE_ADDR"], None, 3)

                if email is None:
                    return JsonResponse({}, status=404)
                
                user = Client.objects.get(email=email)

                user.set_password(form.cleaned_data["password"])
                user.save()

                cache.delete(request.META["REMOTE_ADDR"], 3)
                
                return JsonResponse({}, status=200)
            case _:
                return JsonResponse({}, status=401)
        

class AddShortView(View):
    @staticmethod
    def post(request):
        form = AddShortForm(request.POST, request.FILES)

        if not form.is_valid():
            print(form.errors)
            return JsonResponse({}, status=400)
        
        try:
            short = form.save(commit=False)
            short.client = Client.objects.get(username=request.user)
            short.save()
        except Exception as e:
            print(e)
            return JsonResponse({}, status=400)
        
        return JsonResponse({}, status=201)


class ShortRatingView(View):
    @staticmethod
    def post(request: HttpRequest):
        if not request.user.is_authenticated:
            return JsonResponse({}, status=401)
            
        data = json.loads(request.body)
        action = data["action"]
        short_id = Short.objects.only("id").get(title=data["title"]).id
        client_id = Client.objects.only("id").get(username=request.user).id

        match action:
            case "plus":
                try:
                    short_rating = ShortRating.objects.get(short_id=short_id, client_id=client_id)
                except Exception as e:
                    short_rating = ShortRating.objects.create(short_id=short_id, client_id=client_id, rating=1)
                    tasks.editShortRating.delay(short_id)
                    return JsonResponse({}, status=201)

                match short_rating.rating:
                    case 1:
                        short_rating.rating = 0
                    case 0:
                        short_rating.rating = 1
                    case -1:
                        short_rating.rating = 1
                
                short_rating.save()

                tasks.editShortRating.delay(short_id)

                return JsonResponse({}, status=202)
            case "minus":
                try:
                    short_rating = ShortRating.objects.get(short_id=short_id, client_id=client_id)
                except Exception as e:
                    short_rating = ShortRating.objects.create(short_id=short_id, client_id=client_id, rating=-1)
                    tasks.editShortRating.delay(short_id)
                    return JsonResponse({}, status=201)
                
                match short_rating.rating:
                    case 1:
                        short_rating.rating = -1
                    case 0:
                        short_rating.rating = -1
                    case -1:
                        short_rating.rating = 0

                short_rating.save()

                tasks.editShortRating.delay(short_id)

                return JsonResponse({}, status=202)
            case _:
                return JsonResponse({}, status=400)
