import requests
import psycopg2

from psycopg2.extras import execute_values
from bs4 import BeautifulSoup
import schedule
import time

def parse_page():
    try:
        conn = psycopg2.connect(
            host="127.0.0.1",
            database="codeforce",
            user="postgres",
            password="root"
        )
        conn.autocommit = True
        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT version();"
            )
        data = []
        for p in range(1, 86):
            url = f"https://codeforces.com/problemset/page/{p}?order=BY_SOLVED_DESC&locale=ru"

            r = requests.get(url)

            soup = BeautifulSoup(r.text, 'lxml')

            table = soup.find(class_='problems')

            rows = table.find_all("tr")

            for row in rows[1:]:
                cols = row.find_all("td")
                difficulty = cols[3].text.strip()
                name = cols[0].text.strip()
                link = "https://codeforces.com"+cols[1].find("a")["href"]
                category_task = cols[1].find('a').text
                category = cols[1].find_all('a', class_="notice")
                num_p_done = cols[4].text
                temp_num_p_done = " ".join(num_p_done.split())
                data_temp = []
                for z in category:
                    data_temp.append(z.text)

                data.append([data_temp, temp_num_p_done[1:], " ".join(category_task.split()),
                             name, link, difficulty,])
                with conn.cursor() as cursor:
                    cursor.execute(
                        """INSERT INTO code (data_temp, temp_num_p_done, category_task, name, link,difficulty) VALUES (%s, %s, %s, %s, %s, %s)
                        """, (data_temp, temp_num_p_done[1:], " ".join(category_task.split()), name, link, difficulty))
                    print("[INFO] Data was succefully inserted")

        # with conn.cursor() as cursor:
        #     cursor.execute(
        #         """CREATE TABLE code(
        #             data_temp varchar(256),
        #             temp_num_p_done varchar(256),
        #             category_task varchar(256),
        #             name varchar(256) PRIMARY KEY,
        #             link varchar(256),
        #             difficulty varchar(256)
        #             );"""
        #     )
        #     print(f"Server version: {cursor.fetchone()}")

    except Exception as _ex:
        print("[INFO] Error while working with PostgreSQL", _ex)
    finally:
        if conn:
            conn.close()
            print("[INFO] PostgreSQL connection closed")

schedule.every(1).hour.do(parse_page())

while True:
    schedule.run_pending()
    time.sleep(1)


