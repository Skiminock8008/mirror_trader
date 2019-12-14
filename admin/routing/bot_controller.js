
class RouteBotController {

    /**
     * Constructor
     * @param {*} app 
     */
    constructor(app, ref) {
        this.app = app;
        this.app_process = ref.app_process;
        this.auth = ref.auth;
        this.config = ref.config;
    }


    /**
     * Apply routes
     */
    apply() {
        let ref = this;
        let app = ref.app;
        ref.app_process = this.app_process;
        let exchanges = ref.config.exchanges;


        for (let i = 0; i < exchanges.length; i++){
            turn_on_route(i);
            turn_off_route(i);
        }

        function turn_on_route (i){
            app.post(`/settings/turn_on_${exchanges[i]}`, ref.auth.do, async function (req, res) {
                console.log(`/settings/turn_on_${exchanges[i]}/`);
    
                let result = await ref.app_process.start('main_account.py', exchanges[i]);
    
                let message = '';
                if (result == true) {
                    message = `${exchanges[i]} bot is online.`;
                } else {
                    message = 'Failed to start. Contact support!';
                }
    
                res.json({
                    'result': result,
                    'message': message,
                });
            });
        }

        function turn_off_route (i) {
            app.post(`/settings/turn_off_${exchanges[i]}`, ref.auth.do, async function (req, res) { 
                console.log(`/settings/turn_off_${exchanges[i]}/`);
    
                let result = await ref.app_process.stop('main_account.py');
                
                let message = '';
                if (result == true) {
                    message = `${exchanges[i]} bot is offline.`;
                } else {
                    message = 'Failed to stop. Contact support!';
                }
    
                setTimeout(function(){
                res.json({
                    'result': result,
                    'message': message,
                });
                },5000);
            });
        }

    }

}

module.exports = RouteBotController;