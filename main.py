try:
    import json, time, os, traceback, requests
    # input("\n\033[38;5;240m[ <- ]\033[0m")

    if ".uid" not in os.listdir():
        with open(".uid","w") as f:
            f.write("0")
    if "chardata.json" not in os.listdir():
        with open("chardata.json","w") as f:
            json.dump({},f)
    if "breakpoints.json" not in os.listdir():
        with open("breakpoints.json","w") as f:
            json.dump({},f)
    if "teamdata.json" not in os.listdir():
        with open("teamdata.json","w") as f:
            json.dump({},f)
    if "bridgedata.json" not in os.listdir():
        with open("bridgedata.json","w") as f:
            json.dump({},f)

    with open("breakpoints.json") as f:
        breakpoints = json.load(f)

    with open("bridgedata.json") as f:
        bridgedata = json.load(f)
    for i in breakpoints:
        if i not in bridgedata:
            bridgedata[i] = {}

    with open(".uid") as f:
        uid = f.read()

    if uid == "0":
        while True:
            print("\033c\033[7m Quick-Import Setup               >\033[0m")
            print("\nEnter your UID to look for character data when trying to evaluate them.\nOnly characters featured on your profile page can be accessed.\n\n\033[38;5;240mEnter 0 to skip.\033[0m")
            uid = input("\n> ").strip()
            if uid.isdigit():
                break


    while True:
        print("\033c\033[1mHSR Character Build Rater\033[0m")
        print(f"\033[38;5;240mQuick-Import: {'OFF' if uid == "0" else 'ON ['+uid+']'}\n\033[0m")
        print("[1] - Lookup characters")
        print("[2] - Lookup teams")
        print("[3] - Create/Edit personal character")
        print("[4] - Create/Edit teams")
        print("[5] - Create/Edit breakpoints")
        print("[6] - Create/Edit 'bridges'")
        print("[7] - Quickscan")
        print("\n\033[38;5;240mCancel anything with CTRL C\033[0m")
        
        menuindex = int(input("\n>> "))
        print()
        if menuindex == 1:
            with open("chardata.json") as f:
                characters = json.load(f)
            if len(characters) == 0:
                input("\n\033[31m[ No characters added yet ]\033[0m")
                continue
            print("\033[7m #   | NAME           | SCORE       | ACC      | RANK |\033[0m\n     |                |             |          |      |")
            for h in range(len(characters)):
                allscore = []
                allratio = []
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
                        score = 100000*ratio
                        if ratio == 1:
                            score += abs(value2 - value1)
                        allscore.append(score)
                        allratio.append(ratio)
                score = f"{int((sum(allscore) + min(allscore)*5)/(len(allscore)+5)):,}"
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
                print(f" \033[38;5;{color[grade]}m{h+1:03d} \033[0m| \033[38;5;{color[grade]}m{sorted(list(characters.keys()))[h].upper().ljust(15)}\033[0m| \033[38;5;{color[grade]}m{score.ljust(12)}\033[0m| \033[38;5;{color[grade]}m{acc.ljust(9)}\033[0m| \033[38;5;{color[grade]}m\033[7m {grade.ljust(3)}\033[0m |")
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
            print(f"\n\033[3;38;5;240m{sorted(list(characters.keys()))[x].upper()}\n\033[0m\033[7m ATTR         | COMP                   | SCORE   |\033[0m\n              |                        |         |")
            allscore = []
            allratio = []
            for i in characters[sorted(list(characters.keys()))[x]]:
                if i != "updated":
                    value1 = float(characters[sorted(list(characters.keys()))[x]][i]) + bridgedata[sorted(list(characters.keys()))[x]].get(i,0)
                    value2 = float(breakpoints[sorted(list(characters.keys()))[x]][i])
                    value1 = int(value1) if value1.is_integer() else value1
                    value2 = int(value2) if value2.is_integer() else value2
                    ratio = 2*value1/value2-1
                    if ratio < 0:
                        ratio = 0
                    if ratio > 1:
                        ratio = 1
                    score = 100000*ratio
                    if ratio == 1:
                        score += abs(value2 - value1)
                    allscore.append(score)
                    allratio.append(ratio)
                    xvalue1 = f"{value1:,}"
                    xvalue2 = f"{value2:,}"
                    score = f"{int(score):,}"
                    #196 red
                    #202 orange
                    #220 yellow
                    #40 green
                    colorcode = [40,220,202,196]
                    col_index = 0
                    if value1 < value2:
                        col_index += 1
                    if value1 < (value2 - value2/10):
                        col_index += 1
                    if value1 < (value2 - value2/5):
                        col_index += 1
                    print(f" {i.upper().ljust(13)}| \033[38;5;{colorcode[col_index]}m{xvalue1}\033[38;5;240m / {xvalue2.ljust(21-1-len(xvalue1))}\033[0m| {score.ljust(8)}|")
            print("\n")
            score = (sum(allscore) + min(allscore)*5)/(len(allscore)+5)
            print(f"Total scoring: {int(score):,} \033[38;5;240m({int(sum(allratio*100)/len(allratio)):,}% acc)")
            input("\n\033[38;5;240m[ <- ]\033[0m")
        if menuindex == 2:
            with open("chardata.json") as f:
                characters = json.load(f)
            with open("teamdata.json") as f:
                teams = json.load(f)
            if len(teams) == 0:
                input("\n\033[31m[ No teams configured yet ]\033[0m")
                continue
            print("\033[7m #   | TEAM           | SCORE       | ACC      | RANK |\033[0m\n     |                |             |          |      |")
            for h in range(len(teams)):
                cumulativescore = []
                cumulativeratio = []
                rank_str = ""
                for ii in teams[sorted(list(teams.keys()))[h]]:
                    allscore = []
                    allratio = []
                    for i in characters[ii]:
                        if i != "updated":
                            value1 = float(characters[ii][i])
                            value2 = float(breakpoints[ii][i])
                            value1 = int(value1) if value1.is_integer() else value1
                            value2 = int(value2) if value2.is_integer() else value2
                            ratio = 2*value1/value2-1
                            if ratio < 0:
                                ratio = 0
                            if ratio > 1:
                                ratio = 1
                            score = 100000*ratio
                            if ratio == 1:
                                score += abs(value2 - value1)
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
                score = f"{int((sum(cumulativescore) + min(cumulativescore)*5)/(len(cumulativescore)+5)):,}"
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
            input("\n\033[38;5;240m[ <- ]\033[0m")
        if menuindex == 3:
            with open("chardata.json") as f:
                characters = json.load(f)
            print("\033cSelect character to edit state of:\n")
            nobp = []
            for i in range(len(breakpoints.keys())):
                if list(breakpoints[sorted(list(breakpoints.keys()))[i]].values()) == [-1] * 9:
                    print(f"\033[38;5;245m[{i+1:03}] - \033[31m{sorted(list(breakpoints.keys()))[i].upper()} [No Breakpoints]\033[0m")
                    nobp.append(i+1)
                else:
                    if not sorted(list(breakpoints.keys()))[i] in characters.keys():
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
            if uid != "0":
                api_name = {"topaz":"topaz & numby","march 8th":"march 7th","tb fire":"{nickname}","tb imaginary":"{nickname}","tb physical":"{nickname}","dan heng il":"dan heng • imbibitor lunae"}.get(target,target)
                api_data = requests.get(f"https://api.mihomo.me/sr_info_parsed/{uid}?lang=en&version=v1").json()
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
                    if input("API Data found! Continue using it? (Y/N) > \033[38;5;202m").lower() == "n":
                        api_attr = {}
                else:
                    print("No data available to load. Continue entering manually.")
            else:
                api_attr = {}
            print("\033[0m", end="")
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
            characters[target]["updated"] = int(time.time())
            with open("chardata.json","w") as f:
                json.dump(characters,f)
            input("\n\033[38;5;40m[ Done. ]\033[0m")
        if menuindex == 4:
            with open("teamdata.json") as f:
                teams = json.load(f)
            with open("chardata.json") as f:
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
            with open("teamdata.json","w") as f:
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
                    input("\n\033[38;5;202m[ Character is already present. Press CTRL+C to cancel. ]\033[0m")
                except:
                    continue
            else:
                try:
                    input("\n\033[38;5;202m[ Creating a new character entry. Press CTRL+C to cancel. ]\033[0m")
                except:
                    continue
            prev_breakpoints = breakpoints
            breakpoints[target] = {}
            print("Mark unneeded parameters with '-1'. Use highest recommended values.")
            try:
                for i in ["hp","atk","def","spd","crit rate","crit dmg","break effect","energy regen","effect hit"]:
                    while True:
                        x = input(f"Enter value for \033[1m{i.upper()}\033[0m: \033[38;5;202m")
                        if "," not in x:
                            break
                    print("\033[0m",end="")
                    breakpoints[target][i] = float(x)
                with open("breakpoints.json","w") as f:
                    json.dump(breakpoints,f)
                input("\n\033[38;5;40m[ Done. ]\033[0m")
            except:
                breakpoints = prev_breakpoints
                input("\n\033[38;5;40m[ Aborted. Reverting. ]\033[0m")
                continue
        if menuindex == 6:
            print("\033[38;5;240m\033[1mInfo:\033[22m\nUse bridges to add values not reflected in base stats to characters. These can include Eidolons, Light Cone Effects or specific Relic Set-Boosts.\033[0m\n")
            try:
                target = input("\033[0mEnter name: \033[38;5;202m").lower().strip()
                key = input("\033[0mEnter value key: \033[38;5;202m").lower().strip()
            except:
                continue
            print("\033[0m",end="")
            with open("breakpoints.json") as f:
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
                while True:
                    x = input(f"\033[0mEnter value for \033[1m{key.upper()}\033[0m Bridge: \033[38;5;202m")
                    if "," not in x:
                        break
                print("\033[0m",end="")
                bridgedata[target][key] = int(x)
                with open("bridgedata.json","w") as f:
                    json.dump(bridgedata,f)
                input("\n\033[38;5;40m[ Done. ]\033[0m")
            except:
                input("\n\033[38;5;40m[ Error. Aborting. ]\033[0m")
                continue
        if menuindex == 7:
            print("\033[38;5;240m\033[1mInfo:\033[22m\nQuickscan is used for evaluating characters without saving thier state (e.g. charcters of other users).\nFor your own characters, use menu option #3 instead.\033[0m\n")
            target = input("Enter name: \033[38;5;202m").lower().strip()
            print("\033[0m",end="")
            with open("breakpoints.json") as f:
                breakpoints = json.load(f)
            if not target in breakpoints.keys():
                input(f"\n\033[31m[ Character not recognized. ]\033[0m")
                continue
            if list(breakpoints[target].values()) == [-1] * 9:
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
                score = 100000*ratio
                if ratio == 1:
                    score += abs(value2 - value1)
                allscore.append(score)
                allratio.append(ratio)
                xvalue1 = f"{value1:,}"
                xvalue2 = f"{value2:,}"
                score = f"{int(score):,}"
                #196 red
                #202 orange
                #220 yellow
                #40 green
                colorcode = [40,220,202,196]
                col_index = 0
                if value1 < value2:
                    col_index += 1
                if value1 < (value2 - value2/10):
                    col_index += 1
                if value1 < (value2 - value2/5):
                    col_index += 1
                print(f" {i.upper().ljust(13)}| \033[38;5;{colorcode[col_index]}m{xvalue1}\033[38;5;240m / {xvalue2.ljust(21-1-len(xvalue1))}\033[0m| {score.ljust(8)}|")
            print("\n")
            score = (sum(allscore) + min(allscore)*5)/(len(allscore)+5)
            print(f"Total scoring: {int(score):,} \033[38;5;240m({int(sum(allratio*100)/len(allratio)):,}% acc)")
            input("\n\033[38;5;240m[ <- ]\033[0m")

except Exception as e:
    input(f"\033[31m\nERR:\n{traceback.format_exc()}\033[0m")
