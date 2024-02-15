import psycopg2

# Подключение к базе данных
conn = psycopg2.connect(
    host="127.0.0.1",
    port="5432",
    database="bobr_inf",
    user="pan",
    password="bd!!<FPF22lfyys[33"
)
cursor = conn.cursor()

# Создание таблицы
cursor.execute('''CREATE TABLE organizations
                  (id SERIAL PRIMARY KEY,
                  name TEXT,
                  address TEXT,
                  phone TEXT,
                  working_hours TEXT,
                  description TEXT)''')

# Сохранение изменений и закрытие соединения
conn.commit()
conn.close()