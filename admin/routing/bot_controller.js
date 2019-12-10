
class RouteBotController {

    /**
     * Constructor
     * @param {*} app 
     */
    constructor(app, ref) {
        this.app = app;
        this.app_process = ref.app_process;
        this.auth = ref.auth;
    }


    /**
     * Apply routes
     */
    apply() {
        let ref = this;
        let app = ref.app;
        ref.app_process = this.app_process;

        /**
         * Turn on/off bitmex bot
         */
        app.post("/settings/turn_on_bitmex", ref.auth.do, async function (req, res) {
            console.log(`/settings/turn_on_bitmex/`);

            let result = await ref.app_process.start('main_account.py', 'bitmex');

            let message = '';
            if (result == true) {
                message = 'Bitmex bot is online.';
            } else {
                message = 'Failed to start. Contact support!';
            }

            res.json({
                'result': result,
                'message': message,
            });
        });

        app.post("/settings/turn_off_bitmex", ref.auth.do, async function (req, res) {
            console.log(`/settings/turn_off_bitmex/`);

            let result = await ref.app_process.stop('main_account.py');
            let is_running_bitmex = await ref.app_process.is_running('main_account.py');
            
            let message = '';
            if (result == true) {
                message = 'Bitmex bot is offline.';
            } else {
                message = 'Failed to stop. Contact support!';
            }

            if(is_running_bitmex == false) {
            res.json({
                'result': result,
                'message': message,
            });
            }

        });

    }

}

module.exports = RouteBotController;