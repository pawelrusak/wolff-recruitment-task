from django.db import models
from decimal import Decimal
import uuid


class Enclosure(models.Model):
    """
    Model obudowy elektrycznej.

    Atrybuty:
        name: Nazwa obudowy (CharField, max 200).
        code: Unikalny kod obudowy (CharField, max 50).
        dimension_width: Szerokość obudowy w milimetrach (IntegerField).
        dimension_height: Wysokość obudowy w milimetrach (IntegerField). 
        dimension_depth: Głębokość obudowy w milimetrach (IntegerField).
        price: Cena obudowy 

        mounting_area_top_x: Współrzędna X górnego obszaru montażowego (FloatField, null=True).
        mounting_area_top_y: Współrzędna Y górnego obszaru montażowego (FloatField, null=True).
        mounting_area_down_x: Współrzędna X dolnego obszaru montażowego (FloatField, null=True).
        mounting_area_down_y: Współrzędna Y dolnego obszaru montażowego (FloatField, null=True).
        mounting_area_left_x: Współrzędna X lewego obszaru montażowego (FloatField, null=True).
        mounting_area_left_y: Współrzędna Y lewego obszaru montażowego (FloatField, null=True).
        mounting_area_right_x: Współrzędna X prawego obszaru montażowego (FloatField, null=True).
        mounting_area_right_y: Współrzędna Y prawego obszaru montażowego (FloatField, null=True).

        enclosure_terminals: Pojemność terminali w formacie JSON (JSONField, null=True). 
    """
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=50, unique=True)
    dimension_width = models.IntegerField()
    dimension_height = models.IntegerField()
    dimension_depth = models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

    mounting_area_top_x = models.FloatField(null=True)
    mounting_area_top_y = models.FloatField(null=True)
    mounting_area_down_x = models.FloatField(null=True)
    mounting_area_down_y = models.FloatField(null=True)
    mounting_area_left_x = models.FloatField(null=True)
    mounting_area_left_y = models.FloatField(null=True)
    mounting_area_right_x = models.FloatField(null=True)
    mounting_area_right_y = models.FloatField(null=True)

    enclosure_terminals = models.JSONField(null=True)


class Gland(models.Model):
    """
    Model dławika kablowego.

    Atrybuty:
        size: Rozmiar dławika (CharField, max 10) - np. "M12", "M16".
        diameter_mm: Średnica nominalna dławika w milimetrach (IntegerField).
        physical_diameter_mm: Fizyczna średnica dławika w milimetrach (IntegerField).
        cable_range_min: Minimalna średnica kabla w milimetrach (FloatField).
        cable_range_max: Maksymalna średnica kabla w milimetrach (FloatField).
        material: Materiał dławika (CharField, max 20) - "PA" lub "Brass".
        price: Cena dławika (DecimalField).
        catalog_number: Numer katalogowy dławika (CharField, max 50).
    """
    class Material(models.TextChoices):
        """
        Dostępne materiały dławików kablowych.
        """
        PA = "PA"
        BRASS = "Brass"

    size = models.CharField(max_length=10)
    diameter_mm = models.IntegerField()
    physical_diameter_mm = models.IntegerField()
    cable_range_min = models.FloatField()
    cable_range_max = models.FloatField()
    material = models.CharField(max_length=20, choices=Material.choices)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    catalog_number = models.CharField(max_length=50)


class Terminal(models.Model):
    """
    Model terminala elektrycznego.

    Atrybuty:
        wire_cross_section: Przekrój przewodu (CharField, max 10) - np. "2,5mm".
        width_mm: Szerokość terminala na szynie w milimetrach (FloatField).
        color: Kolor terminala (CharField, max 20) - np. "blue", "yellow".
        voltage: Napięcie terminala w woltach (IntegerField).
        current: Prąd terminala w amperach (FloatField).
        price: Cena terminala (DecimalField).
        catalog_number: Numer katalogowy terminala (CharField, max 50).
    """
    wire_cross_section = models.CharField(max_length=10)
    width_mm = models.FloatField()
    color = models.CharField(max_length=20)
    voltage = models.IntegerField()
    current = models.FloatField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    catalog_number = models.CharField(max_length=50)


class SimpleOrder(models.Model):
    """
    Uproszczony model zamówienia dla zadania rekrutacyjnego.

    Przechowuje kompletne dane zamówienia w JSON + obliczoną cenę.
    """

    # ID zamówienia
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        help_text="Unikalny identyfikator zamówienia"
    )

    # Dane klienta
    customer_name = models.CharField(
        max_length=255,
        help_text="Imię i nazwisko klienta"
    )
    customer_email = models.EmailField(
        help_text="Email klienta"
    )
    user_information = models.TextField(
        blank=True,
        null=True,
        help_text="Dodatkowe informacje od użytkownika"
    )

    # Dane zamówienia (JSON)
    order_data = models.JSONField(
        help_text="Kompletne dane zamówienia (obudowy, dławiki, terminale)"
    )

    # Obliczone ceny
    total_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        help_text="Całkowita cena zamówienia (PLN)"
    )

    enclosures_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        help_text="Suma cen obudów"
    )

    glands_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        help_text="Suma cen dławików"
    )

    terminals_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        help_text="Suma cen terminali"
    )

    # Status walidacji geometrycznej
    geometry_validation_passed = models.BooleanField(
        default=False,
        help_text="Czy walidacja geometryczna przeszła pomyślnie"
    )

    geometry_validation_errors = models.JSONField(
        null=True,
        blank=True,
        help_text="Błędy walidacji geometrycznej (jeśli były)"
    )

    # Metadane
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Data i czas utworzenia zamówienia"
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="Data i czas ostatniej aktualizacji"
    )

    class Meta:
        db_table = 'simple_orders'
        verbose_name = 'Zamówienie (Simple)'
        verbose_name_plural = 'Zamówienia (Simple)'
        ordering = ['-created_at']

    def __str__(self):
        return f"Order {self.id} - {self.customer_name} - {self.total_price} PLN"

    def save(self, *args, **kwargs):
        """
        Przy zapisywaniu automatycznie oblicz cenę jeśli nie jest ustawiona.
        """
        if self.total_price == Decimal('0.00'):
            self.calculate_total_price()

        super().save(*args, **kwargs)

    def calculate_total_price(self):
        """
        Oblicza całkowitą cenę zamówienia.

        TODO: Zaimplementuj tę metodę!
        Powinna sumować ceny:
        - obudów (enclosures_price)
        - dławików (glands_price)
        - terminali (terminals_price)

        I zapisać do self.total_price
        """
        self.total_price = Decimal('0.00')
        # TODO: Implementacja dla kandydata
        pass
