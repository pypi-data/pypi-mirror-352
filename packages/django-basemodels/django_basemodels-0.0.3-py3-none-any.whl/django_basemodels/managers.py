import logging
from django.db import models
from django.db.models import F, Q, Case, When, Value, BooleanField
from django.utils import timezone
from polymorphic.query import PolymorphicQuerySet
from .utils import is_celery_ready

logger = logging.getLogger(__name__)


class ActiveOrNotQuerySet(models.QuerySet):
    def get(self, *args, **kwargs):
        return super().get(*args, **kwargs)

    def activate(self):
        return self.update(is_active=True)

    def deactivate(self):
        return self.update(is_active=False)

    def _active_q(self):
        now = timezone.now()
        always = Q(is_active=True, active_start__isnull=True, active_end__isnull=True)
        timed = (
                Q(active_start__gte=now) & (Q(active_end__lte=now) | Q(active_end__isnull=True)) |
                Q(active_end__lte=now) & (Q(active_start__gte=now) | Q(active_start__isnull=True))
        )
        return always | timed

    def active(self):
        if is_celery_ready():
            return self.filter(is_active=True)
        return self.filter(self._active_q())

    def inactive(self):
        if is_celery_ready():
            return self.filter(is_active=False)

        return self.filter(~self._active_q())

    def update_activity_status(self, batch_size=1000):
        """
        Обновляет is_active для всех объектов в queryset по правилам:
        - Если задан active_start: active_start <= now
        - Если задан active_end: active_end >= now
        - Если оба не заданы: не меняем is_active
        """
        now = timezone.now()
        # Строим условие для нового значения is_active
        is_active_condition = Case(
            # Оба заданы: start <= now <= end
            When(
                Q(active_start__isnull=False, active_end__isnull=False),
                then=Q(active_start__lte=now) & Q(active_end__gte=now)
            ),
            # Только start: start <= now
            When(
                Q(active_start__isnull=False, active_end__isnull=True),
                then=Q(active_start__lte=now)
            ),
            # Только end: end >= now
            When(
                Q(active_start__isnull=True, active_end__isnull=False),
                then=Q(active_end__gte=now)
            ),
            # Ничего не задано: сохраняем текущее состояние
            When(
                Q(active_start__isnull=True, active_end__isnull=True),
                then=F('is_active')
            ),
            default=Value(True),
            output_field=BooleanField()
        )

        return self.update(is_active=is_active_condition)


class BaseModelQuerySet(models.QuerySet):
    pass


class BaseActiveOrNotQuerySet(BaseModelQuerySet, ActiveOrNotQuerySet):
    pass


class PolymorphicActiveOrNotQuerySet(PolymorphicQuerySet, ActiveOrNotQuerySet):
    pass


class PolymorphicBaseModelQuerySet(PolymorphicQuerySet, BaseModelQuerySet):
    pass


class PolymorphicBaseActiveOrNotQuerySet(PolymorphicQuerySet, BaseActiveOrNotQuerySet):
    pass
