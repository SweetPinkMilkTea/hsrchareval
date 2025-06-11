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
            current["sub"].append({"key":substat["field"], "value":round(substat["value"] * 100 if substat["percent"] else 1,2), "count":substat["count"]})
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