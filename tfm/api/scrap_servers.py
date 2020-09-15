import requests
from datetime import date
from requests.exceptions import RequestException
from bs4 import BeautifulSoup

def get_servers_list():
    try:
        r = requests.get('https://status.travian.com/index.php', timeout=5)
        r.raise_for_status()

    except HTTPError as http_err:
        print('HTTP error occurred while getting server list: {http_err}'.format(http_err=http_err))
        raise http_err

    except Timeout as timeout:
        print('Timeout while getting server list: {timeout}'.format(timeout=timeout))
        raise timeout

    else:
        servers_list = []
        country_id_list = []
        rs = BeautifulSoup(r.text, 'html.parser')
        t_countrys = rs.find_all('div', class_='hidden')
        for t_country in t_countrys:
            temp_servers = get_country_servers(t_country)
            servers_list = servers_list + temp_servers
        return servers_list


def get_country_servers(t_country):
    country_id = t_country['id']
    servers = []
    server_rows = t_country.find_all('tr')[1:] #The first row is column labeling
    for row in server_rows:
        cells = row.find_all('td')
        servers.append(create_server(row, country_id))
    return servers

def create_server(row, country_id):

    server = {}
    cells = row.find_all('td')

    server["type"] = "server"
    server["url"] = cells[1].text
    server["last_day"] = date.today().strftime("%d/%m/%Y")
    server["id_country"] = country_id

    if country_id != "com":
        server["url_reference"] = "https://www.travian.com/" + country_id
    else:
        server["url_reference"] = "https://www.travian.com/international"

    if cells[0].next.attrs["src"] != "img/un/a/uparrow.gif":
        server["status"] = False
    else:
        server["status"] = True

    return server
