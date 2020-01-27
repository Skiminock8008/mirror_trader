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
        this.app_process = ref.app_process;
    }

    /**
     * Apply routes
     */
    apply() {
        let ref = this;
        let app = ref.app;
        let exchanges = ref.config.exchanges;
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
                exchanges: exchanges,
            });
        });


        // Status
        app.get("/status", ref.auth.do, async function (req, res) {

            let is_running = [];
            let ex_messages = [];
            let res_object = {}

            let is_running_values = [];
            let ex_messages_values = [];

            //Get variable names
            exchanges.forEach(exchange => {
                is_running.push(`is_running_${exchange}`);
                ex_messages.push(`${exchange}_messages`);
            })

            //Get the values
            for (let i = 0; i < exchanges.length; i++){
                is_running_values.push(await ref.app_process.is_running(`main_${exchanges[i]}`));
                ex_messages_values.push(await ref.app_process.console_message(`${exchanges[i]}`));
            }

            //Create response object
            for(let i in exchanges) {
                res_object[`is_running_${exchanges[i]}`] = is_running_values[i];
                res_object[`${exchanges[i]}_messages`] = ex_messages_values[i];
            }

            res.json({
                ...res_object
            })
        });

        // Non Registered Pages
        app.get("/*", function (req, res) {
            res.redirect("/");
        });
    }

}

module.exports = RoutePage;