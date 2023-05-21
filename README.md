# swans-identification-backend

Server to analyze images and store them in the archive

Weights should be stored in ./checkpoints/ and can be downloaded via link - https://drive.google.com/file/d/1p58HWvVsYd94MhV7WcnRpKxvev4dEUov/view?usp=share_link

To run use `docker compose up`

The program expects ro find `swan_data.db` SQLite3 DataBase with the following schema:

```
CREATE TABLE tag (
  image_id INTEGER NOT NULL,
  tag_name TEXT NOT NULL
);
CREATE TABLE image_data (
  id INTEGER PRIMARY KEY AUTOINCREMENT ,
  original_name TEXT NOT NULL,
  uuid TEXT NOT NULL UNIQUE
  mute REAL NOT NULL,
  whooper REAL NOT NULL,
  bewicks REAL NOT NULL
);

```
