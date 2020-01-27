let CTX = {
  routes: [
    {
      selector: ".update_form",
      source: "#data",
      url: "/settings/update",
      autohide: false
    },


     /**
     * Bot controller
     */
    {
      selector: "#turn_on_bitmex",
      url: "/settings/turn_on_bitmex",
      autohide: true
    },

    {
      selector: "#turn_off_bitmex",
      url: "/settings/turn_off_bitmex",
      autohide: true
    },
    {
      selector: "#turn_on_binance",
      url: "/settings/turn_on_binance",
      autohide: true
    },

    {
      selector: "#turn_off_binance",
      url: "/settings/turn_off_binance",
      autohide: true
    },
    {
      selector: "#turn_on_bybit",
      url: "/settings/turn_on_bybit",
      autohide: true
    },

    {
      selector: "#turn_off_bybit",
      url: "/settings/turn_off_bybit",
      autohide: true
    },
    {
      selector: "#turn_on_deribit",
      url: "/settings/turn_on_deribit",
      autohide: true
    },

    {
      selector: "#turn_off_deribit",
      url: "/settings/turn_off_deribit",
      autohide: true
    },
  ],


    is_error: function(msg) {
        let words = msg.split(' ');
        let errors = ['error', 'exception', 'fail', 'api', 'line', 'invalid', 'file', 'traceback'];
        
        let found, targetMap, i, j, cur;
    
        found = false;
        targetMap = {};
        
        // Put all values in the `target` array into a map, where
        //  the keys are the values from the array
        for (i = 0, j = words.length; i < j; i++) {
            cur = words[i].toLowerCase();
            targetMap[cur] = true;
        }
        
        // Loop over all items in the `toMatch` array and see if any of
        //  their values are in the map from before
        for (i = 0, j = errors.length; !found && (i < j); i++) {
            cur = errors[i].toLowerCase();
            found = !!targetMap[cur];
            // If found, `targetMap[cur]` will return true, otherwise it
            //  will return `undefined`...that's what the `!!` is for
        }
        
        return found;
    },  

    check_status_handler: function(data, ex) {
        let is_running = data[`is_running_${ex}`];

        if (is_running) {
            $(`#turn_on_${ex}`).hide();
            $(`#turn_off_${ex}`).show();
            $(`.${ex}_logo`).addClass("active_exchange");
        } else {
            $(`#turn_on_${ex}`).show();
            $(`#turn_off_${ex}`).hide();
            $(`.${ex}_logo`).removeClass("active_exchange");
        }
        $(`#${ex}_console_messages`).empty();
        $(`#${ex}_console_messages`).append(`<span style='color: #b7b7b0'>${ex}-1.0$ </span> <br>`)
        for(let i in data[`${ex}_messages`]) {
            if(CTX.is_error(data[`${ex}_messages`][i])) {
                $(`#${ex}_console_messages`).append(`<span style='color:#e91313'>${data[`${ex}_messages`][i]} <br> </span>`);
            } else {
                $(`#${ex}_console_messages`).append(`<span style='color:#0d8050'>${data[`${ex}_messages`][i]} <br> </span>`);
            }
            $(`#${ex}_console_messages`).scrollTop($(`#${ex}_console_messages`)[0].scrollHeight);
        }
  },

    /**
     * Check if robot is running
     */
    check_status: function () {
        $.ajax({
            type: "GET",
            url: "/status",
            data: {
                get_param: "value"
            },
            dataType: "json",
            success: function (data) {
                for (let i = 0; i < exchanges.length; i++){
                    CTX.check_status_handler(data, exchanges[i]);
                  }
            }
        })
    },

  /**
   * Main method
   */
  run: function() {
    console.debug("run");

    // Modules
    TabSystem.init();

    // Status checker
    CTX.check_status();
    setInterval(function () {
        CTX.check_status();
    }, 5 * 1000);

    $(".turning_button").on('click', function() {
        CTX.check_status();
    })


    // Message on stop
    $('[id*="turn_off"]').on('click', function(e) {

        e.preventDefault();

        let id = e.target.id;
        let exchange;

        for (const x in exchanges) {
            if (id.includes(exchanges[x])) {
                exchange = exchanges[x];
            }
        }

        messages.push(CTX_TIME.get_time() + " - " + `Shutting down ${exchange} bot...`);

        save_history.empty();
        for (let i in messages) {
            if (messages.length > 3) {
                messages.shift(i);
            }
            save_history.append(`<span>${messages[i]} &nbsp;</span>`);
            save_history.scrollTop = save_history.scrollHeight;
        }
    })


    // Routing
    for (var r in CTX["routes"]) {
        var aobj = CTX["routes"][r];
  
        var selector = aobj["selector"];
        var url = aobj["url"];
        var autohide = aobj["autohide"];
  
        var source = "";
        if (typeof aobj["source"] != "undefined") {
          source = aobj["source"];
        }
        console.debug(source + " | " + selector + " => " + url);
        button_ctrl(source, selector, url, autohide);
      }
  },


};

CTX.run();
