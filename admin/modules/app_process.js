const child_process = require('child_process');


class ModuleAppProcess {

    constructor() {
    }

    /**
     * Find pid of process
     */
    find_pids(name) {
        let ref = this;

        let results = [];

        return new Promise((resolve, reject) => {

            let cmd = [
                'ps',
                'ejfax',
            ];

            cmd = cmd.join(' ');
            
            let opts = {
                maxBuffer: 150 * 1024 * 1024,
            }

            child_process.exec(cmd, opts, (error, stdout, stderr) => {

                let data = stdout;
                data = data.toString('utf-8');
                data = data.split('\n');
                

                for (let d in data) {
                    let row = data[d];
                    row = row.toLowerCase();
                    while (row.indexOf('\t') > -1) {
                        row = row.replace('\t', ' ');
                    }

                    while (row.indexOf('  ') > -1) {
                        row = row.replace('  ', ' ');
                    }


                    
                    if (row.indexOf(name) > -1) {
                        row = row.split(' ');
                        let pid = row[2];

                        pid = parseInt(pid);
                        results.push(pid);
                    }
                }

                resolve(results);
            });
        });
    }


    /**
     * Find children pids of pid
     */
    find_children_pids(name) {
        let ref = this;

        let results = [];

        return new Promise((resolve, reject) => {

            let cmd = [
                'pstree',
                '-pn',
                name,
            ];


            cmd = cmd.join(' ');
            console.log(cmd);
            //process.exit(1);

            let opts = {
                maxBuffer: 15 * 1024 * 1024,
            }

            child_process.exec(cmd, opts, (error, stdout, stderr) => {

                let data = stdout;
                data = data.toString('utf-8');
                data = data.replace('\r', ' ');
                data = data.replace('\n', ' ');
                data = data.replace('\t', ' ');
                data = data.replace('─', ' ')
                data = data.replace('┬', ' ')

                data = data.split(' ');
                

                for (let d in data) {
                    let row = data[d];
                    row = row.toLowerCase();
                    while (row.indexOf('\t') > -1) {
                        row = row.replace('\t', ' ');
                    }

                    while (row.indexOf('  ') > -1) {
                        row = row.replace('  ', ' ');
                    }


                    
                    try {
                        row = row.split('(')[1];
                        if (typeof row === 'undefined') {
                            continue;
                        }
                        row = row.split(')')[0];
    
                        let pid = row;
                        pid = parseInt(pid);
                        results.push(pid);

                    } catch(err) {
                        console.debug(err);
                    }
                }

                resolve(results);
            });
        });
    }



    /**
     * Kill exact pid
     * @param {*} pid 
     */
    async kill(pid) {
        //console.log(`kill(${pid})`);

        try {
            await process.kill(pid, 9);
        } catch(err) {
            //console.log(`kill(${pid}): ${JSON.stringify(err)}`);
        }
        return true;
    }


    /**
     * Check is it running or not
     */
    async is_running(name) {
        let ref = this;

        let pids = await ref.find_pids(name);
        
        if (pids.length == 0) {
            return false;
        } else {
            return true;
        }
    }



    /**
     * Stop process
     */
    async stop(name) {
        let ref = this;

        let pids = await ref.find_pids(name);

        for (let p in pids) {
            let pids_children = await ref.find_children_pids(pids[p]);

            console.debug(`pids[p] = ${JSON.stringify(pids[p])}`);
            console.debug(`pids_children = ${JSON.stringify(pids_children)}`);

            for (let pp in pids_children) {
                ref.kill(pids_children[pp]);
            }
        }

        for (let p in pids) {
            ref.kill(pids[p]);
        }


        return true;
    }

    /**
     * Start process
     */
    async start(name, exchange) {
        let ref = this;

        try {
            let args = [
                __dirname + `/../../engine/${exchange}/` + name,
            ];
            
            console.log(args);

            const ls = child_process.spawn('/usr/bin/python3', args, {
                detached: true
            });


            ls.on('error', (err) => {
                console.log(`${err}`);
            });

            ls.stdout.on('data', (data) => {
                //console.log(`stdout: ${data}`);
            });

            ls.stderr.on('data', (data) => {
                console.log(`stderr: ${data}`);
            });

            ls.on('close', (code) => {
                console.log(`child process exited with code ${code}`);
            });

        } catch (err) {
            console.log(`robot_controller: start(): ${err}`);
        }
        return true;
    }

}


module.exports = ModuleAppProcess;


// if (process.argv.length >= 3) {
//     async function a() {
//         let p = new ModuleAppProcess();

//         let res = await p.is_running('crawler.py');
//         if (res == true) {
//             console.log(`It is running!`);
//             await p.stop();
//             process.exit(0);
//         } else {
//             console.log(`No :(`);
//             //await p.start('crawler.py');
//             process.exit(0);
//         }
//     }

//     a();
// }