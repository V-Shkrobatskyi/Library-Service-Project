from datetime import datetime
from decimal import Decimal

from django.db import models

from book.models import Book
from library_service import settings


FINE_MULTIPLIER = 2


class Borrowing(models.Model):
    borrow_date = models.DateTimeField(auto_now_add=True)
    expected_return_date = models.DateTimeField()
    actual_return_date = models.DateTimeField(null=True, blank=True)
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name="borrowing")
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="borrowing"
    )

    class Meta:
        ordering = ("borrow_date",)

    def __str__(self):
        return f"Borrowing book {self.book.title} by user {self.user} on {self.borrow_date})"

    @staticmethod
    def book_borrowing(book) -> None:
        book.inventory -= 1
        book.save()

    @staticmethod
    def validate_borrowing(inventory, error_to_raise) -> None:
        if inventory == 0:
            raise error_to_raise(
                {"book": "You can't borrowing this book, its inventory is zero."}
            )

    def clean(self) -> None:
        Borrowing.validate_borrowing(self.book.inventory, ValueError)

    def save(self, *args, **kwargs) -> None:
        self.clean()
        return super().save(*args, **kwargs)

    def return_book(self) -> None:
        self.book.inventory += 1
        self.book.save()
        self.actual_return_date = datetime.today()
        self.save()

    def get_borrowing_days(self) -> int:
        last_date = self.expected_return_date.date()
        first_date = self.borrow_date.date()

        return (last_date - first_date).days

    def get_price(self) -> Decimal:
        return self.get_borrowing_days() * self.book.daily_fee

    def get_overdue_days(self) -> int:
        actual_return_date = self.actual_return_date.date()
        expected_return_date = self.expected_return_date.date()

        return (actual_return_date - expected_return_date).days

    def get_overdue_price(self) -> Decimal:
        daily_fee = self.book.daily_fee
        fine_multiplier = Decimal(FINE_MULTIPLIER)

        return self.get_overdue_days() * daily_fee * fine_multiplier
