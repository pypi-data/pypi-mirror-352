from django.contrib import admin
from django.db import models


class Category(models.Model):
    title = models.CharField(max_length=1024)
    text = models.TextField()

    def __str__(self) -> str:
        return self.title

    class Meta:
        verbose_name_plural = "Categories"


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    # all fields are read-only in Admin, because all Categories come from Wikipedia:
    readonly_fields = [field.name for field in Category._meta.fields]
