function gmailAuthenticate() {
    $.ajax({
        type: "GET",
        url: "{% url 'gmail_authenticate' %}",
        success: function (data) {
            console.log('Authentication initiated');
        }
    });
}
