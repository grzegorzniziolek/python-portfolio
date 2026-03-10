Porównywarka ofert (OLX / Vinted / eBay) – dokumentacja projektu

Cel projektu
Program konsolowy pobiera oferty (cena i link) dla podanej frazy z OLX, Vinted i eBay. 
Następnie wypisuje w konsoli podsumowanie i zapisuje wyniki do pliku CSV.

Jak uruchomić
Uruchom w terminalu plik main.py. Program po starcie poprosi o wpisanie parametrów i dopiero potem zacznie pobieranie stron.

Wejście użytkownika (input)
Program wymaga podania wszystkich pól. Jeśli użytkownik zostawi puste pole albo poda złą wartość, program zgłasza błąd.

Wprowadzane dane (nazwa, przykład, walidacja)
1) nazwa produktu, np. spodnie, pole obowiązkowe (nie może być puste)
2) minimalna cena w PLN, np. 10, liczba całkowita 0 lub większa
3) liczba stron do skrapowania, np. 3, liczba całkowita 1 lub większa
4) limit jednoczesnych pobrań (concurrency), np. 4, liczba całkowita 1 lub większa
5) platformy, np. olx,vinted,ebay albo olx,vinted, dozwolone wartości: olx, vinted, ebay (co najmniej jedna poprawna)

Wyjście programu (output)
Program wypisuje w konsoli:
1) ile ofert znaleziono na każdej wybranej platformie
2) najtańsze oferty: po jednej najtańszej ofercie na platformę (platforma, cena, link)

Program zapisuje plik wynikowy:
wynik_csv.csv
Separator w pliku: średnik
Kolumny: platforma, price, url

Jak działa program (w skrócie)
1) Pobranie parametrów od użytkownika.
2) Zbudowanie listy adresów URL do pobrania dla wybranych platform i liczby stron.
3) Asynchroniczne pobranie HTML stron z ograniczeniem liczby jednoczesnych pobrań (semafor).
4) Podział pobranych stron HTML na platformy.
5) Parsowanie HTML i wyciągnięcie ofert (cena i link).
6) Złożenie wyników do DataFrame, konwersja cen na liczby i odrzucenie błędnych rekordów.
7) Wyznaczenie najtańszych ofert per platforma.
8) Zapis wyników do wynik_csv.csv.

Struktura programu i funkcje (co za co odpowiada)
HEADERS
Zawiera nagłówki HTTP używane przy pobieraniu stron (np. User-Agent). Cel: zwiększyć szansę na poprawną odpowiedź serwisu.

conversion(text)
Czyści tekst ceny pobrany z HTML (usuwa waluty i zbędne znaki, usuwa spacje, zamienia przecinek na kropkę). Zwraca tekst przygotowany do konwersji na liczbę.

parsowanie(lista, platforma)
Dostaje listę stron HTML i identyfikator platformy. Dla każdej strony wyszukuje elementy ofert odpowiednimi selektorami HTML, wyciąga cenę i link oraz zwraca listę rekordów (cena, link).

fetch(session, url, sem)
Funkcja asynchroniczna pobierająca HTML jednej strony. Używa semafora, żeby ograniczyć liczbę jednoczesnych pobrań. Przy błędzie zwraca pusty tekst, aby program mógł działać dalej.

main()
Główna funkcja programu. Pobiera dane od użytkownika (input), buduje URL-e, pobiera strony asynchronicznie, uruchamia parsowanie, tworzy DataFrame, wypisuje podsumowanie i zapisuje CSV.
