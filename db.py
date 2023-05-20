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
    con.close()


def get_by_tags(tags: list):
    con = sqlite3.connect("swan_data.db")
    cur = con.cursor()

    q = "INTERSECT".join(
        [
            """
        SELECT DISTINCT image_name
        FROM tag JOIN image_data ON image_data.id = tag.image_id
        WHERE tag.tag_name = ?
    """
            for _ in tags
        ]
    )
    res = cur.execute(q, tags)

    # flattening list containing tuples of one element each
    # black magic
    output = [item for t in res.fetchall() for item in t]

    con.close()
    return output
