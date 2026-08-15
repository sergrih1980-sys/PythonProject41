from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


class Habit(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='habits'
    )
    action = models.CharField(_('действие'), max_length=255, help_text=_('Я буду [ДЕЙСТВИЕ]...'))
    place = models.CharField(_('место'), max_length=255, blank=True)
    time_of_day = models.TimeField(_('время выполнения'), null=True, blank=True, help_text=_('Когда выполнять привычку'))
    is_pleasant = models.BooleanField(_('приятная привычка'), default=False, help_text=_('Если True — это вознаграждение, а не полезная привычка'))

    # Связь с «приятной» привычкой (вознаграждение)
    linked_habit = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='linked_from',
        verbose_name=_('связанная привычка (приятная)'),
        help_text=_('Только для полезных привычек: приятная привычка как вознаграждение')
    )

    reward = models.CharField(
        _('вознаграждение'),
        max_length=255,
        blank=True,
        help_text=_('Чем наградить себя после выполнения (если не используется связанная привычка)')
    )

    period_days = models.PositiveIntegerField(
        _('периодичность (дней)'),
        default=1,
        help_text=_('Как часто повторять привычку (в днях)')
    )

    duration_seconds = models.PositiveIntegerField(
        _('время на выполнение (сек)'),
        default=60,
        help_text=_('Предполагаемое время выполнения привычки в секундах')
    )

    is_public = models.BooleanField(_('публичная привычка'), default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = _('привычка')
        verbose_name_plural = _('привычки')

    def clean(self):
        # Правило: нельзя одновременно reward и linked_habit
        if self.reward and self.linked_habit:
            raise ValidationError({'reward': _('Можно указать либо вознаграждение, либо связанную приятную привычку, но не оба поля сразу.')})

        # Приятная привычка не может иметь reward или linked_habit
        if self.is_pleasant:
            if self.reward:
                raise ValidationError({'reward': _('Приятная привычка не должна иметь отдельного вознаграждения.')})
            if self.linked_habit:
                raise ValidationError({'linked_habit': _('Приятная привычка не должна иметь связанной привычки.')})

        # linked_habit может быть только приятной привычкой
        if self.linked_habit and not self.linked_habit.is_pleasant:
            raise ValidationError({'linked_habit': _('Связанной привычкой может быть только приятная привычка.')})

        # duration_seconds <= 120 сек
        if self.duration_seconds > 120:
            raise ValidationError({'duration_seconds': _('Время выполнения привычки не должно превышать 120 секунд.')})

        # period_days: не реже 1 раза в 7 дней (т.е. period_days <= 7)
        if self.period_days < 1 or self.period_days > 7:
            raise ValidationError({'period_days': _('Периодичность должна быть от 1 до 7 дней включительно.')})

    def save(self, *args, **kwargs):
        self.full_clean()  # запускаем валидацию clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.user.email} — {self.action}'


