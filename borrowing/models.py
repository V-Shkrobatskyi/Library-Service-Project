from datetime import datetime

from django.db import models

from book.models import Book
from library_service import settings


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
    def book_borrowing(book):
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

    def return_book(self):
        self.book.inventory += 1
        self.book.save()
        self.actual_return_date = datetime.today()
        self.save()
