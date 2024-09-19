from rest_framework import serializers

from book.serializers import BookSerializer
from borrowing.models import Borrowing


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

    def create(self, validated_data):
        book = validated_data["book"]
        Borrowing.book_borrowing(book)

        borrowing = Borrowing.objects.create(**validated_data)

        return borrowing
