let CTX_CLIENT = {

    //Calculate the existing inputs and add +1 to make space for the new one
    count_client: function() {
        console.log("run");
        return $("input[class*='client_bitmex_apikey']").length + 1;
    },

    //Now that we have info we need from count_client, we can generate input html
    generate_html: function(pos) {
        // Main div
        let html = `<div class="client client_div${pos}">`
        html += ` <input class="client_name" name="settings[bitmex][clients][client${pos}][name]"`;
        html += ` value="Client ${pos}"`;

        // Label for API KEY
        html += ` <label for="client_bitmex_apikey[client${pos}]">`;
        html += " Api Key </label> &nbsp";
        // Input of API KEY
        html += `<input type="text" id="client_bitmex_apikey[client${pos}]"`;
        html += ` class="client_bitmex_apikey[client${pos}]"`; 
        html += ` name="settings[bitmex][clients][client${pos}][api_key]"`;
        //html += ` value="<%= settings.bitmex.clients.client${pos}.api_key %>"`;
        html += `></input>`

        // Label for API SECRET
        html += `<label for="client_bitmex_apisecret[client${pos}]">`;
        html += " Api Secret </label> &nbsp";
        // Input of API SECRET
        html += `<input type="text" id="client_bitmex_apisecret[client${pos}]"`;
        html += ` class="client_bitmex_apisecret[client${pos}]"`; 
        html += ` name="settings[bitmex][clients][client${pos}][api_secret]"`;
        //html += ` value="<%= settings.bitmex.clients.client${pos}.api_secret %>"`;
        html += `></input>`

        html += `</div>`

        return html;
    },

    add_html: function() {
        console.log("added");
        let html = this.generate_html(this.count_client());
        $(".adder_client_bitmex").append(html);
        return false;
    }

    
    //Append delete button next to each input. It deletes input and the label and removes them from settings.json

}