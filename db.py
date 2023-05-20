import sqlite3


def add_image(image_uuid, original_name, tags: list):
    con = sqlite3.connect("swan_data.db")
    cur = con.cursor()
    cur.execute(
        "INSERT INTO image_data (original_name, uuid) VALUES (?, ?)",
        (original_name, image_uuid),
    )
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
        SELECT DISTINCT uuid
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


def get_tags(uuid):
    con = sqlite3.connect("swan_data.db")
    cur = con.cursor()
    res = cur.execute(
        """
        SELECT tag_name FROM tag
        JOIN image_data ON tag.image_id = image_data.id
        WHERE image_data.uuid = ?
        """,
        (uuid,),
    )
    output = [item for t in res.fetchall() for item in t]
    con.close()
    return output


def get_filename(uuid):
    con = sqlite3.connect("swan_data.db")
    cur = con.cursor()
    res = cur.execute(
        """
        SELECT original_name FROM image_data
        WHERE image_data.uuid = ?
        """,
        (uuid,),
    )
    output = res.fetchone()[0]
    con.close()
    return output


def delete_by_uuid(uuid):
    con = sqlite3.connect("swan_data.db")
    cur = con.cursor()
    res = cur.execute("SELECT id FROM image_data WHERE uuid = ?", (uuid,))
    id = res.fetchone()[0]
    cur.execute("DELETE FROM image_data WHERE id = ?", (id,))
    cur.execute("DELETE FROM tag WHERE image_id = ?", (id,))
    con.commit()
    con.close()


def update(uuid, tags):
    con = sqlite3.connect("swan_data.db")
    cur = con.cursor()
    res = cur.execute("SELECT id FROM image_data WHERE uuid = ?", (uuid,))
    id = res.fetchone()[0]

    cur.execute("DELETE FROM tag where image_id = ?", (id,))
    for tag in tags:
        cur.execute("INSERT INTO tag (image_id, tag_name) VALUES (?, ?)", (id, tag))

    con.commit()
    con.close()
