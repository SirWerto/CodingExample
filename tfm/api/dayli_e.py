from parser_map import extract, BadMapExtractionError
from scrap_servers import get_servers_list as get_servers
from scrap_info import scraps, ServerInfoError
from db_couch import db_insert
from cloudant.error import CloudantException

from pyspark import SparkContext



def dayli_e(server):
    
    scraps(server)
    
    data = extract(server)
    data.append(server)
    
    results = db_insert(data)
    
    return results



def dayli_mapper(server):

    try:
        result = dayli_e(server)
    except ServerInfoError as e:
        return None
    except BadMapExtractionError as e:
        return None
    except CloudantException as e:
        return None
    except Exception as e:
        return None
    else:
        return result



def main():

    server_list = get_servers()

    with SparkContext() as sc:
        results = sc.parallelize(server_list).map(dayli_mapper).collect()

    return results
        
        

if __name__ == "__main__":
    main()

    
