from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import *
from .models import Payment
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import json
from payment.payze.client import Payze
from payment.payze.param import PayzeOPS, request as payze_req

import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)





payze = Payze(
    ops=PayzeOPS(
        url="https://payze.io",
        auth_token="0C86926CF5A2439CAC39A474CE574EFC:A7B8DB88CA414B048B13F85D85BDEBAB",
        hooks=payze_req.Hooks(
            web_hook_gateway="https://720f-213-230-125-98.ngrok-free.app/v1/webhook/payze/success",
            error_redirect_gateway="https://noxonfx.uz/",
            success_redirect_gateway="https://noxonfx.uz/",
        )
    )
)



#
# class PaymentView(APIView):
#     def post(self, request):
#         serializer = PaymentSerializer(data=request.data)
#         if serializer.is_valid():
#             amount = serializer.validated_data['amount']
#             order_id = serializer.validated_data['order_id']
#
#             response = payze.create_transaction(
#                 amount=amount,
#                 order_id=order_id
#             )
#
#             transaction_id = response.get('transaction_id')
#             if transaction_id:
#                 payment = Payment.objects.create(
#                     transaction_id=transaction_id,
#                     amount=amount,
#                     order_id=order_id,
#                     card_number=card_number,
#                     status='pending'
#                 )
#                 return Response({'transaction_id': transaction_id}, status=status.HTTP_201_CREATED)
#             else:
#                 return Response({'error': 'Transaction creation failed'}, status=status.HTTP_400_BAD_REQUEST)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#
#
#     def put(self, request, transaction_id):
#         try:
#             payment = Payment.objects.get(transaction_id=transaction_id)
#         except Payment.DoesNotExist:
#             return Response({'error': 'Payment not found'}, status=status.HTTP_404_NOT_FOUND)
#
#         payment_status = request.data.get('status')
#         if payment_status in ['success', 'failure']:
#             payment.status = payment_status
#             payment.save()
#             return Response({'status': 'Payment updated'}, status=status.HTTP_200_OK)
#         return Response({'error': 'Invalid status'}, status=status.HTTP_400_BAD_REQUEST)
#
#

class PaymentView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = PaymentRequestSerializer(data=request.data)
        if serializer.is_valid():
            order_id = serializer.validated_data['order_id']
            amount = serializer.validated_data['amount']

            metadata = payze_req.Metadata(
                order=payze_req.Order(order_id),
            )

            req_params = payze_req.JustPay(
                amount=int(amount),
                metadata=metadata,
            )

            try:
                resp = payze.just_pay(
                    req_params=req_params
                )
                logger.info(f"Payze response: {resp}")

                payment_url = resp.data.payment.payment_url

                try:
                    transaction_id = resp.data.payment.transaction_id
                except AttributeError:
                    transaction_id = None

                Payment.objects.create(order_id=order_id, amount=amount, transaction_id=transaction_id)

                return Response({'payment_url': payment_url}, status=status.HTTP_200_OK)
            except Exception as e:
                logger.error(f"Error during payment initiation: {e}")
                return Response({'error': 'Payment initiation failed.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)




@csrf_exempt
def payze_webhook(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        transaction_id = data.get('transaction_id')
        status = data.get('status')

        try:
            payment = Payment.objects.get(transaction_id=transaction_id)
            payment.status = status
            payment.save()
            return JsonResponse({'status': 'success'}, status=200)
        except Payment.DoesNotExist:
            return JsonResponse({'error': 'Payment not found'}, status=404)

    return JsonResponse({'error': 'Invalid request'}, status=400)