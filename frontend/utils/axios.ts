import Axios from "axios";

function getCookie(cname) {
    var name = cname + "=";
    var decodedCookie = decodeURIComponent(document.cookie);
    var ca = decodedCookie.split(';');
    for(var i = 0; i <ca.length; i++) {
        var c = ca[i];
        while (c.charAt(0) == ' ') {
            c = c.substring(1);
        }
        if (c.indexOf(name) == 0) {
            return c.substring(name.length, c.length);
        }
    }
    return "";
}

let instance = Axios.create({
    baseURL: window.location.origin,
    timeout: 100000,
    headers: {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + getCookie('access_token')
    }
});

export default instance;