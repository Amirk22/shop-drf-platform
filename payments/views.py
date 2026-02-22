from django.db import transaction
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from orders.models import Cart , CartItem
from rest_framework import generics, permissions
from .serializers import *
from django.db.models import F

# Create your views here.


class CheckoutView(APIView):
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def post(self, request):
        cart = Cart.objects.filter(user=request.user).first()

        if not cart or not cart.items.exists():
            return Response({"detail": "Cart is empty"}, status=400)

        total_amount = 0

        order = Order.objects.create(
            user=request.user,
            total_amount=0
        )

        for item in cart.items.select_related("product"):
            if item.quantity > item.product.inventory:
                return Response(
                    {"detail": f"Not enough inventory for {item.product.title}"},
                    status=400
                )

            OrderItem.objects.create(
                order=order,
                product=item.product,
                quantity=item.quantity,
                price=item.product.price
            )

            total_amount += item.product.price * item.quantity

        order.total_amount = total_amount
        order.save()

        payment = Payment.objects.create(
            order=order,
            amount=total_amount
        )

        return Response({
            "order_id": order.id,
            "payment_id": payment.id,
            "amount": payment.amount,
            "status": payment.status
        }, status=201)


class PaymentSuccessView(APIView):
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def post(self, request, order_id):
        order = Order.objects.select_for_update().get(
            id=order_id,
            user=request.user
        )

        if order.status != "pending":
            return Response({"detail": "Order already processed"}, status=400)

        payment = getattr(order, "payment", None)
        if not payment:
            return Response({"detail": "Payment not found"}, status=400)

        for item in order.items.select_related("product"):
            if item.quantity > item.product.inventory:
                return Response(
                    {"detail": f"Inventory changed for {item.product.title}"},
                    status=400
                )

            item.product.inventory = F("inventory") - item.quantity
            item.product.save()
            item.product.refresh_from_db()

        payment.status = "success"
        payment.save()

        order.status = "paid"
        order.save()

        CartItem.objects.filter(cart__user=request.user).delete()

        return Response({"detail": "Payment successful"})


class PaymentFailView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, order_id):
        order = get_object_or_404(Order, id=order_id, user=request.user)

        if order.status != "pending":
            return Response({"detail": "Order already processed"}, status=400)

        order.status = "failed"
        order.save()

        order.payment.status = "failed"
        order.payment.save()

        return Response({"detail": "Payment failed"})


class OrderDetailView(generics.RetrieveAPIView):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)


class PaymentView(generics.ListAPIView):
    serializer_class = PaymentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Payment.objects.filter(order__user=self.request.user)

class PaymentDetailView(generics.RetrieveAPIView):
    serializer_class = PaymentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Payment.objects.filter(order__user=self.request.user)