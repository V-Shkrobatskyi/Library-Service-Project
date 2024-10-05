from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated

from payment.models import Payment
from payment.serializers import (
    PaymentSerializer,
    PaymentDetailSerializer,
)


class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.select_related("borrowing")
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        user = self.request.user

        if not self.request.user.is_staff:
            return self.queryset.filter(borrowing__user=user)

        return self.queryset

    def get_serializer_class(self):
        if self.action in ("retrieve", "success"):
            return PaymentDetailSerializer

        return PaymentSerializer

    @action(methods=["GET"], url_path="success", detail=False)
    def success(self, request, session_id=None):
        pass

    @action(methods=["GET"], url_path="cancel", detail=False)
    def cancel(self, request):
        pass
