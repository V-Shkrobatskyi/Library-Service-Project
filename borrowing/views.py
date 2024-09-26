from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response

from borrowing.models import Borrowing
from borrowing.serializers import (
    BorrowingSerializer,
    BorrowingCreateSerializer,
    BorrowingReturnSerializer,
)
from borrowing.helpers.telegram import send_message


class BorrowingViewSet(viewsets.ModelViewSet):
    queryset = Borrowing.objects.all().select_related("book", "user")
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
        borrowing = serializer.save(user=user)
        message = (
            f"New borrowing:\n"
            f"book: {borrowing.book.title}\n"
            f"user: {borrowing.user}\n"
            f"borrow_date: {borrowing.borrow_date}\n"
            f"expected_return_date: {borrowing.expected_return_date}"
        )
        send_message(message)

    @action(
        detail=True,
        methods=["POST"],
        url_path="return",
        permission_classes=[IsAdminUser],
    )
    def return_borrowing(self, request, pk=None):
        borrowing = self.get_object()
        serializer = BorrowingReturnSerializer(
            borrowing,
            data=request.data,
            partial=True,
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
