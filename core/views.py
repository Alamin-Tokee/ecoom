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
from .models import Item, UserProfile, OrderItem, Order, Address
from .forms import SignUpForm, SignInForm, CheckoutForm, CouponForm


# Create your views here.




# def create_ref_code():
#     return ''.join(random.choice(string.ascii_lowercase + string.digits, k =20))


# def products(request):
#     context = {
#         'items': Item.objects.all( )
#     }
#     return render(request, "product.html", context)


def is_valid_form(values):
    valid = True
    for field in values:
        if field == '':
            valid = False
    return valid



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

    


    

class CheckoutView(View):
    @method_decorator(login_required)
    def get(self, *args, **kwargs):
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            form = CheckoutForm()

            context = {
                'form' : form, 
                'couponform' : CouponForm(),
                'order' : order,
                'DISPLAY_COUPON_FORM' : True
            }

            shipping_address_qs = Address.objects.filter(
                user = self.request.user,
                address_type = 'S',
                default = True
            )

            if shipping_address_qs.exists():
                context.update({'default_shipping_address': shipping_address_qs[0]})
            
            billing_address_qs = Address.objects.filter(
                user = self.request.user,
                address_type = 'B',
                default=True
            )

            if billing_address_qs.exists():
                context.update({'default_billing_address': billing_address_qs[0]})
            return render(self.request, "checkout.html", context)
        except ObjectDoesNotExist:
            messages.info(self.request, "You do not have an active order")
            return redirect('core:chechout')


    @method_decorator(login_required)    
    def post(self, *args, **kwargs):
        form = CheckoutForm(self.request.POST or None)
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            if form.is_valid():
                use_default_shipping = form.cleaned_data.get('use_default_shipping')
                if use_default_shipping:
                    print("Using the default shipping address")
                    address_qs = Address.objects.filter(
                        user = self.request.user,
                        address_type = 'S',
                        default=True
                    )
                    if address_qs.exists():
                        shipping_address = address_qs[0]
                        order.shipping_address = shipping_address
                        order.save()
                    else:
                        messages.info(self.request, "No default shipping address avaiable")
                        return redirect('core:checkout')
                else:
                    print("User is entering a new shipping address")
                    shipping_address1 = form.cleaned_data.get('shipping_address')
                    shipping_address2 = form.cleaned_data.get('shipping_address2')
                    shipping_country = form.cleaned_data.get('shipping_country')
                    shipping_zip = form.cleaned_data.get('shipping_zip')

                    if is_valid_form([shipping_address1, shipping_country, shipping_zip]):
                        shipping_address = Address(
                            user = self.request.user,
                            street_address = shipping_address1,
                            apartment_address = shipping_address2,
                            country = shipping_country,
                            zip = shipping_zip,
                            address_type = 'S'
                        )
                        shipping_address.save()

                        order.shipping_address = shipping_address
                        order.save()

                        set_default_shipping = form.cleaned_data.get('set_default_shipping')
                        if set_default_shipping:
                            shipping_address.default = True
                            shipping_address.save()
                    else:
                        messages.info(self.request, "Please fill in the required shipping address fields")
                    
                    use_default_shipping = form.cleaned_data.get('use_default_billing')
                    same_billing_address = form.cleaned_data.get('same_billing_address')

                    if same_billing_address:
                        billing_address = shipping_address
                        billing_address.pk = None
                        billing_address.save()
                        billing_address.address_type = 'B'
                        billing_address.save()
                        order.billing_address = billing_address
                        order.save()

                    elif use_default_shipping:
                        print("Using the default billing address")
                        address_qs = Address.objects.filter(
                            user = self.request.user,
                            address_type = 'B',
                            default = True
                        )

                        if address_qs.exists():
                            billing_address = address_qs[0]
                            order.billing_address = billing_address
                            order.save()
                        else:
                            messages.info(self.request, "No default billing address avaiable")
                            return redirect('core:chechkout')
                    else:
                        print("User is entering a new billing address")
                        billing_address1 = form.cleaned_data.get('billing_address')
                        billing_address2 = form.cleaned_data.get('billing_address2')
                        billing_country = form.cleaned_data.get('billing_country')
                        billing_zip = form.cleaned_data.get('billing_zip')

                        if is_valid_form([billing_address1, billing_country, billing_zip]):
                            billing_address = Address(
                                user = self.request.user,
                                street_address = billing_address1,
                                apartment_address = billing_address2,
                                country = billing_country, 
                                zip = billing_zip,
                                address_type = 'B'
                            )

                            billing_address.save()

                            order.billing_address = billing_address
                            order.save()

                            set_default_billing = form.cleaned_data.get('set_default_billing')
                            if set_default_billing:
                                billing_address.default = True
                                billing_address.save()
                        else:
                            messages.info(self.request, "Please fill in the required billing address fields")
                    

                    payment_option = form.cleaned_data.get('payement_option')

                    if payment_option == 'S':
                        return redirect('core:payment', payment_option='stripe')
                    elif payment_option == 'P':
                        return redirect('core:payment', payment_option='paypal')
                    else:
                        messages.warning(self.request, "Invalid payment option selected")
                        return redirect('core:checkout')

        except ObjectDoesNotExist:
            messages.warning(self.request, "You do not have an active order")
            return redirect("core:cart")



class PaymentView(View):
    def get(self, *args, **kwargs):
        order = Order.objects.get(user=self.request.user, ordered = False)
        if order.billing_address:
            context = {
                'order':order,
                'DISPLAY_COUPON_FORM':False,
                'STRIPE_PUBLIC_KEY':settings.STRIPE.PUBLIC_KEY
            }
            userprofile = self.request.user.userprofile
            if userprofile.one_click_purchasing:
                #fetch the users card list
                cards = stripe.Customer.list_sources(
                    userprofile.stripe_customer_id,
                    limit=3,
                    object='card'
                )
                card_list = cards['data']
                if len(card_list) > 0:
                    context.update({
                        'card':card_list[0]
                    })
            return render(self.request, "payment.html", context)
        else:
            messages.warning(self.request, "You have not added a billing address")
            return redirect("core:checkout")
        




def get_coupon(request, code):
    try:
        coupon = Coupon.objects.get(code=code)
        return coupon
    except ObjectDoesNotExist:
        messages.info(request, "This coupon does not exist")
        return redirect("core:checkout")


class AddCouponView(View):
    def post(self, *args, **kwargs):
        form = CouponForm(self.request.POST or None)
        if form.is_valid():
            try:
                code = form.cleaned_data.get('code')
                order = Order.objects.get(user = self.request.user, ordered = False)
                order.coupon = get_coupon(self.request, code)
                order.save()
                messages.success(self.request, "Successfully added coupon")
                return redirect("core:checkout")
            except ObjectDoesNotExist:
                messages.info(self.request, "You do not have an active order")
                return redirect("core:checkout")




    
