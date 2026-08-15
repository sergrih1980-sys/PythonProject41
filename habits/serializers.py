from rest_framework import serializers
from .models import Habit


class HabitSerializer(serializers.ModelSerializer):
    class Meta:
        model = Habit
        fields = [
            'id', 'user', 'action', 'place', 'time_of_day',
            'is_pleasant', 'linked_habit', 'reward',
            'period_days', 'duration_seconds', 'is_public',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['user', 'created_at', 'updated_at']

    def validate(self, data):
        # Дублируем логику clean() модели, чтобы ошибки приходили сразу в API
        is_pleasant = data.get('is_pleasant', False)
        reward = data.get('reward', '')
        linked_habit = data.get('linked_habit')
        duration_seconds = data.get('duration_seconds', 0)
        period_days = data.get('period_days', 1)

        if reward and linked_habit:
            raise serializers.ValidationError({'reward': 'Можно указать либо вознаграждение, либо связанную приятную привычку, но не оба.'})

        if is_pleasant:
            if reward:
                raise serializers.ValidationError({'reward': 'Приятная привычка не должна иметь отдельного вознаграждения.'})
            if linked_habit:
                raise serializers.ValidationError({'linked_habit': 'Приятная привычка не должна иметь связанной привычки.'})

        if linked_habit and not linked_habit.is_pleasant:
            raise serializers.ValidationError({'linked_habit': 'Связанной привычкой может быть только приятная привычка.'})

        if duration_seconds > 120:
            raise serializers.ValidationError({'duration_seconds': 'Время выполнения привычки не должно превышать 120 секунд.'})

        if period_days < 1 or period_days > 7:
            raise serializers.ValidationError({'period_days': 'Периодичность должна быть от 1 до 7 дней включительно.'})

        return data