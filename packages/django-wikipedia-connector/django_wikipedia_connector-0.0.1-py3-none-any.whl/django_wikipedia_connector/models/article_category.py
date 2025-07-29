from django.contrib import admin
from django.db import models


class ArticleCategory(models.Model):
    """
    "Through" model for the many-to-many relationship between Articles and Categories.
    """

    category = models.ForeignKey("Category", on_delete=models.PROTECT)
    article = models.ForeignKey("Article", on_delete=models.PROTECT)

    class Meta:
        verbose_name_plural = "Article Categories"


@admin.register(ArticleCategory)
class ArticleCategoryAdmin(admin.ModelAdmin):
    list_display = ["id", "article", "category"]
    # all fields are read-only in Admin, because all Article Categories come from WikiPedia:
    readonly_fields = [field.name for field in ArticleCategory._meta.fields]
