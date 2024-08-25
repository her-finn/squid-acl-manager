#!/usr/bin/env python3
import sys, sqlite3, ipaddress, re
dbname = "nacl.db"

#Initialize or Update Database , if needed
def init_db():
    db = sqlite3.connect(dbname)
    cursor = db.cursor()
    dbchanges = [
        "CREATE TABLE IF NOT EXISTS 'netgroups' ('id' INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT, 'subnet' VARCHAR(18) NOT NULL,'comment' TEXT NULL,'active' TINYINT(1) NOT NULL DEFAULT 1);",
        "CREATE TABLE IF NOT EXISTS 'contentgroups' ('id' INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT, 'type' VARCHAR(20) NOT NULL,'filter' VARCHAR(100) NOT NULL,'comment' TEXT NULL,'active' TINYINT(1) NOT NULL DEFAULT 1);",
        "CREATE TABLE IF NOT EXISTS 'mapping' ('netgroup' INTEGER NOT NULL,'contentgroup' INTEGER NOT NULL,'active' TINYINT(1) NOT NULL DEFAULT 1, 'comment' TEXT NOT NULL DEFAULT '',PRIMARY KEY (netgroup, contentgroup),CONSTRAINT 'netgroup' FOREIGN KEY ('netgroup') REFERENCES 'netgroups' ('id') ON UPDATE NO ACTION ON DELETE NO ACTION,CONSTRAINT 'contentgroup' FOREIGN KEY ('contentgroup') REFERENCES 'contentgroups' ('id') ON UPDATE NO ACTION ON DELETE NO ACTION);"
    ]
    for query in dbchanges:
        cursor.execute(query)

#Returns list of all Network groups, that are active and the subnet column contains the requesting ip
def get_netgroups_for_ip(ip:str):
    db = sqlite3.connect(dbname)
    cursor = db.cursor()
    target_ip = ipaddress.ip_address(ip)
    cursor.execute("SELECT id,subnet FROM netgroups WHERE active=1")
    matching_groups = []
    for group in cursor.fetchall():
        subnet = group[1]
        try:
            network = ipaddress.ip_network(subnet,strict=False)
            if target_ip in network:
                matching_groups.append(group[0])
        except ValueError:
            print(f"Found invalid subnet: {subnet}")
    return matching_groups

#Returns list of all Content groups, that are active and asociated with one of the groups given in the netgroups list argument
def get_contentgroups_for_netgroups(ngroups:list):
    db = sqlite3.connect(dbname)
    cursor = db.cursor()
    cgroups = []
    for ngroup in ngroups:
        cursor.execute(f"SELECT contentgroup FROM mapping WHERE netgroup={ngroup} AND active=1")
        for row in cursor.fetchall():
            cgroups.append(row[0])
    return cgroups

#Gets all Filters for the list given of content groups
def get_filter_for_contentgroups(cgroups:list):
    db = sqlite3.connect(dbname)
    cursor = db.cursor()
    filter = []
    for cgroup in cgroups:
        cursor.execute(f"SELECT type, filter FROM contentgroups WHERE id={cgroup} AND active=1")
        for row in cursor.fetchall():
            filter.append({"type": row[0], "filter": row[1]})
    return filter

#Processes the URL in every filter, until one is true or return false by default
def process_url_in_filters(filters:list,url:str):
    for filter in filters:
        if process_filter(type=filter["type"],filter=filter["filter"],url=url):
            return True
    return False

#Processes the Filter from Content Group
def process_filter(type:str,filter:str,url:str):
    #Typen:
    #Strict
    #Regex
    #Domain
    match type:
        #Strict Filter
        case "strict":
            if url == filter:
                return True
        #Regex Filter
        case "regex":
            pattern = re.compile(filter)
            if pattern.match(url):
                return True
        #Domain Filter
        case "domain":
            if f"://{filter}/" in url:
                return True
        #Filter mismatch
        case _:
            print("Unknown Filter type")
    return False

def check_access(ip:str,url:str):
    netgroups = get_netgroups_for_ip(ip)
    contentgroups = get_contentgroups_for_netgroups(netgroups)
    filter = get_filter_for_contentgroups(contentgroups)
    if process_url_in_filters(filter,url):
        return "OK\n"
    else:
        return "ERR\n"

### Begin Logic ###
if __name__ == "__main__":
    init_db()
    while True:
        line = sys.stdin.readline().strip()
        if not line:
            break
        # Split input in ip and url
        parts = line.split(' ')
        client_ip = parts[0]
        url = parts[1]
        # Check access and return output to squid
        result = check_access(client_ip, url)
        sys.stdout.write(result)
        sys.stdout.flush()