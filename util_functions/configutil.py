import platform, os
from pathlib import Path
import subprocess
import json
import requests
from bs4 import BeautifulSoup

def get_app_data_path(app_name="HSRCharEval"):
    if platform.system() == "Windows":
        return Path(os.getenv('LOCALAPPDATA')) / app_name
    elif platform.system() == "Darwin":  # macOS
        return Path.home() / "Library" / "Application Support" / app_name
    else:  # Linux
        return Path.home() / f".{app_name.lower()}"
    
def open_file_explorer(path):
    system = platform.system()
    try:
        if system == "Windows":
            os.startfile(path)
        elif system == "Darwin":
            subprocess.run(["open", path], check=True)
        elif system == "Linux":
            if "DISPLAY" in os.environ:
                subprocess.run(["xdg-open", path], check=True)
            else:
                raise EnvironmentError("No GUI environment detected (missing DISPLAY)")
        else:
            raise NotImplementedError(f"Unsupported OS: {system}")
    except Exception as e:
        print(f"Could not open file explorer: {e}")

def filesetup():
    if not PATHS.uid.exists():
        with open(PATHS.uid,"w") as f:
            f.write("0")
    if not PATHS.characters.exists():
        with open(PATHS.characters,"w") as f:
            json.dump({},f)
    if not PATHS.breakpoints.exists():
        with open(PATHS.breakpoints,"w") as f:
            json.dump({},f)
    if not PATHS.teams.exists():
        with open(PATHS.teams,"w") as f:
            json.dump({},f)
    if not PATHS.bridgedata.exists():
        with open(PATHS.bridgedata,"w") as f:
            json.dump({},f)
    if not PATHS.importignore.exists():
        with open(PATHS.importignore,"w") as f:
            json.dump({"keys":[]},f)
    if not PATHS.api_name_map.exists():
        with open(PATHS.api_name_map,"w") as f:
            json.dump({},f)
    if not PATHS.relics.exists():
        with open(PATHS.relics,"w") as f:
            json.dump({},f)

    with open(PATHS.breakpoints) as f:
        breakpoints = json.load(f)
        for i in breakpoints:
            if not "inverse" in breakpoints[i].keys():
                breakpoints[i]["inverse"] = []

    with open(PATHS.bridgedata) as f:
        bridgedata = json.load(f)
    for i in breakpoints:
        if i not in bridgedata:
            bridgedata[i] = {}

def first_run_import():
    breakpoints = {}
    while True:
        print("\033c\033[7m First-Run Setup               >\033[0m")
        print("\nImport all available characters to create breakpoint templates?\n\n\033[38;5;240m0: No / 1: Yes.\033[0m")
        index = input("\n> ").strip()
        if index.isdigit():
            break
    if index == "1":
        try:
            with open(PATHS.importignore) as f:
                ignore = json.load(f)
            creation_template = {"hp":-1,"atk":-1,"def":-1,"spd":-1,"crit rate":-1,"crit dmg":-1,"break effect":-1,"energy regen":-1,"effect hit":-1,"inverse":[]}
            response = requests.get("https://www.prydwen.gg/star-rail/characters")
            response.raise_for_status()
            main = BeautifulSoup(response.text, 'html.parser').find_all("div", {"class", "avatar-card"})
            entryindex = len(main)
            for object in main:
                objectid = object.find("span").find("a")["href"].split("/")[-1].replace("-"," ")
                if not (objectid not in breakpoints.keys() and objectid not in ignore["keys"]):
                    entryindex -= 1
            print(f"Expecting {entryindex} entries.")
            print("1: Change name / 2: Accept name")
            for object in main:
                target = object.find("span").find("a")["href"].split("/")[-1].replace("-"," ")
                if target not in breakpoints.keys() and target not in ignore["keys"]:
                    while True:
                        index = input(f"{target.upper()} >> ")
                        if index.isdigit():
                            if int(index) <= 2 and int(index) >= 0:
                                index = int(index)
                                break
                    if index == 0:
                        ignore["keys"].append(target)
                    elif index == 1:
                        ignore["keys"].append(target)
                        target = input("Enter new ID: ").lower()
                        breakpoints[target] = creation_template
                    elif index == 2:
                        breakpoints[target] = creation_template
            with open(PATHS.importignore,"w") as f:
                json.dump(ignore,f)
            with open(PATHS.breakpoints) as f:
                json.dump(breakpoints,f)
            input("\n\033[38;5;40m[ Done. ]\033[0m")
        except requests.exceptions.RequestException as e:
            input("\n\033[31m[ Request has failed. Are you offline? ]\033[0m")
        except KeyboardInterrupt:
            input("\n\033[31m[ Aborted, closing session to reset. ]\033[0m")
            raise KeyboardInterrupt()
        except Exception as e:
            input(f"\n\033[31m[ {e} ]\033[0m")


APP_DATA_DIR = get_app_data_path()
APP_DATA_DIR.mkdir(parents=True, exist_ok=True)

class PATHS:
    uid = APP_DATA_DIR / ".uid"
    characters = APP_DATA_DIR / "chardata.json"
    breakpoints = APP_DATA_DIR / "breakpoints.json"
    teams = APP_DATA_DIR / "teamdata.json"
    bridgedata = APP_DATA_DIR / "bridgedata.json"
    importignore = APP_DATA_DIR / "importignore.json"
    api_name_map = APP_DATA_DIR / "apinamemap.json"
    relics = APP_DATA_DIR / "relics.json"