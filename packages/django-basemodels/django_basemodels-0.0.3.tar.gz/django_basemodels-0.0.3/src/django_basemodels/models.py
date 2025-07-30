from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Manager
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from .managers import BaseModelQuerySet, ActiveOrNotQuerySet, BaseActiveOrNotQuerySet
from .utils import is_celery_ready


class BaseModel(models.Model):
    created_at = models.DateTimeField(
        name="created_at", auto_now_add=True, null=False, blank=True, editable=False, verbose_name=_("Дата создания")
    )
    updated_at = models.DateTimeField(
        name="updated_at", auto_now=True, null=False, blank=True, editable=False,
        verbose_name=_("Время последнего обновления")
    )

    objects = Manager.from_queryset(BaseModelQuerySet)()

    class Meta:
        abstract = True
        ordering = ['-updated_at']


class ActiveOrNotModel(models.Model):
    is_active = models.BooleanField(
        db_column='is_active',
        default=True,
        null=False, blank=True,
        verbose_name=_("Активность")
    )

    active_start = models.DateTimeField(
        null=True, blank=True,
        verbose_name=_("Начало активности")
    )
    active_end = models.DateTimeField(
        null=True, blank=True,
        verbose_name=_("Конец активности")
    )

    objects = Manager.from_queryset(ActiveOrNotQuerySet)()

    def clean(self):
        super().clean()
        if self.active_start and self.active_end and self.active_end < self.active_start:
            raise ValidationError("Конец активности не может быть раньше начала")

    def activate(self):
        self.is_active = True
        self.save()

    def deactivate(self):
        self.is_active = False
        self.save()

    @property
    def is_active_real(self):
        if is_celery_ready():
            return self.is_active

        if not self.active_start and not self.active_end:
            return self.is_active

        now = timezone.now()
        active_start = self.active_start or now
        return (active_start <= now) and (self.active_end >= now if self.active_end else True)

    class Meta:
        abstract = True
        indexes = [
            # Для запросов типа .filter(is_active=True)
            models.Index(fields=['is_active']),

            # Для временных диапазонов
            models.Index(fields=['active_start', 'active_end']),

            # Для часто используемых комбинаций
            models.Index(fields=['is_active', 'active_start']),
            models.Index(fields=['is_active', 'active_end']),

            models.Index(fields=['is_active', 'active_start', 'active_end']),
            models.Index(fields=['active_start']),
            models.Index(fields=['active_end']),
        ]


class BaseActiveOrNotModel(BaseModel, ActiveOrNotModel):
    objects = Manager.from_queryset(BaseActiveOrNotQuerySet)()

    class Meta:
        abstract = True
