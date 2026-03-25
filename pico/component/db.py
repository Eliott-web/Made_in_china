import ujson

DB_PATH = "db.json"


def _load():
    try:
        with open(DB_PATH, "r") as f:
            return ujson.load(f)
    except:
        return {"profiles": {}}


def _save(data):
    with open(DB_PATH, "w") as f:
        ujson.dump(data, f)


def create_profile(name):
    data = _load()
    if name in data["profiles"]:
        return False
    data["profiles"][name] = {
        "name":          name,
        "games_played":  0,
        "games_won":     0,
        "rounds_played": 0,
        "rounds_won":    0,
    }
    _save(data)
    return True


def delete_profile(name):
    data = _load()
    if name in data["profiles"]:
        del data["profiles"][name]
        _save(data)


def get_all_profiles():
    return list(_load()["profiles"].values())


def update_stats(name, games_won, rounds_won, rounds_played):
    data = _load()
    if name not in data["profiles"]:
        return
    p = data["profiles"][name]
    p["games_played"]  += 1
    p["games_won"]     += games_won
    p["rounds_played"] += rounds_played
    p["rounds_won"]    += rounds_won
    _save(data)
