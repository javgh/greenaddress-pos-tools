function show_idle() {
    transition_to("#idle");
}

function show_payment_info(amount, conversion, address, imgdata) {
    $("#address").text(address);
    $("#qrcode").attr("src", imgdata);

    if (conversion == -1) {
        $("#amount").text(amount);
        $("#detail_table").hide();
    } else {
        $("#amount").text(amount + " | " + conversion[0])
        $("#rate").text(conversion[1]);
        $("#source").text(conversion[2]);
        $("#detail_table").show();
    }

    transition_to("#payment_info");
}

function show_payment_received() {
    transition_to("#payment_received");
}

function transition_to(replacement_div) {
    $(active_div).fadeOut("fast", function() {
        $(replacement_div).fadeIn("fast");
    });
    active_div = replacement_div;
}

var active_div = "#idle";
