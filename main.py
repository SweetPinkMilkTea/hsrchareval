from pathlib import Path
import re
import shutil
import json
import time
import os
import traceback
from copy import deepcopy as dcp


from bs4 import BeautifulSoup
import requests

# Own File Imports
from util_functions import reliccom
from util_functions import charcom
from util_functions import configutil

# Constants
coreAttributes = ["hp", "def", "atk", "crit rate", "crit dmg", "spd", "break effect", "effect hit", "energy regen"]
floatingCoreAttributes = ["crit rate", "crit dmg", "energy regen", "break effect", "effect hit"]
supplementaryAttributes = ["physical dmg", "wind dmg", "fire dmg", "ice dmg", "lightning dmg", "quantum dmg", "imaginary dmg", "effect res", "heal boost"]

rankcolor = {"F":"60","D":"57","C":"27","B":"51","A":"46","S":"220","SS":"226", "U":"197","X":"200"}
rankcutoffs_score = {50:"D",70:"C",80:"B",90:"A",95:"S",100:"SS"}
rankcutoffs_relic = {10:"D",30:"C",45:"B",55:"A",65:"S",70:"SS", 90:"U", 95:"X"}

def timespan(ts: int):
    "Returns a string with relative time, calculated with a UNIX timestamp."
    now = time.time()
    diff = int(now - ts)

    if diff < 0:
        return "in the future"

    units = [
        ('year', 60 * 60 * 24 * 365),
        ('month', 60 * 60 * 24 * 30),
        ('week', 60 * 60 * 24 * 7),
        ('day', 60 * 60 * 24),
        ('hour', 60 * 60),
        ('minute', 60),
        ('second', 1),
    ]

    for unit_name, unit_seconds in units:
        value = diff // unit_seconds
        if value > 0:
            return f"{value} {unit_name}{'s' if value > 1 else ''} ago"

    return "just now"

def gradescan(list: dict, mark: float):
    "Returns a rank based on a supplied dict."
    grade = "F"
    for cutoff in list:
        if mark >= cutoff:
            grade = list[cutoff]
        else:
            break
    return grade

try:
    # Setup
    configutil.filesetup()

    with open(configutil.PATHS.characters) as f:
        characters = json.load(f)
    with open(configutil.PATHS.relics) as f:
        relics = json.load(f)
    with open(configutil.PATHS.teams) as f:
        teams = json.load(f)
    with open(configutil.PATHS.breakpoints) as f:
        breakpoints = json.load(f)
    with open(configutil.PATHS.bridgedata) as f:
        bridgedata = json.load(f)

    with open(configutil.PATHS.uid) as f:
        uid = f.read()

    with open(configutil.PATHS.api_name_map) as f:
        api_name_mapping = json.load(f)

    if len(breakpoints) == 0:
        configutil.first_run_import()

    if uid == "0":
        while True:
            print("\033c\033[7m Quick-Import Setup               >\033[0m")
            print("\nEnter your UID to look for character data when trying to evaluate them.\nOnly characters featured on your profile page can be accessed.\n\n\033[38;5;240mEnter 0 to skip.\033[0m")
            uid = input("\n> ").strip()
            if uid.isdigit():
                with open(configutil.PATHS.uid,"w") as f:
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
            if len(characters) == 0:
                input("\n\033[31m[ No characters added yet ]\033[0m")
                continue
            namespacing = len(max(characters, key=len)) if len(max(characters, key=len)) >= 15 else 15
            print("\033cLoading, please wait a moment...")
            characterEval = {}
            for character in characters:
                ev_stats = characters[character]
                ev_breakpoints = breakpoints[character]
                ev_bridges = bridgedata[character]
                try:
                    ev_relics = relics[character]["equipment"]
                    ev_prio = relics[character]["prio"]
                    if ev_relics == [] or ev_prio == {}:
                        raise ValueError("No relics")
                except (KeyError, ValueError):
                    ev_relics = None
                    ev_prio = None
                characterEval[character] = charcom.analyseChar(ev_breakpoints, ev_stats, ev_bridges, ev_relics, ev_prio)
            print(f"\033c\033[7m #   | NAME{(namespacing-4)*' '}| SCORE       | ACC      | RANK |\033[0m\n     | {namespacing*' '}|             |          |      |")
            index = 1
            # Note: Can make custom sorted Character Lists later
            charlist = sorted(list(characters.keys()))
            for target in charlist:
                score = characterEval[target]["stats"]["score"]
                if score > 100000:
                    score = f"X-{score-100000:,}"
                else:
                    score = f"{score:,}"
                r_acc = characterEval[target]["stats"]["accuracy"]
                acc = f"{r_acc:,}%"
                grade = gradescan(rankcutoffs_score, r_acc)
                highlight = "7;" if score[0] == "X" else ""
                sp = ["",""]
                sp[1 if score[0] == "X" else 0] = " "
                updated = timespan(characters[target]["updated"])
                print(f" \033[38;5;{rankcolor[grade]}m{index:03d} \033[0m| \033[38;5;{rankcolor[grade]}m{target.upper().ljust(namespacing)}\033[0m|{sp[0]}\033[{highlight}38;5;{rankcolor[grade]}m{sp[1]}{score.ljust(12)}\033[0m| \033[38;5;{rankcolor[grade]}m{acc.ljust(9)}\033[0m| \033[38;5;{rankcolor[grade]}m\033[7m {grade.ljust(3)}\033[0m | \033[38;5;240m{updated}\033[0m")
                index += 1
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
            target = charlist[x]
            print(f"\n\033[1m{target.upper()}\n\n\033[0m\033[38;5;240mAttributes\n\033[0m\033[7m ATTRIBUTE    | COMP                        | SCORE   |\033[0m\n              |                             |         |")
            for attrKey in characterEval[target]["stats"]["attributes"]:
                current = characterEval[target]["stats"]["attributes"][attrKey]["current"]
                bridgevalue = characterEval[target]["stats"]["attributes"][attrKey]["bridge"]
                goal = characterEval[target]["stats"]["attributes"][attrKey]["goal"]
                isInverse = characterEval[target]["stats"]["attributes"][attrKey]["isInverse"]
                current = int(current) if current.is_integer() else current
                goal = int(goal) if goal.is_integer() else goal
                ratio = 2*current/goal-1
                ratio = max(ratio, 0)
                ratio = min(ratio, 1)
                if ratio > 1:
                    ratio = 1
                score = characterEval[target]["stats"]["attributes"][attrKey]["score"]
                if score >= 100000:
                    ratio = 1
                display_current = f"{current:,}"
                display_goal = f"{goal:,}"
                if score <= 100000:
                    score = f"{int(score):,}"
                else:
                    score = f"\033[7m X-{int(score)-100000:,}"
                #196 red
                #202 orange
                #220 yellow
                #40 green
                colorcode = [40,220,202,196]
                col_index = 0
                if isInverse:
                    comp_symbol = "<"
                    if current > goal:
                        col_index += 3
                else:
                    comp_symbol = "/"
                    if current < goal:
                        col_index += 1
                    if current < (goal - goal/10):
                        col_index += 1
                    if current < (goal - goal/5):
                        col_index += 1
                if not bridgevalue:
                    display = f"{display_current}\033[38;5;240m {comp_symbol} {display_goal}"
                else:
                    display = f"{round(current - bridgevalue,1):,} + {round(bridgevalue,1):,}\033[38;5;240m {comp_symbol} {display_goal}"
                    usesBridge = True
                ansi_escape = re.compile(r'\x1B\[[0-9;]*m')
                vd = len(ansi_escape.sub('', display))
                vd2 = len(ansi_escape.sub('', score))
                print(f" {attrKey.upper().ljust(13)}| \033[38;5;{colorcode[col_index]}m{display}{' '*(28-vd)}\033[0m| {score}{' '*(7-vd2)}\033[0m |")
            score = characterEval[target]["stats"]["score"]
            acc = characterEval[target]["stats"]["accuracy"]
            if score >= 100000:
                print(f"\nAttribute Score: \033[7m X-{int(score)-100000:,} \033[0m \033[38;5;240m({int(acc):,}% acc)")
            else:
                print(f"\nAttribute Score: {int(score):,} \033[38;5;240m({int(acc):,}% acc)")
            if characterEval[target]["relics"] != {}:
                print("\n\033[38;5;240mRelics\n\033[0m\033[7m PC | DETAILS                     | SCORE   | EFFI    |\033[0m\n    |                             |         |         |")
                relicData = characterEval[target]["relics"]
                index = 1
                for relic in relicData["relics"]:
                    score = f"{relic['score']:,}"
                    mainAffix = relic["main"]
                    mainAffixDisplay = mainAffix['key'].upper() if not relic["flags"]["mainfault"] else f"{mainAffix['key'].upper()} [!= {relics[target]['prio']['main'][index-3].upper()}]"
                    grade = gradescan(rankcutoffs_relic, relic["score"])
                    col = rankcolor[grade]
                    print(f"\033[7;38;5;{col}m {index:02d} | {mainAffixDisplay.ljust(27)} | {score.ljust(7)} |   {grade.rjust(2)}    |\033[0m")
                    for sub in relic["sub"]:
                        key = sub["key"].upper()
                        value = sub["value"]
                        count = sub["count"]
                        score = f"{sub['score']:,}"
                        saturation = f"{round(sub['saturation']*100,2):,}"
                        countIndicator = f" [+{count - 1}]" if count > 1 else ""
                        statString = f"{key}: {value}{countIndicator}"
                        if sub["score"] > 0:
                            print(f"    | {statString.ljust(27)} | {score.ljust(7)} | {saturation.ljust(7)} |")
                        else:
                            print(f"    | \033[38;5;240m{statString.ljust(27)}\033[0m | \033[38;5;240m   X   \033[0m | \033[38;5;240m   X   \033[0m |")
                    index += 1
                    print("    |                             |         |         |")
                col = rankcolor[gradescan(rankcutoffs_relic, relicData["fullscore"])]
                print(f"\nRelic Score: \033[38;5;{col}m{relicData["fullscore"]} (Grade \033[7m {gradescan(rankcutoffs_relic, relicData["fullscore"]).ljust(2)} \033[27m)\033[0m")
                if relicData["flags"]["mainfaults"] > 0 or relicData["flags"]["setfaults"] > 0:
                    print(f"\nMainstat Faults: {relicData['flags']['mainfaults']}\nSet Faults: {relicData['flags']['setfaults']}")
            else:
                print("\n[\033[38;5;240mi] No relics available to evaluate.\033[0m")
            input("\n\033[38;5;240m[ <- ]\033[0m")
        if menuindex == 2:
            try:
                if len(teams) == 0:
                    input("\n\033[31m[ No teams configured yet ]\033[0m")
                    continue
                namespacing = len(max(characters, key=len)) if len(max(characters, key=len)) >= 15 else 15
                print("\033cLoading, please wait a moment...")
                characterEval = {}
                for character in characters:
                    ev_stats = characters[character]
                    ev_breakpoints = breakpoints[character]
                    ev_bridges = bridgedata[character]
                    try:
                        ev_relics = relics[character]["equipment"]
                        ev_prio = relics[character]["prio"]
                        if ev_relics == {}:
                            raise ValueError("No relics")
                    except (KeyError, ValueError):
                        ev_relics = None
                        ev_prio = None
                    characterEval[character] = charcom.analyseChar(ev_breakpoints, ev_stats, ev_bridges, ev_relics, ev_prio)
                print("\033[7m #   | TEAM           | SCORE       | ACC      | RANK |\033[0m\n     |                |             |          |      |")
                teams_condense = []
                index = 1
                for target in sorted(list(teams.keys())):
                    cumulativescore = []
                    cumulativeratio = []
                    rank_str = ""
                    team_content = []
                    for character in teams[target]:
                        cumulativescore.append(characterEval[character]["stats"]["score"])
                        cumulativeratio.append(characterEval[character]["stats"]["accuracy"])
                        grade = gradescan(rankcutoffs_score, cumulativeratio[-1])
                        rank_str += grade
                        team_content.append({"name":character,"rank":grade,"score":cumulativescore[-1],"ratio":cumulativeratio[-1]})
                    score = int((sum(cumulativescore) + min(cumulativescore)*5)/(len(cumulativescore)+5))
                    if score > 100000:
                        score = f"X-{score-100000:,}"
                    else:
                        score = f"{score:,}"
                    r_acc = round(sum(cumulativeratio)/len(cumulativeratio),2)
                    acc = f"{r_acc:,}%"
                    grade = gradescan(rankcutoffs_score, r_acc)
                    print(f" \033[38;5;{rankcolor[grade]}m{index:03d} \033[0m| \033[38;5;{rankcolor[grade]}m{target.upper().ljust(15)}\033[0m| \033[38;5;{rankcolor[grade]}m{score.ljust(12)}\033[0m| \033[38;5;{rankcolor[grade]}m{acc.ljust(9)}\033[0m| \033[38;5;{rankcolor[grade]}m\033[7m {grade.ljust(3)}\033[0m | \033[38;5;240m ({rank_str})")
                    teams_condense.append(team_content)
                    index += 1
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
                print(f"\n\033[7m NAME{(namespacing-4)*' '}| SCORE       | ACC      | RANK |\033[0m\n {namespacing*' '}|             |          |      |")
                team = teams_condense[x]
                for character in range(4):
                    theme = rankcolor[teams_condense[x][character]["rank"]]
                    name = teams_condense[x][character]["name"]
                    acc = f'{teams_condense[x][character]["ratio"]:,}%'
                    grade = teams_condense[x][character]["rank"]
                    score = teams_condense[x][character]["score"]
                    if score >= 100000:
                        score = f"X-{score-100000:,}"
                    else:
                        score = f"{score:,}"
                    print(f" \033[38;5;{theme}m{name.upper().ljust(namespacing)}\033[0m| \033[38;5;{theme}m{score.ljust(12)}\033[0m| \033[38;5;{theme}m{acc.ljust(9)}\033[0m| \033[38;5;{theme}m\033[7m {grade.ljust(3)}\033[0m |")
                input("\n\033[38;5;240m[ <- ]\033[0m")
            except:
                continue
        if menuindex == 3:
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
                    if sorted(list(breakpoints.keys()))[i] not in characters.keys():
                        if lm == 1:
                            print(f"\033[38;5;245m[{i+1:03}] - {sorted(list(breakpoints.keys()))[i].upper()} | Not set\033[0m")
                    else:
                        print(f"[{i+1:03}] - {sorted(list(breakpoints.keys()))[i].upper()} \033[38;5;240m| Last updated: {timespan(characters[sorted(list(breakpoints.keys()))[i]]['updated'])}\033[0m")

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
            try:
                if uid != "0":
                    api_name = api_name_mapping.get(target,target)
                    response = requests.get(f"https://api.mihomo.me/sr_info_parsed/{uid}?lang=en&version=v2")
                    response.raise_for_status()
                    api_data = response.json()
                    api_chars = [x['name'].lower() for x in api_data["characters"]]
                    api_attr = {}
                    api_relic = []
                    keymap = {"break dmg":"break effect","sp rate":"energy regen"}
                    if api_name.lower() in api_chars:
                        index = api_chars.index(api_name.lower())
                        for attribute in coreAttributes:
                            api_attr[attribute] = 0
                        api_attr["energy regen"] = 100
                        for section in ["attributes","additions"]:
                            for attribute in api_data["characters"][index][section]:
                                value = attribute["value"]
                                key = attribute["field"].replace("_", " ")
                                try:
                                    api_attr[keymap.get(key,key)] += round(value * (100 if key in ["crit rate","crit dmg","sp rate", "break dmg"] or key.endswith(" dmg") else 1), 1)
                                except KeyError:
                                    api_attr[keymap.get(key,key)] = round(value * (100 if key in ["crit rate","crit dmg","sp rate", "break dmg"] or key.endswith(" dmg") else 1), 1)
                                if section == "attributes" and key in ["atk", "def", "hp"]:
                                    api_attr["base_" + key] = value
                        for value in api_attr:
                            if value not in floatingCoreAttributes:
                                api_attr[value] = int(round(api_attr[value], 0))

                        if target in relics:
                            relicstatus = reliccom.validate(api_data["characters"][index]["relics"])
                            if relicstatus["success"]:
                                api_relic = reliccom.extract(api_data["characters"][index]["relics"])
                        else:
                            relicstatus = {"success": False, "message": "No relic information provided (Use Breakpoints)"}

                        print("API Data found!")
                        print("Relics will be written as well." if relicstatus["success"] else f"Relics cannot be written: {relicstatus['message']}")
                        if input("Continue? (Y/N) > \033[38;5;202m").lower() != "y":
                            api_attr = {}
                            relicstatus = {"success":False, "message":"Import skipped"}

                    else:
                        print("Couldn't match any names. Continue entering manually.\n\033[38;5;240mIf you believe this is unwanted behavior, edit the name-mapping in configuration settings.\033[0m")
                else:
                    api_attr = {}
                    relicstatus = {"success":False, "message":"No API import"}
            except requests.exceptions.RequestException:
                print("Couldn't load from profile because of network issues. Continue entering manually.\n")
                api_attr = {}
                relicstatus = {"success":False, "message":"No connection"}
            except KeyboardInterrupt:
                continue
            print("\033[0m", end="")
            try:
                old_temp = characters[target]
            except KeyError:
                old_temp = None
            characters[target] = {}
            try:
                for attribute in coreAttributes:
                    if breakpoints[target][attribute] != -1:
                        while True:
                            if not api_attr:
                                valueInput = input(f"Enter value for \033[1m{attribute.upper()}\033[0m: \033[38;5;202m").replace(",",".").replace("%","")
                            else:
                                print(f"\033[1m{attribute.upper()}\033[0m: \033[38;5;202m{api_attr[attribute.lower()]}")
                                valueInput = api_attr[attribute.lower()]
                            try:
                                float(valueInput)
                                break
                            except:
                                pass
                        if comp_mode:
                            if attribute not in ["crit rate","crit dmg","break effect","energy regen","effect hit"]:
                                color = 196 if int(valueInput) < int(lastdata[attribute]) else 40
                                if int(valueInput) == int(lastdata[attribute]):
                                    color = 240
                                print(f"\033[38;5;{color}m{'' if int(valueInput) <= int(lastdata[attribute]) else '+'}{int(valueInput) - int(lastdata[attribute])} \033[38;5;240m(from {int(lastdata[attribute])})\033[0m")
                            else:
                                color = 196 if float(valueInput) < float(lastdata[attribute]) else 40
                                if float(valueInput) == float(lastdata[attribute]):
                                    color = 240
                                print(f"\033[38;5;{color}m{'' if float(valueInput) <= float(lastdata[attribute]) else '+'}{round(float(valueInput) - float(lastdata[attribute]),1)} \033[38;5;240m(from {float(lastdata[attribute])})\033[0m")
                        else:
                            print("\033[0m",end="")
                        characters[target][attribute] = valueInput
            except KeyboardInterrupt:
                if old_temp is not None:
                    characters[target] = old_temp
                else:
                    del characters[target]
                continue
            except:
                input("\n\033[31m[ An Error occured and character data was reverted. ]\033[0m")
                if old_temp is not None:
                    characters[target] = old_temp
                else:
                    del characters[target]
                continue
            if relicstatus["success"]:
                relics[target]["equipment"] = api_relic
                relics[target]["base_values"] = {k: v for k, v in api_attr.items() if k.startswith('base')}
                print("\nRelics successfully set.")
            characters[target]["updated"] = int(time.time())
            with open(configutil.PATHS.characters,"w") as f:
                json.dump(characters,f)
            with open(configutil.PATHS.relics,"w") as f:
                json.dump(relics,f)
            input("\n\033[38;5;40m[ Done. ]\033[0m")
        if menuindex == 4:
            if len(teams) == 0:
                print("\n\033[38;5;240m[ No teams ]\033[0m")
            else:
                print("\n\033[38;5;240mTEAM OVERVIEW")
                for i in sorted(list(teams.keys())):
                    print(f"[{i.upper():17}] | {teams[i][0].capitalize()} + {teams[i][1].capitalize()} + {teams[i][2].capitalize()} + {teams[i][3].capitalize()}")
            print("\n\033[0mEnter a team name to edit a preexisting or create a new one \033[38;5;240m(17 chars max)\033[0m:")
            target = ""
            try:
                while len(target) not in range(1,18):
                    target = input("> \033[38;5;202m").strip().lower()
            except:
                continue
            print("\n\033[0mEnter target characters, seperated by comma:")
            try:
                char_target = input("> \033[38;5;202m").lower().split(",")
            except:
                continue
            if len(char_target) != 4:
                input("\n\033[31m[ Invalid team size ]\033[0m")
                continue
            for i in range(len(char_target)):
                char_target[i] = char_target[i].lower().strip()
            bp_ignore = []
            for i in breakpoints:
                if breakpoints[i].values() == [-1] * 9:
                    bp_ignore.append(i)
            team_ok = True
            for i in char_target:
                if i not in breakpoints:
                    input(f"\n\033[31m[ Character not recognized ({i}) ]\033[0m")
                    team_ok = False
                    continue
                if i in bp_ignore:
                    input(f"\n\033[31m[ Character has no breakpoints ({i}) ]\033[0m")
                    team_ok = False
                    continue
                if i not in characters:
                    input(f"\n\033[31m[ No character information yet ({i}) ]\033[0m")
                    team_ok = False
                    continue
            if not team_ok:
                continue
            teams[target] = char_target
            with open(configutil.PATHS.teams,"w") as f:
                json.dump(teams,f)
            input("\n\033[38;5;40m[ Done. ]\033[0m")
        if menuindex == 5:
            print("\033[38;5;202m\033[1mWarning:\033[22m\nYou are editing character target values.\nPress CTRL + C to return to main menu if you just want to enter your own character information.\033[0m\n")
            try:
                target = input("Enter name: \033[38;5;202m").lower().strip()
                if target == "":
                    raise ValueError("Can't be empty.")
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
            prev_breakpoints = dcp(breakpoints)
            prev_relics = dcp(relics)
            breakpoints[target] = {}
            if target not in relics:
                relics[target] = {"equipment":[],"base_values":{},"prio":{"main":[],"sub":{}}}
            print("Mark unneeded parameters with '-1'. Use highest recommended values.")
            try:
                for i in coreAttributes:
                    x = input(f"Enter value for \033[1m{i.upper()}\033[0m: \033[38;5;202m")
                    x.replace(",",".")
                    print("\033[0m",end="")
                    breakpoints[target][i] = float(x)
                print("\nEnter attributes to mark as \033[1minverse\033[0m. Inverse describes attributes that should \033[1mnot be exceeded\033[0m.")
                x = input("Enter attributes (Seperate multiple with comma or leave blank): \033[38;5;202m")
                if x != "":
                    x = x.lower().split(",")
                    xnot = [item.strip() for item in x if item.lower() not in coreAttributes]
                    xs = [item.strip() for item in x if item.lower() in coreAttributes]
                    if len(xnot) == 0:
                        breakpoints[target]["inverse"] = xs
                    else:
                        raise ValueError("Invalid attributes for Inverse supplied.")
                else:
                    breakpoints[target]["inverse"] = []

                print("\033[0m\nEnter Relic Priority:\nList attributes desirable on relic main stats.\033[0m")
                x = input("\033[38;5;240mSeperate with comma and start with Body:\n\033[0m> \033[38;5;202m")
                x = [item.strip().lower() for item in x.split(",")]
                attr_ok = set(attr for attr in coreAttributes + supplementaryAttributes)
                xs = [item.strip() for item in x if item.lower() in attr_ok]
                xn = [item.strip() for item in x if item.lower() not in attr_ok]
                if len(xs) == 4:
                    relics[target]["prio"]["main"] = xs
                else:
                    print(x, xs, attr_ok)
                    raise ValueError(f"Invalid attribute(s): {", ".join(xn)}")

                print("\033[0m\nEnter Relic Priority:\nList attributes desirable on relic sub stats.\033[0m")
                x = input("\033[38;5;240mSeperate with either:\n- '>' (former more important) or \n- '=' (equal):\n\033[0m> \033[38;5;202m")
                priority_groups = [group.strip() for group in x.lower().split(">")]
                prio_dict = {}
                current_rank = 1
                for group in priority_groups:
                    attrs = [attr.strip() for attr in group.split("=")]
                    for attr in attrs:
                        if attr not in coreAttributes + ["atk%","def%","hp%","effect res"]:
                            raise ValueError(f"Invalid attribute supplied: '{attr}'")
                        if attr in ["atk", "def", "hp"]:
                            attr += "%"
                    for attr in attrs:
                        prio_dict[attr] = current_rank
                    current_rank += 1
                relics[target]["prio"]["sub"] = prio_dict

                with open(configutil.PATHS.bridgedata) as f:
                    bridgedata = json.load(f)
                for i in breakpoints:
                    if i not in bridgedata:
                        bridgedata[i] = {}

                with open(configutil.PATHS.characters,"r") as f:
                    characters = json.load(f)

                if [key for key, value in breakpoints[target].items() if value == -1 and key not in coreAttributes] != [key for key, value in prev_breakpoints[target].items() if value == -1 and key not in coreAttributes] and target in characters:
                    print("\n\033[38;5;202m[!] Relevant breakpoint keys have changed. Character data has been reset.\033[0m")
                    del characters[target]
                    with open(configutil.PATHS.characters,"w") as f:
                        json.dump(characters,f)
                with open(configutil.PATHS.breakpoints,"w") as f:
                    json.dump(breakpoints,f)
                with open(configutil.PATHS.bridgedata,"w") as f:
                    json.dump(bridgedata,f)
                with open(configutil.PATHS.relics,"w") as f:
                    json.dump(relics,f)
                input("\n\033[38;5;40m[ Done. ]\033[0m")
            except ValueError as e:
                breakpoints = prev_breakpoints
                input(f"\n\033[31m[ {str(e)} ]\033[0m")
                continue
            except KeyboardInterrupt:
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
            if target not in breakpoints.keys():
                input("\n\033[31m[ Character not recognized. ]\033[0m")
                continue
            if list(breakpoints[target].values()) == [-1] * 9:
                input("\n\033[31m[ Character has no breakpoints ]\033[0m")
                continue
            if key not in coreAttributes:
                input("\n\033[31m[ Value key not recognized. ]\033[0m")
                continue
            try:
                x = input(f"\033[0mEnter value for \033[1m{key.upper()}\033[0m Bridge: \033[38;5;202m").replace(",",".")
                print("\033[0m",end="")
                bridgedata[target][key] = float(x)
                with open(configutil.PATHS.bridgedata,"w") as f:
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
            if target not in breakpoints.keys():
                input("\n\033[31m[ Character not recognized. ]\033[0m")
                continue
            if list(breakpoints[target].values()) == [-1] * 9 + [[]]:
                input("\n\033[31m[ Character has no breakpoints ]\033[0m")
                continue
            q_char = {}
            for attribute in coreAttributes:
                if breakpoints[target][attribute] != -1:
                    while True:
                        x = input(f"Enter value for \033[1m{attribute.upper()}\033[0m: \033[38;5;202m")
                        print("\033[0m",end="")
                        try:
                            float(x)
                            break
                        except:
                            pass
                    q_char[attribute] = x
            print("\n\033[7m ATTRIBUTE    | VALUE                  | SCORE   |\033[27m")
            ev_stats = q_char
            ev_breakpoints = breakpoints[target]
            ev_bridges = {}
            characterEval = charcom.analyseChar(ev_breakpoints, ev_stats, ev_bridges)
            inverse = breakpoints[target]["inverse"]
            for attribute in characterEval["stats"]["attributes"]:
                value1 = float(q_char[attribute])
                value2 = float(breakpoints[target][attribute])
                value1 = int(value1) if value1.is_integer() else value1
                value2 = int(value2) if value2.is_integer() else value2
                score = characterEval["stats"]["attributes"][attribute]["score"]
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
                if attribute in inverse:
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
                print(f" {attribute.upper().ljust(13)}| \033[38;5;{colorcode[col_index]}m{xvalue1}\033[38;5;240m {comp_symbol} {xvalue2.ljust(21-1-len(xvalue1))}\033[0m| {score}{' '*(8-len(score))}|")
            print("\n")
            score = characterEval["stats"]["score"]
            ratio = characterEval["stats"]["accuracy"]
            if score >= 100000:
                print(f"Total scoring: \033[7;38;5;171m X-{int(score)-100000:,} \033[0m \033[38;5;240m({ratio:,}% acc)")
            else:
                print(f"Total scoring: {int(score):,} \033[38;5;240m({ratio:,}% acc)")
            input("\n\033[38;5;240m[ <- ]\033[0m")
        if menuindex == 0:
            print("\033c\033[7m Select option                   >\033[0m\n\n[1] - Fetch new characters\n[2] - Set UID\n[3] - API name translation\n[4] - Manage Savefile")
            try:
                lm = int(input("> "))
                if lm not in range(1,5):
                    raise ValueError("Invalid Index")
            except:
                continue
            if lm == 1:
                try:
                    with open(configutil.PATHS.importignore) as f:
                        ignore = json.load(f)
                    creation_template = {"hp":-1,"atk":-1,"def":-1,"spd":-1,"crit rate":-1,"crit dmg":-1,"break effect":-1,"energy regen":-1,"effect hit":-1,"inverse":[]}
                    response = requests.get("https://www.prydwen.gg/star-rail/characters")
                    response.raise_for_status()
                    isOffline = False
                    cards = BeautifulSoup(response.text, 'html.parser').find_all("div", {"class", "avatar-card"})
                    entryindex = len(cards)
                    for object in cards:
                        objectid = object.find("span").find("a")["href"].split("/")[-1].replace("-"," ")
                        if not (objectid not in breakpoints.keys() and objectid not in ignore["keys"]):
                            entryindex -= 1
                    if entryindex == 0:
                        input("\n\033[38;5;40m[ You're already up to date! ]\033[0m")
                        continue
                    print(f"Expecting {entryindex} new entries.")
                    print("0: Ignore / 1: Change name and add / 2: Directly add")
                    for object in cards:
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
                    with open(configutil.PATHS.importignore,"w") as f:
                        json.dump(ignore,f)
                    with open(configutil.PATHS.breakpoints,"w") as f:
                        json.dump(breakpoints,f)
                    input("\n\033[38;5;40m[ Done. ]\033[0m")
                except requests.exceptions.RequestException:
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
                            with open(configutil.PATHS.uid,"w") as f:
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
                        response = requests.get(f"https://api.mihomo.me/sr_info_parsed/{uid}?lang=en&version=v2")
                        response.raise_for_status()
                        api_data = response.json()
                        api_chars = [x['name'].lower() for x in api_data["characters"]]
                    except KeyboardInterrupt:
                        continue
                    except requests.exceptions.RequestException:
                        input("\n\033[31m[ Connection failed. ]\033[0m")
                        continue
                    except Exception:
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
                                    input(f"\nSet the following?:\n{syn[0]} --> {syn[1]}\nENTER: Yes / CTRL C: No")
                                except:
                                    continue
                                api_name_mapping[syn[1]] = syn[0]
                                with open(configutil.PATHS.api_name_map,"w") as f:
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
                                with open(configutil.PATHS.api_name_map,"w") as f:
                                    json.dump(api_name_mapping,f)
                                input("\n\033[38;5;40m[ Done. ]\033[0m")
                                continue
                            else:
                                input("\n\033[31m[ Unrecognized Prefix. ]\033[0m")
                        except KeyboardInterrupt:
                            break
            elif lm == 4:
                with open(configutil.PATHS.characters) as f:
                    characters = json.load(f)
                with open(configutil.PATHS.breakpoints) as f:
                    breakpoints = json.load(f)
                with open(configutil.PATHS.bridgedata) as f:
                    bridgedata = json.load(f)
                with open(configutil.PATHS.teams) as f:
                    teams = json.load(f)
                print("\033c\033[7m Select option                   >\033[0m\n\n[1] - Create a backup\n[2] - Delete a character\n[3] - Delete a breakpoint and character\n[4] - Delete a characters bridges\n[5] - Delete a team\n[6] - Wipe save\n\n\033[38;5;240mOr, if you like tinkering:\n\n[0] - Open save directory to edit files directly\033[0m")
                try:
                    lm = int(input("\n> "))
                    if lm not in range(0,7):
                        raise ValueError("Invalid Index")
                except:
                    continue
                if lm == 1:
                    shutil.make_archive(Path.home() / f"HSRCE-Backup-{int(time.time())}", 'zip', configutil.APP_DATA_DIR)
                    input("\n\033[38;5;40m[ Backup created in user directory. ]\033[0m")
                if lm == 2:
                    target = input("Target Name:").strip().lower()
                    if target in characters:
                        del characters[target]
                        if target in bridgedata:
                            del bridgedata[target]
                        tbr = None
                        for team in teams.keys():
                            if target in teams[team]:
                                tbr = team
                        if tbr:
                            del teams[tbr]
                        with open(configutil.PATHS.characters, "w") as f:
                            json.dump(characters, f)
                        with open(configutil.PATHS.breakpoints, "w") as f:
                            json.dump(breakpoints, f)
                        with open(configutil.PATHS.bridgedata, "w") as f:
                            json.dump(bridgedata, f)
                        with open(configutil.PATHS.teams, "w") as f:
                            json.dump(teams, f)
                        input("\n\033[38;5;40m[ Deletion complete ]\033[0m")
                    else:
                        input("\n\033[31m[ Entry doesn't exist in characters ]\033[0m")
                if lm == 3:
                    target = input("Target Name:").strip().lower()
                    if target in breakpoints:
                        del breakpoints[target]
                        del characters[target]
                        if target in bridgedata:
                            del bridgedata[target]
                        tbr = None
                        for team in teams:
                            if target in teams[team]:
                                tbr = teams[team]
                        if tbr:
                            del tbr
                        with open(configutil.PATHS.characters, "w") as f:
                            json.dump(characters, f)
                        with open(configutil.PATHS.breakpoints, "w") as f:
                            json.dump(breakpoints, f)
                        with open(configutil.PATHS.bridgedata, "w") as f:
                            json.dump(bridgedata, f)
                        with open(configutil.PATHS.teams, "w") as f:
                            json.dump(teams, f)
                        input("\n\033[38;5;40m[ Deletion complete ]\033[0m")
                    else:
                        input("\n\033[31m[ Entry doesn't exist in breakpoints ]\033[0m")
                if lm == 4:
                    target = input("Target Name:").strip().lower()
                    if target in bridgedata:
                        bridgedata[target] = {}
                        with open(configutil.PATHS.characters, "w") as f:
                            json.dump(characters, f)
                        with open(configutil.PATHS.breakpoints, "w") as f:
                            json.dump(breakpoints, f)
                        with open(configutil.PATHS.bridgedata, "w") as f:
                            json.dump(bridgedata, f)
                        input("\n\033[38;5;40m[ Deletion complete ]\033[0m")
                    else:
                        input("\n\033[31m[ Entry doesn't exist or has no bridges ]\033[0m")
                if lm == 5:
                    target = input("Target Name:").strip().lower()
                    if target in teams:
                        del teams[target]
                        with open(configutil.PATHS.teams, "w") as f:
                            json.dump(teams, f)
                        input("\n\033[38;5;40m[ Deletion complete ]\033[0m")
                    else:
                        input("\n\033[31m[ Entry doesn't exist ]\033[0m")
                if lm == 6:
                    print("\033c\033[31;7m !!!                   >\033[0m\n\n\033[31mAre you SURE that you want to wipe all data?\nIf yes, type 'CONFIRM' to continue.")
                    if input("\n> ") != "CONFIRM":
                        continue
                    folder = configutil.get_app_data_path()
                    for filename in os.listdir(folder):
                        file_path = os.path.join(folder, filename)
                        try:
                            if os.path.isfile(file_path) or os.path.islink(file_path):
                                os.unlink(file_path)
                            elif os.path.isdir(file_path):
                                shutil.rmtree(file_path)
                        except Exception as e:
                            raise Exception(f"\033[31m\nFailed to delete {file_path} ({e}).\nTry to delete the offending data yourself.\033[0m")
                    raise Exception("Reset complete. Start the program again to start fresh.")
                if lm == 0:
                    configutil.open_file_explorer(configutil.get_app_data_path())
                    input("\n\033[38;5;240m[ <- ]\033[0m")

except ModuleNotFoundError:
    input(f"\033[31m\nOne or more modules required for this script are not installed:\n\n{traceback.format_exc()}\033[0m")
except Exception:
    input(f"\033[31m\n\033[7mAn error occurred!            |\033[27m\n{traceback.format_exc()}\033[0m")
