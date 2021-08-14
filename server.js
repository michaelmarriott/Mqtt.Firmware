"use strict";

var app = require("./app.js");

require("greenlock-express")
    .init({
        packageRoot: __dirname,

        // contact for security and critical bug notices
        configDir: "./greenlock.d",
        maintainerEmail: 'michaelm@coderworx.co.za',
        // whether or not to run at cloudscale
        cluster: false
    })
    // Serves on 80 and 443
    // Get's SSL certificates magically!
    .serve(app);