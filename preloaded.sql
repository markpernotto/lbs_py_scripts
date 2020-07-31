--
-- File generated with SQLiteStudio v3.2.1 on Fri Jul 31 14:22:45 2020
--
-- Text encoding used: UTF-8
--
PRAGMA foreign_keys = off;
BEGIN TRANSACTION;

-- Table: inventory
CREATE TABLE inventory (
    itemID       INTEGER PRIMARY KEY
                         NOT NULL,
    description  TEXT,
    title        TEXT,
    author       TEXT,
    storeQty     INTEGER DEFAULT (0),
    reorderPoint INTEGER,
    reorderLevel INTEGER,
    price        REAL    DEFAULT (0.0),
    threeMonth   INTEGER DEFAULT (0),
    sixMonth     INTEGER DEFAULT (0),
    twelveMonth  INTEGER DEFAULT (0),
    isbnList     TEXT,
    category     TEXT,
    subcategory1 TEXT,
    subcategory2 TEXT,
    cost         REAL    DEFAULT (0.0),
    warehouseQty INTEGER DEFAULT (0),
    systemSku    TEXT,
    createTime   TEXT,
    updateTime   TEXT
);


COMMIT TRANSACTION;
PRAGMA foreign_keys = on;
