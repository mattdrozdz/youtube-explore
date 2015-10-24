import mysql.connector
from mysql.connector import errorcode

__author__ = 'mateusz'

config = {
  'user': 'root',
  'password': 'root',
  'host': '127.0.0.1',
  'database': 'youtube'
}

try:
    cnx = mysql.connector.connect(**config)
except mysql.connector.Error as err:
    if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
        print("Something is wrong with your user name or password")
    elif err.errno == errorcode.ER_BAD_DB_ERROR:
        print("Database does not exist")
    else:
        print(err)


cursor = cnx.cursor()

add_channel = ("INSERT INTO channel "
               "(channel_id, title, description, published_at, country) "
               "VALUES (%s, %s, %s, %s, %s)")

data_channel = ('test_ch_id2', 'sometitle', 'coolDescription', '1977-6-14 12:12:12', 'Poland')
# insert channel
cursor.execute(add_channel, data_channel)
channel_no = cursor.lastrowid

print(channel_no)


# Make sure data is committed to the database
cnx.commit()

cursor.close()

print 'Closing...'
cnx.close()