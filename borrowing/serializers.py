from django.db.transaction import atomic
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from book.serializers import BookSerializer
from borrowing.models import Borrowing
from payment.models import Payment
from payment.stripe_payment import create_stripe_session


class BorrowingSerializer(serializers.ModelSerializer):
    book = BookSerializer(read_only=True)
    user = serializers.CharField(read_only=True, source="user.email")

    class Meta:
        model = Borrowing
        fields = (
            "id",
            "borrow_date",
            "expected_return_date",
            "actual_return_date",
            "book",
            "user",
        )


class BorrowingCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Borrowing
        fields = (
            "id",
            "book",
            "expected_return_date",
        )

    def validate(self, attrs):
        data = super(BorrowingCreateSerializer, self).validate(attrs)

        user = self.context["request"].user
        pending_payment = Payment.objects.filter(
            borrowing__user=user,
            status__in=(
                Payment.StatusChoices.PENDING,
                Payment.StatusChoices.EXPIRED,
            ),
        ).first()

        if pending_payment:
            raise ValidationError(
                {
                    "You cannot borrow new books until pending/expired payment exist. "
                    "Detail of your the payment:": [
                        f"id: {pending_payment.id}",
                        f"status: {pending_payment.status}",
                        f"type: {pending_payment.type}",
                        f"money to pay: {pending_payment.money_to_pay}",
                        f"session id: {pending_payment.session_id}",
                        f"session url: {pending_payment.session_url}",
                        f"borrowing book: {pending_payment.borrowing.book}",
                    ]
                }
            )

        Borrowing.validate_borrowing(
            attrs["book"].inventory, serializers.ValidationError
        )

        return data

    @atomic
    def create(self, validated_data):
        book = validated_data["book"]
        Borrowing.book_borrowing(book)

        borrowing = Borrowing.objects.create(**validated_data)
        request = self.context.get("request")
        borrowing_days = borrowing.get_borrowing_days()
        borrowing_price = borrowing.get_price()

        create_stripe_session(
            borrowing,
            request,
            Payment.TypeChoices.PAYMENT,
            borrowing_price,
            borrowing_days,
        )

        return borrowing


class BorrowingReturnSerializer(serializers.ModelSerializer):
    class Meta:
        model = Borrowing
        fields = ("id",)

    def validate(self, attrs):
        data = super(BorrowingReturnSerializer, self).validate(attrs)
        borrowing = self.instance
        actual_return_date = borrowing.actual_return_date

        if borrowing.actual_return_date:
            raise serializers.ValidationError(
                {
                    f"Borrowing: {borrowing}": f"The borrowing already returned on {actual_return_date}."
                }
            )

        return data

    @atomic
    def update(self, instance, validated_data):
        instance.return_book()

        if instance.actual_return_date.date() > instance.expected_return_date.date():
            request = self.context["request"]

            overdue_days = instance.get_overdue_days()
            overdue_price = instance.get_overdue_price()

            create_stripe_session(
                instance, request, Payment.TypeChoices.FINE, overdue_price, overdue_days
            )

        return instance
