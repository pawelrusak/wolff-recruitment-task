# Notatki dotyczące implementacji

## Uruchomienie projektu

```bash
# Sklonuj repozytorium
git clone git@github.com:pawelrusak/wolff-recruitment-task.git

# Przejdź do katalogu projektu
cd wolff-recruitment-task

# Utwórz i aktywuj wirtualne środowisko
python -m venv .venv
source .venv/bin/activate  # Na Windows użyj: .venv\Scripts\activate

# Zainstaluj wymagane pakiety
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

# Uruchom migracje bazy danych
python manage.py makemigrations
python manage.py migrate

# Załaduj dane testowe
python manage.py import_enclosures fixtures/enclosures.json
python manage.py import_glands fixtures/glands.json
python manage.py import_terminals fixtures/terminals.json

# Uruchom serwer deweloperski
python manage.py runserver

# Przetestuj funkcję calculate_order_price()
curl -X POST http://localhost:8000/api/recruitment/orders/create/ \
  -H "Content-Type: application/json" \
  -d @fixtures/order_example.json
```

## Zostało zaimplementowane

Poniższe zadania zostały całkowicie zrealizowane zgodnie z wymaganiami:

- Część 1: Modele Django
- Część 2: Import danych
- Część 3: API i obliczanie ceny

Bonusy

Brak dodatkowych funkcji bonusowych, pomimo chęci, ze względu na limit czasowy

## Problemy / Uwagi

### Ogólne uwagi

Musiałem dwukrotnie przerywać zadanie w międzyczasie, dlatego godziny z Gita nie odzwierciedlają rzeczywistego czasu pracy nad zadaniem. Niemniej jednak na telefonie włączyłem timer i starałem się liczyć czas pracy — który podałem w wiadomości e-mail.

### Uwagi do poszczególnych części:

#### Część 2

- Po wywołaniu pierwszej komendy importującej otrzymałem błąd typu „nie znaleziono komendy”. Było to powodowane literówką w ścieżce do pliku z komendą. Poprawiłem to i mogłem kontynuować. Choć zajeło mi to kilka minut.

#### Część 3

- Starałem się trzymać wszystkich wytycznych z pliku `fixtures/ZADANIE_REKRUTACYJNE.md`, łącznie z sugerowaną tam strukturą plików.

- `OrderSerializer` nie odpowiadał kształtowi podanemu w pliku `fixtures/order_example.json`, więc musiałem go zmodyfikować.

- Zmodyfikowałem dołączone dane z pliku `fixtures/order_example.json`, ponieważ pierwotnie `saveBox[0].quantity` miało wartość **0**, natomiast z opisu zadania wynikało, że powinno być **2**. Po tej zmianie otrzymałem wynik zgodny z opisem z pliku `fixtures/ZADANIE_REKRUTACYJNE.md`.
