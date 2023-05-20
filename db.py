import sqlite3


def add_image_with_tags(image_uuid, tags: list):
    con = sqlite3.connect("swan_data.db")
    cur = con.cursor()
    print(image_uuid)
    cur.execute("INSERT INTO image_data (image_name) VALUES (?)", (image_uuid,))
    image_id = cur.lastrowid
    for tag in tags:
        cur.execute(
            "INSERT INTO tag (image_id, tag_name) VALUES (?, ?)", (image_id, tag)
        )
    con.commit()
