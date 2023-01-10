import random
import string

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages

from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone
from django.views.generic import ListView, DetailView, View
from django.contrib.auth import login, authenticate, logout #add this
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Item, UserProfile, OrderItem, Order
from .forms import SignUpForm, SignInForm


# Create your views here.




# def create_ref_code():
#     return ''.join(random.choice(string.ascii_lowercase + string.digits, k =20))


# def products(request):
#     context = {
#         'items': Item.objects.all( )
#     }
#     return render(request, "product.html", context)


# def is_valid_form(values):
#     valid = True
#     for field in values:
#         if field == '':
#             valid = False
#     return valid






class SigninPageView(View):
    template_name = 'signin.html'
    form_class = SignInForm

    def get(self, request):
        form = self.form_class()
        message = 'Login Page'
        return render(request, self.template_name, context={'form': form, 'message': message})

    def post(self, request):
        form = self.form_class(request.POST)
        if form.is_valid():

            print(form.cleaned_data['username'])
            user = authenticate(
                username=form.cleaned_data['username'],
                password=form.cleaned_data['password'],
            )
        
            if user is not None:
                login(request, user)
                return redirect('core:home')
        message = 'Login failed'

        return render(request, self.template_name, context={'form':form, 'message':message})

class SignupPageView(View):
    template_name = 'signup.html'
    form_class = SignUpForm

    def get(self, request):
        form = self.form_class()
        message = {'Signup Page'}
        return render(request, self.template_name, context={'form': form, 'message': message})

    def post(self, request):
        form = self.form_class(request.POST)
       
        if form.is_valid():
            user = form.save()
            # print(user)
            user = authenticate(
                username=form.cleaned_data['username'],
                password=form.cleaned_data['password1'],
            )

            print(user)

            if user is not None:
                login(request, user)
                return redirect('core:home')
        message = 'Registration failed'
        return render(request, self.template_name, context={'form':form, 'message':message})



@login_required
def signout(request):
    logout(request)
    messages.info(request, "You have successfully logged out.") 
    return redirect("core:home")


class ProductView(ListView):
    model = Item
    paginate_by = 1
    template_name = "product.html"


class HomeProductView(ListView):
    model = Item
    template_name = "home.html"
    traditional = []
    normal = []


    def get_context_data(self, **kwargs):
        context = super(HomeProductView, self).get_context_data(**kwargs)
        if not self.traditional:
            self.traditional = Item.objects.filter(category__icontains='S')
        # print(Item.objects.filter(category__icontains='S'))
        if not self.normal:
            self.normal = Item.objects.filter(category__icontains='Ow')
        context.update({
            'traditional': self.traditional,
            'normal':self.normal
        })
    
        return context

class ProductDetails(DetailView):
    model = Item
    template_name = "single-product.html"



class OrderSummaryView(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        try:
            order = Order.objects.get(user = self.request.user, ordered = False)
            context = {
                'object': order
            }
            return render(self.request, 'cart.html', context)
        except ObjectDoesNotExist:
            messages.warning(self.request, "You do not have active order")
            return redirect('core:home')




@login_required
def add_to_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_item, created = OrderItem.objects.get_or_create(
        item = item,
        user = request.user,
        ordered = False
    )

    order_qs = Order.objects.filter(user=request.user, ordered=False)
    if order_qs.exists():
        order = order_qs[0]
        if order.items.filter(item__slug=item.slug).exists():
            order_item.quantity += 1
            order_item.save()
            messages.info(request, "This item quantity was updated.")
            return redirect("core:cart")
        else:
            order.items.add(order_item)
            messages.info(request, "This item was added to your cart.")
    else:
        ordered_date = timezone.now()
        order = Order.objects.create(user = request.user, ordered_date=ordered_date)
        order.items.add(order_item)
        messages.info(request, "This item was added to your cart.")
        return  redirect("core:cart")



@login_required
def remove_from_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_qs = Order.objects.filter(
        user = request.user,
        ordered = False
    )
    if order_qs.exists():
        order = order_qs[0]
        #chech if the order item is in the order
        if order.items.filter(item__slug=item.slug).exists():
            order_item =OrderItem.objects.filter(
                item=item,
                user=request.user,
                ordered=False
            )[0]
            order.items.remove(order_item)
            order_item.delete()
            messages.info(request, "This item was removed from your cart.")
            return redirect("core:cart")
        else:
            messages.info(request, "This item was not in your cart")
            return redirect("core:product", slug=slug)
    else:
        messages.info(request, "You do not have an active order")
        return  redirect("core:product", slug=slug)
        

@login_required
def remove_single_item_from_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_qs = Order.objects.filter(
        user=request.user,
        ordered=False
    )
    if order_qs.exists():
        order = order_qs[0]
        #chech if the order item is in the order 
        if order.items.filter(item__slug=item.slug).exists():
            order_item = OrderItem.objects.filter(
                item=item,
                user=request.user,
                ordered=False
            )[0]
            if order_item.quantity > 1:
                order_item.quantity -= 1
                order_item.save()
            else:
                order.items.remove(order_item)
            messages.info(request, "This item quantity was updated.")
            return redirect("core:cart")
        else:
            messages.info(request, "This item was not in your cart")
            return redirect("core:product", slug=slug)
    else:
        messages.info(request, "You do not have an active order")
        return redirect("core:product", slug=slug)

    


    
