from rest_framework import generics, status, filters
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny, IsAuthenticatedOrReadOnly
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import Group, User
from .serializers import OrderSerializer, MenuItemSerializer, RegisterSerializer, CategorySerializer, CartSerializer
from .models import MenuItem, Category, OrderItem
from datetime import date

# User can view, managers can edit
class MenuItemView(generics.ListCreateAPIView):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['price']

# Check if is Manager
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def manager_view(request):
    if request.user.groups.filter(name='Manager').exists():
        return Response({'message': 'You are a manager ✅'})
    return Response({'message': 'You are not a manager ❌'}, status=status.HTTP_403_FORBIDDEN)


# Admin 管理员可以添加或删除 Manager 组用户
@api_view(['POST', 'DELETE'])
@permission_classes([IsAdminUser])
def managers(request):
    username = request.data.get('username')

    if not username:
        return Response({'error': 'username is required'}, status=status.HTTP_400_BAD_REQUEST)

    user = get_object_or_404(User, username=username)
    group = get_object_or_404(Group, name='Manager')

    if request.method == 'POST':
        group.user_set.add(user)
        return Response({'message': f'✅ {username} added to Manager group'}, status=status.HTTP_201_CREATED)

    elif request.method == 'DELETE':
        group.user_set.remove(user)
        return Response({'message': f'❌ {username} removed from Manager group'}, status=status.HTTP_200_OK)
    

# 6.	Managers can update the item of the day

@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def update_item_of_the_day(request, pk):
    # 只允许 Manager
    if not request.user.groups.filter(name='Manager').exists():
        return Response({'detail': 'You are not a manager.'}, status=status.HTTP_403_FORBIDDEN)
    
    menu_item = get_object_or_404(MenuItem, pk=pk)
    featured = request.data.get('featured', None)
    if featured is not None:
        menu_item.featured = featured
        menu_item.save()
        return Response({'message': f'{menu_item.title} updated', 'featured': menu_item.featured})
    return Response({'error': 'Missing featured field'}, status=status.HTTP_400_BAD_REQUEST)

#7. Managers can assign users to the Delivery Crew
@api_view(['POST', 'DELETE'])
@permission_classes([IsAuthenticated])
def delivery_crew_users(request):
    # 只允许 Manager 操作
    if not request.user.groups.filter(name='Manager').exists():
        return Response({'detail': 'You are not a manager.'}, status=status.HTTP_403_FORBIDDEN)
    
    username = request.data.get('username')
    if not username:
        return Response({'error': 'username is required'}, status=status.HTTP_400_BAD_REQUEST)

    user = get_object_or_404(User, username=username)
    delivery_group, created = Group.objects.get_or_create(name='Delivery Crew')

    if request.method == 'POST':
        delivery_group.user_set.add(user)
        return Response({'message': f'{username} added to Delivery Crew group'})
    elif request.method == 'DELETE':
        delivery_group.user_set.remove(user)
        return Response({'message': f'{username} removed from Delivery Crew group'})
    
#8 Managers can assign orders to the Delivery Crew

from .models import Order

@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def assign_order_to_delivery(request, order_id):
    if not request.user.groups.filter(name='Manager').exists():
        return Response({'detail': 'You are not a manager.'}, status=status.HTTP_403_FORBIDDEN)
    
    username = request.data.get('username')
    if not username:
        return Response({'error': 'username is required'}, status=status.HTTP_400_BAD_REQUEST)

    user = get_object_or_404(User, username=username)
    order = get_object_or_404(Order, id=order_id)

    # 确保这个用户是配送组成员
    if not user.groups.filter(name='Delivery Crew').exists():
        return Response({'error': f'{username} is not in Delivery Crew'}, status=status.HTTP_400_BAD_REQUEST)

    order.delivery_crew = user
    order.save()
    return Response({'message': f'Order {order_id} assigned to {username}'})


#9. Delivery Crew can view orders assigned to them

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def delivery_orders(request):
    user = request.user
    # ✅ Only show orders assigned to the logged-in delivery crew
    if user.groups.filter(name='Delivery crew').exists():
        orders = Order.objects.filter(delivery_crew=user)
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data)
    return Response({'detail': 'You are not in the Delivery crew'}, status=status.HTTP_403_FORBIDDEN)

#-------------------------------

#10 Delivery Crew can mark an order as delivered


@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def mark_order_delivered(request, order_id):
    # Check if user is in Delivery Crew group
    if not request.user.groups.filter(name='Delivery Crew').exists():
        return Response({'detail': 'You are not in the Delivery Crew.'}, status=403)
    
    order = get_object_or_404(Order, id=order_id)

    # Only allow updating if the order is assigned to this user
    if order.delivery_crew != request.user:
        return Response({'detail': 'This order is not assigned to you.'}, status=403)
    
    order.status = True
    order.save()
    return Response({'message': f'Order {order_id} marked as delivered.'}, status=200)


#11 Register

@api_view(['POST'])
@permission_classes([AllowAny])  # Anyone can register
def register(request):
    serializer = RegisterSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response({'message': 'User registered successfully'}, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#13 browse all categories

class CategoryListView(generics.ListAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

#18- 19 Cart API

from .models import Cart
from .serializers import CartSerializer

@api_view(['GET', 'POST', 'DELETE'])
@permission_classes([IsAuthenticated])
def cart_view(request):
    user = request.user
    if request.method == 'GET':
        items = Cart.objects.filter(user=user)
        serializer = CartSerializer(items, many=True)
        return Response(serializer.data)
    
    elif request.method == 'POST':
        data = request.data.copy()
        data['user'] = user.id
        serializer = CartSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)

    elif request.method == 'DELETE':
        Cart.objects.filter(user=user).delete()
        return Response({'message': 'Cart cleared'})
    

#19-20 Customer Order place and view

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def orders_view(request):
    user = request.user

    # 🧾 GET - Show user's own orders
    if request.method == 'GET':
        orders = Order.objects.filter(user=user)
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data)

    # ➕ POST - Place a new order
    elif request.method == 'POST':
        cart_items = Cart.objects.filter(user=user)
        if not cart_items.exists():
            return Response({'message': 'Cart is empty'}, status=status.HTTP_400_BAD_REQUEST)

        # Calculate total
        total = sum(item.price for item in cart_items)

        # Create order
        order = Order.objects.create(
            user=user,
            total=total,
            date=date.today()
        )

        # Create order items
        for item in cart_items:

            OrderItem.objects.create(
                order=order,
                menuitem=item.menuitem,
                quantity=item.quantity,
                unit_price=item.unit_price,
                price=item.price
            )   

        # Clear cart
        cart_items.delete()

        serializer = OrderSerializer(order)
        return Response(serializer.data, status=status.HTTP_201_CREATED)