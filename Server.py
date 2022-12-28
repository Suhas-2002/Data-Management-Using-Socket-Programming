import socket
import os
import threading
import pandas as pd
from csv import writer
SEPARATOR = "<SEPARATOR>"

cols =  ['movietitle', 'language', 'status', 'releasedate', 'revenue', 'voteaverage']
df = pd.DataFrame(columns=cols)

if (os.stat("Movie_Data.csv").st_size != 0): df = pd.read_csv('Movie_Data.csv')

HOST = socket.gethostname()
PORT = 1234
ADDR = (HOST, PORT)
CHUNK_SIZE = 1024
FORMAT = 'utf-8'

# Initialise socket obj
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# Bind to address
server.bind(ADDR)

def add_row(conn_socket, movietitle,language,status,releasedate,revenue,voteaverage):
    releasedate = pd.to_datetime(releasedate)
    revenue=int(revenue)
    voteaverage=float(voteaverage)
    newrow = [movietitle,language,status,releasedate,revenue,voteaverage]
    with open('Movie_Data.csv', 'a') as f_object:
        writer_object = writer(f_object)
        writer_object.writerow(newrow)
        f_object.close()
    conn_socket.send(b"Added Row to Movie_Data.csv Successfully")


def send_all(conn_socket):
    df=pd.read_csv('Movie_Data.csv')
    df['releasedate'] = pd.to_datetime(df['releasedate'])
    conn_socket.send(df.to_string().encode(FORMAT))

def view_popular(conn_socket):
    df=pd.read_csv('Movie_Data.csv')
    df1=df.sort_values('voteaverage',ascending=False)
    conn_socket.send(df1.to_string().encode(FORMAT))

def update_row(conn_socket,new_rating,movie_to_query):
    df=pd.read_csv('Movie_Data.csv')
    df.set_index("movietitle", inplace=True)
    df.at[movie_to_query, 'voteaverage'] = new_rating
    df.to_csv('Movie_Data.csv')
    conn_socket.send(b"Data updated successfully")

def sort_by_lang(conn_socket, lang):
    df=pd.read_csv('Movie_Data.csv')
    df1=df[df['language']==lang]
    conn_socket.send(df1.to_string().encode(FORMAT))

# Method to serve data to client
def on_new_client(clientsocket,addr,host):
    while True:
        msg = clientsocket.recv(1024).decode()
        args = msg.split(SEPARATOR)
        #print(args)
        if (args[0] == "B"): break
        elif (args[0] == "I"): add_row(clientsocket, args[1], args[2], args[3], args[4],args[5], args[6])
        elif (args[0] == "V"): send_all(clientsocket)
        elif (args[0]=="P"): view_popular(clientsocket)
        elif (args[0]=="U"): update_row(clientsocket,args[1],args[2])
        elif (args[0]=="L"): sort_by_lang(clientsocket,args[1])
    clientsocket.close()

def start():
    # Listen for connections
    server.listen()
    print('[SERVER] Listening on:', ADDR)
    while True:
        conn, addr = server.accept()
        print('client connected',addr)
        thread = threading.Thread(target=on_new_client,args=(conn, addr, HOST))
        thread.start()
        print(f'[ACTIVE CONNECTIONS] {threading.activeCount() - 1}')
print('[SERVER] Starting...')
start()
