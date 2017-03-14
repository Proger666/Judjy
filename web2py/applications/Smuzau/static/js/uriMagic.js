/**
 * Created by Scorpa on 3/14/2017.
 */
function removeParam(name, value) {
        var newUrl = window.location.href.split("?")[0],
                sourceURL = window.location.href,
        param,
        params_arr = [],
        queryString = (sourceURL.indexOf("?") !== -1) ? sourceURL.split("?")[1] : "";
    if (queryString !== "") {
        params_arr = queryString.split("&");
        for (var i = params_arr.length - 1; i >= 0; i -= 1) {
            param = params_arr[i].split("&")[0];
            if (param.indexOf(name) !== -1) {
                if (params_arr[i].indexOf("%s") !== -1) {
                    params_arr[i] = param.replace("%s" + value , "");
                }
                else {
                    params_arr[i] = param.replace(name + "=" + value, "");
                }
                if (params_arr[i].indexOf(value) !== -1 ){
                    params_arr[i] = param.replace(value + "%s", "");
                }
            }
        }
        if (params_arr[0] !== "") {
            newUrl = newUrl + "?" + params_arr.join("&");
        }

    }
    window.history.pushState(null,"", newUrl);
}

    function addQSParam(name, value) {
    var url=window.location.href,
    separator = (url.indexOf("?")===-1)?"?":"%s";
        if (!(url.indexOf(name) ==-1)) {
           newParam=separator + value;
           newUrl=url.replace(newParam,"");
           newUrl+=newParam;
        }
        else {
        newParam=separator + name + '=' + value;
    newUrl=url.replace(newParam,"");
    newUrl+=newParam;
        }
    window.history.pushState(null,"", newUrl);
    }
