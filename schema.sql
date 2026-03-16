CREATE TABLE IF NOT EXISTS users (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    username   TEXT NOT NULL UNIQUE,
    password   TEXT NOT NULL,
    role       TEXT NOT NULL DEFAULT 'user',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS posts (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    username     TEXT NOT NULL,
    caption      TEXT NOT NULL,
    image_url    TEXT NOT NULL DEFAULT '',
    status       TEXT NOT NULL DEFAULT 'draft',
    likes        INTEGER DEFAULT 0,
    reach        INTEGER DEFAULT 0,
    scheduled_at TEXT,
    media_file   TEXT DEFAULT '',
    media_type   TEXT DEFAULT 'image',
    created_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS profiles (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    username      TEXT NOT NULL DEFAULT 'my_account',
    bio           TEXT DEFAULT '',
    profile_photo TEXT DEFAULT '',
    followers     INTEGER DEFAULT 0,
    following     INTEGER DEFAULT 0,
    is_followed   INTEGER DEFAULT 0
);

CREATE TABLE IF NOT EXISTS hashtags (
    id       INTEGER PRIMARY KEY AUTOINCREMENT,
    post_id  INTEGER NOT NULL,
    tag      TEXT NOT NULL,
    FOREIGN KEY (post_id) REFERENCES posts(id)
);

CREATE TABLE IF NOT EXISTS comments (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    post_id    INTEGER NOT NULL,
    commenter  TEXT NOT NULL,
    body       TEXT NOT NULL,
    type       TEXT NOT NULL DEFAULT 'comment',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (post_id) REFERENCES posts(id)
);

CREATE TABLE IF NOT EXISTS analytics (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    followers     INTEGER NOT NULL,
    following     INTEGER NOT NULL,
    total_posts   INTEGER NOT NULL,
    avg_likes     REAL DEFAULT 0,
    avg_reach     REAL DEFAULT 0,
    recorded_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
