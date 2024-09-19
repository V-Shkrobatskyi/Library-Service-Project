from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from borrowing.models import Borrowing
from borrowing.serializers import (
    BorrowingSerializer,
    BorrowingCreateSerializer,
    BorrowingReturnSerializer,
)


class BorrowingViewSet(viewsets.ModelViewSet):
    queryset = Borrowing.objects.all()
    serializer_class = BorrowingSerializer
    permission_classes = (IsAuthenticated,)

    def get_serializer_class(self):
        if self.action == "create":
            return BorrowingCreateSerializer
        if self.action == "return_borrowing":
            return BorrowingReturnSerializer
        return BorrowingSerializer

    def get_queryset(self):
        queryset = self.queryset
        is_active = self.request.query_params.get("is_active")
        user_id = self.request.query_params.get("user_id")
        user = self.request.user

        if is_active:
            queryset = queryset.filter(actual_return_date__isnull=True)

        if user_id and user.is_staff:
            queryset = queryset.filter(user__id=user_id)

        if not user.is_staff:
            return queryset.filter(user=user).select_related("user")

        return queryset

    def perform_create(self, serializer):
        user = self.request.user
        serializer.save(user=user)
