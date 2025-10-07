from collections import Counter
from copy import deepcopy as dcp

# Arrays: [0] is minimum, [1] maximum; per roll
roll_dist = {
    "hp": [33, 42],
    "atk": [16, 21],
    "def": [16, 21],
    "hp%": [3.4, 4.4],
    "atk%": [3.4, 4.4],
    "def%": [4.3, 5.4],
    "crit rate": [2.5, 3.2],
    "crit dmg": [5.1, 6.5],
    "effect hit": [3.4, 4.3],
    "effect res": [3.4, 4.3],
    "break effect": [5.1, 6.5],
    "spd": [2, 2.6]
}

def extract(rawdata):
    exp = []
    set_ids = {}
    keymap = {"break dmg":"break effect","sp rate":"energy regen", "heal rate":"heal boost", "thunder dmg": "lightning dmg"}
    for relic in rawdata:
        current = {}
        # set id
        if relic["set_id"] not in set_ids:
            set_ids[relic["set_id"]] = chr(65+len(list(set_ids.keys())))
        current["set"] = set_ids[relic["set_id"]]
        # main stat
        key = relic["main_affix"]["field"].replace("_", " ")
        key = keymap.get(key, key)
        current["main"] = {"key":key}
        # sub stats
        current["sub"] = []
        for substat in relic["sub_affix"]:
            key = substat["field"].replace("_", " ")
            key = keymap.get(key, key)
            if key in ["atk", "def", "hp"] and substat["percent"]:
                key += "%"
            value = round(substat["value"] * 100 if substat["percent"] else substat["value"],2)
            count = substat["count"]
            current["sub"].append({"key":key, "value":value, "count":count})
        exp.append(current)
    return exp
    
def validate(rawdata):
    try:
        assert len([x for x in rawdata if x["level"] == 15]) == 6
    except AssertionError:
        return {"success": False,"message": "Validation failed."}
    except:
        return {"success": False,"message": "Computation failed."}
    else:
        return {"success": True,"message": "OK"}

# targets: Info about correct Main Stats and prioritized Subs
def analyse(relics: list, targets: dict, debug: bool = False):
    result = {
        "relics": [],
        "fullscore": 0,
        "flags": {
            "setfaults": 0,
            "mainfaults": 0
        },
        "prio":targets["sub"]
    }
        
    # --- Check Set config ---
    setarray = [piece["set"] for piece in relics]
    counter = Counter(setarray)
    set_faults = 0
    for count in counter.values():
        if count not in (2, 4):
            set_faults += 1
    result["flags"]["setfaults"] = set_faults
    
    pieceindex = 0
    
    for piece in relics:
        if debug: 
            print(f"\n=== Analyzing piece {pieceindex+1} ({piece['set']}) ===")
        
        ### --- Check Main Stats ---
        mainkey = piece["main"]["key"]
        mainstattargets = ["hp", "atk"] + targets["main"]
        targetkey = mainstattargets[pieceindex]
        
        main_fault = mainkey != targetkey
        low_fault_impact = (mainkey.endswith("dmg") or mainkey.endswith("atk")) and (targetkey.endswith("dmg") or targetkey.endswith("atk"))
        
        if main_fault:
            result["flags"]["mainfaults"] += 1 
        
        ev_mainstat = {"key": mainkey, "target": targetkey}
        
        ### --- Check Subs and calc score ---
        minus_one_roll = sum([x["count"] for x in piece["sub"]]) < 9
        
        substatprio = dcp(targets["sub"])
        
        # Remove Substat Prio from piece if it's a main stat
        if mainkey in substatprio:
            removed_value = substatprio[mainkey]
            del substatprio[mainkey]
            if removed_value not in substatprio.values():
                for key in substatprio:
                    if substatprio[key] > removed_value:
                        substatprio[key] -= 1
        
        # Prio adjustments if subs are spotted in piece
        piece_keys = [d["key"] for d in piece["sub"]]
        maxDepth = max(substatprio.values())
        passedLevel = 0
        for level in range(1, 1+maxDepth):
            levelKeys = [k for k, v in substatprio.items() if v == level]
            if all(elem in piece_keys for elem in levelKeys):  # <-- flipped
                passedLevel += 1
            else:
                break

        substatprio = {k: max(1, v - passedLevel) for k, v in substatprio.items()}
        
        # Grace removes unavoidable 0-score rolls (due to <4 subprio)
        grace = 4 - min([4, len(substatprio)])
        
        flatstattriggers = [k.replace("%","") for k in substatprio.keys() if k in ("atk%", "def%", "hp%")]

        
        if debug:
            print(f"Priority: {substatprio} (Grace {grace})")
            print(f"Flat triggers (base keys): {flatstattriggers}")
        
        ev_substats = []
        substatscores = []
        for substat in piece["sub"]:
            key = substat["key"]
            value = substat["value"]
            count = substat["count"]
            
            if key in list(substatprio.keys()) + flatstattriggers:
                priokey = key + ("%" if key in flatstattriggers else "")
                distibution = roll_dist[key]  # assumes global roll_dist
                avg_roll = value / count
                saturation = (avg_roll - distibution[0]) / (distibution[1] - distibution[0])
                weight = 1 - (0.2 * (substatprio[priokey] - 1))
                
                # Penalize flattriggers
                if key in flatstattriggers:
                    weight *= 0.4
            else:
                priokey = None
                saturation = 0
                weight = 0
            
            score = round(100 * (0.8 + (0.2 * saturation)) * weight, 2)
            
            if debug:
                print(f" Substat {key} (val={value}, rolls={count}) → "
                      f"prio={priokey}, sat={saturation:.3f}, weight={weight:.3f}, score={score}")
            
            ev_substats.append({
                "key": key,
                "value": value,
                "count": count,
                "score": score,
                "saturation": saturation,
                "weight": weight
            })
            
            for i in range(count):
                if grace == 0 or score > 0:
                    substatscores.append(score)
                else:
                    grace -= 1
        
        if minus_one_roll:
            substatscores.append(0)        
        
        score = sum(substatscores) / len(substatscores) if substatscores else 0
        if main_fault:
            score *= 0.2 if low_fault_impact else 0.9
        else:
            score = 10 + score * 0.9 if pieceindex > 1 else score
        score = round(score, 2)
        
        result["relics"].append({
            "score": score,
            "main": ev_mainstat,
            "sub": ev_substats,
            "flags": {
                "minusone": minus_one_roll,
                "mainfault": main_fault
            }
        })
        
        if debug:
            print(f"\nPiece Score: {score} ({substatscores})")
            
        pieceindex += 1
    
    scorearray = [x["score"] for x in result["relics"]]
    result["fullscore"] = round((sum(scorearray) / len(scorearray)), 2) if scorearray else 0
    
    return result