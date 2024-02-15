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

# Вставка данных об организации (больница)
cursor.execute("INSERT INTO organizations (name, address, phone, working_hours, description) VALUES (%s, %s, %s, %s, %s)",
               ('Больница', 'ул. Больничная, 1', '+7 123 456-78-90', 'пн-пт 9:00-18:00', 'Описание больницы'))

# Вставка данных об организации (детская больница)
cursor.execute("INSERT INTO organizations (name, address, phone, working_hours, description) VALUES (%s, %s, %s, %s, %s)",
               ('Детская больница', 'ул. Детская, 2', '+7 123 456-78-91', 'пн-пт 8:00-17:00', 'Описание детской больницы'))

# Сохранение изменений и закрытие соединения
conn.commit()
conn.close()