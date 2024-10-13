import stripe
from django.db.transaction import atomic
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from borrowing.serializers import BorrowingSerializer
from payment.models import Payment
from payment.serializers import (
    PaymentSerializer,
    PaymentDetailSerializer,
    PaymentSuccessSerializer,
)
from payment.stripe_payment import create_stripe_session


class PaymentViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Payment.objects.select_related("borrowing")
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        user = self.request.user

        if not self.request.user.is_staff:
            return self.queryset.filter(borrowing__user=user)

        return self.queryset

    def get_serializer_class(self):
        if self.action == "retrieve":
            return PaymentDetailSerializer
        if self.action == "success":
            return PaymentSuccessSerializer

        return PaymentSerializer

    @action(methods=["GET"], url_path="success", detail=False)
    def success(self, request, session_id=None):
        session_id = request.query_params.get("session_id", None)
        if not session_id:
            return Response(
                {"message": "Payment parameter not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        payment = get_object_or_404(
            Payment,
            session_id=request.GET.get("session_id"),
            status=Payment.StatusChoices.PENDING,
            type=Payment.TypeChoices.PAYMENT,
        )
        session = stripe.checkout.Session.retrieve(session_id)

        if session["status"] == "complete":
            data = {
                "status": Payment.StatusChoices.PAID,
                "type": Payment.TypeChoices.PAYMENT,
            }
            serializer = self.get_serializer(payment, data=data)
            borrowing = payment.borrowing

            if serializer.is_valid():
                serializer.save()
                borrowing.return_book()

                return Response(serializer.data, status=status.HTTP_200_OK)

            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        return Response(status=status.HTTP_404_NOT_FOUND)

    @action(methods=["GET"], url_path="cancel", detail=False)
    def cancel(self, request):
        raise ValidationError(
            "Payment can be paid a bit later, but the session is available for only 24h."
        )

    @action(
        detail=False,
        methods=["GET"],
        url_path="renew",
    )
    @atomic
    def renew_session(self, request, pk=None):
        user = request.user
        payment = Payment.objects.filter(
            status=Payment.StatusChoices.EXPIRED, borrowing__user=user
        ).first()

        if payment:
            if payment.type == Payment.TypeChoices.PAYMENT:
                days = payment.borrowing.get_borrowing_days()
            else:
                days = payment.borrowing.get_overdue_days()

            new_session = create_stripe_session(
                payment.borrowing, request, payment.type, payment.money_to_pay, days
            )

            payment.session_url = new_session.url
            payment.session_id = new_session.id
            payment.status = Payment.StatusChoices.PENDING
            payment.save()

            borrowing_data = BorrowingSerializer(payment.borrowing).data
            return Response(
                {
                    "detail:": "Payment session renewed.",
                    "id": payment.id,
                    "new status": payment.status,
                    "type": payment.type,
                    "money to pay": payment.money_to_pay,
                    "new session id": payment.session_id,
                    "new session url": payment.session_url,
                    "borrowing": borrowing_data,
                }
            )
        return Response(
            {"detail": "There is no expired payment session."},
            status=status.HTTP_404_NOT_FOUND,
        )
