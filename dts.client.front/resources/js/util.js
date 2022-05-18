! function() {
    var proxyUrl = '';
    var API = {};
    API.URLS = {
        LOGIN: proxyUrl + '/public/login'
    };
    API.METHODS = {
        /**
         *
         * @param {*} canvasElement
         * @param {*} filename
         */
        saveToPngDownload: function(canvasElement, filename) {
            var canvas = canvasElement;
            var url = canvas.toDataURL("image/png");
            var oA = document.createElement("a");
            oA.download = filename || '下载'; // 设置下载的文件名，默认是'下载'
            oA.href = url;
            document.body.appendChild(oA);
            oA.click();
            oA.remove();
        },
        /**
         *
         * @param {*} textFieldElement  原生dom 的 textarea 或 input
         * @param {*} content  copy的内容
         */
        copyText: function(textFieldElement, content) {
            var info = content;
            var tmp = info.replace(/\s/g, '')
            if (document.execCommand) {
                try {
                    var e = textFieldElement;
                    e.value = tmp
                    e.select();
                    e.setSelectionRange(0, e.value.length);
                    document.execCommand("Copy");
                    e.value = info;
                } catch (ex) {
                    var input = document.createElement("input");
                    input.style.position = 'fixed';
                    input.style.right = '-9999px';
                    input.style.top = '-9999px';
                    input.style.opacity = '0';
                    input.value = info;
                    document.body.appendChild(input);
                    input.select();
                    input.setSelectionRange(0, input.value.length);
                    document.execCommand('Copy');
                    document.body.removeChild(input);
                }
            }
            if (window.clipboardData) {
                window.clipboardData.setData("Text", info);
                return true;
            }
            return false;
        },
        setRightSideTablePagination: function(selector, options) {
            var options = options || {  layout: ['first', 'prev', 'sep', 'manual', 'sep', 'next', 'last', 'sep', 'refresh'] }
            $($(selector).datagrid('getPager')).pagination(options); 
        },
        /**
         * 表格设置选中行
         * selector 表格id
         * rowFieldKey 对应row的字段
         * searchValue 查找字段的匹配的值
         *  */
        setSelectRow: function(selector, rowFieldKey, searchValue) {
            var res = $(selector).datagrid('getData').rows || [];
            res.forEach(function(value, index) {
                if (value[rowFieldKey] == searchValue) {
                    $(selector).datagrid('selectRow', index)
                }
            })
        },
        thousandth: function(num) {
            var num_str = num + ""
            var numSplitArr = num_str.split('.');
            var int_num = numSplitArr[0].replace(/(\d)(?=(?:\d{3})+$)/g, '$1,');
            if (num_str.indexOf('.') !== -1) {
                return int_num + "." + numSplitArr[1];
            } else {
                return int_num;
            }
        },
        numberFormatter: function(value, row, index, fixCount) {
            var fixCount = fixCount || 2;
            return API.METHODS.formatCallBack(value, row, index, function(value) {
                return API.METHODS.thousandth(API.METHODS.fomatFloat(value, fixCount));
            })
        },
        numberFormatterInt: function(value, row, index) {
            return API.METHODS.formatCallBack(value, row, index, parseInt)
        },
        colorNumberFormatter: function(value, row, index, fixCount) {
            var fixCount = fixCount || 2;
            return API.METHODS.formatCallBack(value, row, index, function() {
                return API.METHODS.numDisplayByValue(value, API.METHODS.numberFormatter(value, row, index, fixCount))
            })
        },
        colorNumberFormatterInt: function(value, row, index) {
            return API.METHODS.formatCallBack(value, row, index, function() {
                return API.METHODS.numDisplayByValue(value, API.METHODS.numberFormatterInt(value, row, index))
            })
        },
        numDisplayByValue: function(value, res) {
            if (value > 0) {
                return '<span style="color:#FF4C4C;">' + res + '</span>'
            } else if (value == 0) {
                return 0;
            } else {
                return '<span style="color:#29A63D;">' + res + '</span>'
            }
        },
        fomatFloat: function(num, n) {
            var f = parseFloat(num);
            var isMinum = false;
            if (isNaN(f)) {
                return false;
            }
            if (f < 0) {
                isMinum = true;
                f = -f;
            }
            f = Math.round(f * Math.pow(10, n)) / Math.pow(10, n); // n 幂
            if (isMinum) { f = -f; }
            var s = f.toString();
            var rs = s.indexOf('.');
            //判定如果是整数，增加小数点再补0
            if (rs < 0) {
                rs = s.length;
                s += '.';
            }
            while (s.length <= rs + n) {
                s += '0';
            }
            return s;
        },
        isNum: function(value) {
            return !isNaN(value) && value !== null && value !== undefined && value !== '';
        },
        formatCallBack: function(value, row, index, callBack) {
            if (API.METHODS.isNum(value)) {
                return callBack(value);
            } else {
                return '--'
            }
        },
        colorPercentFormatter: function(value, row, index) {
            if (!isNaN(value) && value !== null && value !== undefined && value !== '') {
                if (value > 0) {
                    return '<span style="color:#f55d5d;">' + value + '%</span>'
                } else if (value == 0) {
                    return 0;
                } else {
                    return '<span style="color:#227b1a;">' + value + '%</span>'
                }
            } else {
                return '--';
            }
        },
        percentFormatter: function(value, row, index) {
            if (API.METHODS.isNum(value)) {
                return value + '%';
            } else {
                return '--';
            }
        },
        formatDateToString: function(v) {
            if (!v) return '--';
            let dateTime = new Date(v);
            let hour = dateTime.getHours() >= 10 ? dateTime.getHours() : ('0' + dateTime.getHours()),
                minute = dateTime.getMinutes() >= 10 ? dateTime.getMinutes() : ('0' + dateTime.getMinutes()),
                seconds = dateTime.getSeconds() >= 10 ? dateTime.getSeconds() : ('0' + dateTime.getSeconds());
            return hour + ':' + minute + ':' + seconds;
        },
        formatCurrentDate: function() {
            let dateTime = new Date(),
                year = dateTime.getFullYear(),
                month = (dateTime.getMonth() + 1) >= 10 ? dateTime.getMonth() + 1 : ('0' + (dateTime.getMonth() + 1)),
                date = dateTime.getDate() >= 10 ? dateTime.getDate() : ('0' + dateTime.getDate());
            return year + '-' + month + '-' + date;
        },
        clearErrormsg: function(selector) {
            $(selector).html('');
        },
        checkLogin: function() {
            var user = STORAGE.getItem('user')
            if (user) {
                return true;
            }
            return false;
        },
        removeUserInfo: function() {
            STORAGE.removeItem('user');
            // var opener = window.opener ? window.opener.window : window.top.window;
            // opener.location.href = '/login.html';
            // var index_frames = $('#index_page .index_frame');
            // index_frames && index_frames.remove();
        },
        getData: function(url, options, callback, method, errCallBack) {
            let userInfo = STORAGE.getItem('user') || {};
            let opts = $.extend(userInfo, options, { _v: 2 });

            // 增加companyId
            callback = callback || function() {};
            $.ajax({
                url: proxyUrl + url,
                method: method || 'GET',
                data: opts,
                cache: false,
                success: function(res) {
                    // var  jo = JSON.parse(res);
                    if (res['status'] == '-2103' || res['status'] == '-2104' || res['status'] == '-2002') {
                        API.METHODS.removeUserInfo();
                    } else {
                        callback && callback(res);
                    }
                },
                error: function(err) {
                    errCallBack && errCallBack(err);
                }
            })
        },
        uploadFileData: function(vm, url, options, callback, method, errCallBack) {
            // 增加companyId
            callback = callback || function() {};
            $.ajax({
                url: proxyUrl + url,
                method: method || 'POST',
                data: options,
                /**
                 *必须false才会自动加上正确的Content-Type
                 */
                contentType: false,
                /**
                 * 必须false才会避开jQuery对 formdata 的默认处理
                 * XMLHttpRequest会对 formdata 进行正确的处理
                 */
                processData: false,
                success: function(res) {
                    if (res['status'] == '-2103' || res['status'] == '-2104' || res['status'] == '-2002') {
                        API.METHODS.removeUserInfo();
                    } else {
                        callback && callback(vm, res);
                    }
                },
                error: function(err) {
                    errCallBack && errCallBack(err);
                }
            })
        },
        resetSearchEvent: function(selector, toolbar) {
            /*
            reset 按钮必须设置  class="table_reset" 默认reload
            如果不想 reload 则额外传递传递 class="table_no_reload"
            */
            var that = this;
            $(toolbar).find('.table_reset').off('click');
            $(toolbar).find('.table_reset').on('click', function() {
                var inputs = $(toolbar).find('.textbox-f');
                $.each(inputs, function(index, ele) {
                    if ($(ele).hasClass('combo-f')) {
                        if ($(ele).hasClass('datebox-f')) {
                            $(ele).datebox('reset');
                        } else {
                            that.setDefaultComboBoxValue(ele);
                        }
                    } else {
                        $(ele).textbox('reset');
                    }
                })
                console.log($(toolbar).find('.table_reset').hasClass('table_no_reload'))
                if ($(toolbar).find('.table_reset').hasClass('table_no_reload')) return
                setTimeout(function() {
                    $(selector).datagrid('gotoPage', 1);
                }, 100)
            });
        },
        setDefaultComboBoxValue: function(ele) {
            var options = $(ele).combobox('options');
            if (!options.data) return;
            var data = options.data;
            var res = [];
            $.each(data, function(index, item) {
                item.selected && res.push(item);
            })
            if (options.multiple) {
                res = $.map(res, function(item, id) {
                    return item.id
                });
                // 多选
                $(ele).combobox('setValues', res.join(','));
            } else {
                // 单选
                $(ele).combobox('setValue', res[0].id);
            }
        },
        loadData: function(selector, optionData, columnNotMoving) {
            optionData['onLoadError'] = function(e) {
                console.log(e)
            }
            if (!isMac()) delete optionData['scrollbarSize'];
            var that = this;
            var f = optionData['onBeforeLoad'];
            optionData['onBeforeLoad'] = function(param) {
                f && f(param)
                if (param['rows']) {
                    param['pagesize'] = param['rows'];
                    delete param.rows;
                }
                let userInfo = STORAGE.getItem('user');
                $.extend(param, userInfo, { _v: 2 });
                return param;
            }

            optionData['toolbar'] && that.resetSearchEvent(selector, optionData['toolbar']);

            if (!optionData['loadFilter']) {
                optionData['loadFilter'] = function(data) {
                    // 拖拽会触发 loadFilter事件
                    // 但是数据第一次加载已经是ajax后过滤好的格式
                    // 需要判断如果是老数据则 不进行过滤
                    // 默认拖拽是
                    if (!columnNotMoving && data['isFilter']) {
                        return data;
                    } else {
                        if (data['status'] == '-2103' || data['status'] == '-2104' || data['status'] == '-2002') {
                            API.METHODS.removeUserInfo();
                            return { "rows": [], 'total': 0, "isFilter": true, 'raw': [] };
                        } else {
                            if (data.status == '0') {
                                if (optionData.pagination) {
                                    return { "rows": data['data']['list'], 'total': data.data.total, "isFilter": true, 'raw': data.data };
                                }
                                return { "rows": data['data']['list'], "isFilter": true, 'raw': data.data };

                            } else {
                                return { "rows": [], 'total': 0, "isFilter": true, 'raw': data.data };
                            }
                        }
                    }

                };
            }
            $(selector).datagrid(optionData);

        },
        strEllipsis: function(str, subLength) {
            var realLength = 0,
                len = str.length,
                charCode = -1;
            for (var i = 0; i < len; i++) {
                charCode = str.charCodeAt(i);
                if (realLength < subLength) {
                    if (charCode >= 0 && charCode <= 128) {
                        realLength += 1;
                    } else {
                        realLength += 2;
                    }
                } else {
                    return str.substr(0, i) + '...';
                }
            }
            return str;
        }
    };

    var STORAGE = {
        setItem: function(key, data) {
            if (window.localStorage) {
                try {
                    localStorage.setItem(key, JSON.stringify(data));
                } catch (e) {
                    alert('请关闭无痕浏览模式')
                }
            }
        },
        getItem: function(key) {
            var data = window.localStorage ? localStorage.getItem(key) : null;
            if (data && data != 'undefined') {
                return JSON.parse(data);
            }
            return '';

        },
        removeItem: function(key) {
            if (window.localStorage) {
                try {
                    localStorage.removeItem(key);
                } catch (e) {}

            }
        },
        setSessionItem: function(key, data) {
            if (window.sessionStorage) {
                try {
                    sessionStorage.setItem(key, JSON.stringify(data));
                } catch (e) {
                    alert('请关闭无痕浏览模式')
                }
            }
        },
        getSessionItem: function(key) {
            var data = window.sessionStorage ? sessionStorage.getItem(key) : null;
            if (data && data != 'undefined') {
                return JSON.parse(data);
            }
            return '';
        },
        removeSessionItem: function(key) {
            if (window.sessionStorage) {
                try {
                    sessionStorage.removeItem(key);
                } catch (e) {

                }
            }
        }
    }
    window.eventBus = {
        selectedEvents: {},
        unSelectedEvents: {},
        closeEvents: {},
        addSelectedEvent: function(presentUrl, fn) {
            this.selectedEvents[presentUrl] = fn;
        },
        addUnSelected: function(presentUrl, fn) {
            this.unSelectedEvents[presentUrl] = fn;
        },
        addCloseEvent: function(presentUrl, fn) {
            this.closeEvents[presentUrl] = fn;
        },
        removeSelectedEvent: function(presentUrl) {
            if (this.selectedEvents.hasOwnProperty(presentUrl)) {
                delete this.selectedEvents[presentUrl]
            }
        },
        removeUnSelectedEvent: function(presentUrl) {
            if (this.unSelectedEvents.hasOwnProperty(presentUrl)) {
                delete this.unSelectedEvents[presentUrl]
            }
        },
        removeCloseEvent: function(presentUrl) {
            if (this.closeEvents.hasOwnProperty(presentUrl)) {
                delete this.closeEvents[presentUrl]
            }
        },
        actionSelectedEvent: function(url) {
            console.log(this.selectedEvents)
            if (this.selectedEvents.hasOwnProperty(url)) {
                this.selectedEvents[url]();
            }
        },
        actionUnSelectedEvent: function(url) {
            if (this.unSelectedEvents.hasOwnProperty(url)) {
                this.unSelectedEvents[url]();
            }
        },
        actionCloseEvent: function(url) {
            if (this.closeEvents.hasOwnProperty(url)) {
                this.closeEvents[url]();
                this.removeSelectedEvent(url);
                this.removeUnSelectedEvent(url);
                this.removeCloseEvent(url);
            }
        }

    }

    // 获取股票实时信息
    var Stock = function(stock_code, c) {
        if (c.stock) {
            c.stock.close(stock_code);
        }
        this.websocket = null;
        this.forbidden = false; // 当forbidden为true时，websocket强制关闭，不再通过websocket.onclose触发
        this.interval = null; // 当websocket发生错误，或者数据不正确时，启用定时器请求其他接口
        this.getStockInfo(stock_code, c);
    };

    Stock.prototype = {
        getStockInfo: function(stock_code, c) {
            console.log('getStockInfo00000');
            console.log(c.level);
            c.level == 2 ? this.getInfo_by_local_websocket(stock_code, c) : this.getInfo_by_websocket(stock_code, c);
        },
        source: null,
        close: function(stock_code) { // 数据请求结束
            this.forbidden = true;
            if (this.websocket) {
                switch (Stock.source) {
                    case 'local':
                        this.websocket.send('{"event":"unsub","code":"' + stock_code + '", "type" : "tick"}');
                        this.websocket.send('{"event":"unsub","code":"' + stock_code + '", "type" : "trade"}')
                        break;
                    case 'remote':
                        this.websocket.close()
                        break;
                }
            }
            this.websocket = null;
            this.interval ? clearInterval(this.interval) : null;
            this.interval = null;
        },
        // 通过本地websocket服务实时获取level2行情数据
        getInfo_by_local_websocket(stock_code, c) {
            console.log('getInfo_by_local_websocket11111');
            var vm = this;
            try {
                this.close();
                this.forbidden = false; // 打开websocket重启开关
                // var ws = new WebSocket("ws://10.0.0.30:9777/ws/level2");
                var ws = this.websocket = new WebSocket("wss://push.hq.youlikj.com/ws/level2");

                ws.onerror = function(event) {
                    vm.getInfo_by_websocket(stock_code, c);
                }
                Stock.source = 'local';
                ws.onmessage = function(e) {
                    var data = JSON.parse(e.data);
                    var tradeLength = 30; // 只取最新的30条数据
                    if (Array.isArray(data)) {
                        if (data.length > 1) {
                            c.trade = data.slice(-tradeLength);
                        } else {
                            if (c.trade.length < tradeLength) {
                                data.length == 1 ? c.trade.push(data[0]) : null;
                            } else {
                                data.length == 1 ? c.trade.push(data[0]) : null;
                                c.trade = c.trade.slice(-tradeLength);
                            }
                        }
                    } else {
                        c.s_pLevels = [
                            [],
                            []
                        ];
                        c.s_mLevels = [
                            [],
                            []
                        ];
                        let info = {
                            'stock_code': data.code,
                            'curPrice': parseFloat(data.price) || parseFloat(data.pre) || 0,
                            'high_price': data.high,
                            'low_price': data.low,
                            'start_price': data.open,
                            'end_price': data.prev,
                        };
                        c.s_info = Object.assign({}, info);
                        c.yesterdayPrice = parseFloat(data.pre);
                        data.asks.forEach(function(v, i) {
                            c.s_mLevels[0].push(parseFloat(data.asks[i].price));
                            c.s_mLevels[1].push(parseFloat(data.asks[i].volume / 100).toFixed(0));
                        })

                        data.bids.forEach(function(v, i) {
                            c.s_pLevels[0].push(data.bids[i].price);
                            c.s_pLevels[1].push((data.bids[i].volume / 100).toFixed(0));
                        })
                    }
                };
                ws.onopen = function() {
                    ws.send('{"event":"sub","code":"' + stock_code + '", "type" : "tick"}');
                    ws.send('{"event":"sub","code":"' + stock_code + '", "type" : "trade"}');

                };

                ws.onclose = function() {
                    vm.getInfo_by_websocket(stock_code, c);
                    c.getPrice();
                }

            } catch (e) {
                vm.getInfo_by_websocket(stock_code, c);
                c.getPrice();
            }
        },
        /* ******通过新浪websocket实时获取股票基本数据
         ** stock_code => 股票代码
         ** c => vue实例
         ****************************************/
        getInfo_by_websocket(stock_code, c) {
            console.log('getInfo_by_websocket222222')
            this.close();
            this.forbidden = false; // 打开websocket重启开关
            let tempS;
            if (parseInt(stock_code) >= 600000) {
                tempS = 'sh' + stock_code; // 如果股票代码以6开头则加上sh前缀
            } else {
                tempS = 'sz' + stock_code; // 否则认为是深圳指数
            }
            let protocol = location.protocol.indexOf('https') == 0 ? 'wss' : 'ws';
            let wsServer = protocol + '://hq.sinajs.cn/wskt?list=' + tempS; //服务器地址
            try {
                this.websocket = new WebSocket(wsServer);
                Stock.source = 'remote';
                this.websocket.onclose = (evt) => {
                    // 当forbidden为false时，需要在websocket关闭后自动重新连接
                    if (!this.forbidden) {
                        this.getInfo_by_websocket(stock_code, c)
                    }
                };

                this.websocket.onmessage = (evt) => { // 收到服务器消息，使用evt.data提取
                    let info;
                    let arr = (evt.data).split('=')[1].split(',');
                    info = {
                        'stock_name': arr[0],
                        'stock_code': stock_code,
                        'curPrice': parseFloat(arr[3]) > 0 ? arr[3] : arr[2],
                        'high_price': arr[4],
                        'low_price': arr[5],
                        'start_price': arr[1],
                        'end_price': arr[2],
                        'money': (arr[9] / 10000).toFixed(2),
                        'count': (arr[8] / 100).toFixed(0)
                    };
                    c.yesterdayPrice = arr[2];
                    c.s_info = info;
                    // 创建五档的二维数组，第一个元素为价格集合，第二个元素为买卖量集合
                    c.s_pLevels = [
                        [],
                        []
                    ];
                    c.s_mLevels = [
                        [],
                        []
                    ];

                    arr.slice(10, 20).map(function(v, i) {
                        if (i % 2 == 0) {
                            c.s_pLevels[1].push(v / 100)
                        } else {
                            c.s_pLevels[0].push(v)
                        }
                    })

                    arr.slice(20, 30).map(function(v, i) {
                        if (i % 2 == 0) {
                            c.s_mLevels[1].push(v / 100)
                        } else {
                            c.s_mLevels[0].push(v)
                        }
                    })

                    c.yesterdayPrice = info.end_price
                };

                this.websocket.onerror = (evt) => {
                    this.close();
                    this.getInfo_by_api(stock_code, c);
                    this.interval = setInterval(() => {
                        this.getInfo_by_api(stock_code, c);
                    }, 5000)
                };
            } catch (e) {
                this.close();
                this.getInfo_by_api(stock_code, c);
                this.interval = setInterval(() => {
                    this.getInfo_by_api(stock_code, c);
                }, 5000)
            }
        },
        // 通过行情接口获取股票基本数据
        getInfo_by_api(stock_code, c) {
            console.log('getInfo_by_api33333');
            let vm = this;
            let userInfo = STORAGE.getItem('user');
            let opts = $.extend(userInfo, { code: stock_code });
            $.ajax({
                type: "GET",
                url: '/api/quote/get',
                data: opts,
                contentType: "text/plain",
                timeout: 2000,
                success: function(res, textStatus, jqXHR) {
                    console.log(res);
                    if (res.status == 0) {
                        let data = res && res.data;
                        res.data = {
                            "price": data.price, // 当前价
                            "high": data.high, //今日最高价
                            'ask_v': data.ask_v, // 卖一量至卖五量
                            "open": data.open, //今日开盘价
                            'ask_p': data.ask_p, // 卖一价至卖五价
                            'down_limit': data.down_limit, // 跌停价
                            "low": data.low, //今日最低价
                            "prev_price": data.prev_price, //昨收价
                            'bid_p': data.bid_p, // 买一价至买五价
                            'up_limit': data.up_limit, // 涨停价
                            'bid_v': data.bid_v, // 买一量至买五量
                            'code': data.code, // 股票代码
                            'name': data.name, // 股票名称
                        };
                        //将数据处理好放到对象里，然后push到数组里，按顺序来，到时候按顺序遍历
                        try {
                            let data = res.data;
                            // 创建五档的二维数组，第一个元素为价格集合，第二个元素为买卖量集合
                            c.s_pLevels = [
                                [],
                                []
                            ];
                            c.s_mLevels = [
                                [],
                                []
                            ];

                            let info = {
                                'stock_name': data.name,
                                'stock_code': data.code,
                                'curPrice': data.price || 0,
                                'high_price': data.high,
                                'low_price': data.low,
                                'start_price': data.open,
                                'end_price': data.prev_price,
                            };

                            c.s_info = Object.assign({}, info);
                            c.yesterdayPrice = data.prev_price;

                            res.data.ask_p.forEach(function(v, i) {
                                c.s_mLevels[0].push(res.data.ask_p[i]);
                                c.s_mLevels[1].push((res.data.ask_v[i]).toFixed(0));
                            })

                            res.data.bid_p.forEach(function(v, i) {
                                c.s_pLevels[0].push(res.data.bid_p[i]);
                                c.s_pLevels[1].push((res.data.bid_v[i]).toFixed(0));
                            })
                        } catch (e) {
                            ACTION.showToast({ msg: '行情数据获取失败，正在重新获取aaaaa...' });
                            clearInterval(vm.interval);
                            setTimeout(() => {
                                vm.getStockInfo(stock_code, c)
                            }, 5000)
                        }
                    } else {
                        ACTION.showToast({ msg: '行情数据获取失败，正在重新获取bbbbb...' });
                        clearInterval(vm.interval);
                        setTimeout(() => {
                            vm.getStockInfo(stock_code, c)
                        }, 5000)
                    }

                },
                error: function() {
                    ACTION.showToast({ msg: '行情数据获取失败，正在重新获取...' });
                    clearInterval(vm.interval);
                    setTimeout(() => {
                        vm.getStockInfo(stock_code, c)
                    }, 5000)
                }
            });
        },
    }

    // 常用操作
    var ACTION = {
        showToast: function({ msg, timer = 2500 }) {
            var html = '<div class="toast">' + msg + '</div>';
            if ($('.toast').length == 0) {
                $('body').append(html);
                setTimeout(function() {
                    $('.toast').remove();
                }, timer)
            }
        }
    }

    window.API = API;
    window.STORAGE = STORAGE;
    window.Stock = Stock;
    window.ACTION = ACTION;
    window.openWindow = function(url, name, pageWidth, pageHeight) {
        var availTop = window.screen.availTop, // 返回浏览器可用空间上边距离屏幕（系统桌面）左边界的距离。
            availLeft = window.screen.availLeft, // 返回浏览器可用空间左边距离屏幕（系统桌面）左边界的距离。
            availHeight = window.screen.availHeight, // 浏览器在显示屏上的可用高度，即当前屏幕高度
            availWidth = window.screen.availWidth, // 浏览器在显示屏上的可用宽度，即当前屏幕宽度
            pageWidth = pageWidth || availWidth, // 弹出窗口的宽度
            ua = navigator.userAgent,
            pageHeight = pageHeight || availHeight, // 弹出窗口的高度
            pageTop = (availHeight - pageHeight) / 2, // 窗口的垂直位置
            pageLeft = (availWidth - pageWidth) / 2; // 窗口的水平位置;
        if (navigator.userAgent.indexOf('Chrome') !== -1) { // 兼容chrome的bug
            pageTop += availTop // 距顶偏移值
            pageLeft += availLeft // 距左偏移值
        }

        return window.open(url, name, 'left=' + pageLeft + 'px,top=' + pageTop + 'px, width=' + pageWidth + 'px, height=' + pageHeight + 'px,menubar=yes,resizable=yes,location=no');
    }

    //防止页面后退
    if ((window.isMac && window.isMac()) || (window.getIEVersion && window.getIEVersion() > 9)) {
        history.pushState(null, null, document.URL);
        window.addEventListener('popstate', function() {
            history.pushState(null, null, document.URL);
        });
    }
}();