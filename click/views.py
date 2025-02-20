from django.shortcuts import redirect
from rest_framework.generics import CreateAPIView
from click.serializers import *
from click.models import ClickOrder
from pyclick import PyClick
from pyclick.views import PyClickMerchantAPIView



class CreateClickOrderView(CreateAPIView):
    serializer_class = ClickOrderSerializer

    def post(self, request, *args, **kwargs):
        amount = request.POST.get('amount')
        order = ClickOrder.objects.create(amount=amount)
        return_url = 'http://127.0.0.1:8000/'
        url = PyClick.generate_url(order_id=order.id, amount=str(amount), return_url=return_url)
        return redirect(url)


class OrderCheckAndPayment(PyClick):
    def check_order(self, order_id: str, amount: str):
        if order_id:
            try:
                order = ClickOrder.objects.get(id=order_id)
                if int(amount) == order.amount:
                    return self.ORDER_FOUND
                else:
                    return self.INVALID_AMOUNT
            except ClickOrder.DoesNotExist:
                return self.ORDER_NOT_FOUND

    def successfully_payment(self, order_id: str, transaction: object):
        """ Эта функция вызывается после успешной оплаты """
        try:
            order = ClickOrder.objects.get(id=order_id)
            order.is_paid = True
            order.save()
        except ClickOrder.DoesNotExist:
            print(f"no order object not found: {order_id}")


class OrderTestView(PyClickMerchantAPIView):
    VALIDATE_CLASS = OrderCheckAndPayment
