const exchanges = ["bitmex", "binance", "bybit", "verbit"];

let CTX_CLIENT = {

    // Calculate the existing inputs and add +1 to make space for the new one
    // If earlier input has been deleted fill that space first
    count_client: function(exchange) {
        let num_of_clients = $(`input[class*="client_${exchange}_apikey"]`).length;
        for(let i = 1; i <= num_of_clients; i++) {
            if (document.getElementById(`client_${exchange}_apikey[client${i}]`) == null){
                return i;
            }
        }
        return num_of_clients + 1; 
    },

    // Now that we have info we need from count_client, we can generate input html
    generate_html: function(pos, exchange) {
        // Main div
        let html = `<div class="client ${exchange}_client${pos}_div">`;
        html += ` <input class="client_name" name="settings[${exchange}][clients][client${pos}][name]"`;
        html += ` value="Client ${pos}" />`;

        // Label for API KEY
        html += ` <label for="client_${exchange}_apikey[client${pos}]">`;
        html += ` Api Key </label>`;
        // Input of API KEY
        html += `<input type="text" id="client_${exchange}_apikey[client${pos}]"`;
        html += ` class="client_${exchange}_apikey[client${pos}] bp3-input"`; 
        html += ` name="settings[${exchange}][clients][client${pos}][api_key]"`;
        //html += ` value="<%= settings.${exchange}.clients.client${pos}.api_key %>"`;
        html += `></input>`

        // Label for API SECRET
        html += `<label for="client_${exchange}_apisecret[client${pos}]">`;
        html += " Api Secret </label>";
        // Input of API SECRET
        html += `<input type="text" id="client_${exchange}_apisecret[client${pos}]"`;
        html += ` class="client_${exchange}_apisecret[client${pos}] bp3-input"`; 
        html += ` name="settings[${exchange}][clients][client${pos}][api_secret]"`;
        //html += ` value="<%= settings.${exchange}.clients.client${pos}.api_secret %>"`;
        html += `></input>`

       
        //Button
        html += ` <button class="delete_client bp3-button bp3-intent-danger bp3-small"`;
        html += ` id="delete_${exchange}[client${pos}]"`
        html += ` type="button" onclick="return CTX_CLIENT.delete_me(this.id)">`
        html += `X </button>`;

        html += `</div>`

        return html;
    },

    add_html: function(exchange) {
        let html = this.generate_html(this.count_client(exchange), exchange);
        $(`.adder_client_${exchange}`).append(html);

        // Focus on api key field once added
        clicked_btn = $(`.${exchange}_new`);
        all_inputs = clicked_btn.closest("div").find(`input[class*=client_${exchange}_apikey]`);
        last_input = all_inputs.last();

        last_input.focus();

        console.log(last_input);

        return false;
    },

    
    // Append delete button next to each input. It calculates which client its associated with and runs function on it
    delete_me: function(e) {
        let id = e.replace(/\D/g, "");
        let exchange;

        for (const x in exchanges) {
            if (e.includes(exchanges[x])) {
                exchange = exchanges[x];
            }
        }

        //Remove from front end
        $(`.${exchange}_client${id}_div`).remove();
        
        //Remove from back end
        $.ajax({
            url: "/settings/delete",
            data: {id: id, exchange: exchange},
            type: "POST",
            cache: false,
            async: true,
            timeout: 30 * 1000
        })
        .fail(function (data, text_status, error_thrown) {
            console.log(error_thrown);
        })
        .done(function (res) {
            console.log(e);
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