const fs = require('fs');
const config = require('./../config');

class RoutePage {
    
    /**
     * Constructor
     * @param {*} app 
     */
    constructor(app, ref) {
        this.app = app;
        this.settings = ref.settings;
        this.config = ref.config;
        this.auth = ref.auth;
    }

    /**
     * Apply routes
     */
    apply() {
        let ref = this;
        let app = ref.app;
        let refresh_json = async function() {
            let data = false;
            try {
                data = fs.readFileSync(config['locations']['settings']);
                ref.settings = JSON.parse(data);
            } catch (err) {
                console.log(`Error in parsing file ${config['locations']['settings']} -> ${err}`);
            }
        }
        
        // Home Page
        app.get("/", ref.auth.do, async function (req, res) {

            refresh_json();

            res.render("app", {
                settings: ref.settings,
                exchanges: ref.config.exchanges,
            });
        });

        // Non Registered Pages
        app.get("/*", function (req, res) {
            res.redirect("/");
        });
    }

}

module.exports = RoutePage;