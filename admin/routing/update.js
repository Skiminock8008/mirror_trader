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

        // Update settings
        app.post("/settings/update", ref.auth.do, async function (req, res) {

            // Update shit
            //req.body.shit
            //ref.settings.shit = shit

            let data = false;

            data = JSON.stringify(ref.settings, null, 2);
            try {
                await fs.writeFile(config['locations']['settings'], data, () => {});
            } catch (err) {
                console.log(`/settings/update: err-1 ${err}`);
            }

            res.json({
                'status': 1,
                'message': 'saved',
            });

        });

    }

}

module.exports = RouteUpdate;