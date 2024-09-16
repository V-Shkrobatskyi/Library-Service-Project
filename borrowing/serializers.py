from rest_framework import serializers

from book.serializers import BookSerializer
from borrowing.models import Borrowing


class BorrowingSerializer(serializers.ModelSerializer):
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


class BorrowingListSerializer(serializers.ModelSerializer):
    book = serializers.CharField(read_only=True, source="book.__str__")

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


class BorrowingDetailSerializer(BorrowingSerializer):
    book = BookSerializer(many=False)

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


class BorrowingCreateSerializer(BorrowingSerializer):
    class Meta:
        model = Borrowing
        fields = (
            "expected_return_date",
            "book",
        )

    def validate(self, attrs):
        data = super(BorrowingCreateSerializer, self).validate(attrs)
        book_obj = attrs["book"]
        book_title = book_obj.title
        book_inventory = book_obj.inventory

        if book_inventory <= 0:
            raise serializers.ValidationError(
                f"You can't borrowing book '{book_title}'. It is not available."
            )

        return data

    def create(self, validated_data):
        book = validated_data.get("book")
        book.book_borrowing()
        borrowing = Borrowing.objects.create(**validated_data)

        return borrowing
