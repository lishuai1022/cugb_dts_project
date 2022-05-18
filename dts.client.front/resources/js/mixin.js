!function(){
    window.COMMON_DATA = {
        statusPersistTime: [
            {text: '10秒', value: 10, select: true},
            {text: '20秒', value: 20},
            {text: '30秒', value: 30}
        ],
        timerList: [
            {text: '3秒', value: 3, select: true},
            {text: '5秒', value: 5},
            {text: '10秒', value: 10},
            {text: '15秒', value: 15},
            {text: '30秒', value: 30},
            {text: '45秒', value: 45},
            {text: '1分钟', value: 60},
            {text: '5分钟', value: 300}
        ],
        consoleStatus:{
            execute:'执行',
            unexecute:'不执行',
            execute_canceled:'执行',
            buy_success:'买入成交',
            bcanceled_fail:'买入成交',
            sell_success:'卖出成交',
            scanceled_fail:'卖出成交',
            buy_fail:'废单',
            sell_fail:'废单',
            scanceled_success:'已撤',
            bcanceled_success:'已撤',
            update_ocode:'更新委托编号'
        },
        mapToArray: function (map) {
            var tempData = [];
            for (var key in map) {
                if('' ==key){
                    tempData.push({"id": key, "name": map[key],"selected":true})
                }else{
                    tempData.push({"id": key, "name": map[key]})
                }

            }
            ;
            return tempData;
        },
        checkFileType: function (fileName) {
            var flag = false;
            var allowFilsType = ['xls','xlsx'];
            var extensionName = fileName.split(".")[1];
            if (allowFilsType.indexOf(extensionName) != -1) {
                flag = true;
            } else {
                flag = false;
            }
            return flag;
        }
    }

    window.ENUM_UTIL = {
        ENUM:{},
        convert:{
            'bdlx':'money_detail_item',//资金流水-变动类型
            'tl':'trader_limit',//交易员交易限制
            'os':'order_status',//订单委托状态
            'tsb':'trade_strategy_sbuy',//证券账户委托状态
            'tss':'trade_strategy_ssell',//证券账户委托状态
            'as':'account_status',//账户状态
            'pc':'position_contrast',//持仓对比结果
            'ot':'order_type',//委托方向
            'tbdlx':'trade_money_detail_item',//交易账户变动类型
            'sbdlx':'money_detail_item',//证券账户变动类型
            'ass':'access_status',//接入状态
            'sls':'security_login_status',//登录状态
            'las':'lender_account_status',//交易员禁用标识
            'oss':'order_status_shrink',//监控台状态
            'cosl':'console_order_status_list',//工作台状态
            'asn':'account_status_no',//状态  正常，禁用
            'fcs':'fee_cleared_status'//费用管理-状态
        },
        getEnumList: function (type,cb) {
            return window.ENUM_UTIL.mapToArray(this.convert[type],cb);
        },
        getEnum:function(key){
            return this.ENUM[this.convert[key]]||{};
        },
        mapToArray: function (key,cb) {
            var data = this.ENUM[key];
            var toArray = function (map) {
                var tempData = [];
                for (var key in map) {
                    if('' ==key){
                        tempData.push({"id": key, "name": map[key],"selected":true})
                    }else{
                        tempData.push({"id": key, "name": map[key]})
                    }

                }
                cb(tempData);
            }
            if(this.ENUM && data){
                toArray(data);
            }else{
                this.initAllEnum(function (data) {
                    toArray(data[key]);

                })
            }

        },
        initAllEnum:function(cb){
            API.METHODS.getData(null,'/api/enum/info',{type:''},function (vm,res) {
                if(res.status==0){
                    ENUM_UTIL.ENUM = res['data'];
                    if (cb) cb(res['data']);
                }
            })
        }
    };
    // window.ENUM_UTIL.initAllEnum();
    // 保持事件唯一性
    window.cacheBindedEvents = {};
    // 全局混入
    Vue.mixin({
        data:{
          sTimeout:null
        },
        mounted:function(){
            $('.easyui-window').on('click',function(){
                $('.tooltip.tooltip-right').remove();
            })
        },
        methods:{
            setDefaultDateByState:function(state,selectArr){
                var res = this.setDateRange(state);
                this.$nextTick(function(){
                    $(selectArr[0]).datebox('setValue',res[0]);
                    if(selectArr.length===2){
                        $(selectArr[1]).datebox('setValue',res[1]);
                    }
                })
            },
            setDateRange:function(val){
                var res = null;
                if(val==='all'){
                    res = ['',''];
                }else if(val==='currentDay'){
                    res = [this.getFormatDateString(new Date()),this.getFormatDateString(new Date())]
                }else if(val==='currentWeek'){
                    var oDate = new Date();
                    var currentDay = oDate.getDay() - 1;
                    // console.log(currentDay)
                    oDate.setDate(oDate.getDate()-currentDay);

                    res = [this.getFormatDateString(oDate),this.getFormatDateString(new Date())]
                }else if(val==='currentMonth'){
                    var oDate = new Date();
                    oDate.setDate(1);
                    res = [this.getFormatDateString(oDate),this.getFormatDateString(new Date())]

                }else if(val==='currentYear'){
                    var oDate = new Date();
                    oDate.setMonth(0);
                    oDate.setDate(1);
                    res = [this.getFormatDateString(oDate),this.getFormatDateString(new Date())]
                }else{
                    res = ['','']
                }
                return res;
            },
            getFormatDateString:function(date){
                var y = date.getFullYear();
                var m = date.getMonth()+1;
                var d = date.getDate();
                return y+'-' + this.toDou(m) + '-' + this.toDou(d);
            },
            toDou:function(n){
                return n>=10?n+'':'0'+n;
            },
            initAccount_TraderSelector:function(accountOpt,traderOpt){
                var url = '/api/stock/allocation/menu';
                var that = this;
                API.METHODS.getData(this,url,{},function(vm,res){
                    var accountList = window.COMMON_DATA.mapToArray(res.data.account);
                    var traderList = window.COMMON_DATA.mapToArray(res.data.trader);
                    if(accountOpt){
                        accountOpt.el  && vm.initSelect(accountOpt.el,accountList,{multiple:false,editable:true,firstData:{'id':'',name:'全部'}});
                    }
                    if(traderOpt){
                        traderOpt.el  && vm.initSelect(traderOpt.el,traderList,{multiple:false,editable:true,firstData:{'id':'',name:'全部'}});
                    }
                },'get');
            },
            isShowClearButton:function(){
                return this.isTimeRangeButtonDisabled();
            },
            isTimeRangeButtonDisabled:function(start,end){
                //default 9.15 ～ 3.15
                var disableStart = null;
                var disableEnd = null;
                if(start && end){
                   disableStart = start;
                   disableEnd = end;
                }else{
                    disableStart =  new Date();
                    disableStart.setHours(9);
                    disableStart.setMinutes(15);

                    disableEnd =  new Date();
                    disableEnd.setHours(15);
                    disableEnd.setMinutes(15);
                }

                var now = new Date();
                var result = true;
                if((now - disableStart) > 0 && (now - disableEnd) < 0 ){
                    result = false;
                }
                return result;
            },
            openWindow:function(selector,okCallBack,title){
                if(title){
                    $(selector).window('setTitle',title);
                }
                $(selector).window('open');
                $(selector).window('center');
                $('.reset-text-button .l-btn').removeAttr('href');//inpunt带有button 会导致按tab时获取焦点
                $(selector).find('form').form('reset');
                var btnOk = document.querySelector(selector+' .dialog_footer .btn-ok');
                var btnNo = document.querySelector(selector+' .dialog_footer .btn-no');
                btnOk ? (
                    btnOk.onclick = function () {
                        okCallBack();
                    }
                ):null
                btnNo ? (btnNo.onclick = function () {
                    $(selector).window('close');
                }):null

            },
            getTableSelected:function(selector){
                return $(selector).datagrid('getSelected');
            },
            getTableSelectedRowIndex:function(selector){
                // 未选中返回 -1
                return $(selector).datagrid('getRowIndex',$(selector).datagrid('getSelected'));
            },
            updateTableRowByIndex:function(selector,index,row){
                $(selector).datagrid('updateRow',{
                    index: index,
                    row: row
                });
            },
            deleteTableRow:function(selector){
                var index = this.getTableSelectedRowIndex(selector);
                $(selector).datagrid('deleteRow',index);
            },
            updateTableRow:function(selector,uRow){
                var sIndex = this.getTableSelectedRowIndex(selector);
                this.updateTableRowByIndex(selector,sIndex,uRow);
            },
            refreshTableRow:function(selector,index){
                if(index == undefined){
                    index = this.getTableSelectedRowIndex(selector);
                }
                $(selector).datagrid('refreshRow',index);
            },
            insertTableRow:function(selector,index,row){
                $(selector).datagrid('insertRow',{
                    index:index,
                    row:row
                });
            },
            /**
             * @param {*} options {}
             * {
             *  el:事件委托的表格,
             *  entrustEl:委托监听的元素（删除／编辑 ）,
             *  attr: 委托元素绑定的属性值 默认为 data-index 根据 它来获取对应 row信息
             *  event:事件名称,
             *  callBack:回调函数的参数为 (事件源 target, 点击行row信息)
             * }
             */
            tableEventEntrust:function(options){
                var el = options.el;
                if(!el){
                    throw Error("表格操作的事件委托需要传递表格容器ID");
                }
                var event = options.event || 'click';
                var attr = options.attr || 'data-index';
                // 委托的事件元素
                var entrustEl = options.entrustEl;
                var callBack = options.callBack;
                if(window.cacheBindedEvents["tableEventEntrust_" +entrustEl] === event){
                    $(document).off(event,entrustEl)
                }
                window.cacheBindedEvents["tableEventEntrust_" +entrustEl] = event;
                $(document).on(event,entrustEl,function(){
                    var target = this;
                    var index =$(target).attr(attr);
                    var row = $(el).datagrid('getRows')[index];
                    callBack&&callBack(target,row,index);
                })
            },
            // treegrid column的formatter(val ,row,index) 不返回 它的index = undefined
            treeEventEntrust:function(options){
                var el = options.el;
                var attr = options.attr;
                if(!el){
                    throw Error("tree表格操作的事件委托需要传递表格容器ID");
                }
                if(!attr){
                    throw Error("tree表格操作的事件委托需要传递匹配的属性值");
                }
                var event = options.event || 'click';
                // 委托的事件元素
                var entrustEl = options.entrustEl;
                var callBack = options.callBack;
                if(window.cacheBindedEvents["treeEventEntrust" +entrustEl] === event){
                    $(document).off(event,entrustEl)
                }
                window.cacheBindedEvents["treeEventEntrust" +entrustEl] = event;
                $(document).on(event,entrustEl,function(){
                    var target = this;
                    var filter_id =$(target).attr(attr);
                    var row = null;
                    var treedata = $(el).treegrid('getData');
                    for(var i=0;i<treedata.length;i++){
                        if(treedata[i][attr] == filter_id){
                            row = treedata[i];
                            break;
                        }
                        if(treedata[i].children.length>0){
                            var deepArr = treedata[i].children
                            for(var j=0;j<deepArr.length;j++){
                                if(deepArr[j][attr] == filter_id){
                                    row = deepArr[j];
                                    break;
                                }
                            }
                        }
                    }
                    callBack&&callBack(target,row);
                })
            },
            initSelect:function(selector,data,options){
                var options = options || {}
                var pr = {
                    valueField:'id',
                    textField:'name',
                    data:data,
                    multiple:false,// 默认单选
                    editable:false,// 默认不可以输入
                    autoSelect:true,// 默认自动选中
                    firstData:null,//第一项数据 例：{id:'',name:'全部'} 默认不添加第一条数据
                }
                var newOptions = Object.assign(pr,options)
                if(newOptions['firstData']){
                    newOptions['data'].unshift(newOptions['firstData']);
                }
                if(newOptions['multiple']){
                    newOptions['onLoadSuccess'] = function(){
                        if(data.length!=0&&newOptions['autoSelect']){
                            $(selector).combobox('setValue',data[0]['id']);
                        }
                        if(options['onLoadSuccess']){
                            options['onLoadSuccess'](data);
                        }
                    }
                    newOptions['onClick'] = function(row){
                        var values, index;
                        if(row.id==''){
                            $(this).combobox('clear');
                        } else {
                            values = $(this).combobox('getValues');
                            index = values.indexOf('');
                            if(index!=-1){
                                values.splice(index,1);
                                $(this).combobox('setValues',values);
                            }
                        }
                        if(options['onClick']){
                            options['onClick'](row);
                        }
                    }
                    $(selector).combobox(newOptions);
                }else{
                    newOptions['onLoadSuccess'] = function(){
                        if(data.length!=0&&newOptions['autoSelect']){
                            $(selector).combobox('setValue',data[0]['id']);
                        }
                        if(options['onLoadSuccess']){
                            options['onLoadSuccess'](data);
                        }
                    }
                    newOptions['onClick'] = function(row){
                        if(options['onClick']){
                            options['onClick'](row);
                        }
                    }
                    // 单选
                    $(selector).combobox(newOptions);
                }
            },
            submitForm:function(selector,option){
                var ob = Object.assign({},option);
                ob['success'] = function(resStr){
                    var jo = JSON.parse(resStr);
                    if(jo['status']=='-1000'){
                        API.METHODS.removeUserInfo();
                    }else{
                        option['success'](jo)
                    }
                }
                $(selector).form('submit',ob)
            },
            getTabsIndex:function(selector){
                var tab = $(selector).tabs('getSelected');
                var index = $(selector).tabs('getTabIndex',tab);
                return index;
            },
            formatDate:function(now) {
                var year=now.getFullYear();
                var month=now.getMonth()+1;
                var date=now.getDate();
                var hour=now.getHours();
                var minute=now.getMinutes();
                var second=now.getSeconds();
                return year+"-"+month+"-"+date+" "+hour+":"+minute+":"+second;
            },
            getUTime:function(){
                var now = new Date();
                var hour=now.getHours();
                var minute=now.getMinutes();
                var second=now.getSeconds();
                return (hour<10?'0'+hour:hour)+":"+(minute<10?'0'+minute:minute)+":"+(second<10?'0'+second:second);
            },
            createHash:function(){
                var key =  new Date().getTime() + Math.random();
                var hash = md5('value', key);
                return hash
            },
            initTraderSelect(selector,opt){

            },
            toast: function(msg,duration){
                var duration=isNaN(duration)?2000:duration;
                var m = document.createElement('div');
                m.innerHTML = msg;
                m.style.cssText="max-width:60%;min-width: 150px;padding:0 14px;height: 40px;color: rgb(255, 255, 255);line-height: 40px;text-align: center;border-radius: 4px;position: fixed;top: 50%;left: 50%;transform: translate(-50%, -50%);z-index: 999999;background: rgba(0, 0, 0,.7);font-size: 16px;";
                document.body.appendChild(m);
                setTimeout(function() {
                    var d = 0.5;
                    m.style.webkitTransition = '-webkit-transform ' + d + 's ease-in, opacity ' + d + 's ease-in';
                    m.style.opacity = '0';
                    setTimeout(function() { document.body.removeChild(m) }, d * 1000);
                }, duration);
            },
            exportExcel:function(selector){
                var ob =$(selector).datagrid('options');
                var queryParams = ob['onBeforeLoad']({});
                var param = {export:1};
                Object.assign(param,queryParams);
                this.downloadExcel(ob.url,param);
            },
            downloadExcel:function(baseUrl,param){
                let userInfo = STORAGE.getItem('user');
                let params = $.extend(userInfo, param);
                var iframe = document.getElementById('downloadIframe') || null;
                if(!iframe){
                    iframe = document.createElement("iframe");
                    iframe.style.position = 'fixed';
                    iframe.style.right = '-9999px';
                    iframe.style.top = '-9999px';
                    iframe.style.opacity = '0';
                    iframe.id = "downloadIframe"
                    document.body.appendChild(iframe);
                }

                //防止猛点
                var _this = this;
                clearTimeout(_this.timer);
                _this.timer = setTimeout(function(){
                    var str_params = '';
                    for(var name in params){
                        str_params += '&' + name + '='+ params[name]
                    }
                    var url =  baseUrl + '?' + str_params.substring(1);
                    iframe.src = url;
                },300)
            },
            setDateRange:function(val){
                var res = null;
                if(val==='all'){
                    res = ['',''];
                }else if(val==='currentDay'){
                    res = [this.getFormatDateString(new Date()),this.getFormatDateString(new Date())]
                }else if(val==='currentWeek'){
                    var oDate = new Date();
                    var currentDay = oDate.getDay() - 1;
                    // console.log(currentDay)
                    oDate.setDate(oDate.getDate()-currentDay);

                    res = [this.getFormatDateString(oDate),this.getFormatDateString(new Date())]
                }else if(val==='currentMonth'){
                    var oDate = new Date();
                    oDate.setDate(1);
                    res = [this.getFormatDateString(oDate),this.getFormatDateString(new Date())]

                }else if(val==='currentYear'){
                    var oDate = new Date();
                    oDate.setMonth(0);
                    oDate.setDate(1);
                    res = [this.getFormatDateString(oDate),this.getFormatDateString(new Date())]
                }else{
                    res = ['','']
                }
                return res;
            },
            getFormatDateString:function(date){
                var y = date.getFullYear();
                var m = date.getMonth()+1;
                var d = date.getDate();
                return y+'-' + this.toDou(m) + '-' + this.toDou(d);
            },
            toDou:function(n){
                return n>=10?n+'':'0'+n;
            }
        }
    })
}();