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

class AppleHealthKitScrapper(ABC):

    def __init__(self, html_path=None):
        html_text = ""
        with open(html_path, "r") as f:
            html_text = f.read()

        soup = BeautifulSoup(html_text, "html.parser")
        soup.encode("utf-8")
        self.items = soup.find_all("div", ["link-block", "topic"])

        self.clean_html = re.compile("<.*?>")
        self.clean_multi_spaces = re.compile(" +")

    @abstractmethod
    def get_dataframe_from_html(self):
        pass

class GeneralAppleHealthKitScrapper(AppleHealthKitScrapper):
    
    def get_dataframe_from_html(self):
        health_app_datatypes = []
        for item in list(self.items):
            clean_item = re.sub(self.clean_html, " ", str(item))
            clean_item = re.sub(self.clean_multi_spaces, " ", clean_item)

            # Only get types
            if "static let " not in str(clean_item):
                continue

            # Get datatype, category, description
            datatype = ""
            category = ""
            description = ""

            datatype, category = clean_item.split(":")

            # Clean datatype
            datatype = datatype.replace("static let", "").replace(" ", "").strip()

            tmp = category.split("\n")

            # Clean category
            category = tmp[0].replace(" ", "").strip()

            # Clean description
            description = tmp[1:-1]
            description = "".join(description).strip()

            health_app_datatypes.append(
                {"category": category, "datatype": datatype, "description": description}
            )

        return pd.DataFrame(health_app_datatypes)

class SpecificAppleHealthKitScrapper(AppleHealthKitScrapper):

    def get_dataframe_from_html(self):
        health_app_datatypes = []
        for item in list(self.items):
            item = str(item).replace('<div class="content" data-v-01f7f080="" data-v-7ea0aa49="">', "!")
            clean_item = re.sub(self.clean_html, " ", str(item))
            clean_item = re.sub(self.clean_multi_spaces, " ", clean_item)


            # Only get types
            if "static let " not in str(clean_item):
                continue

            # Get datatype, category, description
            datatype = ""
            category = ""
            description = ""

            datatype, category = clean_item.split(":")

            # Clean datatype
            datatype = datatype.replace("static let", "").replace(" ", "").strip()

            category, description = category.split("!")

            # Clean category
            category = category.replace(" ", "").strip()

            # Clean description
            description = description.strip()

            health_app_datatypes.append(
                {"category": category, "datatype": datatype, "description": description}
            )

        return pd.DataFrame(health_app_datatypes)


HTML_FILE_PATH = "/Users/ladvien/Documents/apple_health_data_types.html"
NUTRITION_HTML_PATH = "/Users/ladvien/Documents/apple_health_nutrition_data_types.html"
SYMPTOMS_HTML_PATH = "/Users/ladvien/Documents/apple_health_nutrition_data_types_files/apple_health_symptoms_data_types.html"

OUT_GENERAL = "./general_datatypes.csv"


scrap = GeneralAppleHealthKitScrapper(HTML_FILE_PATH)
df1 = scrap.get_dataframe_from_html()
scrap = SpecificAppleHealthKitScrapper(NUTRITION_HTML_PATH)
df2 = scrap.get_dataframe_from_html()
scrap = SpecificAppleHealthKitScrapper(SYMPTOMS_HTML_PATH)
df3 = scrap.get_dataframe_from_html()

df = pd.concat([df1, df2, df3])
df.to_csv(OUT_GENERAL, index=False, encoding='utf-8-sig')