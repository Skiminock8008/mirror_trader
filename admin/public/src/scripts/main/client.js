let CTX_CLIENT = {

    //Calculate the existing inputs and add +1 to make space for the new one
    //If earlier input has been deleted fill that space first
    count_client: function() {
        let inputs_length = $("input[class*='client_bitmex_apikey']").length;
        for(let i = 1; i <= inputs_length; i++) {
            if (document.getElementById("client_bitmex_apikey[client" + i + "]") == null){
                return i;
            }
        }
        return $("input[class*='client_bitmex_apikey']").length + 1; 
    },

    //Now that we have info we need from count_client, we can generate input html
    generate_html: function(pos) {
        // Main div
        let html = `<div class="client client_div${pos}">`;
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
        let html = this.generate_html(this.count_client());
        $(".adder_client_bitmex").append(html);
        return false;
    },

    
    //Append delete button next to each input. It calculates which client its associated with and runs function on it
    delete_me: function(e) {
        let id = e.replace(/\D/g, "");

        //Remove from front end
        $(".client_div" + id).remove();
        
        //Remove from back end
        

        //Delete client from front end and back end in settings.json
        
        //Re-sort the list so if page refresh is made it doesn't crash and there are no missing numbers
    }

}