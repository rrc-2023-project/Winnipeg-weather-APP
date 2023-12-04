#db
import sqlite3

import matplotlib.pyplot as plt
import datetime

db_name="weather_project.sqlite"

conn = sqlite3.connect(db_name)
cursor = conn.cursor()

# get 2023 11 1~30 data
cursor.execute('SELECT * FROM weather_daily WHERE year = 2023 AND month = 10')
rows = cursor.fetchall()
print(rows)

# draw graph
# X axis: day
# Y axis: Max, Min, Mean

x = []
y_max = []
y_min = []
y_mean = []

for row in rows:
    x.append(datetime.date(row[1], row[2], row[3]))
    y_max.append(row[4])
    y_min.append(row[5])
    y_mean.append(row[6])

plt.plot(x, y_max, label='Max')
plt.plot(x, y_min, label='Min')
plt.plot(x, y_mean, label='Mean')

plt.xlabel('day')
plt.ylabel('Temperature')
plt.title('Weather in 2023 10')

plt.show()






