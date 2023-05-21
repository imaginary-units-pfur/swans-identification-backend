# .schema
# CREATE TABLE tag (
#   image_id INTEGER NOT NULL,
#   tag_name TEXT NOT NULL
# );
# CREATE TABLE image_data (
#   id INTEGER PRIMARY KEY AUTOINCREMENT ,
#   original_name TEXT NOT NULL,
#   uuid TEXT NOT NULL UNIQUE
#   mute REAL NOT NULL,
#   whooper REAL NOT NULL,
#   bewicks REAL NOT NULL
# );


import sqlite3


def add_image(image_uuid, original_name, analysis, tags: list):
    con = sqlite3.connect("swan_data.db")
    cur = con.cursor()
    cur.execute(
        """
        INSERT INTO image_data (original_name, uuid, mute, whooper, bewicks)
        VALUES (?, ?, ?, ?, ?)
        """,
        (
            original_name,
            image_uuid,
            analysis["шипун"],
            analysis["кликун"],
            analysis["малый"],
        ),
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
        SELECT DISTINCT original_name, uuid, mute, whooper, bewicks
        FROM tag JOIN image_data ON image_data.id = tag.image_id
        WHERE tag.tag_name = ?
    """
            for _ in tags
        ]
    )
    res = cur.execute(q, tags)

    output = res.fetchall()
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
