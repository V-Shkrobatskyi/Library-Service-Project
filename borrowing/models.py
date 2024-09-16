from django.db import models

from book.models import Book
from library_service import settings


class Borrowing(models.Model):
    borrow_date = models.DateTimeField(auto_now_add=True)
    expected_return_date = models.DateTimeField()
    actual_return_date = models.DateTimeField(null=True, blank=True)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    class Meta:
        ordering = ("borrow_date",)

    def __str__(self):
        return f"{self.book} (user: {self.user}, borrow date: {self.borrow_date})"
