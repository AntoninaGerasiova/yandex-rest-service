DROP TABLE IF EXISTS citizens;
DROP TABLE IF EXISTS kinship;

CREATE TABLE citizens (
    import_id INTEGER NOT NULL,
    citizen_id INTEGER NOT NULL,
    town TEXT NOT NULL,
    street TEXT NOT NULL,
    building TEXT NOT NULL,
    appartement int NOT NULL,
    name TEXT NOT NULL,
    birth_date DATE NOT NULL,
    gender TEXT NOT NULL,
    PRIMARY KEY (import_id, citizen_id)
);

CREATE TABLE kinship (
    import_id INTEGER NOT NULL,
    citizen_id INTEGER NOT NULL,
    relative_id INTEGER NOT NULL,
    PRIMARY KEY (import_id, citizen_id, relative_id)
);
