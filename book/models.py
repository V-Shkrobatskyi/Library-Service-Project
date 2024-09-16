from django.db import models


class Book(models.Model):
    class CoverChoices(models.TextChoices):
        HARD = "Hard"
        SOFT = "Soft"

    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255)
    cover = models.CharField(max_length=15, choices=CoverChoices.choices)
    inventory = models.PositiveIntegerField()
    daily_fee = models.DecimalField(max_digits=7, decimal_places=2)

    class Meta:
        ordering = ("title",)

    def __str__(self):
        return f"{self.title} (author: {self.author}, daily fee: {self.daily_fee})"

    def book_borrowing(self):
        self.inventory -= 1
        self.save()
        return self
