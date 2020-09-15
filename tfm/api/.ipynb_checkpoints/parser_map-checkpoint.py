from datetime import date
import requests

def tuple_line(line):
    p_line = []
    ret = line[30:-2]
    ret = ret.split("'")
    temp = ret[0][:-1].split(",")
    temp = [int(x) for x in temp]

    p_line.append(int(temp[0])) #Grid 0
    p_line.append(int(temp[1])) #X 1
    p_line.append(int(temp[2])) #Y 2
    p_line.append(int(temp[3])) #Race 3
    p_line.append(int(temp[4])) #Village Id 4
    p_line.append(ret[1])  #Village Name 5
    p_line.append(int(ret[2][1:-1])) #Player Id 6
    p_line.append(ret[3])  #Player Name 7
    p_line.append(int(ret[4][1:-1])) #Alliance Id 8
    p_line.append(ret[5])  #Alliance Name 9
    p_line.append(int(ret[6][1:]))   #Population 10

    if len(p_line) != 11:
        raise BadLineError(p_line, "Error on line parsed")
        
    return tuple(p_line)


def map2tuples(lines):
    parsed = []
    for line in lines:
        try:
            temp = tuple_line(line)
        except BadLineError:
            pass
        else:
            parsed.append(temp)

    if len(parsed) == 0:
        raise EmptyMapError("Empty Map")
            
    return parsed
    

def create_village(map_tuple, today):

    village = {}
    village["last_day"] = today
    village["type"] = "village"
    village["id_v"] = map_tuple[4]
    village["grid"] = map_tuple[0]
    village["x"] = map_tuple[1]
    village["y"] = map_tuple[2]
    village["race"] = [[map_tuple[3], today]]
    village["name_v"] = [[map_tuple[5], today]]
    village["id_p"] = [[map_tuple[6], today]]
    village["population"] = [[map_tuple[10], today]]

    return village

def create_player(map_tuple, today):

    player = {}
    player["last_day"] = today
    player["type"] = "player"
    player["id_p"] = map_tuple[6]
    player["name_p"] = [[map_tuple[7], today]]
    player["id_a"] = [[map_tuple[8], today]]

    return player

def create_alliance(map_tuple, today):

    alliance = {}
    alliance["last_day"] = today
    alliance["type"] = "alliance"
    alliance["id_a"] = map_tuple[8]
    alliance["name_a"] = [[map_tuple[9], today]]

    return alliance

def create_structures(map_tuples, id_s):

    today = date.today().strftime("%d/%m/%Y")
    map_items = []
    players = []
    alliances = []
    for tup in map_tuples:
        village = create_village(tup, today)
        village["_id"] = str(village["id_v"]) + str(id_s) + "v"
        village["id_s"] = str(id_s)
        map_items.append(village)
        player = create_player(tup, today)
        player["_id"] = str(player["id_p"]) + str(id_s) + "p"
        player["id_s"] = str(id_s)
        if player not in players:
            players.append(player)
        alliance= create_alliance(tup, today)
        alliance["_id"] = str(alliance["id_a"]) + str(id_s) + "a"
        alliance["id_s"] = str(id_s)
        if alliance not in alliances:
            alliances.append(alliance)

    return map_items + players + alliances

def extract_items_from_map(map_split, id_s):
    return create_structures(map2tuples(map_split), id_s)

    
def extract(server):

    try:
        r = requests.get(server["url"] + "/map.sql")
        r.raise_for_status()
    except requests.exceptions.HTTPError as e:
        raise BadMapExtractionError(e, "Can't obtain the map due to requests STATUS")
    except requests.exceptions.RequestException as e:
        raise BadMapExtractionError(e, "Can't obtain the map due to requests ERROR")
    else:
        return extract_items_from_map(r.text.splitlines(), server["_id"])
        






###ERRORS

class MapError(Exception):
    """Base class for errors while parsing the map"""
    pass

class BadLineError(MapError):
    """Bad line parsed for map"""
    def __init__(self, expression, message):
        self.expression = expression
        self.message = message

class EmptyMapError(MapError):
    """Map has 0 lines parsed"""
    def __init__(self, message):
        self.message = message

class BadMapExtractionError(MapError):
   """Can not obtain any map""" 
   def __init__(self, expression, message):
        self.expression = expression
        self.message = message
