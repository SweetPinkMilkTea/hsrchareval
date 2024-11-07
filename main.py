import json, time, os, traceback

# input("\n\033[38;5;240m[ <- ]\033[0m")

if "chardata.json" not in os.listdir():
    with open("chardata.json","w") as f:
        json.dump({},f)

with open("breakpoints.json") as f:
    breakpoints = json.load(f)
try:
    while True:
        print("\033cHSR Character Build Rater\n\n",end="")
        print("[1] - Lookup single characters")
        print("[2] - Lookup all characters")
        print("[3] - Create/Edit personal character")
        print("[4] - Create/Edit breakpoints")
        print("\033[38;5;240mCancel anything with CTRL C\033[0m")
        
        menuindex = int(input("\n> "))
        if menuindex == 1:
            with open("chardata.json") as f:
                characters = json.load(f)
            if len(characters) == 0:
                input("\n\033[31m[ No characters added yet ]\033[0m")
                continue
            print()
            for i in range(len(characters)):
                print(f"[{i+1:03}] - {list(characters.keys())[i].upper()} \033[38;5;240m| Last updated: {int((time.time() - characters[list(characters.keys())[i]]['updated'])/3600/24)}d ago\033[0m")
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
            print(f"\n\033[3;38;5;240m{list(characters.keys())[x].upper()}\n\033[0m\033[7m ATTR         | COMP                   | SCORE   |\033[0m\n              |                        |         |")
            allscore = []
            allratio = []
            for i in characters[list(characters.keys())[x]]:
                if i != "updated":
                    value1 = float(characters[list(characters.keys())[x]][i])
                    value2 = float(breakpoints[list(characters.keys())[x]][i])
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
        elif menuindex == 2:
            with open("chardata.json") as f:
                characters = json.load(f)
            if len(characters) == 0:
                input("\n\033[31m[ No characters added yet ]\033[0m")
                continue
            print("\033[7m NAME           | SCORE       | ACC      | RATE |\033[0m\n                |             |          |      |")
            for h in range(len(characters)):
                allscore = []
                allratio = []
                for i in characters[list(characters.keys())[h]]:
                    if i != "updated":
                        value1 = float(characters[list(characters.keys())[h]][i])
                        value2 = float(breakpoints[list(characters.keys())[h]][i])
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
                #print(f"Total scoring: {int(score):,} \033[38;5;240m({int(sum(allratio*100)/len(allratio)):,}% acc)")
                #print(f"[{i+1:03}] - {list(characters.keys())[h].upper()} | Last updated: {int((time.time() - characters[list(characters.keys())[h]]['updated'])/3600/24)}d ago\033[0m")
                print(f" \033[38;5;{color[grade]}m{list(characters.keys())[h].upper().ljust(15)}\033[0m| \033[38;5;{color[grade]}m{score.ljust(12)}\033[0m| \033[38;5;{color[grade]}m{acc.ljust(9)}\033[0m| \033[38;5;{color[grade]}m\033[7m {grade.ljust(3)}\033[0m |")
            input("\n\033[38;5;240m[ <- ]\033[0m")
        elif menuindex == 3:
            with open("chardata.json") as f:
                characters = json.load(f)
            print("\033cSelect character:\n")
            nobp = []
            for i in range(len(breakpoints.keys())):
                if list(breakpoints[list(breakpoints.keys())[i]].values()) == [-1] * 9:
                    print(f"\033[38;5;245m[{i+1:03}] - \033[31m{list(breakpoints.keys())[i].upper()} [No Breakpoints]\033[0m")
                    nobp.append(i)
                else:
                    if not list(breakpoints.keys())[i] in characters.keys():
                        print(f"\033[38;5;245m[{i+1:03}] - {list(breakpoints.keys())[i].upper()} | Not set\033[0m")
                    else:
                        print(f"[{i+1:03}] - {list(breakpoints.keys())[i].upper()} \033[38;5;240m| Last updated: {int((time.time() - characters[list(breakpoints.keys())[i]]['updated'])/(3600*24))}d ago\033[0m")
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
            target = list(breakpoints.keys())[int(x)-1]
            comp_mode = False
            if target in characters.keys():
                lastdata = characters[target]
                comp_mode = True
            characters[target] = {}
            for i in ["hp","atk","def","spd","C-Rate","C-Dmg","break","energy regen","effect hit"]:
                if breakpoints[target][i] != -1:
                    while True:
                        x = input(f"Enter value for \033[1m{i.upper()}\033[0m: \033[38;5;202m")
                        try:
                            float(x)
                            break
                        except:
                            pass
                    if comp_mode:
                        if not i in ["C-Rate","C-Dmg","break","energy regen","effect hit"]:
                            print(f"\033[38;5;{196 if int(x) <= int(lastdata[i]) else 40}m{'' if int(x) <= int(lastdata[i]) else '+'}{int(x) - int(lastdata[i])} \033[38;5;240m(from {int(lastdata[i])})\033[0m")
                        else:
                            print(f"\033[38;5;{196 if float(x) <= float(lastdata[i]) else 40}m{'' if float(x) <= float(lastdata[i]) else '+'}{round(float(x) - float(lastdata[i]),1)} \033[38;5;240m(from {float(lastdata[i])})\033[0m")
                    else:
                        print("\033[0m",end="")
                    characters[target][i] = x
            characters[target]["updated"] = int(time.time())
            with open("chardata.json","w") as f:
                json.dump(characters,f)
            input("\n\033[38;5;40m[ Done. ]\033[0m")
        elif menuindex == 4:
            target = input("Enter name: \033[38;5;202m").lower().strip()
            print("\033[0m",end="")
            if target in breakpoints.keys():
                try:
                    input("\n\033[38;5;202m[ Character is already present. Press CTRL+C to cancel. ]\033[0m")
                except:
                    continue
            prev_breakpoints = breakpoints
            breakpoints[target] = {}
            print("Mark unneeded parameters with '-1'. Use highest recommended values.")
            try:
                for i in ["hp","atk","def","spd","C-Rate","C-Dmg","break","energy regen","effect hit"]:
                    while True:
                        x = input(f"Enter value for \033[1m{i.upper()}\033[0m: \033[38;5;202m")
                        if "," not in x:
                            break
                    print("\033[0m",end="")
                    breakpoints[target][i] = int(x)
                with open("breakpoints.json","w") as f:
                    json.dump(breakpoints,f)
                input("\n\033[38;5;40m[ Done. ]\033[0m")
            except:
                breakpoints = prev_breakpoints
                input("\n\033[38;5;40m[ Aborted. Reverting. ]\033[0m")
                continue
                
except Exception as e:
    print(f"\033[31m\nERR:\n{traceback.format_exc()}\033[0m")