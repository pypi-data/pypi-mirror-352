from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException, TimeoutException # Ajout de TimeoutException
import time # Ajout de l'import time
import re # Ajout de l'import re

from models.song import Song
from utils import get_soup


def get_songs_from_table(table):
    table_rows = table.find_all("tr")

    songs: list[Song] = []

    for tr in table_rows:
        tds = tr.find_all("td")
        idx = tds[0].text.strip()
        link = tds[1].find("a")["href"]
        name = tds[1].find("a").text.strip()
        artist = tds[-1].text.strip()

        songs.append(Song(idx, name, link, artist))

    return songs


class ParolesNet:
    def __init__(self):
        self.base_url = "https://www.paroles.net/"

    def get_songs_by_table_id(self, table_idx):
        soup = get_soup(self.base_url)
        tables = soup.find_all("table")
        table = tables[table_idx]
        songs = get_songs_from_table(table)
        return songs

    def get_new_songs(self):
        return self.get_songs_by_table_id(0)

    def get_best_songs(self):
        return self.get_songs_by_table_id(1)

    def search_song(self, query: str):
        # Initialiser le driver (exemple avec Chrome)
        # Assurez-vous que chromedriver est dans votre PATH ou spécifiez le chemin
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        options.add_argument('--disable-gpu')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument("window-size=1920,1080") # Définir une taille de fenêtre peut aider en headless
        # options.add_argument('--remote-debugging-port=9222') # Pour débogage si nécessaire
        
        driver = webdriver.Chrome(options=options)
        driver.set_page_load_timeout(120) # Réduit un peu, car 180 n'a pas aidé, le problème est peut-être ailleurs
        songs: list[Song] = []

        try:
            for attempt in range(3): # Essayer de charger la page 3 fois
                try:
                    print(f"Tentative de chargement de {self.base_url} (essai {attempt + 1}/3)...")
                    driver.get(self.base_url)
                    print("Page d'accueil chargée.")
                    break # Sortir de la boucle si le chargement réussit
                except TimeoutException:
                    print(f"Timeout lors du chargement de {self.base_url} (essai {attempt + 1}/3).")
                    if attempt == 2: # Si c'est la dernière tentative
                        raise # Relancer l'exception pour qu'elle soit gérée plus bas
                    time.sleep(5) # Attendre 5 secondes avant de réessayer
                except Exception as e_get_inner:
                    print(f"Erreur non-Timeout lors du driver.get (essai {attempt+1}/3): {e_get_inner}")
                    if attempt == 2:
                        raise
                    time.sleep(5)


            # Localiser le champ de recherche, entrer la requête et soumettre
            search_box = WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.ID, "search-input"))
            )
            search_box.clear() # Effacer le champ avant de taper
            search_box.send_keys(query)
            search_box.send_keys(Keys.RETURN)
            
            print(f"URL après soumission recherche : {driver.current_url}")

            # Attendre que la page de résultats de recherche se charge (ou une redirection)
            WebDriverWait(driver, 30).until( # Augmentation du timeout
                EC.presence_of_element_located((By.XPATH, "//div[@class='content'] | //div[contains(@class,'search_results')] | //body[not(@id='homepage')]")) # Body ne doit pas être celui de la homepage
            )
            print(f"URL sur la page de résultats de recherche : {driver.current_url}")

            artist_url_part = query.lower().replace(" ", "-")
            song_elements = []

            # Étape 1: Trouver le lien vers la page de l'artiste basé sur l'inspection du HTML sauvegardé
            # Le lien est sous un h2 "Artiste", dans une table.class="song-list", td.class="song-name"
            artist_page_link_xpath = f"//h2[normalize-space()='Artiste']/following-sibling::div//table[@class='song-list']//td[@class='song-name']//a[contains(@href, '/{artist_url_part}') and contains(translate(normalize-space(.), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), '{query.lower()}')]"
            
            print(f"XPath pour le lien de la page artiste: {artist_page_link_xpath}")
            
            try:
                artist_link_element = WebDriverWait(driver, 15).until(
                    EC.element_to_be_clickable((By.XPATH, artist_page_link_xpath))
                )
                artist_href = artist_link_element.get_attribute('href')
                print(f"Lien vers la page artiste trouvé: {artist_href}")
                
                current_url_before_click = driver.current_url
                print(f"URL avant clic sur lien artiste: {current_url_before_click}")
                
                # Tenter de cliquer, possiblement gérer des overlays
                try:
                    driver.execute_script("arguments[0].click();", artist_link_element) # Clic JavaScript, peut contourner certains problèmes
                    print("Clic sur le lien artiste effectué via JavaScript.")
                except Exception as e_click_js:
                    print(f"Clic JavaScript a échoué ({e_click_js}), tentative de clic normal.")
                    artist_link_element.click()
                    print("Clic normal sur le lien artiste effectué.")

                # Attendre que la navigation se produise et que la nouvelle page se charge
                WebDriverWait(driver, 20).until(EC.url_contains(artist_url_part)) # Attendre que l'URL contienne la partie artiste
                # Ou une attente plus robuste si l'URL ne change pas de manière prévisible :
                # WebDriverWait(driver, 20).until(EC.staleness_of(search_box)) # Attendre que l'ancien search_box devienne stale

                print(f"URL après tentative de navigation vers page artiste: {driver.current_url}")

                # Attendre un élément distinctif de la page artiste
                WebDriverWait(driver, 30).until(
                    EC.presence_of_element_located((By.XPATH, f"//h1[contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), '{query.lower()}')] | //div[@id='artprofile'] | //table[contains(@class,'songlist')] | //ul[contains(@class,'song-list')]"))
                )
                print(f"Confirmation: URL sur la page de l'artiste : {driver.current_url}")

                # Étape 2: Extraire les chansons de la page de l'artiste
                # Basé sur l'inspection de artist_page_Imagine_Dragons.html, les chansons sont dans des
                # <table class="song-list"> puis <td class="song-name"><p><a>...</a></p></td>
                songs_on_artist_page_xpath = f"//table[@class='song-list']//td[@class='song-name']/p/a[contains(@href, '/{artist_url_part}/paroles-')]"
                print(f"XPath pour les chansons sur la page artiste: {songs_on_artist_page_xpath}")
                song_elements = driver.find_elements(By.XPATH, songs_on_artist_page_xpath)
                print(f"Nombre d'éléments de chanson trouvés sur la page artiste: {len(song_elements)}")

                if not song_elements:
                    # Essayer un XPath un peu plus large si le premier ne trouve rien (au cas où la structure varie légèrement)
                    songs_on_artist_page_xpath_fallback = f"//div[contains(@class, 'song-listing-extra-inner')]//table[@class='song-list']//td[@class='song-name']/p/a"
                    print(f"XPath de fallback pour les chansons sur la page artiste: {songs_on_artist_page_xpath_fallback}")
                    song_elements = driver.find_elements(By.XPATH, songs_on_artist_page_xpath_fallback)
                    print(f"Nombre d'éléments de chanson trouvés sur la page artiste (fallback): {len(song_elements)}")
                    if not song_elements:
                        print("Aucune chanson trouvée sur la page artiste même avec le XPath de fallback.")
                        # La sauvegarde du HTML n'est plus nécessaire ici car on a déjà analysé le fichier.
                        # Si cela échoue encore, c'est que la page est dynamique ou la structure a encore changé.

            except TimeoutException:
                print(f"Timeout lors de la navigation ou du chargement de la page artiste pour '{query}'.")
                # Il n'est plus nécessaire de sauvegarder le HTML ici car nous avons utilisé le HTML précédemment sauvegardé.
                # Si cela échoue encore, le XPath est toujours incorrect ou la page est différente de ce que nous attendons.
                print("Poursuite avec l'extraction depuis la page de recherche actuelle (fallback).")
                fallback_xpath_songs = "//table//tr[.//a[contains(@href, '/paroles-')]]"
                song_elements = driver.find_elements(By.XPATH, fallback_xpath_songs)
                print(f"Nombre d'éléments de chanson trouvés (fallback XPath): {len(song_elements)}")

            except Exception as e_artist_nav:
                print(f"Erreur inattendue lors de la recherche du lien artiste pour '{query}': {e_artist_nav}")
                print("Poursuite avec l'extraction depuis la page de recherche actuelle (fallback).")
                fallback_xpath_songs = "//table//tr[.//a[contains(@href, '/paroles-')]]"
                song_elements = driver.find_elements(By.XPATH, fallback_xpath_songs)
                print(f"Nombre d'éléments de chanson trouvés (fallback XPath): {len(song_elements)}")

            # Boucle d'extraction des chansons
            # La variable `song_elements` est soit peuplée par les chansons de la page artiste,
            # soit par les chansons du fallback (si la navigation vers la page artiste a échoué).
            # La variable `in_fallback_mode` détermine comment traiter `item_element`.
            
            in_fallback_mode = artist_url_part not in driver.current_url
            if in_fallback_mode:
                print(f"Mode Fallback actif car l'URL actuelle ({driver.current_url}) ne contient pas '{artist_url_part}'.")
            else:
                print(f"Mode Page Artiste actif (URL: {driver.current_url}).")

            for i, item_element in enumerate(song_elements):
                try:
                    name = ""
                    link = None
                    artist_text = query # Par défaut pour la page artiste

                    if not in_fallback_mode: # On est sur la page artiste
                        # item_element est déjà l'élément <a>
                        link_element_loop = item_element
                        raw_name = link_element_loop.text.strip()
                        link = link_element_loop.get_attribute("href")
                        name = raw_name
                        if name.lower().endswith(f" - {artist_text.lower()}"): # Nettoyage simple
                            name = name[:-(len(artist_text) + 3)].strip()
                    else: # On est en mode Fallback (sur la page de recherche générale), item_element est un <tr>
                        row_element = item_element
                        # print(f"Fallback: Traitement ligne: {row_element.text[:70]}")
                        try:
                            link_tag_fallback = row_element.find_element(By.XPATH, ".//td[@class='song-name']//a | .//td[1]//a")
                            raw_name = link_tag_fallback.text.strip()
                            link = link_tag_fallback.get_attribute("href")
                            name = raw_name # Nom initial avant extraction artiste

                            try:
                                artist_cells = row_element.find_elements(By.XPATH, "./td")
                                # Sur la page de recherche, l'artiste est souvent dans la 2e ou 3e cellule visible
                                # La première cellule peut être un numéro ou une image.
                                # La cellule du titre est souvent td[@class='song-name']
                                # On cherche une cellule après celle du titre.
                                artist_text_candidate = ""
                                # Chercher la cellule du titre d'abord
                                title_cell_index = -1
                                link_href = link_tag_fallback.get_attribute('href')

                                for idx, cell in enumerate(artist_cells):
                                    cell_html = cell.get_attribute('innerHTML')
                                    if link_href and cell_html and link_href in cell_html:
                                        title_cell_index = idx
                                        break
                                
                                if title_cell_index != -1 and title_cell_index + 1 < len(artist_cells):
                                    artist_text_candidate = artist_cells[title_cell_index + 1].text.strip()
                                
                                if artist_text_candidate: # Si on a trouvé un candidat dans la cellule adjacente
                                    artist_text = artist_text_candidate
                                elif " - " in raw_name:
                                    parts = raw_name.split(" - ", 1)
                                    if len(parts) > 1 and parts[-1].strip():
                                        artist_text = parts[-1].strip()
                                        name = parts[0].strip()
                                else:
                                    artist_text = "Artiste Inconnu (Fallback)"
                            except:
                                if " - " in raw_name:
                                    parts = raw_name.split(" - ", 1)
                                    if len(parts) > 1 and parts[-1].strip():
                                        artist_text = parts[-1].strip()
                                        name = parts[0].strip()
                                else:
                                    artist_text = "Artiste Inconnu (Fallback)"
                        except Exception as e_parse_row:
                            print(f"  Erreur parsing ligne en fallback: {e_parse_row} - Ligne: {row_element.text[:70]}")
                            continue
                    
                    # Nettoyage final du nom
                    if artist_text and artist_text != "Artiste Inconnu (Fallback)" and name.lower().endswith(f" - {artist_text.lower()}"):
                        name = name[:-(len(artist_text) + 3)].strip()
                    
                    # Enlever les numéros et sauts de ligne au début du nom (ex: "1\nBeliever")
                    match_leading_num = re.match(r"^\d+\s*\n(.*)", name, re.DOTALL)
                    if match_leading_num:
                        name = match_leading_num.group(1).strip()
                    
                    name = name.strip() # Nettoyage final

                    if name and link:
                        songs.append(Song(idx=str(i+1), name=name, link=link, artist=artist_text))
                    else:
                        print(f"  Chanson ignorée (nom ou lien manquant): Titre='{name}', Lien='{link}'")

                except StaleElementReferenceException:
                    print(f"Élément devenu 'stale' lors de l'extraction de la chanson {i+1}. Ignoré.")
                    continue
                except Exception as ex_song:
                    print(f"Erreur lors de l'extraction d'une chanson: {ex_song} - Élément HTML (approx): {item_element.text[:200]}")
            
            if not song_elements and len(driver.find_elements(By.XPATH, "//*[contains(text(), 'Aucun résultat') or contains(text(),'pas de résultats')]")) > 0:
                print("Aucun résultat trouvé pour la recherche sur le site.")

        except TimeoutException as e_timeout:
            print(f"Timeout Selenium global lors de la recherche: {e_timeout}")
        except StaleElementReferenceException as e_stale:
            print(f"Erreur StaleElementReferenceException globale: {e_stale}")
        except Exception as e_general: # Attrape les erreurs de la boucle driver.get() si elles sont relancées
            print(f"Erreur Selenium générale inattendue (peut-être lors du chargement initial): {e_general}")
        finally:
            print("Fermeture du driver Selenium.")
            if 'driver' in locals() and driver: # S'assurer que driver est défini
                driver.quit()
        
        return songs
