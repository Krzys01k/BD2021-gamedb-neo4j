# BD2021-gamedb-neo4j
Grafowa baza danych realizowana w ramach kursu BD2021 AGH

# Technologie
neo4j, python

# Autorstwo
Krzysztof Jędrychowski,
Szymon Rynkowski

# Temat projktu
Grafowa baza danych w której przechoujemy informacje o grach, użytkownikach, recenzjach na temat gier wystawionych przez użytkowników oraz o użytkownikach obserwowanych przez danego użytkownika.

# Reprezentacja w bazie
## Użytkownik
Reprezentowany przez wierzchołek o etykiecie User oraz atrybutach:
1. name - nazwa użytkownika
2. password - zahaszowane hasło

## Gra 
Reprezentowana przez wierzchołek o etykiecie Game oraz atrybutach:
1. title - tytuł gry
2. desc - któtki opis
3. desc_long - opis rozszerzony
4. photo_url - url do zdjęcia reprezentującego gre
5. relased - data wydania

## Recenzja
Reprezentowana przez wierzchołek o etykiecie Review oraz atrybutach:
1. score - punktowa ocena w zakresie 0 - 100
2. content - treść recenzji

## Relacje
relacje pomiędzy wierzchołkami w bazie
1. FOLLOWS - reprezentuje obserwowanie użytkownika - w postaci (u1:User)-[f:FOLLOWS]->(u2:User)
2. WROTE - oznacza relacje napisania przez -  w postaci (u:User)-[f:WROTE]->(r:Review)
3. ADDRESSES - oznacze dodyczenie przez recenzje - w postaci (r:Review)-[f:ADDRESSES]->(g:Game)

## Wizualizacja Schematu
![Wizualizacja Schematu](/Images/BDschema_vizualization.PNG)

## Aplikacja
Stworzymy aplikacje webową pozwalającą na
1. Rejestracje nowych użytkoników
2. Logowanie istniejących użytkowników
3. Przeglądanie listy gier w bazie
4. Podgląd detali gier oraz opinii na ich temat
5. Podgląd profili użytkowników zawierających
    1. Nazwę użytkownika
    2. Listę użytkowników obserwowanych przez użytkownika
    3. Listę użytkowników obserwujących użytkownika
    4. Listę recenzji wystawionych przez użytkownika
6. Dla zalogowanych użytkowników udostępniamy możliwości
    1. Dodanie innego użytkownika do obserwowanych
    2. Usunięcie innego użytkownika z obserwowanych
    3. Dodanie recenzji do gry (o ile już nie istnieje)

Aplikacja zostanie zrealizowana w języku Python za pomocą frameworka Flask
