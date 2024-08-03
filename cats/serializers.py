from rest_framework import serializers

from .models import Cat, Owner, Achievement, AchievementCat

import datetime as dt


class AchievementSerializer(serializers.ModelSerializer):

    class Meta:
        model = Achievement
        fields = ("id", "name")


class CatSerializer(serializers.ModelSerializer):
    # owner = serializers.StringRelatedField(read_only=True)
    achievements = AchievementSerializer(many=True, required=False)
    age = serializers.SerializerMethodField()

    class Meta:
        model = Cat
        fields = ("id", "name", "color", "birth_year", "age", "owner", "achievements")

    def get_age(self, obj):
        return dt.datetime.now().year - obj.birth_year

    def create(self, validated_data):
        # Если в исходном запросе не было поля achievements
        if "achievements" not in self.initial_data:
            # То создаём запись о котике без его достижений
            cat = Cat.objects.create(**validated_data)
            return cat
        # Уберём список достижений из словаря validated_data и сохраним его
        achievements = validated_data.pop("achievements")

        # Создадим нового котика пока без достижений, данных нам достаточно
        cat = Cat.objects.create(**validated_data)

        # Для каждого достижения из списка достижений
        for achievement in achievements:
            # Создадим новую запись или получим существующий экземпляр из БД
            current_achievement, status = Achievement.objects.get_or_create(
                **achievement
            )
            # Поместим ссылку на каждое достижение во вспомогательную таблицу
            # Не забыв указать к какому котику оно относится
            AchievementCat.objects.create(achievement=current_achievement, cat=cat)
        return cat


class OwnerSerializer(serializers.ModelSerializer):
    cats = serializers.StringRelatedField(many=True, read_only=True)

    class Meta:
        model = Owner
        fields = ("first_name", "last_name", "cats")
