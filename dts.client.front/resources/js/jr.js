if (typeof Object.assign != 'function') {
    Object.assign = function(target) {
        'use strict';
        if (target == null) {
            throw new TypeError('Cannot convert undefined or null to object');
        }

        target = Object(target);
        for (var index = 1; index < arguments.length; index++) {
            var source = arguments[index];
            if (source != null) {
                for (var key in source) {
                    if (Object.prototype.hasOwnProperty.call(source, key)) {
                        target[key] = source[key];
                    }
                }
            }
        }
        return target;
    };
}
(function () {
    window.isMac = function() {
        return /macintosh|mac os x/i.test(navigator.userAgent);
    };
    window.getIEVersion = function () {
        // 取得浏览器的userAgent字符串
        var userAgent = navigator.userAgent;
        // 判断是否为小于IE11的浏览器
        var isLessIE11 = userAgent.indexOf('compatible') > -1 && userAgent.indexOf('MSIE') > -1;
        // 判断是否为IE的Edge浏览器
        var isEdge = userAgent.indexOf('Edge') > -1 && !isLessIE11;
        // 判断是否为IE11浏览器
        var isIE11 = userAgent.indexOf('Trident') > -1 && userAgent.indexOf('rv:11.0') > -1;
        if (isLessIE11) {
            var IEReg = new RegExp('MSIE (\\d+\\.\\d+);');
            // 正则表达式匹配浏览器的userAgent字符串中MSIE后的数字部分，，这一步不可省略！！！
            IEReg.test(userAgent);
            // 取正则表达式中第一个小括号里匹配到的值
            var IEVersionNum = parseFloat(RegExp['$1']);
            if (IEVersionNum === 7) {
                // IE7
                return 7
            } else if (IEVersionNum === 8) {
                // IE8
                return 8
            } else if (IEVersionNum === 9) {
                // IE9
                return 9
            } else if (IEVersionNum === 10) {
                // IE10
                return 10
            } else {
                // IE版本<7
                return 6
            }
        } else if (isEdge) {
            // edge
            return 'edge'
        } else if (isIE11) {
            // IE11
            return 11
        } else {
            // 不是ie浏览器
            return -1
        }
    }

    var checkIEVersion = function(){
        console.log(window.navigator.userAgent);
        var ieVersion = this.getIEVersion();
        if(ieVersion!=-1 && ieVersion<9){
            alert('当前IE版本为'+ieVersion+'，请更换大于IE8的版本。建议更换为谷歌或火狐浏览器，体验会更佳！')
        }
    };
    checkIEVersion();
})();
