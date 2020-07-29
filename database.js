var {Pool} = require('pg');
var {database_config} = require('./config.js');

const pool = new Pool(database_config)

const getVersion = async (deviceId) => {
    try {
        var query = `SELECT device_id FROM device
            WHERE username = $1 `
        const { rows } = await pool.query(query, [deviceId]);
        if(rows != null && rows.length > 0){
          return rows[0];
        }
        return null;
    } catch (err) {
        console.error('Database ' + err)
        return null;
    }
}
exports.getVersion = getVersion;