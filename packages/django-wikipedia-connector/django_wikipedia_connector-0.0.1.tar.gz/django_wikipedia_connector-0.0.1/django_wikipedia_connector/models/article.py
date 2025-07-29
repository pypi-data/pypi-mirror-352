from django.contrib import admin
from django.db import models


class Article(models.Model):
    title = models.CharField(max_length=1024)
    text = models.TextField()
    categories = models.ManyToManyField("Category", through="ArticleCategory")

    def __str__(self) -> str:
        return self.title

    class Meta:
        verbose_name_plural = "Articles"


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    # all fields are read-only in Admin, because all Articles come from Wikipedia:
    readonly_fields = [field.name for field in Article._meta.fields]
