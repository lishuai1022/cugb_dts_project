$(document).ready(function () {
    var titleBar = $('.title-bar');
    if(window.navigator.userAgent.indexOf('Electron')!=-1){
        var url= window.location.href;
        if(url.indexOf('iframe')!=-1){
            titleBar.hide();
        }else{
            if(!window.isMac()){
                titleBar.height(50);
            }
            titleBar.show();
        }

    }else{
        titleBar.hide();
    }
})
