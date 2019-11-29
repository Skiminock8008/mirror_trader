const fs = require('fs');
const config = require('./../config');

class RouteUpdate {

    /**
     * Constructor
     * @param {*} app 
     */
    constructor(app, ref) {
        this.app = app;
        this.settings = ref.settings;
        this.auth = ref.auth;
    }


    /**
     * Apply routes
     */
    apply() {
        let ref = this;
        let app = ref.app;
        let save = async function() {
            let data = false;

            data = JSON.stringify(ref.settings, null, 2);
            try {
                await fs.writeFile(config['locations']['settings'], data, () => {});
            } catch (err) {
                console.log(`/settings/update: err-1 ${err}`);
            }
        };

        // Update settings
        app.post("/settings/update", ref.auth.do, async function (req, res) {

            //Bitmex
            ref.settings.bitmex.main.api_key = req.body.settings.bitmex.main.api_key;
            ref.settings.bitmex.main.api_secret = req.body.settings.bitmex.main.api_secret;

            let bitmex_clients = Object.keys(req.body.settings.bitmex.clients).length;
            
            for(let i = 1; i <= bitmex_clients; i++) {
              if(ref.settings.bitmex.clients["client" + i] == undefined) {
                ref.settings.bitmex.clients = {...ref.settings.bitmex.clients, 
                                           ["client" + i]: {"name": ["client" + i], 
                                                            "api_key": "",
                                                            "api_secret": "" }}
              }  
                if(req.body.settings.bitmex.clients["client" + i].api_key != "") {
                ref.settings.bitmex.clients["client" + i].name = req.body.settings.bitmex.clients["client" + i].name;
                ref.settings.bitmex.clients["client" + i].api_key = req.body.settings.bitmex.clients["client" + i].api_key;
                ref.settings.bitmex.clients["client" + i].api_secret = req.body.settings.bitmex.clients["client" + i].api_secret;
                } else {
                    delete ref.settings.bitmex.clients["client" + i];
                }
            }

            save();

            res.json({
                'status': 1,
                'message': 'Saved',
            });

        });
        
        app.post("/settings/delete", ref.auth.do, async function (req, res) {
            let id = req.body.id;
            delete ref.settings.bitmex.clients["client" + id];

            save();

            res.json({
                'status': 1,
                'message': `Client ${id} deleted`,
            });
        });
    }

}

module.exports = RouteUpdate;