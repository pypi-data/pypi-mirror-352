# ParolesNet

Ce projet permet de récupérer les paroles de chansons de [paroles.net](https://www.paroles.net/).

## Installation

Cloner le repo et installer les dépendances avec pip :

    git clone https://github.com/Starland9/paroles-net-wrapper
    pip install -r requirements.txt

## Utilisation

    from paroles_net import ParolesNet

    if __name__ == '__main__':
        pn = ParolesNet()
        songs = pn.get_best_songs()

        song = songs[0]
        print(song)
        print(song.get_lyrics(and_save=True))

        song = songs[1]
        print(song)
        print(song.get_lyrics())

        song = songs[2]
        print(song)
        print(song.get_lyrics(and_save=True))

## Licence

Ce projet est sous la [licence MIT](LICENSE)

## Auteur

    https://github.com/Starland9