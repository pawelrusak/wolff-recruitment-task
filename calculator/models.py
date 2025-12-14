from django.db import models


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
