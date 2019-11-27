
class RoutePage {
    
    /**
     * Constructor
     * @param {*} app 
     */
    constructor(app, ref) {
        this.app = app;
        this.settings = ref.settings;
        this.config     = ref.config;
        this.auth = ref.auth;
    }

    /**
     * Apply routes
     */
    apply() {
        let ref = this;
        let app = ref.app;
        
        // Home Page
        app.get("/", ref.auth.do, async function (req, res) {

            let bitmex_clients = Object.keys(ref.settings.bitmex.clients).length;

            res.render("app", {
                settings: ref.settings,
                bmx_clients: bitmex_clients
            });
        });

        // Non Registered Pages
        app.get("/*", function (req, res) {
            res.redirect("/");
        });
    }

}

module.exports = RoutePage;