from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from .views import (

    # signup,
    signout,
    ProductView,
    HomeProductView,
    ProductDetails,
    SignupPageView,
    SigninPageView,
    add_to_cart,
    OrderSummaryView
    )


app_name = 'core'

urlpatterns = [
    path('', HomeProductView.as_view() , name='home'),
    path('signin/', SigninPageView.as_view(), name='signin'),
    path('siginup/', SignupPageView.as_view(), name='signup'),
    path('signout/', signout , name='signout'),
    path('product/',ProductView.as_view(), name='product' ),
    path('product/<slug:slug>',ProductDetails.as_view(), name='single-product'),
    path('add-to-cart/<slug:slug>/', add_to_cart, name='add-to-cart'),
    path('cart/', OrderSummaryView.as_view(), name='cart'),
    
]

# if settings.DEBUG:
#     import debug_toolbar
    # urlpatterns += [path('__debug__/', include(debug_toolbar.urls))]
# urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

