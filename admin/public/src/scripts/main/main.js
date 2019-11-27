let CTX = {
  routes: [
    {
      selector: ".update_form",
      source: "#data",
      url: "/settings/update",
      autohide: false
    },

    {
      selector: "#turn_on_bot",
      url: "/settings/turn_on_bot",
      autohide: true
    },

    {
      selector: "#turn_off_bot",
      url: "/settings/turn_off_bot",
      autohide: true
    }
  ],



  /**
   * Main method
   */
  run: function() {
    console.debug("run");

    // Modules
    TabSystem.init();

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
