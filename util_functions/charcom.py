from util_functions import reliccom

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

def analyseChar(breakpoints, stats, bridges, relics = None, prio = None):
    result = {}
    # Classic Stats comparision
    allscore = []
    allratio = []
    attributes = {}
    inverse = breakpoints["inverse"]
    for attribute in stats:
        if attribute != "updated":
            current = float(stats[attribute]) + bridges.get(attribute,0)
            goal = float(breakpoints[attribute])
            goal = int(goal) if goal.is_integer() else goal
            ratio = 2*current/goal-1
            if ratio < 0:
                ratio = 0
            if ratio > 1:
                ratio = 1
            score = attributeScore(attribute, current, goal, attribute in inverse)
            if score >= 100000:
                ratio = 1
            attributes[attribute] = {
                "current": float(stats[attribute]),
                "bridge": bridges.get(attribute,False),
                "goal": goal,
                "score": score,
                "isInverse": attribute in inverse
                }
            allscore.append(score)
            allratio.append(ratio)
    score = int((sum(allscore) + min(allscore)*5)/(len(allscore)+5))
    r_acc = round(sum(allratio*100)/len(allratio),2)
    result["stats"] = {
        "score": score,
        "accuracy": r_acc,
        "attributes": attributes
        }
    # Relic Scoring
    if relics is None:
        result["relics"] = {}
    else:
        result["relics"] = reliccom.analyse(relics, prio)
    return result