const basic_auth = require('basic-auth');
const config = require('../config');

class ModuleAuth {
    
    /**
     * Constructor
     */
    constructor() {
    }


    /**
     * Auth - allows only authorized user to use the app
     */
    do(req, res, next) {
        function unauthorized(res) {
            res.set('WWW-Authenticate', 'Basic realm=Authorization Required');
            return res.sendStatus(401);
        };

        var user = basic_auth(req);

        if (!user || !user.name || !user.pass) {
            return unauthorized(res);
        };

        
        let _username = config['credentials']['username'];
        let _password = config['credentials']['password'];

        if (user.name === _username && user.pass === _password) {
            return next();
        } else {
            return unauthorized(res);
        };
    }


}

module.exports = ModuleAuth;