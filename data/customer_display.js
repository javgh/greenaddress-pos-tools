function show_idle() {
    $("#idle").show();
    $("#payment_info").hide();
    $("#payment_received").hide();
}

function show_payment_info(amount, conversion, address, imgdata) {
    $("#amount").text(amount);
    $("#conversion").text(conversion);
    $("#address").text(address);
    $("#qrcode").attr("src", imgdata)

    $("#idle").hide();
    $("#payment_info").show();
    $("#payment_received").hide();
}

function show_payment_received() {
    $("#idle").hide();
    $("#payment_info").hide();
    $("#payment_received").show();
}
