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


        // Status
        app.get("/status", ref.auth.do, async function (req, res) {

            let is_running_bitmex = await ref.app_process.is_running('main_bitmex.py');
            let bitmex_messages = await ref.app_process.console_message('bitmex');

            let is_running_binance = await ref.app_process.is_running('main_binance.py');
            let binance_messages = await ref.app_process.console_message('binance');

            let is_running_bybit = await ref.app_process.is_running('main_bybit.py');
            let bybit_messages = await ref.app_process.console_message('bybit');

            let is_running_deribit = await ref.app_process.is_running('main_deribit.py');
            let deribit_messages = await ref.app_process.console_message('deribit');

            res.json({
                'is_running_bitmex': is_running_bitmex,
                'bitmex_messages': bitmex_messages,
                'is_running_binance': is_running_binance,
                'binance_messages': binance_messages,
                'is_running_bybit': is_running_bybit,
                'bybit_messages': bybit_messages,
                'is_running_deribit': is_running_deribit,
                'deribit_messages': deribit_messages,
            })
        });

        // Non Registered Pages
        app.get("/*", function (req, res) {
            res.redirect("/");
        });
    }

}

module.exports = RoutePage;