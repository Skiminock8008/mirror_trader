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

            for (const x in exchanges) {
                let ex = exchanges[x];

                ref.settings[ex].main.api_key = req.body.settings[ex].main.api_key;
                ref.settings[ex].main.api_secret = req.body.settings[ex].main.api_secret;
    
                let clients = Object.keys(req.body.settings[ex].clients).length;
                  
                for(let i = 1; i <= clients; i++) {
                  if(ref.settings[ex].clients["client" + i] == undefined) {
                    ref.settings[ex].clients = {...ref.settings[ex].clients, 
                                               ["client" + i]: {"name": ["client" + i], 
                                                                "api_key": "",
                                                                "api_secret": "" }}
                  }  
                    if(req.body.settings[ex].clients["client" + i].api_key != "") {
                    ref.settings[ex].clients["client" + i].name = req.body.settings[ex].clients["client" + i].name;
                    ref.settings[ex].clients["client" + i].api_key = req.body.settings[ex].clients["client" + i].api_key;
                    ref.settings[ex].clients["client" + i].api_secret = req.body.settings[ex].clients["client" + i].api_secret;
                    } else {
                        delete ref.settings[ex].clients["client" + i];
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