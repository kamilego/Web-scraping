from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
import time
import sys

"""
py soccer.py 5 2.4 0
"""

if len(sys.argv) != 4:
    raise Exception("""Command should looks like: py soccer.py 5 2.4 0
                       Where 5 means: number of days h2h to analyze
                           2.4 means: avg goals
                             0 means: day to analyze from today""")

last_matches = int(sys.argv[1])
avg_goals = float(sys.argv[2])
next_days = int(sys.argv[3])

print()
print(f"Analyzing last -{last_matches}- matches where AVG goals are greater than -{avg_goals}-")
print()

website_url = r"https://www.flashscore.com/"
chromedriver_path = r"C:\Users\default.DESKTOP-E4TLVMN\Downloads\chromedriver.exe"

service = Service(chromedriver_path)
options = webdriver.ChromeOptions()
# options.add_argument("headless")
options.add_experimental_option('excludeSwitches', ['enable-logging'])
options.add_experimental_option("detach", True)

driver = webdriver.Chrome(service=service, options=options)
driver.maximize_window()

driver.get(website_url)
time.sleep(2)
cookies = driver.find_element(By.ID, "onetrust-accept-btn-handler").click()
# button = driver.find_element(By.CLASS_NAME, "wizard__closeButton").click()

if next_days > 0:
    for _ in range(next_days):
        next_day = driver.find_element(By.CLASS_NAME, "calendar__navigation--tomorrow").click()
        time.sleep(1)

all_events = driver.find_elements(By.CSS_SELECTOR, '.sportName, .soccer')[1]
main_events = all_events.find_elements(By.CSS_SELECTOR, '.wclLeagueHeader, .event__match')

events_dict = {}
for num, elem in enumerate(main_events[:10]):
    if "wclLeagueHeader" in elem.get_attribute('innerHTML'):
        if "Unpin this league" in elem.get_attribute('innerHTML'):
            title = elem.find_element(By.CLASS_NAME, 'event__title').text
            events_dict[title] = []
        else:
            break
    else:
        events_dict[title].append(elem)

multiple_odds = 1
for league, matches in events_dict.items():
    print(league.replace("\n", ""))
    print("-"*30)
    for match in matches:
        time.sleep(1)
        match.click()
        time.sleep(1)
        new_window = driver.window_handles
        driver.switch_to.window(new_window[1])
        driver.find_element(By.XPATH, "//a[@href='#/h2h']").click()
        time.sleep(2)
        groups = driver.find_elements(By.CLASS_NAME, "h2h__section")
        group_dict = {}
        for group in groups:
            team_title = group.find_element(By.CLASS_NAME, "section__title").text
            results = group.find_elements(By.CLASS_NAME, "h2h__result")[:last_matches]
            num_of_h2h_matches = len(group.find_elements(By.CLASS_NAME, "h2h__row"))
            goal_sum = 0
            for result in results:
                goals = [int(elem) for elem in result.text.split("\n")]
                goal_sum += sum(goals)
            if num_of_h2h_matches:
                if last_matches > num_of_h2h_matches:
                    group_dict[team_title] = round(goal_sum/num_of_h2h_matches, 2)
                else:
                    group_dict[team_title] = round(goal_sum/last_matches, 2)
            else:
                group_dict[team_title] = "No historical matches between teams"
        if all([result >= avg_goals for result in list(group_dict.values())[:2]]): # taking only matches of teams not h2h
            current_date = driver.find_element(By.CLASS_NAME, "duelParticipant__startTime").text
            match_status = driver.find_element(By.CLASS_NAME, "fixedHeaderDuel__detailStatus").text
            driver.find_element(By.XPATH, "//a[@href='#/odds-comparison']").click()
            time.sleep(5)
            driver.find_element(By.XPATH, "//a[@href='#/odds-comparison/over-under']").click()
            time.sleep(5)
            odds = driver.find_elements(By.CLASS_NAME, "oddsCell__odds")[2] # list off odds over 1.5 goal
            first_odd_1_5 = odds.find_element(By.CSS_SELECTOR, '.oddsCell__odd, .oddsCell__highlight').text
            if "finished" not in match_status.lower():
                multiple_odds *= float(first_odd_1_5)
            print(f"{current_date} | {match_status}")
            time.sleep(1)
            for key, value in group_dict.items():
                print(f"{key:<35}", value)
            print(f"Over 1.5 goals odd: {first_odd_1_5}")
            print("-"*5)
        driver.close()
        driver.switch_to.window(new_window[0])
print(f"Overall over 1.5 goals odds: {multiple_odds:.2f}")

driver.close()