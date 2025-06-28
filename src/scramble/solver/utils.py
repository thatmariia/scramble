from itertools import combinations


def are_disjoint(groups):
    seen = []
    for group in groups:
        for item in group:
            for other in seen:
                if item == other:
                    return False
            seen.append(item)
    return True