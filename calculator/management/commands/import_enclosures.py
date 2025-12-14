
import json
from pathlib import Path
from django.conf import settings

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from calculator.models import Enclosure


class Command(BaseCommand):
    help = "Importuje dane obudów elektronicznych z pliku JSON i zapisuje je do bazy danych."

    def add_arguments(self, parser):
        """
        Docstring for add_arguments

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
            f"Otwieranie danych obudów elektrycznych z pliku: {options['file_path']}"
        )
        options["file_path"]
        fixtures_dir = Path(settings.BASE_DIR) / options["file_path"]

        enclosure_fixtures = self._open_json_file(fixtures_dir)

        self.stdout.write(
            self.style.MIGRATE_HEADING("Zapisywanie danych obudów elektrycznych do bazy danych...")
        )

        self._save_enclosure_data(enclosure_fixtures)

        self.stdout.write(
            self.style.SUCCESS('Import obudów elektronicznych zakończony pomyślnie.')
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
            data = raw['enclosures']
        except KeyError:
            raise CommandError("Nieprawidłowa struktura JSON: brak klucza 'enclosures'")

        return data

    def _save_enclosure_data(self, enclosure_data: list[dict]):
        """
        Zapisuje dane obudów elektrycznych do bazy danych.

        Parametry
            enclosure_data (list[dict]): Lista danymi obudów elektrycznych.
        """
        try:
            with transaction.atomic():
                for item in enclosure_data:
                    try:
                        name = item["name"]
                        code = item["code"]
                        dimension_width = item["dimension_width"]
                        dimension_height = item["dimension_height"]
                        dimension_depth = item["dimension_depth"]
                        price = item["price"]
                    except KeyError as e:
                        raise CommandError(
                            f"Brak wymaganych pól w danych obudowy: {e}"
                        )

                    mounting_areas = item.get("mounting_areas", {})

                    mounting_area_top = mounting_areas.get("top", {})
                    mounting_area_down = mounting_areas.get("down", {})
                    mounting_area_left = mounting_areas.get("left", {})
                    mounting_area_right = mounting_areas.get("right", {})

                    enclosure_terminals = item.get("enclosure_terminals")

                    Enclosure.objects.update_or_create(
                        code=code,  # kod produktu (traktuje go jako unikalny identyfikator)
                        defaults={
                            "name": name,
                            "dimension_width": dimension_width,
                            "dimension_height": dimension_height,
                            "dimension_depth": dimension_depth,
                            "price": price,

                            "mounting_area_top_x": mounting_area_top.get("x"),
                            "mounting_area_top_y": mounting_area_top.get("y"),
                            "mounting_area_down_x": mounting_area_down.get("x"),
                            "mounting_area_down_y": mounting_area_down.get("y"),
                            "mounting_area_left_x": mounting_area_left.get("x"),
                            "mounting_area_left_y": mounting_area_left.get("y"),
                            "mounting_area_right_x": mounting_area_right.get("x"),
                            "mounting_area_right_y": mounting_area_right.get("y"),

                            "enclosure_terminals": enclosure_terminals,
                        },
                    )
        except Exception as exception:
            raise CommandError(
                f"Import obudów elektrycznych nie powiódł się. Powód: {exception}"
            ) from exception
