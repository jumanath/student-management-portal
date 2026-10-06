from django.db import models


class Student(models.Model):

    registration_no = models.CharField(
        max_length=20,
        unique=True
    )

    name = models.CharField(
        max_length=100
    )

    course = models.CharField(
        max_length=100
    )

    join_date = models.DateField()

    course_fees = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    paid_fees = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    to_pay = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )

    balance = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        editable=False
    )

    certificate = models.CharField(
        max_length=100
    )

    remarks = models.CharField(
        max_length=200,
        blank=True
    )

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):

        self.balance = self.course_fees - self.paid_fees

        if self.balance < 0:
            self.balance = 0

        super().save(*args, **kwargs)