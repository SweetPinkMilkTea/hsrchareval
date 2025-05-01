import platform
import re
import json, time, os, traceback
from pathlib import Path

from bs4 import BeautifulSoup
import requests


def get_app_data_path(app_name="HSRCharEval"):
    if platform.system() == "Windows":
        return Path(os.getenv('LOCALAPPDATA')) / app_name
    elif platform.system() == "Darwin":  # macOS
        return Path.home() / "Library" / "Application Support" / app_name
    else:  # Linux
        return Path.home() / f".{app_name.lower()}"

def attributeScore(key, metric, target, isInverse):
    # Logic on Inverse
    if isInverse:
        score = 100000 if metric < target else 0
    else:
        # Setup of lower bound (Score 0)
        lower = target / 2
        if key == "spd" and target > 95:
            lower = (95 + target) / 2
        if key == "energy regen":
            lower = (100 + target) / 2
        # Score calculation
        if metric < target:
            # Get score for non fulfilled target
            score = (metric - lower) / (target - lower) * 100000
        else:
            # Calculated bonus if score exceeds target
            diff = metric - target
            score = 100000
            if key in ["hp","atk","def"]:
                score += int(diff / 10)
            if key in ["crit rate"]:
                score += int(diff)
            if key in ["crit dmg","break effect","effect hit"]:
                score += int(diff / 2)
            if key in ["energy regen", "spd"]:
                score += int(diff * 2)
    if score < 0:
        score = 0
    return score

APP_DATA_DIR = get_app_data_path()
APP_DATA_DIR.mkdir(parents=True, exist_ok=True)

# Paths
class PATHS:
    uid = APP_DATA_DIR / ".uid"
    characters = APP_DATA_DIR / "chardata.json"
    breakpoints = APP_DATA_DIR / "breakpoints.json"
    teams = APP_DATA_DIR / "teamdata.json"
    bridgedata = APP_DATA_DIR / "bridgedata.json"
    importignore = APP_DATA_DIR / "importignore.json"
    api_name_map = APP_DATA_DIR / "apinamemap.json"

try:
    # Setup
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

    with open(PATHS.breakpoints) as f:
        breakpoints = json.load(f)

    with open(PATHS.bridgedata) as f:
        bridgedata = json.load(f)
    for i in breakpoints:
        if i not in bridgedata:
            bridgedata[i] = {}

    with open(PATHS.uid) as f:
        uid = f.read()
        
    with open(PATHS.api_name_map) as f:
        api_name_mapping = json.load(f)

    if len(breakpoints) == 0:
        while True:
            print("\033c\033[7m First-Run Setup               >\033[0m")
            print("\nImport all available characters to create breakpoint templates?\n\n\033[38;5;240m0: No / 1: Yes.\033[0m")
            index = input("\n> ").strip()
            if index.isdigit():
                break
        if index == "1":
            try:
                with open("importignore.json") as f:
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
                with open("importignore.json","w") as f:
                    json.dump(ignore,f)
                with open("breakpoints.json","w") as f:
                    json.dump(breakpoints,f)
                input("\n\033[38;5;40m[ Done. ]\033[0m")
            except requests.exceptions.RequestException as e:
                input("\n\033[31m[ Request has failed. Are you offline? ]\033[0m")
            except KeyboardInterrupt:
                input("\n\033[31m[ Aborted, closing session to reset. ]\033[0m")
                raise KeyboardInterrupt()
            except Exception as e:
                input(f"\n\033[31m[ {e} ]\033[0m")

    if uid == "0":
        while True:
            print("\033c\033[7m Quick-Import Setup               >\033[0m")
            print("\nEnter your UID to look for character data when trying to evaluate them.\nOnly characters featured on your profile page can be accessed.\n\n\033[38;5;240mEnter 0 to skip.\033[0m")
            uid = input("\n> ").strip()
            if uid.isdigit():
                with open(PATHS.uid,"w") as f:
                    f.write(str(uid))
                break

    try:
        print("Connection test...\n\033[38;5;240mSkip it with CTRL + C\033[0m")
        response = requests.get("https://www.prydwen.gg/star-rail/characters")
        response.raise_for_status()
    except:
        isOffline = True
    else:
        isOffline = False

    while True:
        print("\033c\033[1mHSR Character Build Rater\033[0m")
        if isOffline:
            print("\033[38;5;240mQuick-Import: No connection\n\033[0m")
        else:
            print(f"\033[38;5;240mQuick-Import: {'OFF' if uid == '0' else 'ON ['+uid+']'}\n\033[0m")
        print("[1] - Lookup characters")
        print("[2] - Lookup teams")
        print("[3] - Create/Edit personal character")
        print("[4] - Create/Edit teams")
        print("[5] - Create/Edit breakpoints")
        print("[6] - Create/Edit 'bridges'")
        print("[7] - Quickscan")
        print("\033[38;5;240m[0] - Edit configuration")
        print("\n\033[38;5;240mCancel anything with CTRL C\033[0m")
        try:
            menuindex = int(input("\n>> "))
        except:
            continue
        print()
        if menuindex == 1:
            with open(PATHS.chardata) as f:
                characters = json.load(f)
            if len(characters) == 0:
                input("\n\033[31m[ No characters added yet ]\033[0m")
                continue
            print("\033[7m #   | NAME           | SCORE       | ACC      | RANK |\033[0m\n     |                |             |          |      |")
            for h in range(len(characters)):
                allscore = []
                allratio = []
                inverse = breakpoints[sorted(list(characters.keys()))[h]]["inverse"]
                for i in characters[sorted(list(characters.keys()))[h]]:
                    if i != "updated":
                        value1 = float(characters[sorted(list(characters.keys()))[h]][i]) + bridgedata[sorted(list(characters.keys()))[h]].get(i,0)
                        value2 = float(breakpoints[sorted(list(characters.keys()))[h]][i])
                        value1 = int(value1) if value1.is_integer() else value1
                        value2 = int(value2) if value2.is_integer() else value2
                        ratio = 2*value1/value2-1
                        if ratio < 0:
                            ratio = 0
                        if ratio > 1:
                            ratio = 1
                        score = attributeScore(i, value1, value2, i in inverse)
                        if score >= 100000:
                            ratio = 1
                        allscore.append(score)
                        allratio.append(ratio)
                score = int((sum(allscore) + min(allscore)*5)/(len(allscore)+5))
                if score > 100000:
                    score = f"X-{score-100000:,}"
                else:
                    score = f"{score:,}"
                r_acc = round(sum(allratio*100)/len(allratio),2)
                acc = f"{r_acc:,}%"
                grade = "F"
                gradelist = {50:"D",70:"C",80:"B",90:"A",95:"S",100:"S+"}
                for i in [50,70,80,90,95,100]:
                    if r_acc >= i:
                        grade = gradelist[i]
                    else:
                        break
                color = {"F":"125","D":"196","C":"202","B":"220","A":"76","S":"81","S+":"171"}
                highlight = "7;" if score[0] == "X" else ""
                sp = ["",""]
                sp[1 if score[0] == "X" else 0] = " "
                print(f" \033[38;5;{color[grade]}m{h+1:03d} \033[0m| \033[38;5;{color[grade]}m{sorted(list(characters.keys()))[h].upper().ljust(15)}\033[0m|{sp[0]}\033[{highlight}38;5;{color[grade]}m{sp[1]}{score.ljust(12)}\033[0m| \033[38;5;{color[grade]}m{acc.ljust(9)}\033[0m| \033[38;5;{color[grade]}m\033[7m {grade.ljust(3)}\033[0m |")
            print("\n\033[38;5;240mEnter ID for detailed overview, CTRL + C to return.\033[0m")
            try:
                x = input("> ")
            except:
                continue
            if x.isdigit():
                if int(x) < 1 or int(x) > len(characters.keys()):
                    input("\n\033[31m[ Not an index ]\033[0m")
                    continue
            else:
                input("\n\033[31m[ Not an index ]\033[0m")
                continue
            x = int(x)-1
            print(f"\n\033[3;38;5;240m{sorted(list(characters.keys()))[x].upper()}\n\033[0m\033[7m ATTR         | COMP                        | SCORE   |\033[0m\n              |                             |         |")
            allscore = []
            allratio = []
            inverse = breakpoints[sorted(list(characters.keys()))[x]]["inverse"]
            for i in characters[sorted(list(characters.keys()))[x]]:
                if i != "updated":
                    bridgevalue = bridgedata[sorted(list(characters.keys()))[x]].get(i,0)
                    value1 = float(characters[sorted(list(characters.keys()))[x]][i]) + bridgevalue
                    value2 = float(breakpoints[sorted(list(characters.keys()))[x]][i])
                    value1 = int(value1) if value1.is_integer() else value1
                    value2 = int(value2) if value2.is_integer() else value2
                    ratio = 2*value1/value2-1
                    if ratio < 0:
                        ratio = 0
                    if ratio > 1:
                        ratio = 1
                    score = attributeScore(i, value1, value2, i in inverse)
                    if score >= 100000:
                        ratio = 1
                    allscore.append(score)
                    allratio.append(ratio)
                    xvalue1 = f"{value1:,}"
                    xvalue2 = f"{value2:,}"
                    if score <= 100000:
                        score = f"{int(score):,}"
                    else:
                        score = f"\033[7;38;5;171m X-{int(score)-100000:,}"
                    #196 red
                    #202 orange
                    #220 yellow
                    #40 green
                    colorcode = [40,220,202,196]
                    col_index = 0
                    if i in inverse:
                        comp_symbol = "<"
                        if value1 > value2:
                            col_index += 3
                    else:
                        comp_symbol = "/"
                        if value1 < value2:
                            col_index += 1
                        if value1 < (value2 - value2/10):
                            col_index += 1
                        if value1 < (value2 - value2/5):
                            col_index += 1
                    usesBridge = False
                    if bridgevalue == 0:
                        display = f"{xvalue1}\033[38;5;240m {comp_symbol} {xvalue2}"
                    else:
                        display = f"{round(value1 - bridgevalue,1):,} + {round(bridgevalue,1):,}\033[38;5;240m {comp_symbol} {xvalue2}"
                        usesBridge = True
                    ansi_escape = re.compile(r'\x1B\[[0-9;]*m')
                    vd = len(ansi_escape.sub('', display))
                    vd2 = len(ansi_escape.sub('', score))
                    print(f" {i.upper().ljust(13)}| \033[38;5;{colorcode[col_index]}m{display}{' '*(28-vd)}\033[0m| {score}{' '*(7-vd2)}\033[0m |")
            print("\n")
            score = (sum(allscore) + min(allscore)*5)/(len(allscore)+5)
            if score >= 100000:
                print(f"Total scoring: \033[7;38;5;171m X-{int(score)-100000:,} \033[0m \033[38;5;240m({int(sum(allratio*100)/len(allratio)):,}% acc)")
            else:
                print(f"Total scoring: {int(score):,} \033[38;5;240m({int(sum(allratio*100)/len(allratio)):,}% acc)")
            if usesBridge:
                print("\n[i] Bridges for this character are set and visible above.")
            input("\n\033[38;5;240m[ <- ]\033[0m")
        if menuindex == 2:
            try:
                with open(PATHS.characters) as f:
                    characters = json.load(f)
                with open(PATHS.teams) as f:
                    teams = json.load(f)
                if len(teams) == 0:
                    input("\n\033[31m[ No teams configured yet ]\033[0m")
                    continue
                print("\033[7m #   | TEAM           | SCORE       | ACC      | RANK |\033[0m\n     |                |             |          |      |")
                teams_condense = []
                for h in range(len(teams)):
                    cumulativescore = []
                    cumulativeratio = []
                    rank_str = ""
                    team_content = []
                    for ii in teams[sorted(list(teams.keys()))[h]]:
                        allscore = []
                        allratio = []
                        inverse = breakpoints[ii]["inverse"]
                        for i in characters[ii]:
                            if i != "updated":
                                value1 = float(characters[ii][i]) + bridgedata[ii].get(i,0)
                                value2 = float(breakpoints[ii][i])
                                value1 = int(value1) if value1.is_integer() else value1
                                value2 = int(value2) if value2.is_integer() else value2
                                ratio = 2*value1/value2-1
                                if ratio < 0:
                                    ratio = 0
                                if ratio > 1:
                                    ratio = 1
                                score = attributeScore(i, value1, value2, i in inverse)
                                if score >= 100000:
                                    ratio = 1
                                allscore.append(score)
                                allratio.append(ratio)
                        cumulativescore.append(int((sum(allscore) + min(allscore)*5)/(len(allscore)+5)))
                        cumulativeratio.append(round(sum(allratio*100)/len(allratio),2))
                        grade = "F"
                        gradelist = {50:"D",70:"C",80:"B",90:"A",95:"S",100:"S+"}
                        for i in [50,70,80,90,95,100]:
                            if cumulativeratio[-1] >= i:
                                grade = gradelist[i]
                            else:
                                break
                        rank_str += grade
                        team_content.append({"name":ii,"rank":grade,"score":cumulativescore[-1],"ratio":cumulativeratio[-1]})
                    score = int((sum(cumulativescore) + min(cumulativescore)*5)/(len(cumulativescore)+5))
                    if score > 100000:
                        score = f"X-{score-100000:,}"
                    else:
                        score = f"{score:,}"
                    r_acc = round(sum(cumulativeratio)/len(cumulativeratio),2)
                    acc = f"{r_acc:,}%"
                    grade = "F"
                    gradelist = {50:"D",70:"C",80:"B",90:"A",95:"S",100:"S+"}
                    for i in [50,70,80,90,95,100]:
                        if r_acc >= i:
                            grade = gradelist[i]
                        else:
                            break
                    color = {"F":"125","D":"196","C":"202","B":"220","A":"76","S":"81","S+":"171"}
                    print(f" \033[38;5;{color[grade]}m{h+1:03d} \033[0m| \033[38;5;{color[grade]}m{sorted(list(teams.keys()))[h].upper().ljust(15)}\033[0m| \033[38;5;{color[grade]}m{score.ljust(12)}\033[0m| \033[38;5;{color[grade]}m{acc.ljust(9)}\033[0m| \033[38;5;{color[grade]}m\033[7m {grade.ljust(3)}\033[0m | \033[38;5;240m ({rank_str})")
                    teams_condense.append(team_content)
                print("\n\033[38;5;240mEnter ID for review characters assigned to team, CTRL + C to return.\033[0m")
                try:
                    x = input("> ")
                except:
                    continue
                if x.isdigit():
                    if int(x) < 1 or int(x) > len(teams.keys()):
                        input("\n\033[31m[ Not an index ]\033[0m")
                        continue
                else:
                    input("\n\033[31m[ Not an index ]\033[0m")
                    continue
                x = int(x)-1
                print("\n\033[7m NAME           | SCORE       | ACC      | RANK |\033[0m\n                |             |          |      |")
                team = teams_condense[x]
                color = {"F":"125","D":"196","C":"202","B":"220","A":"76","S":"81","S+":"171"}
                for character in range(4):
                    theme = color[teams_condense[x][character]["rank"]]
                    name = teams_condense[x][character]["name"]
                    acc = f'{teams_condense[x][character]["ratio"]:,}%'
                    grade = teams_condense[x][character]["rank"]
                    score = teams_condense[x][character]["score"]
                    if score >= 100000:
                        score = f"X-{score-100000:,}"
                    else:
                        score = f"{score:,}"
                    print(f" \033[38;5;{theme}m{name.upper().ljust(15)}\033[0m| \033[38;5;{theme}m{score.ljust(12)}\033[0m| \033[38;5;{theme}m{acc.ljust(9)}\033[0m| \033[38;5;{theme}m\033[7m {grade.ljust(3)}\033[0m |")
                input("\n\033[38;5;240m[ <- ]\033[0m")
            except:
                continue
        if menuindex == 3:
            with open(PATHS.characters) as f:
                characters = json.load(f)
            print("\033c\033[7m Select List Mode                 >\033[0m\n\n[1] - All\n[2] - Only already set")
            try:
                lm = int(input("> "))
                if lm not in [1,2]:
                    raise ValueError("Invalid Index")
            except:
                continue
            print("\033cSelect character to edit state of:\n")
            nobp = []
            for i in range(len(breakpoints.keys())):
                if list(breakpoints[sorted(list(breakpoints.keys()))[i]].values()) == [-1] * 9 + [[]]:
                    if lm == 1:
                        print(f"\033[38;5;245m[{i+1:03}] - \033[31m{sorted(list(breakpoints.keys()))[i].upper()} [No Breakpoints]\033[0m")
                        nobp.append(i+1)
                else:
                    if not sorted(list(breakpoints.keys()))[i] in characters.keys():
                        if lm == 1:
                            print(f"\033[38;5;245m[{i+1:03}] - {sorted(list(breakpoints.keys()))[i].upper()} | Not set\033[0m")
                    else:
                        print(f"[{i+1:03}] - {sorted(list(breakpoints.keys()))[i].upper()} \033[38;5;240m| Last updated: {int((time.time() - characters[sorted(list(breakpoints.keys()))[i]]['updated'])/(3600*24))}d ago\033[0m")

            try:
                x = input("> ")
            except:
                continue
            if x.isdigit():
                if int(x) < 1 or int(x) > len(breakpoints.keys()):
                    input("\n\033[31m[ Not an index ]\033[0m")
                    continue
                if int(x) in nobp:
                    input("\n\033[31m[ No breakpoints. Create them first. ]\033[0m")
                    continue
            else:
                input("\n\033[31m[ Not an index ]\033[0m")
                continue
            target = sorted(list(breakpoints.keys()))[int(x)-1]
            comp_mode = False
            if target in characters.keys():
                lastdata = characters[target]
                comp_mode = True
            characters[target] = {}
            try:
                if uid != "0":
                    api_name = api_name_mapping.get(target,target)
                    response = requests.get(f"https://api.mihomo.me/sr_info_parsed/{uid}?lang=en&version=v1")
                    response.raise_for_status()
                    api_data = response.json()
                    api_chars = [x['name'].lower() for x in api_data["characters"]]
                    api_attr = {}
                    if api_name.lower() in api_chars:
                        index = api_chars.index(api_name.lower())
                        for i in api_data["characters"][index]["property"]:
                            if "%" in i['base']:
                                i['base'] = i['base'][:-1]
                            i['base'] = float(i['base'])
                            if i['name'] == 'Energy Regeneration Rate':
                                api_attr['energy regen'] = i['base']
                            elif i['name'] == 'Effect Hit Rate':
                                api_attr['effect hit'] = i['base']
                            else:
                                api_attr[i['name'].lower()] = i['base']
                            if i['name'] in ['Energy Regeneration Rate']:
                                api_attr['energy regen'] += 100
                            if not i['addition'] is None:
                                api_attr[i['name'].lower()] += float(i['addition'])
                        if "energy regen" not in api_attr:
                            api_attr['energy regen'] = 100
                        if "break effect" not in api_attr:
                            api_attr['break effect'] = 0
                        if "effect hit" not in api_attr:
                            api_attr['effect hit'] = 0
                        if input("API Data found! Continue using it? (Y/N) > \033[38;5;202m").lower() != "y":
                            api_attr = {}
                    else:
                        print("Couldn't match any names. Continue entering manually.\n\033[38;5;240mIf you believe this is unwanted behavior, edit the name-mapping in configuration settings.\033[0m")
                else:
                    api_attr = {}
            except requests.exceptions.RequestException:
                print("Couldn't load from profile because of network issues. Continue entering manually.\n")
                api_attr = {}
            print("\033[0m", end="")
            old_temp = characters[target]
            try:
                for i in ["hp","atk","def","spd","crit rate","crit dmg","break effect","energy regen","effect hit"]:
                    if breakpoints[target][i] != -1:
                        while True:
                            if api_attr == {}:
                                x = input(f"Enter value for \033[1m{i.upper()}\033[0m: \033[38;5;202m").replace(",",".").replace("%","")
                            else:
                                print(f"\033[1m{i.upper()}\033[0m: \033[38;5;202m{api_attr[i.lower()]}")
                                x = api_attr[i.lower()]
                            try:
                                float(x)
                                break
                            except:
                                pass
                        if comp_mode:
                            if not i in ["crit rate","crit dmg","break effect","energy regen","effect hit"]:
                                color = 196 if int(x) < int(lastdata[i]) else 40
                                if int(x) == int(lastdata[i]):
                                    color = 240
                                print(f"\033[38;5;{color}m{'' if int(x) <= int(lastdata[i]) else '+'}{int(x) - int(lastdata[i])} \033[38;5;240m(from {int(lastdata[i])})\033[0m")
                            else:
                                color = 196 if float(x) < float(lastdata[i]) else 40
                                if float(x) == float(lastdata[i]):
                                    color = 240
                                print(f"\033[38;5;{color}m{'' if float(x) <= float(lastdata[i]) else '+'}{round(float(x) - float(lastdata[i]),1)} \033[38;5;240m(from {float(lastdata[i])})\033[0m")
                        else:
                            print("\033[0m",end="")
                        characters[target][i] = x
            except:
                characters[target] = old_temp
                continue
            characters[target]["updated"] = int(time.time())
            with open(PATHS.characters,"w") as f:
                json.dump(characters,f)
            input("\n\033[38;5;40m[ Done. ]\033[0m")
        if menuindex == 4:
            with open(PATHS.teams) as f:
                teams = json.load(f)
            with open(PATHS.characters) as f:
                characters = json.load(f)
            if len(teams) == 0:
                print("\n\033[38;5;240m[ No teams ]\033[0m")
            else:
                print("\n\033[38;5;240mTEAM OVERVIEW")
                for i in sorted(list(teams.keys())):
                    print(f"[{i.upper():17}] | {teams[i][0].capitalize()} + {teams[i][1].capitalize()} + {teams[i][2].capitalize()} + {teams[i][3].capitalize()}")
            print("\n\033[0mEnter a team name to edit a preexisting or create a new one \033[38;5;240m(17 chars max)\033[0m:")
            target = ""
            try:
                while not (len(target) in range(1,18)):
                    target = input("> \033[38;5;202m").strip().lower()
            except:
                continue
            print("\n\033[0mEnter target characters, seperated by comma:")
            try:
                char_target = input("> \033[38;5;202m").lower().split(",")
            except:
                continue
            if len(char_target) != 4:
                input(f"\n\033[31m[ Invalid team size ]\033[0m")
                continue
            for i in range(len(char_target)):
                char_target[i] = char_target[i].lower().strip()
            bp_ignore = []
            for i in breakpoints:
                if breakpoints[i].values() == [-1] * 9:
                    bp_ignore.append(i)
            team_ok = True
            for i in char_target:
                if not i in breakpoints:
                    input(f"\n\033[31m[ Character not recognized ({i}) ]\033[0m")
                    team_ok = False
                    continue
                if i in bp_ignore:
                    input(f"\n\033[31m[ Character has no breakpoints ({i}) ]\033[0m")
                    team_ok = False
                    continue
                if not i in characters:
                    input(f"\n\033[31m[ No character information yet ({i}) ]\033[0m")
                    team_ok = False
                    continue
            if not team_ok:
                continue
            teams[target] = char_target
            with open(PATHS.teams,"w") as f:
                json.dump(teams,f)
            input("\n\033[38;5;40m[ Done. ]\033[0m")
        if menuindex == 5:
            print("\033[38;5;202m\033[1mWarning:\033[22m\nYou are editing character target values.\nPress CTRL + C to return to main menu if you just want to enter your own character information.\033[0m\n")
            try:
                target = input("Enter name: \033[38;5;202m").lower().strip()
            except:
                continue
            print("\033[0m",end="")
            if target in breakpoints.keys():
                try:
                    input("\n\033[38;5;202m[ Character is already present. Enter: Continue / CTRL+C: Cancel. ]\033[0m")
                except:
                    continue
            else:
                try:
                    input("\n\033[38;5;202m[ Creating a new character entry. Enter: Continue / CTRL+C: Cancel. ]\033[0m")
                except:
                    continue
            prev_breakpoints = breakpoints
            breakpoints[target] = {}
            attributes = ["hp","atk","def","spd","crit rate","crit dmg","break effect","energy regen","effect hit"]
            print("Mark unneeded parameters with '-1'. Use highest recommended values.")
            try:
                for i in attributes:
                    x = input(f"Enter value for \033[1m{i.upper()}\033[0m: \033[38;5;202m")
                    x.replace(",",".")
                    print("\033[0m",end="")
                    breakpoints[target][i] = float(x)
                print("\nEnter attributes to mark as \033[1minverse\033[0m. Inverse describes attributes that should \033[1mnot be exceeded\033[0m.")
                x = input(f"Enter attributes (Seperate multiple with comma or leave blank): \033[38;5;202m")
                if x != "":
                    x = x.lower().split(",")
                    xnot = [item.strip() for item in x if item.lower() not in attributes]
                    xs = [item.strip() for item in x if item.lower() in attributes]
                    if len(xnot) == 0:
                        breakpoints[target]["inverse"] = xs
                    else:
                        raise ValueError("Invalid attributes for Inverse supplied.")
                else:
                    breakpoints[target]["inverse"] = []
                with open(PATHS.breakpoints,"w") as f:
                    json.dump(breakpoints,f)
                with open(PATHS.bridgedata) as f:
                    bridgedata = json.load(f)
                for i in breakpoints:
                    if i not in bridgedata:
                        bridgedata[i] = {}
                input("\n\033[38;5;40m[ Done. ]\033[0m")
            except ValueError as e:
                breakpoints = prev_breakpoints
                input(f"\n\033[31m[ {str(e)} ]\033[0m")
                continue
            except:
                breakpoints = prev_breakpoints
                input("\n\033[31m[ Aborted. Reverting. ]\033[0m")
                continue
        if menuindex == 6:
            print("\033[38;5;240m\033[1mInfo:\033[22m\nUse bridges to add values not reflected in base stats to characters. These can include Eidolons, Light Cone Effects or specific Relic Set-Boosts.\033[0m\n")
            try:
                target = input("\033[0mEnter name: \033[38;5;202m").lower().strip()
                key = input("\033[0mEnter value key: \033[38;5;202m").lower().strip()
            except:
                continue
            print("\033[0m",end="")
            with open(PATHS.breakpoints) as f:
                breakpoints = json.load(f)
            if not target in breakpoints.keys():
                input(f"\n\033[31m[ Character not recognized. ]\033[0m")
                continue
            if list(breakpoints[target].values()) == [-1] * 9:
                input(f"\n\033[31m[ Character has no breakpoints ]\033[0m")
                continue
            if not key in ["hp","atk","def","spd","crit rate","crit dmg","break effect","energy regen","effect hit"]:
                input(f"\n\033[31m[ Value key not recognized. ]\033[0m")
                continue
            try:
                x = input(f"\033[0mEnter value for \033[1m{key.upper()}\033[0m Bridge: \033[38;5;202m").replace(",",".")
                print("\033[0m",end="")
                bridgedata[target][key] = float(x)
                with open(PATHS.bridgedata,"w") as f:
                    json.dump(bridgedata,f)
                input("\n\033[38;5;40m[ Done. ]\033[0m")
            except:
                input("\n\033[31m[ Error. Aborting. ]\033[0m")
                continue
        if menuindex == 7:
            print("\033[38;5;240m\033[1mInfo:\033[22m\nQuickscan is used for evaluating characters without saving thier state (e.g. charcters of other users).\nFor your own characters, use menu option #3 instead.\nWarning: Bridges will not apply. A character's build quality won't be able to be fully evaluated.\033[0m\n")
            try:
                target = input("Enter name: \033[38;5;202m").lower().strip()
            except:
                continue
            print("\033[0m",end="")
            with open(PATHS.breakpoints) as f:
                breakpoints = json.load(f)
            if not target in breakpoints.keys():
                input(f"\n\033[31m[ Character not recognized. ]\033[0m")
                continue
            if list(breakpoints[target].values()) == [-1] * 9 + [[]]:
                input(f"\n\033[31m[ Character has no breakpoints ]\033[0m")
                continue
            q_char = {}
            for i in ["hp","atk","def","spd","crit rate","crit dmg","break effect","energy regen","effect hit"]:
                if breakpoints[target][i] != -1:
                    while True:
                        x = input(f"Enter value for \033[1m{i.upper()}\033[0m: \033[38;5;202m")
                        print("\033[0m",end="")
                        try:
                            float(x)
                            break
                        except:
                            pass
                    q_char[i] = x
            print()
            allscore = []
            allratio = []
            inverse = breakpoints[target]["inverse"]
            for i in q_char:
                value1 = float(q_char[i])
                value2 = float(breakpoints[target][i])
                value1 = int(value1) if value1.is_integer() else value1
                value2 = int(value2) if value2.is_integer() else value2
                ratio = 2*value1/value2-1
                if ratio < 0:
                    ratio = 0
                if ratio > 1:
                    ratio = 1
                score = attributeScore(i, value1, value2, i in inverse)
                if score >= 100000:
                    ratio = 1
                allscore.append(score)
                allratio.append(ratio)
                xvalue1 = f"{value1:,}"
                xvalue2 = f"{value2:,}"
                if score < 100000:
                    score = f"{int(score):,}"
                else:
                    score = f"X-{int(score)-100000:,}"
                #196 red
                #202 orange
                #220 yellow
                #40 green
                colorcode = [40,220,202,196]
                col_index = 0
                if i in inverse:
                    comp_symbol = "<"
                    if value1 > value2:
                        col_index += 3
                else:
                    comp_symbol = "/"
                    if value1 < value2:
                        col_index += 1
                    if value1 < (value2 - value2/10):
                        col_index += 1
                    if value1 < (value2 - value2/5):
                        col_index += 1
                print(f" {i.upper().ljust(13)}| \033[38;5;{colorcode[col_index]}m{xvalue1}\033[38;5;240m {comp_symbol} {xvalue2.ljust(21-1-len(xvalue1))}\033[0m| {score}{' '*(8-len(score))}|")
            print("\n")
            score = (sum(allscore) + min(allscore)*5)/(len(allscore)+5)
            if score >= 100000:
                print(f"Total scoring: \033[7;38;5;171m X-{int(score)-100000:,} \033[0m \033[38;5;240m({int(sum(allratio*100)/len(allratio)):,}% acc)")
            else:
                print(f"Total scoring: {int(score):,} \033[38;5;240m({int(sum(allratio*100)/len(allratio)):,}% acc)")
            input("\n\033[38;5;240m[ <- ]\033[0m")
        if menuindex == 0:
            print("\033c\033[7m Select option                   >\033[0m\n\n[1] - Fetch new characters\n[2] - Set UID\n[3] - API name translation\n")
            try:
                lm = int(input("> "))
                if lm not in range(1,4):
                    raise ValueError("Invalid Index")
            except:
                continue
            if lm == 1:
                try:
                    with open(PATHS.importignore) as f:
                        ignore = json.load(f)
                    creation_template = {"hp":-1,"atk":-1,"def":-1,"spd":-1,"crit rate":-1,"crit dmg":-1,"break effect":-1,"energy regen":-1,"effect hit":-1}
                    response = requests.get("https://www.prydwen.gg/star-rail/characters")
                    response.raise_for_status()
                    isOffline = False
                    main = BeautifulSoup(response.text, 'html.parser').find_all("div", {"class", "avatar-card"})
                    entryindex = len(main)
                    for object in main:
                        objectid = object.find("span").find("a")["href"].split("/")[-1].replace("-"," ")
                        if not (objectid not in breakpoints.keys() and objectid not in ignore["keys"]):
                            entryindex -= 1
                    if entryindex == 0:
                        input("\n\033[38;5;40m[ You're already up to date! ]\033[0m")
                        continue
                    print(f"Expecting {entryindex} new entries.")
                    print("0: Ignore / 1: Change name and add / 2: Directly add")
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
                                if target in breakpoints:
                                    input("\033[38;5;202mWARNING: New ID would overwrite a breakpoint entry with same name!\nContinue with ENTER, reset and abort with CTRL C.\033[0m")
                                breakpoints[target] = creation_template
                            elif index == 2:
                                breakpoints[target] = creation_template
                    with open(PATHS.importignore,"w") as f:
                        json.dump(ignore,f)
                    with open(PATHS.breakpoints,"w") as f:
                        json.dump(breakpoints,f)
                    input("\n\033[38;5;40m[ Done. ]\033[0m")
                except requests.exceptions.RequestException as e:
                    input("\n\033[31m[ Request has failed. ]\033[0m")
                except KeyboardInterrupt:
                    input("\n\033[31m[ Aborted, closing session to reset. ]\033[0m")
                    raise KeyboardInterrupt()
                except Exception as e:
                    input(f"\n\033[31m[ Error. Closing session. ]\n033[36;5;240m{e}\033[0m")
            elif lm == 2:
                try:
                    print("\nNew UID ('0' to disable):")
                    while True:
                        uid = input("> ").strip()
                        if uid.isdigit():
                            with open(PATHS.uid,"w") as f:
                                f.write(str(uid))
                            break
                except:
                    continue
            elif lm == 3:
                if uid == 0:
                    input("Feature available once UID has been set.")
                    continue
                print("\033c\033[7m Select option                   >\033[0m\n\n[1] - Get API names for current UID\n[2] - Edit Name Mapping")
                try:
                    lm = int(input("> "))
                    if lm not in range(1,3):
                        raise ValueError("Invalid Index")
                except:
                    continue
                if lm == 1:
                    try:
                        response = requests.get(f"https://api.mihomo.me/sr_info_parsed/{uid}?lang=en&version=v1")
                        response.raise_for_status()
                        api_data = response.json()
                        api_chars = [x['name'].lower() for x in api_data["characters"]]
                    except KeyboardInterrupt:
                        continue
                    except requests.exceptions.RequestException as e:
                        input("\n\033[31m[ Connection failed. ]\033[0m")
                        continue
                    except Exception as e:
                        #print(f"\033[38;5;240m{traceback.format_exc()}\033[0m")
                        input("\n\033[31m[ An error occured. ]\033[0m")
                    isOffline = False
                    print("\nCurrent keys under UID:\n")
                    for i in api_chars:
                        if i in breakpoints:
                            print("\033[38;5;40mSYNCED | ", end="")
                        elif i in api_name_mapping.values():
                            print("\033[38;5;220mMAPPED | ", end="")
                        else:
                            print("\033[38;5;196mUNBOUND | ", end="")
                        print(i)
                    print("\n\033[38;5;240mSynced  : API matches Breakpoint Identifier.\nMapped  : Name mapping has been configured.\nUnbound : Name is not known in any way.")
                    print("\nChanges to your characters ingame (Availability and Stats alike) will be reflected after a few minutes of delay.\033[0m")
                    input("\n\033[38;5;240m[ <- ]\033[0m")
                if lm == 2:
                    while True:
                        print("\033c\033[7m Mappings                   >\033[0m\n")
                        if len(api_name_mapping) == 0:
                            print("\033[38;5;240mNothing here yet.\033[0m\n")
                        else:
                            index = 1
                            print("\033[38;5;240m[i] API Name --> Breakpoint Identifier\033[0m\n")
                            for na, sy in api_name_mapping.items():
                                print(f"INDEX {' ' if index > 9 else ''}{index} | {sy} --> {na}")
                                index += 1
                            print("\nControls:")
                            print("Add/Edit : '+,APINAME,BPIDENTIFIER'")
                            print("Delete   : 'x,INDEX'")
                            print("\n\033[38;5;240mPress CTRL C to exit.\033[0m")
                        try:
                            syn = input("\n > ")
                            if syn == "":
                                continue
                            if syn[0] == "+":
                                if syn.count(",") != 2:
                                    input("\n\033[31m[ Expected 2 commas. If any name requires a comma, replace it with <COMMA>. ]\033[0m")
                                    continue
                                syn = [x.strip().replace("<COMMA>",",").lower() for x in syn.split(",")[1:]]
                                if "" in syn:
                                    input("\n\033[31m[ One or more Arguments are empty. ]\033[0m")
                                    continue
                                try:
                                    input(f"\nSet the following?:\n{syn[1]} --> {syn[0]}\nENTER: Yes / CTRL C: No")
                                except:
                                    continue
                                api_name_mapping[syn[0]] = syn[1]
                                with open(PATHS.api_name_map,"w") as f:
                                    json.dump(api_name_mapping,f)
                                input("\n\033[38;5;40m[ Done. ]\033[0m")
                                continue
                            elif syn[0] == "x":
                                if syn.count(",") != 1:
                                    input("\n\033[31m[ Expected 1 comma. If any name requires a comma, replace it with <COMMA>. ]\033[0m")
                                    continue
                                syn = syn.split(",")[1].strip().replace("<COMMA>",",").lower()
                                if not syn.isdigit():
                                    input("\n\033[31m[ Expected a numeric index. ]\033[0m")
                                    continue
                                syn = int(syn) - 1
                                if syn < 0 or syn > len(api_name_mapping) - 1:
                                    input("\n\033[31m[ Index is out of range ]\033[0m")
                                    continue
                                del api_name_mapping[list(api_name_mapping.keys())[syn]]
                                with open(PATHS.api_name_map,"w") as f:
                                    json.dump(api_name_mapping,f)
                                input("\n\033[38;5;40m[ Done. ]\033[0m")
                                continue
                            else:
                                input("\n\033[31m[ Unrecognized Prefix. ]\033[0m")
                        except KeyboardInterrupt:
                            break

except ModuleNotFoundError:
    input(f"\033[31m\nOne or more modules required for this script are not installed:\n\n{traceback.format_exc()}\033[0m")
except Exception as e:
    input(f"\033[31m\nERR:\n{traceback.format_exc()}\033[0m")
