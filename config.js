const database_config = {
  user: 'postgres', // env var: PGUSER
  database: 'mqqtdb', // env var: PGDATABASE
  password: 'R3dDr@g0nP', // env var: PGPASSWORD
  host: 'localhost', // Server hosting the postgres database
  port: 5433, // env var: PGPORT
  max: 10, // max number of clients in the pool
  idleTimeoutMillis: 30000 // how long a client is allowed to remain idle before being closed
}
exports.database_config = database_config;

const app_config = {
  client_ids:["6820da21-b47a-46bc-903c-f30435b18907"],
  tokenKey:"sd3djghhhhuuwiwuewieuwieur"
}
exports.app_config = app_config;