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
        this.config = ref.config;
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
        let exchanges = ref.config.exchanges;

        // Update settings
        app.post("/settings/update", ref.auth.do, async function (req, res) {

            //Loop through every exchange (might be bit excessive, can be changed in future)
            for (const x in exchanges) {
                let ex = exchanges[x];

                //Update main api keys if they changed
                let new_client = req.body.settings[ex].main;
                let old_client = ref.settings[ex].main;

                if (new_client.api_key != old_client.api_key) {
                    old_client.api_key = new_client.api_key;
                }
                if (new_client.api_secret != old_client.api_secret) {
                    old_client.api_secret = new_client.api_secret
                }

                for (let i in req.body.settings[ex].clients)  {
                    
                    let w = i.replace(/\D/g, "");
                    let new_client = req.body.settings[ex].clients[i];       
                    let old_client = ref.settings[ex].clients[i];

                    if(old_client == undefined) {
                        ref.settings[ex].clients = {...ref.settings[ex].clients, 
                                                   [i]: {"name": "client" + w, 
                                                                    "api_key": new_client.api_key,
                                                                    "api_secret": new_client.api_secret }}
                      }    else {  
                        if(new_client.api_key != "" || new_client.api_secret != "") {
                            old_client.name = new_client.name;
                            old_client.api_key = new_client.api_key;
                            old_client.api_secret = new_client.api_secret;
                        } else {
                            delete ref.settings[ex].clients[i];
                        }
                    }

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
            let ex = req.body.exchange;
            delete ref.settings[ex].clients["client" + id];

            save();

            res.json({
                'status': 1,
                'message': `Client ${id} deleted`,
            });
        });
    }

}

module.exports = RouteUpdate;