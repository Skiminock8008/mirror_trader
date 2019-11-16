/**
 * Backend for User Interface of Trading Robot
 * Alt accounts on crypto exchanges follow every trade 
 * that master account makes
 * 
 * Author: Uros Tadic (urostadic@gmail.com)
 * 
 */

//  app
const express = require('express');
const app = express();
const body_parser = require('body-parser');

//modules
const auth = require('./modules/auth');

// routes
const route_page = require('./routing/page');
const route_update = require('./routing/update');

//config
const config = require('./config');
const fs = require('fs');

class Master {

    /**
     * CONSTRUCTOR OF CLASS
     */
    constructor() {
        let ref = this;

        app.set("view engine", "ejs");
        app.use(express.static(__dirname + "/public"));
        app.use(body_parser.urlencoded({
            extended: true
        }));

        let data = false;
        try {
            data = fs.readFileSync(config['locations']['settings']);
            ref.settings = JSON.parse(data);
        } catch (err) {
            console.log(`Error in parsing file ${config['locations']['settings']} -> ${err}`);
        }

        // references
        ref.auth = new auth();
        ref.config = config;

        // apply routes
        ref.routes = [];
        ref.routes['page'] = new route_page(app, ref);
        ref.routes['update'] = new route_update(app, ref);
        
        for (let r in ref.routes) {
            let route = ref.routes[r];
            route.apply();
        }
    }

    /**
     * MAIN METHOD
     */
    init() {
        app.listen(3000, function () {
            console.log("Server Booted on http://localhost:3000");
        });
    }
}

let a = new Master();
a.init();