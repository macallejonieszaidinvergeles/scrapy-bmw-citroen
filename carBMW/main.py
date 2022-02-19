from lib2to3.pgen2 import driver
import random
import time
from selenium.webdriver.common.by import By
import undetected_chromedriver as uc
import json
from lib2to3.pytree import convert
import re


class CocheBMWClass:
    def main(self):
        # driver = uc.Chrome()
        global driver

        user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.53 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:96.0) Gecko/20100101 Firefox/96.0",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.121 Safari/537.36",
            "Mozilla/5.0 (X11; Ubuntu; Linux i686; rv:24.0) Gecko/20100101 Firefox/24.0",
        ]
        agents = len(user_agents) - 1

        pages = [
            "https://www.coches.net/segunda-mano/?MakeId=7&MinYear=2010&MaxYear=2020",
            # 'https://www.coches.net/segunda-mano/?MakeId=7&MinYear=2010&MaxYear=2020&pg=2',
            # 'https://www.coches.net/segunda-mano/?MakeId=7&MinYear=2010&MaxYear=2020&pg=3',
            # 'https://informatica.ieszaidinvergeles.org:10099/pia/practica2/cochesnet.html'
        ]
        first = True

        start_urls = []

        for page in pages:
            increment = 100
            agent_number = random.randint(0, agents)
            driver.execute_cdp_cmd(
                "Network.setUserAgentOverride", {
                    "userAgent": user_agents[agent_number]}
            )
            print(f"user_agents:{user_agents}")
            driver.get(page)
            if first:
                button = driver.find_element_by_xpath(
                    "/html/body/div[1]/div/div[2]/div[2]/div/div/div/footer/div/button[2]"
                )
                button.click()
                first = False
            while True:
                driver.execute_script(
                    "window.scrollTo(0, " + str(increment) + ");")
                time.sleep(1)
                # elements = driver.find_elements(By.CLASS_NAME, "mt-CardBasic-titleLink")
                elements = driver.find_elements(
                    By.CLASS_NAME, "mt-CardAd-media")

                # probar esto
                # start_urls = list(dict.fromkeys(start_urls))

                increment += 200
                if len(elements) >= 30 or increment >= 6000:
                    # aqui se obtendra la info de cada coche y se añadira a una lista o algo
                    break

            time.sleep(random.randint(3, 5))

        for element in elements:
            start_urls.append(element.get_attribute("href"))

        print(f"start_urls: {start_urls}")
        print(f"len start_urls: {len(start_urls)}")

        for url in start_urls:
            time.sleep(5)
            driver.get(url)
            time.sleep(10)
            self.parse()
            time.sleep(7)

        time.sleep(random.randint(3, 5))

    # def getinfoMio():
    #     driver = uc.Chrome()
    #     page = "https://informatica.ieszaidinvergeles.org:10099/pia/practica2/opel.html"
    #     driver.get(page)
    #     # time.sleep(3)
    #     scripts = driver.find_element_by_xpath("/html/body/script[3]")
    #     scripts = scripts.get_attribute("innerHTML")
    #     scripts = scripts[39:len(scripts)-3]
    #     scripts = scripts.replace('\\\\\\"', "")
    #     scripts = scripts.replace('\\"', '"')
    #     scripts = re.sub(r"^\s+|\s+$\t", "", scripts)
    #     # time.sleep(3)
    #     # archivo = json.loads(scripts)
    #     print(f"archivo: \n {scripts[39:len(scripts)-3]}")

    keys = {
        "color": "ad",
        "fuelTypeId": "ad",
        "fuelType": "leadData",
        "id": "ad",
        "km": "ad",
        "make": "ad",
        "makeId": "ad",
        "model": "ad",
        "modelId": "ad",
        "price": "ad",
        "province": "ad",
        "provinceId": "ad",
        "title": "ad",
        "transmissionType": "ad",
        "transmissionTyId": "ad",
        "year": "ad",
        "brand": "leadData",
        "brand_id": "leadData",
        "fuel_type": "ad",
        "km": "leadData",
        "model": "leadData",
        "model_id": "leadData",
        "price": "leadData",
        "seller_type": "leadData",
        "bodyType": "vehicleInfo/specifications",
        "cubicCapacity": "vehicleInfo/specifications",
        "doors": "vehicleInfo/specifications",
        "hp": "vehicleInfo/specifications",
    }

    def parse(self):
        global driver

        keys_and_values = {}
        scripts = driver.find_element_by_xpath("/html/body/script[3]")
        scripts = scripts.get_attribute("innerHTML")
        data_json = self.get_data_in_dictionary(scripts)
        for key in self.keys:
            path = self.get_path(self.keys, key)
            keys_and_values[key] = self.search_all_coincidences(
                key, path, data_json)
        keys_and_values = self.get_only_fisrt_value(keys_and_values)
        json_response = json.dumps(keys_and_values)
        # yield keys_and_values
        return keys_and_values

    def get_only_fisrt_value(self, keys_and_values):
        for key in keys_and_values:
            datas = keys_and_values[key]
            if len(datas) == 0:
                keys_and_values[key] = ""
            else:
                keys_and_values[key] = keys_and_values[key][0]
        return keys_and_values

    def search_all_coincidences(self, key, path, data_json):
        coincidences = []
        data_json = self.get_sub_path(path, data_json)
        if isinstance(data_json, list):
            for data in data_json:
                if isinstance(data, dict) or isinstance(data, list):
                    coincidences = coincidences + self.search_all_coincidences(
                        key, None, data
                    )
        else:
            for data_key in data_json:
                data = data_json[data_key]
                if key == data_key:
                    coincidences.append(data)
                elif isinstance(data, dict) or isinstance(data, list):
                    coincidences = coincidences + self.search_all_coincidences(
                        key, None, data
                    )
        return coincidences

    def get_path(self, keys, key):
        path = None
        if isinstance(keys, dict):
            path = keys[key]
        return path

    def get_sub_path(self, path, data_json):
        if path != None:
            path = path.split("/")
            for sub_path in path:
                data_json = data_json[sub_path]
        return data_json

    def get_data_in_dictionary(self, scripts):
        # for script in scripts:
        scriptText = scripts
        print(f"scriptText:{scriptText}")
        if scriptText.startswith('window.__INITIAL_PROPS__ = JSON.parse("'):
            initialPos = scriptText.find('parse("') + 7
            lastPos = len(scriptText) - 3
            searchStringAd = scriptText[initialPos:lastPos]
            searchStringAd = searchStringAd.replace('\\\\\\"', "")
            searchStringAd = searchStringAd.replace('\\"', '"')
            archivo = json.loads(searchStringAd)
            print(f"archivo:{archivo}")
            return json.loads(searchStringAd)


if __name__ == "__main__":
    bmw = CocheBMWClass()
    driver = uc.Chrome()
    bmw.main()
    # bmw.getinfoMio()


# start_urls = ['https://www.coches.net/bmw-serie-3-318d-gran-turismo-5p-diesel-2017-en-madrid-51139859-covo.aspx', 'https://www.coches.net/bmw-serie-3-318d-touring-5p-diesel-2019-en-barcelona-51242929-covo.aspx', 'https://www.coches.net/bmw-x5-xdrive30d-5p-diesel-2011-en-madrid-51160972-covo.aspx', 'https://www.coches.net/bmw-x6-m50d-5p-diesel-2017-en-vizcaya-48932150-covo.aspx', 'https://www.coches.net/bmw-x6-xdrive40d-5p-diesel-2015-en-madrid-51209365-covo.aspx', 'https://www.coches.net/bmw-x6-xdrive40d-5p-diesel-2016-en-leon-50709570-covo.aspx', 'https://www.coches.net/bmw-x5-xdrive40e-5p-electrico-hibrido-2015-en-madrid-51206461-covo.aspx', 'https://www.coches.net/bmw-x3-m40i-5p-gasolina-2019-en-madrid-51100648-covo.aspx', 'https://www.coches.net/bmw-x4-xdrive30d-diesel-2015-en-valencia-49929730-covo.aspx', 'https://www.coches.net/bmw-serie-5-520da-4p-diesel-2018-en-madrid-51039348-covo.aspx',
#               'https://www.coches.net/bmw-serie-1-118d-5p-diesel-2019-en-malaga-49595915-covo.aspx', 'https://www.coches.net/bmw-serie-5-520da-business-4p-diesel-2017-en-guipuzcoa-51184325-covo.aspx', 'https://www.coches.net/bmw-x4-xdrive20d-5p-diesel-2019-en-murcia-50951177-covo.aspx', 'https://www.coches.net/bmw-serie-2-216d-dct-gran-coupe-4p-diesel-2020-en-murcia-51001957-covo.aspx', 'https://www.coches.net/bmw-serie-6-640d-2p-diesel-2015-en-madrid-51151358-covo.aspx', 'https://www.coches.net/bmw-serie-3-320d-automatico-xdrive-gran-turismo-diesel-2017-en-pontevedra-51339143-covo.aspx', 'https://www.coches.net/bmw-serie-3-318d-gran-turismo-5p-diesel-2014-en-guadalajara-51339107-covo.aspx', 'https://www.coches.net/bmw-serie-3-318d-diesel-2016-en-malaga-51018895-covo.aspx', 'https://www.coches.net/bmw-serie-1-116d-diesel-2017-en-malaga-50979296-covo.aspx', 'https://www.coches.net/bmw-x6-xdrive30d-5p-diesel-2018-en-las_palmas-50366752-covo.aspx']
