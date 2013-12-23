function show_idle() {
    $("#idle").show();
    $("#payment_info").hide();
    $("#payment_received").hide();
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

    $("#idle").hide();
    $("#payment_info").show();
    $("#payment_received").hide();
}

function show_payment_received() {
    $("#idle").hide();
    $("#payment_info").hide();
    $("#payment_received").show();
}
