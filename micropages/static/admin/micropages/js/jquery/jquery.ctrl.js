// http://www.gmarwaha.com/blog/2009/06/16/ctrl-key-combination-simple-jquery-plugin/
(function($) {
    $.ctrl = function(key, callback, args) {
        $(document).bind('keydown', function(e) {
            if(!args) args=[]; // IE barks when args is null
            if(e.keyCode == key.charCodeAt(0) && e.ctrlKey) {
                callback.apply(this, args);
                e.preventDefault();
                return false;
            }
        });
    };
})(jQuery);