# BD2021-gamedb-neo4j
Grafowa baza danych realizowana w ramach kursu BD2021 AGH. 
W bazie danych przechowujemy informacje o grach, użytkownikach, oraz recenzjach na temat gier.

# Technologie
neo4j, python, flask

# Autorstwo
Krzysztof Jędrychowski,
Szymon Rynkowski

# Reprezentacja w bazie
## Wizualizacja Schematu
![Wizualizacja Schematu](/Images/BDschema_vizualization.PNG)

## Użytkownik
Reprezentowany przez wierzchołek o etykiecie User oraz atrybutach:
1. name - nazwa użytkownika
2. password - zahaszowane hasło

## Gra 
Reprezentowana przez wierzchołek o etykiecie Game oraz atrybutach:
1. title - tytuł gry
2. desc - któtki opis
3. photo_url - url do zdjęcia reprezentującego gre
4. relased - data wydania

## Recenzja
Reprezentowana przez wierzchołek o etykiecie Review oraz atrybutach:
1. score - punktowa ocena w zakresie 0 - 100
2. content - treść recenzji

## Relacje
Relacje pomiędzy wierzchołkami w bazie
1. FOLLOWS - reprezentuje obserwowanie użytkownika - w postaci (u1:User)-[f:FOLLOWS]->(u2:User)
2. WROTE - oznacza relacje napisania przez -  w postaci (u:User)-[f:WROTE]->(r:Review)
3. ADDRESSES - oznacze dodyczenie przez recenzje - w postaci (r:Review)-[f:ADDRESSES]->(g:Game)


## Aplikacja
Aplikacja webowa pozwala na
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
7. Przeglądanie listy opinii w bazie


## Endpointy
### GET:
- /games
- /games/<game_title>
- /add_review/<game_title>
- /update_review/<user_name>/<game_title>
- /delete_review/<user_name>/<game_title>
- /reviews
- /users
- /users/<user_name>
- /login
- /register
- /logout
- /register_success
- /login_success

### POST:
- /add_review/<game_title>
- /update_review/<user_name>/<game_title>
- /delete_review/<user_name>/<game_title>
- /users
- /users/<user_name>
- /follow
- /unfollow
- /login
- /register
