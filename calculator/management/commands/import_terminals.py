
import json
from pathlib import Path
from django.conf import settings

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from calculator.models import Terminal


class Command(BaseCommand):
    help = "Importuje dane terminali elektrycznych z pliku JSON i zapisuje je do bazy danych."

    def add_arguments(self, parser):
        """
        Dodaje argumenty do komendy zarządzania.


        Parametry
            parser: obiekt parsera argumentów
        """
        parser.add_argument(
            "file_path",
            type=str,
            help="Ścieżka do pliku JSON (np. fixtures/terminals.json)",
        )

    def handle(self, *args, **options):
        self.stdout.write(
            f"Otwieranie danych terminali elektrycznych z pliku: {options['file_path']}"
        )
        options["file_path"]
        fixtures_dir = Path(settings.BASE_DIR) / options["file_path"]

        enclosure_fixtures = self._open_json_file(fixtures_dir)

        self.stdout.write(
            self.style.MIGRATE_HEADING(
                "Zapisywanie danych terminali elektrycznych do bazy danych...")
        )

        self._save_enclosure_data(enclosure_fixtures)

        self.stdout.write(
            self.style.SUCCESS('Import terminali elektrycznych zakończony pomyślnie.')
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
            data = raw['terminals']
        except KeyError:
            raise CommandError("Nieprawidłowa struktura JSON: brak klucza 'terminals'")

        return data

    def _save_enclosure_data(self, enclosure_data: list[dict]):
        """
        Zapisuje dane terminali elektrycznych do bazy danych.

        Parametry
            enclosure_data (list[dict]): Lista danymi terminali elektrycznych.
        """
        try:
            with transaction.atomic():
                for item in enclosure_data:
                    try:
                        wire_cross_section = item["wire_cross_section"]
                        width_mm = item["width_mm"]
                        color = item["color"]
                        voltage = item["voltage"]
                        price = item["price"]
                        current = item["current"]
                        catalog_number = item["catalog_number"]
                    except KeyError as e:
                        raise CommandError(
                            f"Brak wymaganych pól w danych dławika kablowego: {e}"
                        )

                    Terminal.objects.update_or_create(
                        # numer katalogowy (traktuje go jako unikalny identyfikator)
                        catalog_number=catalog_number,
                        defaults={
                            "wire_cross_section": wire_cross_section,
                            "width_mm": width_mm,
                            "color": color,
                            "voltage": voltage,
                            "price": price,
                            "current": current,
                        },
                    )

        except Exception as exception:
            raise CommandError(
                f"Import terminali elektrycznych nie powiódł się. Powód: {exception}"
            ) from exception
