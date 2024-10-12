from django.db.transaction import atomic
from rest_framework import serializers

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
        read_only_fields = ("actual_return_date",)


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

    def update(self, instance, validated_data):
        instance.return_book()

        return instance
