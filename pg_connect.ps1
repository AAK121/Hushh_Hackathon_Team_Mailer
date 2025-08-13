# Load PostgreSQL environment variables
$env:PGUSER = "postgres"
$env:PGPASSWORD = "postgres"
$env:PGHOST = "localhost"
$env:PGPORT = "5432"
$env:PGDATABASE = "relationship_memory"

# Test the connection
psql -c "\conninfo"
