baseURL = 'http://localhost'
servers = {5000}

def addServer( port) :
    servers.add(port)

def removeServer( port) :
    servers.remove(port)

def get_all_servers() :
    return servers