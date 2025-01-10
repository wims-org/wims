// Create the database

db.createCollection("items")
db.items.createIndex( { "tag_uuid": 1 }, { unique: true } )
