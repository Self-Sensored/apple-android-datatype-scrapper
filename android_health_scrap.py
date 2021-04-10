from abc import ABC, abstractmethod
import requests
import re
from bs4 import BeautifulSoup
import pandas as pd

# General Datatypes
# https://developer.apple.com/documentation/healthkit/data_types

# Nutritions Datatypes
# https://developer.apple.com/documentation/healthkit/data_types/nutrition_type_identifiers

# Symptoms Datatypes
# https://developer.apple.com/documentation/healthkit/data_types/symptom_type_identifiers

class AndroidScrapper(ABC):

    def __init__(self, html_path=None, table_index = 0):
        html_text = ""
        with open(html_path, "r") as f:
            html_text = f.read()

        soup = BeautifulSoup(html_text, "html.parser")
        soup.encode("utf-8")
        self.items = soup.find_all("table", {"class": "jd-sumtable"})[table_index]
        self.items = soup.find_all("tr")

        self.clean_html = re.compile("<.*?>")
        self.find_link = re.compile("href=\".*?\"")
        self.clean_multi_spaces = re.compile(" +")

    @abstractmethod
    def get_dataframe_from_html(self):
        pass

class GeneralAndroidScrapper(AndroidScrapper):
    
    def get_dataframe_from_html(self, type = 'one'):
        health_app_datatypes = []
        for item in list(self.items):
            lil_soup = BeautifulSoup(str(item), "html.parser")

            if type == 'one':
                link, category, description = self.extract_one(lil_soup, item)
            elif type == 'two':
                link, category, description = self.extract_two(lil_soup, item)

            if not link:
                continue

            health_app_datatypes.append(
                {"category": category, "description": description, "link": link}
            )

        return pd.DataFrame(health_app_datatypes)


    def extract_one(self, lil_soup, item):
        try:
            link = re.findall(self.find_link, str(item))[0].replace("href=\"", "").replace("\"", "")
            category = lil_soup.find('a').getText().strip()
            
            tmp = lil_soup.find_all('td', {"class": "jd-descrcol"})
            description = re.sub(self.clean_multi_spaces, " ", tmp[0].getText().strip().replace("\n", ""))

            if category in ["Field", "Object", "String", "Class"]:
                return (None, None, None)

            return (link, category, description)
        except:
            return (None, None, None)

    def extract_two(self, lil_soup, item):
        
        # print(item)
        category = lil_soup.find_all("td", {"class": "jd-linkcol"})
        description = lil_soup.find_all("td", {"class": "jd-descrcol"})

        try:
            link = re.findall(self.find_link, str(item))[0].replace("href=\"", "").replace("\"", "")
            category = re.sub(self.clean_multi_spaces, " ", category[0].getText().replace("\n", "").strip())
            description = re.sub(self.clean_multi_spaces, " ", description[0].getText().replace("\n", "").strip())
            
            return (link, category, description)
        except:
            return (None, None, None)

        return (None, None, None)


# https://developers.google.com/android/reference/com/google/android/gms/fitness/data/HealthFields
HEALTH_HTML_FILE = "/Users/ladvien/Documents/apple_health_nutrition_data_types_files/android_health.html"

scrap = GeneralAndroidScrapper(HEALTH_HTML_FILE, 1)
df1 = scrap.get_dataframe_from_html()
df1["datatype"] = "HealthDataTypes"

print(df1)

# https://developers.google.com/android/reference/com/google/android/gms/fitness/data/SleepStages
SLEEP_HTML_FILE = "/Users/ladvien/Documents/apple_health_nutrition_data_types_files/android_sleep.html"
scrap = GeneralAndroidScrapper(SLEEP_HTML_FILE)
df2 = scrap.get_dataframe_from_html()
df2["datatype"] = "SleepStagesDataTypes"

print(df2)

# https://developers.google.com/android/reference/com/google/android/gms/fitness/data/WorkoutExercises
ACTIVITIES_HTML_FILE = "/Users/ladvien/Documents/apple_health_nutrition_data_types_files/android_activities.html"
scrap = GeneralAndroidScrapper(ACTIVITIES_HTML_FILE)
df3 = scrap.get_dataframe_from_html(type='two')
df3["datatype"] = "ExerciseDataTypes"

print(df3)

# https://developers.google.com/android/reference/com/google/android/gms/fitness/data/Field
NUTRITION_HTML_FILE = "/Users/ladvien/Documents/apple_health_nutrition_data_types_files/android_nutrition.html"
scrap = GeneralAndroidScrapper(NUTRITION_HTML_FILE)
df4 = scrap.get_dataframe_from_html(type='two')
df4["datatype"] = "NutritionDataTypes"

print(df4)

# https://developers.google.com/android/reference/com/google/android/gms/fitness/data/DataType
NUTRITION_HTML_FILE = "/Users/ladvien/Documents/apple_health_nutrition_data_types_files/android_general.html"
scrap = GeneralAndroidScrapper(NUTRITION_HTML_FILE)
df5 = scrap.get_dataframe_from_html(type='two')
df5["datatype"] = "GeneralDataTypes"

print(df5)

OUT_ANDROID = "./android_datatypes.csv"
df = pd.concat([df1, df2, df3, df4, df5])
df.to_csv(OUT_ANDROID, index=False, encoding='utf-8-sig')