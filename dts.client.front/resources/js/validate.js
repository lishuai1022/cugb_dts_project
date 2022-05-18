!function () {
    $.extend($.fn.validatebox.defaults.rules, {
        minLength: {
            validator: function(value, param){
                return value.length >= param[0];
            },
            message: '输入长度不能小于{0}'
        }
    });
    $.extend($.fn.validatebox.defaults.rules, {
        maxLength: {
            validator: function(value, param){
                return value.length <= param[0];
            },
            message: '输入长度不能大于{0}'
        }
    });
    $.extend($.fn.validatebox.defaults.rules, {
        maxNumber: {
            validator: function(value, param){
                return value <= param[0];
            },
            message: '输入值不能大于{0}'
        }
    });
    $.extend($.fn.validatebox.defaults.rules, {
        minNumber: {
            validator: function(value, param){
                return value > param[0];
            },
            message: '输入值不能小于{0}'
        }
    });
    $.extend($.fn.validatebox.defaults.rules, {
        range: {
            validator: function(value, param){
                return value >=param[0]&&value<=param[1];
            },
            message: '输入值需要在{0}至{1}之间'
        }
    });
    $.extend($.fn.validatebox.defaults.rules, {
        limitLength: {
            validator: function(value, param){
                return value.length==param[0];
            },
            message: '输入值必须为{0}位'
        }
    });

}();