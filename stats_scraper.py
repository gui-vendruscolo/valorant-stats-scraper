from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from player_class import PlayerStats
import undetected_chromedriver as uc
import json
import os
import time
import csv


playernames_path = './resources/playernames.txt'
player_nickname = "savero rebaixada rkt"
url = "https://api.tracker.gg/api/v2/valorant/standard/matches/riot/LFT%20P0PPIN%234529?type=competitive&season=&agent=all&map=all"
match_url = 'https://api.tracker.gg/api/v2/valorant/standard/matches/'
player_url = 'https://tracker.gg/valorant/profile/riot/'
seconds_between_calls = 3

# chrome_options = Options()
# chrome_options.add_argument("--headless") 
# driver = webdriver.Chrome()

options = webdriver.ChromeOptions() 
options.add_argument("start-maximized")
#options.add_argument("--headless")
driver = uc.Chrome(options=options)

file_size = 0
try:
    file_size = os.path.getsize(playernames_path)
except Exception:
    file_size = 0


def extract_nicks():
    driver.get(url)
    time.sleep(10)
    page_content = driver.page_source
    driver.implicitly_wait(3)



    # Extraia o JSON da página
    json_start = page_content.find("{")
    json_end = page_content.rfind("}") + 1
    json_text = page_content[json_start:json_end]

    matches_data = json.loads(json_text)

    player_nicks = []
    for match in matches_data['data']['matches']:
        time.sleep(seconds_between_calls)
        match_id = match['attributes']['id']
        driver.get(match_url + match_id)
        players_page_content = driver.page_source
        
        # Extraia o JSON da página
        json_start = players_page_content.find("{")
        json_end = players_page_content.rfind("}") + 1

        json_text = json.loads(players_page_content[json_start:json_end])

        segments = json_text['data']['segments']

        platform_identifiers = []
        for elements in segments:
            if elements['type'] != 'player-round-kills':
                continue

            player_locations = elements['metadata']['playerLocations']
            platform_identifiers = platform_identifiers + [player['platformUserIdentifier'] for player in player_locations]
            platform_identifiers = list(set(platform_identifiers))

            if len(platform_identifiers) > 9:
                break
            
        player_nicks = player_nicks + platform_identifiers

    

    player_nicks = list(set(player_nicks))
    print(player_nicks)
    print(len(player_nicks))
    with open(playernames_path, 'a', encoding='utf-8') as file:
        for item in player_nicks:
            file.write(str(item) + '\n')

if file_size <= 0:
    print("Extracting nicks")

    extract_nicks()


print('\nnicks already written\n')


players = []
players_stats = []
with open(playernames_path, 'r', encoding='utf-8') as players_file:

    players_csv = "./resources/validation_plus.csv"
    #header = ['Nome', 'k/d ratio', 'dmg/round', 'headshot', 'kast', 'dd delta', 'kills', 'rank']
    with open(players_csv, mode='a+', newline='', encoding='utf=8') as csv_file:

        writer = csv.writer(csv_file, delimiter=";")
    
        for line in players_file:
            players.append(line.strip())

        players_stats = []
        success = 0
        errors = 0
        for player in players:
            link = player_url + player.replace("#", "%23")

            try:
                profile_page = driver.get(link)

                driver.implicitly_wait(3)

                try:
                    error = driver.find_element(By.XPATH, "/html/body/div[2]/div/div[2]/div[3]/div/main/div[4]/div[2]/span")

                    print(f"{player} profile is private. Proceeding.")
                    errors += 1
                    continue

                except NoSuchElementException:

                    try:
                        popup_closebutton = driver.find_element(By.XPATH, '//*[@id="trn-teleport-modal"]/div/div[2]/div/div/div[2]')
                        popup_closebutton.click()
                        print("POPUP DE NATAL FECHADO")

                    except NoSuchElementException: 
                        print("POPUP nao encontrado.")

                    finally:

                        try:
                            kdratio = driver.find_element(By.XPATH, "/html/body/div/div/div[2]/div[3]/div/main/div[4]/div[3]/div[2]/div[2]/div[1]/div[1]/div[3]/div[2]/div/div[2]/span[2]").text
                            dmgperround = driver.find_element(By.XPATH, "/html/body/div/div/div[2]/div[3]/div/main/div[4]/div[3]/div[2]/div[2]/div[1]/div[1]/div[3]/div[1]/div/div[2]/span[2]").text
                            headshot = driver.find_element(By.XPATH, "/html/body/div/div/div[2]/div[3]/div/main/div[4]/div[3]/div[2]/div[2]/div[1]/div[1]/div[3]/div[3]/div/div[2]/span[2]").text.replace("%", "")
                            kast = driver.find_element(By.XPATH, "/html/body/div/div/div[2]/div[3]/div/main/div[4]/div[3]/div[2]/div[2]/div[1]/div[1]/div[5]/div[2]/div/div[2]/span[2]").text.replace("%", "")
                            dddelta = driver.find_element(By.XPATH, "/html/body/div/div/div[2]/div[3]/div/main/div[4]/div[3]/div[2]/div[2]/div[1]/div[1]/div[5]/div[3]/div/div[2]/span[2]").text
                            kills = driver.find_element(By.XPATH, "/html/body/div/div/div[2]/div[3]/div/main/div[4]/div[3]/div[2]/div[2]/div[1]/div[1]/div[5]/div[4]/div/div[2]/span[2]").text
                            acs = driver.find_element(By.XPATH, "/html/body/div/div/div[2]/div[3]/div/main/div[4]/div[3]/div[2]/div[2]/div[1]/div[1]/div[5]/div[7]/div/div[2]/span[2]").text
                            kad = driver.find_element(By.XPATH, "/html/body/div/div/div[2]/div[3]/div/main/div[4]/div[3]/div[2]/div[2]/div[1]/div[1]/div[5]/div[8]/div/div[1]/span[2]").text
                            rank = driver.find_element(By.XPATH, "/html/body/div/div/div[2]/div[3]/div/main/div[4]/div[3]/div[2]/div[2]/div[1]/div[1]/div[2]/div[2]/div/div[1]/div/div[1]/span[2]").text
                            rad_immort_rank = driver.find_element(By.XPATH, "/html/body/div/div/div[2]/div[3]/div/main/div[4]/div[3]/div[2]/div[2]/div[1]/div[1]/div[2]/div[2]/div/div[1]/div/div[1]/span[1]").text

                            if rad_immort_rank == "Rating":
                                stats = PlayerStats(name=player, kdratio=kdratio, dmgperround=dmgperround, headshot=headshot, kast=kast, dddelta=dddelta, kills=kills, acs=acs, kad=kad, rank=rank)
                            else:
                                stats = PlayerStats(name=player, kdratio=kdratio, dmgperround=dmgperround, headshot=headshot, kast=kast, dddelta=dddelta, kills=kills, acs=acs, kad=kad, rank=rad_immort_rank)

                            players_stats.append(stats)
                            writer.writerow(stats.get_attr_list())
                            print(stats)
                            success += 1
                            driver.implicitly_wait(3)                        
                        
                        except Exception as e:
                            print(f"There was an error while retrieving {player} stats. Proceeding.\n")
                            errors += 1

            except Exception as e:
                print(f"There was an error while retrieving {player} stats. Proceeding.\n")
                errors += 1



print(f"Fim. \nO numero de jogadores registrados foi {success}\nHouve {errors} jogadores que não puderam ser registrados")


        

            
        