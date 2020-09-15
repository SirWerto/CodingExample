from cloudant.client import CouchDB
from cloudant.error import CloudantException
#from cloudant.database import CouchDataBase


def db_client():
    # actual variables from bagheera couchdb
    # connection
    ip_bagheera = '192.168.1.70'
    port_bagheera = '5984'
    url='http://' + ip_bagheera + ':' + port_bagheera
    # account
    username = 'Praetorian'
    password = '427bdf3c866807601ace1ac3c1f35029ad9830180957faa6f9c0daef9f5e5e75'
    # Use CouchDB to create a CouchDB client
    client = CouchDB(username, auth_token = password, url=url, connect=True)

    return client

def db_db(client, name="travian", fetch_limit=100):
    return client[name]
    #return CouchDB.CouchDataBase(client, name, fetch_limit)


def db_connexion():

    client = db_client()
    db = db_db(client)

    return db, client
#Poner try catchs al iniciar las conexiones


def db_insert(structs):
    #pull docs
    #disconnect client
    #push docs
    #disconnect client

    keys = get_keys(structs)

    try:
        db, client = db_connexion()
    except CloudantException as e:
        client.disconnect()
        raise 

    try:
        db, client = db_connexion()
        old_structs = db.all_docs(keys=keys, include_docs=True) #Try catch
    except CloudantException as e:
        client.disconnect()
        raise 
    finally:
        client.disconnect()

    upt_structs = update_all_structs(structs, old_structs)

    try:
        db, client = db_connexion()
        results = db.bulk_docs(upt_structs)
    except CloudantException as e:
        raise 
    else:
        return results
    finally:
        client.disconnect()

def get_keys(structs):
    return [x["_id"] for x in structs]


def update_all_structs(structs, old_structs):
    return [upt_struct(x, old_structs) for x in structs]

def search_old_struct(struct, old_structs):
    for old in old_structs["rows"]:
        if "error" not in old and struct["_id"] == old["doc"]["_id"]:
            return old
    return None

def upt_struct(struct, old_structs):

    switcher = {
        "village": _upt_villages,
        "player": _upt_player,
        "alliance": _upt_alliance,
        "server": _upt_server}

    old = search_old_struct(struct, old_structs)
    if old != None:
        return switcher[struct["type"]](struct, old)
    else:
        return struct


def _upt_villages(new, old):

    #print(new["race"])
    #print(old)
    #print(old["doc"]["race"])
    if new["race"][0][0] != old["doc"]["race"][-1][0]:
         old["doc"]["race"].append(new["race"][0])

    if new["name_v"][0][0] != old["doc"]["name_v"][-1][0]:
         old["doc"]["name_v"].append(new["name_v"][0])

    if new["id_p"][0][0] != old["doc"]["id_p"][-1][0]:
         old["doc"]["id_p"].append(new["id_p"][0])

    if new["population"][0][0] != old["doc"]["population"][-1][0]:
         old["doc"]["population"].append(new["population"][0])

    old["doc"]["last_day"] = new["last_day"]

    if 'id_s' not in old["doc"]:
        old["doc"]["id_s"] = new["id_s"]

    return old["doc"]

def _upt_player(new, old):

    if new["name_p"][0][0] != old["doc"]["name_p"][-1][0]:
         old["doc"]["name_p"].append(new["name_p"][0])

    if new["id_a"][0][0] != old["doc"]["id_a"][-1][0]:
         old["doc"]["id_a"].append(new["id_a"][0])

    old["doc"]["last_day"] = new["last_day"]

    if 'id_s' not in old["doc"]:
        old["doc"]["id_s"] = new["id_s"]


    return old["doc"]

def _upt_alliance(new, old):
    if new["name_a"][0][0] != old["doc"]["name_a"][-1][0]:
         old["doc"]["name_a"].append(new["name_a"][0])

    old["doc"]["last_day"] = new["last_day"]

    if 'id_s' not in old["doc"]:
        old["doc"]["id_s"] = new["id_s"]

    return old["doc"]


def _upt_server(new, old):
    old["doc"]["last_day"] = new["last_day"]
    return old["doc"]
