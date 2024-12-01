from pymilvus import connections, utility

connections.connect("default", host="localhost", port="19530")
collections = utility.list_collections()
print(collections)
