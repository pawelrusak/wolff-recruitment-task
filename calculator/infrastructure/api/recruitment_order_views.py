"""
Szablon widoku API dla zadania rekrutacyjnego.

Ten plik pokazuje uproszczoną strukturę widoku.
"""

from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from decimal import Decimal
import logging
from typing import TypedDict, Literal, Iterable


from .order_serializers import OrderSerializer
from calculator.models import Enclosure, Gland, Terminal, SimpleOrder


# TODO: Import walidatorów (po implementacji)


logger = logging.getLogger(__name__)


@api_view(['POST'])
def create_order(request):
    """
    Tworzy nowe zamówienie z walidacją geometryczną.

    Endpoint: POST /api/orders/create/

    Request body: OrderSerializer (JSON)

    Returns:
        201: Zamówienie utworzone pomyślnie
        400: Błąd walidacji danych lub geometrii
        401: Brak autoryzacji
        500: Błąd serwera
    """

    # KROK 1: Walidacja autoryzacji (opcjonalne dla zadania rekrutacyjnego)

    # KROK 2: Walidacja danych wejściowych (serializacja)
    serializer = OrderSerializer(data=request.data)
    if not serializer.is_valid():
        logger.error(f"Validation error: {serializer.errors}")
        return Response(
            {
                "success": False,
                "errors": serializer.errors,
                "message": "Dane wejściowe są niepoprawne"
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    # KROK 3: Walidacja geometryczna - ZADANIE DLA KANDYDATA
    validated_data = serializer.validated_data

    # TODO: (OPCJONALNIE) Zaimplementuj walidację geometryczną
    # validation_errors = []
    # for box_data in validated_data.get('saveBox', []):
    #     # Walidacja dławików i terminali
    #     pass
    #
    # if validation_errors:
    #     return Response({
    #         "success": False,
    #         "errors": validation_errors
    #     }, status=status.HTTP_400_BAD_REQUEST)

    # KROK 4: Obliczenie ceny - ZADANIE DLA KANDYDATA
    try:
        total_price = calculate_order_price(validated_data)

        # KROK 5: Zapisanie zamówienia do bazy
        order = SimpleOrder.objects.create(
            customer_name=validated_data['name'],
            customer_email=validated_data['email'],
            user_information=validated_data.get('userInformation', ''),
            order_data=validated_data,
            total_price=total_price,
            # TODO: Dodaj pozostałe ceny
            # enclosures_price=...,
            # glands_price=...,
            # terminals_price=...,
            geometry_validation_passed=True  # TODO: Użyj wyniku walidacji
        )

        # KROK 6: Zwróć odpowiedź
        return Response({
            "success": True,
            "order_id": str(order.id),
            "total_price": str(total_price),
            "message": "Zamówienie utworzone pomyślnie"
        }, status=status.HTTP_201_CREATED)

    except Exception as e:
        logger.error(f"Error creating order: {str(e)}", exc_info=True)
        return Response(
            {
                "success": False,
                "error": str(e),
                "message": "Wystąpił błąd podczas tworzenia zamówienia"
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
def validate_order_layout(request):
    """
    Waliduje układ komponentów bez tworzenia zamówienia.

    Endpoint: POST /api/orders/validate/

    To jest endpoint BONUS - pozwala frontendowi sprawdzić
    czy komponenty zmieszczą się PRZED utworzeniem zamówienia.

    Request body: OrderSerializer (JSON)

    Returns:
        200: Walidacja pomyślna + szczegóły (pozycje dławików, etc.)
        400: Błąd walidacji
    """

    # TODO: Zaimplementuj walidację bez tworzenia zamówienia
    # Bardzo podobne do create_order, ale:
    # 1. Nie tworzy zamówienia w bazie
    # 2. Zwraca szczegółowe info o rozmieszczeniu komponentów

    serializer = OrderSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(
            {
                "valid": False,
                "errors": serializer.errors
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    validated_data = serializer.validated_data

    # TODO: Uruchom walidatory geometryczne
    # Zwróć szczegółowe informacje:
    response_data = {
        "valid": True,
        "message": "Wszystkie komponenty zmieszczą się w wybranych obudowach",
        "details": {

        }
    }

    return Response(response_data, status=status.HTTP_200_OK)


class GlandItem(TypedDict):
    size: str
    quantity: int
    material: Literal["PA", "Brass"]


class GlandSide(TypedDict):
    side: str
    items: Iterable[GlandItem]


class TerminalItem(TypedDict):
    size: str
    quantity: int
    color: str


class CurrentConfig(TypedDict):
    box_type: str
    comment: str
    glands: Iterable[GlandSide]
    terminals: Iterable[TerminalItem]


class SaveBox(TypedDict):
    id: str
    name: str
    code: str
    quantity: int
    currentConfig: CurrentConfig


class OrderData(TypedDict):
    name: str
    email: str
    userInformation: str
    saveBox: Iterable[SaveBox]


def get_glands_list(glands: Iterable[GlandSide]) -> Iterable[GlandItem]:
    """
    Spłaszcza strukturę dławików kablowych które byly pogrupowane według stron.
    """
    glands_list: list[GlandItem] = []

    for side in glands:
        glands_list.extend(side['items'])

    return glands_list


def calculate_glands_price(glands: Iterable[GlandItem]) -> Decimal:
    """
    Oblicza łączną cenę dławików kablowych.

    Parametry:
        glands (Iterable[GlandItem]): Lista dławików kablowych w zamówieniu.
    """
    glands_total_price = Decimal('0.00')

    for gland in glands:
        gland_size = gland['size']
        gland_material = gland['material']
        gland_quantity = gland['quantity']

        db_gland = Gland.objects.get(size=gland_size, material=gland_material)
        gland_price = Decimal(db_gland.price) * gland_quantity
        glands_total_price += gland_price

    return glands_total_price


def calculate_terminals_price(terminals: Iterable[TerminalItem]) -> Decimal:
    """
    Oblicza łączną cenę terminali elektrycznych.

    Parametry: 
        terminals (Iterable[TerminalItem]): Lista terminali w zamówieniu.
    """
    terminals_total_price = Decimal('0.00')

    for terminal in terminals:
        terminal_size = terminal['size']
        terminal_quantity = terminal['quantity']
        terminal_color = terminal['color']

        db_terminal = Terminal.objects.get(wire_cross_section=terminal_size, color=terminal_color)

        terminal_price = Decimal(db_terminal.price) * terminal_quantity

        terminals_total_price += terminal_price

    return terminals_total_price


def calculate_order_price(order_data: OrderData) -> Decimal:
    """
    Oblicza cenę zamówienia.

    Parametry:
        order_data (OrderData): Dane zamówienia.
    """
    total_price = Decimal('0.00')

    for box_data in order_data.get('saveBox', []):
        # 1. Cena obudowy
        enclosure_code = box_data['code']
        db_enclosure = Enclosure.objects.get(code=enclosure_code)
        enclosure_price = Decimal(db_enclosure.price)

        # 2. Ceny dławików
        glands_order = box_data['currentConfig'].get('glands', [])
        glands_list = get_glands_list(glands_order)
        glands_price = calculate_glands_price(glands_list)

        # 3. Ceny terminali
        terminals_order = box_data['currentConfig'].get('terminals', [])
        terminals_price = calculate_terminals_price(terminals_order)

        box_price = (enclosure_price + glands_price +
                     terminals_price) * box_data['quantity']

        total_price += box_price

    return total_price
