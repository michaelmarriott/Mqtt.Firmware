var express = require('express');
var bodyParser = require("body-parser");
var cors = require('cors');
const jwt = require("jsonwebtoken");
var { app_config } = require('./config.js');
var database = require('./database.js');

const app = express();
app.use(cors());
app.options('*', cors());

//app.use(logger('dev'));
app.use(bodyParser.json());
app.use(bodyParser.urlencoded({ extended: true }));

const authenticateJWT = (req, res, next) => {
  const authHeader = req.headers.authorization;

  if (authHeader) {
      const token = authHeader.split(' ')[1];
      jwt.verify(token, app_config.tokenKey, (err, data) => {
          if (err) {
              return res.sendStatus(403);
          }
          req.token = data;
          next();
      });
  } else {
      res.sendStatus(401);
  }
};

// respond with "hello world" when a GET request is made to the homepage
app.get('/', function (req, res) {
  console.log("firmware service")
  res.send('firmware service')
})

app.get('/firmware/:deviceid', authenticateJWT, async (req, res) => {
  console.log(`firmware` + req.params.deviceid);
  console.log(req.token);
 // version = database.getVersion(req.token.id)
  res.send({ "version": 2 });
});

app.get('/firmware/:deviceid/:version', authenticateJWT, async (req, res) => {
  console.log(`firmware-version`);
  console.log(req.params.deviceid);
  console.log(req.params.version);
  console.log(req.token);
  if(req.params.version == 2 && req.params.deviceid == "CRPI_0001"){
      const file = `${__dirname}\\firmware\\install.zip`;
      console.log(file);
      res.sendFile(file);
      return
  }else{
    res.sendStatus(400);
  }
});


if (require.main === module) { app.listen(3004); }