# Arrays: [0] is minimum, [1] maximum; per roll
roll_dist = {
    "hp": [33, 42],
    "atk": [16, 21],
    "def": [16, 21],
    "hp%": [3.4, 4.4],
    "atk%": [3.4, 4.4],
    "def%": [4.3, 5.4],
    "crit_rate": [2.5, 3.2],
    "crit_dmg": [5.1, 6.5],
    "effect_hit": [3.4, 4.3],
    "effect_res": [3.4, 4.3],
    "break_effect": [5.1, 6.5],
    "spd": [2, 2.6]
}

def extract(rawdata):
    exp = []
    set_ids = {}
    for relic in rawdata:
        current = {}
        # set id
        if not relic["set_id"] in set_ids:
            set_ids[relic["set_id"]] = chr(65+len(list(set_ids.keys())))
        current["set"] = set_ids[relic["set_id"]]
        # main stat
        current["main"] = {"key":relic["main_affix"]["field"]}
        # sub stats
        current["sub"] = []
        for substat in relic["sub_affix"]:
            key = substat["field"]
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
# stats: relevant base values to compare flat and percent stats
def analyse(relics, targets, stats):
    return 0