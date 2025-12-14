
import json
from pathlib import Path
from django.conf import settings

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from calculator.models import Gland


class Command(BaseCommand):
    help = "Importuje dane dławików kablowych z pliku JSON i zapisuje je do bazy danych."

    def add_arguments(self, parser):
        """
        Dodaje argumenty do komendy zarządzania.


        Parametry
            parser: obiekt parsera argumentów
        """
        parser.add_argument(
            "file_path",
            type=str,
            help="Ścieżka do pliku JSON (np. fixtures/enclosures.json)",
        )

    def handle(self, *args, **options):
        self.stdout.write(
            f"Otwieranie danych dławikóœ kablowych z pliku: {options['file_path']}"
        )
        options["file_path"]
        fixtures_dir = Path(settings.BASE_DIR) / options["file_path"]

        enclosure_fixtures = self._open_json_file(fixtures_dir)

        self.stdout.write(
            self.style.MIGRATE_HEADING("Zapisywanie danych dławików kablowych do bazy danych...")
        )

        self._save_enclosure_data(enclosure_fixtures)

        self.stdout.write(
            self.style.SUCCESS('Import dławików kablowych zakończony pomyślnie.')
        )

    def _open_json_file(self, file_path: Path):
        """
        Otwiera plik JSON na podstawie podanej ścieżki i zwraca jego zawartość.

        Parametry
            file_path: ścieżka do pliku JSON
        """
        if not file_path.exists():
            raise CommandError(f"Plik nie istnieje: {file_path}")

        try:
            with open(file_path, mode="r", encoding="utf-8") as file:
                raw = json.load(file)
        except json.JSONDecodeError:
            raise CommandError(f"Nieprawidłowy format JSON w pliku: {file_path}")

        try:
            data = raw['glands']
        except KeyError:
            raise CommandError("Nieprawidłowa struktura JSON: brak klucza 'enclosures'")

        return data

    def _save_enclosure_data(self, enclosure_data: list[dict]):
        """
        Zapisuje dane dławików kablowych do bazy danych.

        Parametry
            enclosure_data (list[dict]): Lista danymi dławików kablowych.
        """
        try:
            with transaction.atomic():
                for item in enclosure_data:
                    try:
                        size = item["size"]
                        diameter_mm = item["diameter_mm"]
                        physical_diameter_mm = item["physical_diameter_mm"]
                        cable_range_min = item["cable_range_min"]
                        cable_range_max = item["cable_range_max"]
                        material = item["material"]
                        price = item["price"]
                        catalog_number = item["catalog_number"]
                    except KeyError as e:
                        raise CommandError(
                            f"Brak wymaganych pól w danych dławika kablowego: {e}"
                        )

                    Gland.objects.update_or_create(
                        # numer katalogowy (traktuje go jako unikalny identyfikator)
                        catalog_number=catalog_number,
                        defaults={
                            "size": size,
                            "diameter_mm": diameter_mm,
                            "physical_diameter_mm": physical_diameter_mm,
                            "cable_range_min": cable_range_min,
                            "cable_range_max": cable_range_max,
                            "material": material,
                            "price": price,
                        },
                    )

        except Exception as exception:
            raise CommandError(
                f"Import dławików kablowych nie powiódł się. Powód: {exception}"
            ) from exception
