
source .env

psql -h $DB_HOST -U $DB_USER -d $DB_NAME -p $DB_PORT -f schema.sql

echo "Database build complete using schema.sql file."