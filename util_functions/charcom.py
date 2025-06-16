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

def analyseChar():
    return 1