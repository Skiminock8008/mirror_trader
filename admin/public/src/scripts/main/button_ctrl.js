let messages = [];
let save_history = $(".save_history");

// Ajax Post Template of all form elements
function button_ctrl(source, selector, url, autohide) {

    if (autohide == true) {
        var selector_on = selector.replace('_off_', '_on_');
        var selector_off = selector.replace('_on_', '_off_');

        if (selector.indexOf('_on_') > -1) {
            $(selector_on).hide();
            $(selector_off).show();
        } else {
            $(selector_on).show();
            $(selector_off).hide();
        }
    }

    $(selector).on('click', function (e) {

        e.preventDefault();
        e.stopPropagation();


        var data = {};

        if (typeof source !== 'undefined') {
            data = $(source).serialize();
        }
        
        console.debug(data);

        console.debug('button_ctrl(): ' + source + ' | ' + selector + ' => ' + url);

        $.ajax({
                url: url,
                data: data,
                type: "POST",
                cache: false,
                async: true,
                timeout: 30 * 1000
            })
            .fail(function (data, text_status, error_thrown) {
                console.log(error_thrown);
            })
            .done(function (res) {
                //CTX.check_status();

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
    });
}