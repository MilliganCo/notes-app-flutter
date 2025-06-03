import mysql.connector
import pandas
import random

mydb = mysql.connector.connect(
  host="localhost",
  user="notes_db",
  password="admin456123",
  database="notes_db_mysql"
)

mycursor = mydb.cursor()

ROWS_COUNT = random.randint(1, 25)

mycursor.execute(f"SELECT * FROM notes ORDER BY RAND() LIMIT {ROWS_COUNT}")

myresult = mycursor.fetchall()

mycursor.close()


df = pandas.DataFrame(myresult)

# Переименование столбцов
df.columns = ['id', 'username', 'text', 'latitude', 'longitude', 'address', 'nearest_metro', 'metro_distance', 'series_id', 'series_order']
df['count'] = ROWS_COUNT


f = open("test_dump.json", "w", encoding="utf-8")
f.write(df.to_json(orient="records", force_ascii=False))
print(f)
f.close()
