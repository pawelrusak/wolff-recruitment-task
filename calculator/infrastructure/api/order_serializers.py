import uuid
from rest_framework import serializers


class TerminalSerializer(serializers.Serializer):
    id = serializers.IntegerField(min_value=0)
    size = serializers.CharField(max_length=50)
    quantity = serializers.IntegerField(min_value=0)


class GlandSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    size = serializers.CharField(max_length=50)
    side = serializers.CharField(max_length=50)
    quantity = serializers.IntegerField(min_value=0)
    material = serializers.CharField(required=True, max_length=100)


class CurrentConfigSerializer(serializers.Serializer):
    terminals = serializers.ListField(child=TerminalSerializer())
    glands = serializers.ListField(child=GlandSerializer())


class SaveBoxSerializer(serializers.Serializer):
    id = serializers.CharField(required=True, max_length=100)
    name = serializers.CharField(required=True, max_length=100)
    quantity = serializers.IntegerField(min_value=1)
    currentConfig = CurrentConfigSerializer()
    comment = serializers.CharField(required=False, allow_blank=True)


class OrderSerializer(serializers.Serializer):
    """
    Serializer do walidacji danych wejściowych dla tworzenia zamówienia.
    Na podstawie rzeczywistej struktury danych z API.
    """
    name = serializers.CharField(max_length=255)
    email = serializers.EmailField()
    userInformation = serializers.CharField(max_length=1000, required=False, allow_blank=True)
    saveBox = serializers.ListField(child=SaveBoxSerializer())

    def validate(self, data):
        """
        Dodatkowa walidacja na poziomie całego obiektu.
        """
        # Sprawdź czy saveBox nie jest pustą listą
        if not data.get('saveBox'):
            raise serializers.ValidationError("Lista saveBox nie może być pusta.")

        # Sprawdź czy każdy element w saveBox ma poprawną konfigurację
        for box in data.get('saveBox', []):
            if not box.get('currentConfig'):
                raise serializers.ValidationError("Każdy element saveBox musi mieć currentConfig.")

            # Sprawdź czy quantity jest większe od 0
            if box['currentConfig'].get('quantity', 0) <= 0:
                raise serializers.ValidationError("Ilość musi być większa od 0.")

        return data
