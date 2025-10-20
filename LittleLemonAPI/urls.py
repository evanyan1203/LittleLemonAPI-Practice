from django.urls import path
from . import views
from rest_framework.authtoken.views import obtain_auth_token
urlpatterns = [
    path('menu-items/', views.MenuItemView.as_view(), name='menu-items'),
    path('groups/manager/users/', views.managers, name='manager-users'),
    path('manager-view/', views.manager_view, name='manager-view'), 
    path('api-token-auth/', obtain_auth_token), # see tokens
    path('menu-items/<int:pk>/featured/', views.update_item_of_the_day),#6
    path('groups/delivery-crew/users/', views.delivery_crew_users),#7
    path('orders/<int:order_id>/assign/', views.assign_order_to_delivery),#8 assign orders  


    
    path('delivery/orders/', views.delivery_orders, name='delivery-orders'),# 9
    path('delivery/orders/<int:order_id>/delivered/', views.mark_order_delivered, name='mark-order-delivered'),#10

    path('register/', views.register, name='register'), #11

    path('categories/', views.CategoryListView.as_view(), name='categories'), #13

    path('cart/', views.cart_view, name='cart'), # 18 -19 cart

    path('orders/', views.orders_view, name='orders'),




]