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
        let html = `<div class="client client${pos}_div">`;
        html += ` <input class="client_name" name="settings[bitmex][clients][client${pos}][name]"`;
        html += ` value="Client ${pos}" />`;

        // Label for API KEY
        html += ` <label for="client_bitmex_apikey[client${pos}]">`;
        html += ` Api Key </label>`;
        // Input of API KEY
        html += `<input type="text" id="client_bitmex_apikey[client${pos}]"`;
        html += ` class="client_bitmex_apikey[client${pos}]"`; 
        html += ` name="settings[bitmex][clients][client${pos}][api_key]"`;
        //html += ` value="<%= settings.bitmex.clients.client${pos}.api_key %>"`;
        html += `></input>`

        // Label for API SECRET
        html += `<label for="client_bitmex_apisecret[client${pos}]">`;
        html += " Api Secret </label>";
        // Input of API SECRET
        html += `<input type="text" id="client_bitmex_apisecret[client${pos}]"`;
        html += ` class="client_bitmex_apisecret[client${pos}]"`; 
        html += ` name="settings[bitmex][clients][client${pos}][api_secret]"`;
        //html += ` value="<%= settings.bitmex.clients.client${pos}.api_secret %>"`;
        html += `></input>`

       
        //Button
        html += ` <button class="delete_client delete_bitmex[client${pos}]" `;
        html += `type="button" onclick="return CTX_CLIENT.delete_me(this.className)">`
        html += `Delete me </button>`;

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
        $(`.client${id}_div`).remove();
        
        //Remove from back end
        $.ajax({
            url: "/settings/delete",
            data: {id: id},
            type: "POST",
            cache: false,
            async: true,
            timeout: 30 * 1000
        })
        .fail(function (data, text_status, error_thrown) {
            console.log(error_thrown);
        })
        .done(function (res) {

            messages.push(CTX_TIME.get_time() + " - " + res['message']);

            save_history.empty();
            for (let i in messages) {
                if (messages.length > 3) {
                    messages.shift(i);
                }
                save_history.append(`<span>${messages[i]} &nbsp;</span>`);
                save_history.scrollTop = save_history.scrollHeight;
            }
        });

    }

}