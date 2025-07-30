from paroles_net import ParolesNet
from utils import get_soup  # Ajout de l'import
from bs4.element import Tag  # Importation explicite de Tag

if __name__ == '__main__':
    pn = ParolesNet()

    # Test de la recherche par nom d'artiste (actuellement commenté)
    # search_query_artist = "Imagine Dragons"
    # print(f"\nRecherche de chansons pour l'artiste : '{search_query_artist}'")
    # found_songs_artist = pn.search_song(search_query_artist)
    # if found_songs_artist:
    #     print(f"\nChansons trouvées pour {search_query_artist} ({len(found_songs_artist)}):")
    #     for i, song in enumerate(found_songs_artist[:10]): # Afficher les 10 premières
    #         print(f"  {i+1}. {song.name} par {song.artist} (Lien: {song.link})")
    # else:
    #     print(f"Aucune chanson trouvée pour l'artiste {search_query_artist}.")

    # print("\n" + "="*50 + "\n") # Séparateur

    # Test de la recherche par titre de chanson
    search_query_title = "bang bang"
    print(f"\nRecherche de chanson par titre : '{search_query_title}'")
    found_songs_title = pn.search_song(search_query_title)

    if found_songs_title:
        print(
            f"\nChansons trouvées pour le titre '{search_query_title}' ({len(found_songs_title)}):")
        for i, song in enumerate(found_songs_title):
            print(f"  {i+1}. {song.name} par {song.artist} (Lien: {song.link})")
    else:
        print(f"Aucune chanson trouvée pour le titre '{search_query_title}'.")

    # Ancien code pour get_new_songs (peut être décommenté pour tester séparément)
    # print("\n--- Test de get_new_songs ---")
    # songs = pn.get_new_songs()
    # if songs:
    #     song = songs[0]
    #     print(song)
    #     # print(song.get_lyrics(and_save=True)) # Attention: and_save n'est pas un paramètre standard de get_lyrics dans Song
    #     # Correction: song.get_lyrics() puis sauvegarder manuellement si besoin
    #     # lyrics = song.get_lyrics()
    #     # if lyrics:
    #     #     with open(f"{song.name}_lyrics.txt", "w") as f:
    #     #         f.write(lyrics)
    #     #     print(f"Paroles sauvegardées dans {song.name}_lyrics.txt")
    # else:
    #     print("Impossible de récupérer les nouvelles chansons.")
