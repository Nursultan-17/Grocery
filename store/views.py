from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth import logout
from django.http import HttpResponse
from .models import *

def signInView(request):
    if request.method == 'GET':
        context = {
            'categories': Category.objects.all(),


        }
        return render(request=request, template_name='sign_in.html', context=context)
    if request.method == 'POST':
        Nickname = request.POST.get('Nickname')
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = authenticate(email=email, password=password)
        # authenticate - Если найден юзер в БД с таким имейлом и паролем то возвращает его, иначе None
        if user is not None:
            login(request, user)
            if 'Nickname' not in request.session.keys():
                request.session['Nickname'] = Nickname
                request.session.modified = True
            return redirect('home_url')
        context = {
            'error': 'Не верный логин и/или пароль',
            'email': email,
            'categories': Category.objects.all(),
            'Nickname': request.session['Nickname'],

        }
        return render(request=request, template_name='sign_in.html', context=context)


def homeView(request):
    if 'cart' in request.session.keys():
        context = {
            'categories': Category.objects.all(),
            'cart': request.session['cart'],
            'Nickname': request.session['Nickname'],

        }
    elif 'Nickname' in request.session.keys():
            context = {
                'categories': Category.objects.all(),
                'Nickname': request.session['Nickname'],
            }
    else:
            context = {
                'categories': Category.objects.all(),

        }
    return render(request=request, template_name='home.html', context=context)


def signUpView(request):
    if request.method == 'GET':
        context = {
            'categories': Category.objects.all(),
        }
        return render(request=request, template_name='sign_up.html', context=context)
    elif request.method == 'POST':
        email = request.POST.get('email')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        password = request.POST.get('password')
        phone = request.POST.get('phone')
        birth_date = request.POST.get('birth_date')
        try:
            Customer.object.get(email=email)
        except Customer.DoesNotExist:
            customer = Customer(
                email=email,
                first_name=first_name,
                last_name=last_name,
                phone=phone,
                birth_date=birth_date
            )
            customer.set_password(password)
            customer.save()
            return redirect('sign_in_url')
        else:
            context = {
                'error': 'This email is already taken!',
                'email': email,
                'first_name': first_name,
                'last_name': last_name,
                'phone': phone,
                'birth_date': birth_date,
                'categories': Category.objects.all(),
            }
    return render(request=request, template_name='sign_up.html', context=context)


def signOutView(request):
    logout(request)# Встроенная функция, которая выкидывает из системы юзера(Видит юзера по request.user)
    return redirect('home_url')  # Перенаправляем по url 'home_url'


def productsView(request):
    if 'Nickname' in request.session.keys():
        context = {
            'categories': Category.objects.all(),
            'products': Product.objects.all(),
            'category': 'All Products',
            'Nickname': request.session['Nickname'],
        }
    else:
        context = {
            'categories': Category.objects.all(),
            'products': Product.objects.all(),
            'category': 'All Products',
        }
    return render(request=request, template_name='products.html', context=context)


def addToCartView(request, product_id):
    if 'cart' not in request.session.keys():
        request.session['cart'] = [product_id]
    else:
        request.session['cart'].append(product_id)
        request.session.modified = True
    return HttpResponse()


def cartDetailView(request):
    if request.method == 'GET':
        if 'Nickname' in request.session.keys():
            context = {
                'categories': Category.objects.all(),
                'Nickname': request.session['Nickname'],
            }
        else:
            context = {
                'categories': Category.objects.all(),
            }
            total = 0
            if 'cart' in request.session.keys():
                context['cart'] = []
                count = 1
                for product_id in request.session['cart']:
                    product = Product.objects.get(id=product_id)
                    product.count = count  # Создаем у объекта новый атрибут, его не будет в бд, только на этот вью
                    context['cart'].append(product)
                    count += 1
                    total += product.price
            context['total'] = total
        return render(request=request, template_name='cart.html', context=context)
    elif request.method == 'POST':
        total = int(request.POST.get('total'))
        if request.user.wallet >= total:
            request.user.wallet -= total
            request.user.save()
            request.session.pop('cart')
            return redirect('profile_url')
        else:
            context = {
                'categories': Category.objects.all(),
                'error': 'Balance on you Wallet is not enough!',
                'Nickname': request.session['Nickname'],
            }
            if 'cart' in request.session.keys():
                context['cart'] = []
                count = 1
                for product_id in request.session['cart']:
                    product = Product.objects.get(id=product_id)
                    product.count = count  # Создаем у объекта новый атрибут, его не будет в бд, только на этот вью
                    context['cart'].append(product)
                    count += 1
                context['total'] = total
            return render(request=request, template_name='cart.html', context=context)


def profileView(request):
    if request.user.is_authenticated:
        context = {
            'categories': Category.objects.all(),
            'Nickname': request.session['Nickname'],
        }
        return render(request=request, template_name='profile.html', context=context)
    return redirect('sign_in_url')


def productsByCategoryView(request, category_id):
    category = Category.objects.get(id=category_id)
    products = Product.objects.filter(category=category)
    if 'Nickname' in request.session.keys():
        context = {
            'categories': Category.objects.all(),
            'products': products,
            'category': category.name,
            'Nickname': request.session['Nickname'],
        }
    else:
        context = {
            'categories': Category.objects.all(),
            'products': products,
            'category': category.name,
        }
    return render(request=request, template_name='products.html', context=context)

def about_us_view(request):
    if 'Nickname' in request.session.keys():
        context = {
            'categories': Category.objects.all(),
            'Nickname': request.session['Nickname'],
        }
    else:
        context = {
            'categories': Category.objects.all(),
        }
    return render(request=request,template_name='about_us.html',context=context)

def productDetailView(request,product_id):
    product = Product.objects.get(id=product_id)
    print(HttpResponse())
    if 'Nickname' in request.session.keys():
        context = {
            'product': product,
            'Nickname': request.session['Nickname'],
        }
    else:
        context = {
            'product': product,
        }
    return render(request=request,template_name='product_detail.html',context=context)
