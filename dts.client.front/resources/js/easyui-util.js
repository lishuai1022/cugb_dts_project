! function() {
    window.cacheBindedEvents = {}
    window.EUtils = {
        setDefaultDateByState: function(state, selectArr) {
            var res = this.setDateRange(state);
            setTimeout(() => {
                $(selectArr[0]).datebox('setValue', res[0]);
                if (selectArr.length === 2) {
                    $(selectArr[1]).datebox('setValue', res[1]);
                }
            }, 100);
        },
        setDateRange: function(val) {
            var res = null;
            if (val === 'all') {
                res = ['', ''];
            } else if (val === 'currentDay') {
                res = [this.getFormatDateString(new Date()), this.getFormatDateString(new Date())]
            } else if (val === 'currentWeek') {
                var oDate = new Date();
                var currentDay = oDate.getDay() - 1;
                // console.log(currentDay)
                oDate.setDate(oDate.getDate() - currentDay);

                res = [this.getFormatDateString(oDate), this.getFormatDateString(new Date())]
            } else if (val === 'currentMonth') {
                var oDate = new Date();
                oDate.setDate(1);
                res = [this.getFormatDateString(oDate), this.getFormatDateString(new Date())]

            } else if (val === 'currentYear') {
                var oDate = new Date();
                oDate.setMonth(0);
                oDate.setDate(1);
                res = [this.getFormatDateString(oDate), this.getFormatDateString(new Date())]
            } else {
                res = ['', '']
            }
            return res;
        },
        getFormatDateString: function(date) {
            var y = date.getFullYear();
            var m = date.getMonth() + 1;
            var d = date.getDate();
            return y + '-' + this.toDou(m) + '-' + this.toDou(d);
        },
        getFormatDateTimeString: function(date) {
            var y = date.getFullYear();
            var m = date.getMonth() + 1;
            var d = date.getDate();
            var h = date.getHours();
            var mm = date.getMinutes();
            var ss = date.getSeconds();
            return y + '-' + this.toDou(m) + '-' + this.toDou(d) + " " + this.toDou(h) + ':' + this.toDou(mm) + ':' + this.toDou(ss);
        },
        toDou: function(n) {
            return n >= 10 ? n + '' : '0' + n;
        },
        initAccount_TraderSelector: function(accountOpt, traderOpt) {
            var url = '/api/stock/allocation/menu';
            var that = this;
            API.METHODS.getData(this, url, {}, function(vm, res) {
                var accountList = window.COMMON_DATA.mapToArray(res.data.account);
                var traderList = window.COMMON_DATA.mapToArray(res.data.trader);
                if (accountOpt) {
                    accountOpt.el && EUTIL.METHODS.initSelect(accountOpt.el, accountList, { multiple: false, editable: true, firstData: { 'id': '', name: '全部' } });
                }
                if (traderOpt) {
                    traderOpt.el && EUTIL.METHODS.initSelect(traderOpt.el, traderList, { multiple: false, editable: true, firstData: { 'id': '', name: '全部' } });
                }
            }, 'get');
        },
        isShowClearButton: function() {
            return this.isTimeRangeButtonDisabled();
        },
        isTimeRangeButtonDisabled: function(start, end) {
            //default 9.15 ～ 3.15
            var disableStart = null;
            var disableEnd = null;
            if (start && end) {
                disableStart = start;
                disableEnd = end;
            } else {
                disableStart = new Date();
                disableStart.setHours(9);
                disableStart.setMinutes(15);

                disableEnd = new Date();
                disableEnd.setHours(15);
                disableEnd.setMinutes(15);
            }

            var now = new Date();
            var result = true;
            if ((now - disableStart) > 0 && (now - disableEnd) < 0) {
                result = false;
            }
            return result;
        },
        openWindow: function(selector, okCallBack, title) {
            if (title) {
                $(selector).window('setTitle', title);
            }
            $(selector).window('open');
            $(selector).window('center');
            $('.reset-text-button .l-btn').removeAttr('href'); //inpunt带有button 会导致按tab时获取焦点
            $(selector).find('form').form('reset');
            var btnOk = document.querySelector(selector + ' .dialog_footer .btn-ok');
            var btnNo = document.querySelector(selector + ' .dialog_footer .btn-no');
            btnOk ? (
                btnOk.onclick = function() {
                    okCallBack();
                }
            ) : null
            btnNo ? (btnNo.onclick = function() {
                $(selector).window('close');
            }) : null

        },
        closeWindow: function(selector) {
            $(selector).window('close')
        },
        getTableSelected: function(selector) {
            return $(selector).datagrid('getSelected');
        },
        getTableSelectedRowIndex: function(selector) {
            // 未选中返回 -1
            return $(selector).datagrid('getRowIndex', $(selector).datagrid('getSelected'));
        },
        updateTableRowByIndex: function(selector, index, row) {
            $(selector).datagrid('updateRow', {
                index: index,
                row: row
            });
        },
        deleteTableRow: function(selector) {
            var index = this.getTableSelectedRowIndex(selector);
            $(selector).datagrid('deleteRow', index);
        },
        updateTableRow: function(selector, uRow) {
            var sIndex = this.getTableSelectedRowIndex(selector);
            this.updateTableRowByIndex(selector, sIndex, uRow);
        },
        refreshTableRow: function(selector, index) {
            if (index == undefined) {
                index = this.getTableSelectedRowIndex(selector);
            }
            $(selector).datagrid('refreshRow', index);
        },
        insertTableRow: function(selector, index, row) {
            $(selector).datagrid('insertRow', {
                index: index,
                row: row
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
        tableEventEntrust: function(options) {
            var el = options.el;
            if (!el) {
                throw Error("表格操作的事件委托需要传递表格容器ID");
            }
            var event = options.event || 'click';
            var attr = options.attr || 'data-index';
            // 委托的事件元素
            var entrustEl = options.entrustEl;
            var callBack = options.callBack;
            if (window.cacheBindedEvents["tableEventEntrust_" + entrustEl] === event) {
                $(document).off(event, entrustEl)
            }
            window.cacheBindedEvents["tableEventEntrust_" + entrustEl] = event;
            $(document).on(event, entrustEl, function() {
                var target = this;
                var index = $(target).attr(attr);
                var row = $(el).datagrid('getRows')[index];
                callBack && callBack(target, row, index);
            })
        },
        // treegrid column的formatter(val ,row,index) 不返回 它的index = undefined
        treeEventEntrust: function(options) {
            var el = options.el;
            var attr = options.attr;
            if (!el) {
                throw Error("tree表格操作的事件委托需要传递表格容器ID");
            }
            if (!attr) {
                throw Error("tree表格操作的事件委托需要传递匹配的属性值");
            }
            var event = options.event || 'click';
            // 委托的事件元素
            var entrustEl = options.entrustEl;
            var callBack = options.callBack;
            if (window.cacheBindedEvents["treeEventEntrust" + entrustEl] === event) {
                $(document).off(event, entrustEl)
            }
            window.cacheBindedEvents["treeEventEntrust" + entrustEl] = event;
            $(document).on(event, entrustEl, function() {
                var target = this;
                var filter_id = $(target).attr(attr);
                var row = null;
                var treedata = $(el).treegrid('getData');
                for (var i = 0; i < treedata.length; i++) {
                    if (treedata[i][attr] == filter_id) {
                        row = treedata[i];
                        break;
                    }
                    if (treedata[i].children.length > 0) {
                        var deepArr = treedata[i].children
                        for (var j = 0; j < deepArr.length; j++) {
                            if (deepArr[j][attr] == filter_id) {
                                row = deepArr[j];
                                break;
                            }
                        }
                    }
                }
                callBack && callBack(target, row);
            })
        },
        initSelect: function(selector, data, options) {
            var options = options || {}
            var pr = {
                valueField: 'id',
                textField: 'name',
                data: [].concat(data),
                multiple: false, // 默认单选
                editable: false, // 默认不可以输入
                autoSelect: true, // 默认自动选中
                firstData: null, //第一项数据 例：{id:'',name:'全部'} 默认不添加第一条数据
                selectedList: [] //需要选中的下标
            }
            var newOptions = Object.assign(pr, options);

            if (newOptions['firstData']) {
                newOptions['data'].unshift(newOptions['firstData']);
            }
            if (newOptions['selectedList'].length > 0) {
                $.each(newOptions['selectedList'], function(i, sIndex) {
                    newOptions['data'][sIndex]['selected'] = true;
                })
            }
            if (data.length != 0 && newOptions['autoSelect'] && newOptions['selectedList'] == 0) {
                newOptions['data'][0]['selected'] = true;
            }
            if (newOptions['multiple']) {
                newOptions['onLoadSuccess'] = function() {
                    console.log(newOptions);
                    if (options['onLoadSuccess']) {
                        options['onLoadSuccess'](data);
                    }
                }
                newOptions['onClick'] = function(row) {
                    var values, index;
                    if (row.id == '') {
                        $(this).combobox('clear');
                    } else {
                        values = $(this).combobox('getValues');
                        index = values.indexOf('');
                        if (index != -1) {
                            values.splice(index, 1);
                            $(this).combobox('setValues', values);
                        }
                    }
                    if (options['onClick']) {
                        options['onClick'](row);
                    }
                }
                $(selector).combobox(newOptions);
            } else {
                newOptions['onLoadSuccess'] = function() {
                    if (options['onLoadSuccess']) {
                        options['onLoadSuccess'](data);
                    }
                }
                newOptions['onClick'] = function(row) {
                        if (options['onClick']) {
                            options['onClick'](row);
                        }
                    }
                    // 单选
                $(selector).combobox(newOptions);
            }
            var vm = this;
            setTimeout(function() {
                vm.comboboxOnBlurByInputValueNotExist(selector, data, options, newOptions);
            }, 100)
        },
        findComboboxDataDefaultSelectValue: function(data) {
            var values = [];
            $.each(data, function(i, item) {
                if (item.selected) {
                    values.push(item.id);
                }
            });
            if (values.length == 0) {
                var value = data[0] ? data[0].id : undefined;
                if (value === undefined || value === null) {
                    value = '';
                }
                return [value]
            }
            return values;
        },
        comboboxOnBlurByInputValueNotExist: function(selector, data, option, newOptions) {
            var that = this;
            var data = [].concat(data);
            var multiple = option.multiple;
            var debug = !true;

            try {
                $(selector).combobox('textbox').off('blur');
                $(selector).combobox('textbox').on('blur', function(e) {
                    var exist = false;
                    var multiple_exist = false;
                    var selectValue = $(selector).combobox('getValue');
                    var selectValues = $(selector).combobox('getValues');
                    var selectText = $(selector).combobox('getText');
                    debug && console.log("value=" + selectValue + ",text=" + selectText)

                    if (multiple) {
                        debug && console.log('多选')
                        debug && console.log('选中的values=', selectValues);
                        var defauleValues = that.findComboboxDataDefaultSelectValue(newOptions.data);
                        debug && console.log('defaultValues=', defauleValues);
                        if (selectValues.length === 0) {
                            debug && console.log('3.1 输入框被清空，设置默认值 values=', selectValues);
                            that.initSelect(selector, data, option)

                        } else if (selectValues.length === 1 && selectValues[0] == '') {
                            debug && console.log('3.2 选中值是 全部')
                            $(selector).combobox('setText', selectText);
                            $(selector).combobox('setValue', selectValue);

                        } else {
                            var map = {};
                            $.each(newOptions.data, function(index, item) {
                                map[item.id] = true;
                            });
                            var count = 0;
                            var legal_value = [];
                            $.each(selectValues, function(index, item) {
                                if (map[item]) {
                                    legal_value.push(item);
                                    count++;
                                }
                            });
                            multiple_exist = count === selectValues.length;
                            if (!multiple_exist) {
                                debug && console.log('3.3 输入内容有一个不存在，保留合法值')
                                $(selector).combobox('setValues', legal_value.join(','));
                            } else {
                                debug && console.log('3.4 输入内容都存在，设置 输入值');
                                $(selector).combobox('setValues', selectValues.join(','));
                            }
                        }
                    } else {
                        debug && console.log('单选')
                        $.each(newOptions.data, function(index, item) {
                            debug && console.log(selectValue, item.id)
                            if (selectValue == item.id) {
                                exist = true;
                            }
                        });
                        var selectValueArr = that.findComboboxDataDefaultSelectValue(newOptions.data);
                        debug && console.log('exist:' + exist, '获取默认值数组', selectValueArr);
                        if (!exist) {
                            debug && console.log('1.1失去焦点,不存在设置默认值', selectValueArr);
                            $(selector).combobox('setText', '');
                            $(selector).combobox('setValue', selectValueArr);
                        } else {
                            if (selectValue != '') {
                                debug && console.log('2.1 存在，而且 value=' + selectValue + ',text=' + selectText);
                                $(selector).combobox('setText', selectText);
                                $(selector).combobox('setValue', selectValue);
                            } else {
                                debug && console.log('2.2 存在，而且 但是输入框为空')
                                if (selectValueArr[0] !== '') {
                                    debug && console.log('2.2.1 存在，而且 但是输入框为空,默认值不为空')
                                        // that.initSelect(selector,data,option);
                                } else {
                                    debug && console.log('2.2.2 存在，而且 但是输入框为空,默认值为空')
                                    that.initSelect(selector, data, option)
                                }
                            }
                        }
                    }

                });
            } catch (e) {
                console.log(e)
            }
        },
        submitForm: function(selector, option) {
            var ob = Object.assign({}, option);
            ob['success'] = function(resStr) {
                var jo = JSON.parse(resStr);
                if (jo['status'] == '-1000') {
                    API.METHODS.removeUserInfo();
                } else {
                    option['success'](jo)
                }
            }
            $(selector).form('submit', ob)
        },
        getTabsIndex: function(selector) {
            var tab = $(selector).tabs('getSelected');
            var index = $(selector).tabs('getTabIndex', tab);
            return index;
        },
        formatDate: function(date) {
            var year = date.getFullYear();
            var month = date.getMonth() + 1;
            var day = date.getDate();
            var hour = date.getHours();
            var minute = date.getMinutes();
            var second = date.getSeconds();
            return year + "-" + month + "-" + day + " " + hour + ":" + minute + ":" + second;
        },
        getUTime: function() {
            var now = new Date();
            var hour = now.getHours();
            var minute = now.getMinutes();
            var second = now.getSeconds();
            return (hour < 10 ? '0' + hour : hour) + ":" + (minute < 10 ? '0' + minute : minute) + ":" + (second < 10 ? '0' + second : second);
        },
        createHash: function() {
            var key = new Date().getTime() + Math.random();
            var hash = md5('value', key);
            return hash
        },
        initTraderSelect(selector, opt) {

        },
        toast: function(msg, duration) {
            var duration = isNaN(duration) ? 2000 : duration;
            var m = document.createElement('div');
            m.innerHTML = msg;
            m.style.cssText = "max-width:60%;min-width: 150px;padding:0 14px;height: 40px;color: rgb(255, 255, 255);line-height: 40px;text-align: center;border-radius: 4px;position: fixed;top: 50%;left: 50%;transform: translate(-50%, -50%);z-index: 999999;background: rgba(0, 0, 0,.7);font-size: 16px;";
            document.body.appendChild(m);
            setTimeout(function() {
                var d = 0.5;
                m.style.webkitTransition = '-webkit-transform ' + d + 's ease-in, opacity ' + d + 's ease-in';
                m.style.opacity = '0';
                setTimeout(function() { document.body.removeChild(m) }, d * 1000);
            }, duration);
        },
        exportExcel: function(selector) {
            var ob = $(selector).datagrid('options');
            var queryParams = ob['onBeforeLoad']({});
            var param = { export: 1 };
            Object.assign(param, queryParams);
            this.downloadExcel(ob.url, param);
        },
        downloadExcel: function(baseUrl, param) {
            let userInfo = STORAGE.getItem('user');
            let params = $.extend(userInfo, param);
            var iframe = document.getElementById('downloadIframe') || null;
            if (!iframe) {
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
            _this.timer = setTimeout(function() {
                var str_params = '';
                for (var name in params) {
                    str_params += '&' + name + '=' + params[name]
                }
                var url = baseUrl + '?' + str_params.substring(1);
                iframe.src = url;
            }, 300)
        },
        setDateRange: function(val) {
            var res = null;
            if (val === 'all') {
                res = ['', ''];
            } else if (val === 'currentDay') {
                res = [this.getFormatDateString(new Date()), this.getFormatDateString(new Date())]
            } else if (val === 'currentWeek') {
                var oDate = new Date();
                var currentDay = oDate.getDay() - 1;
                // console.log(currentDay)
                oDate.setDate(oDate.getDate() - currentDay);

                res = [this.getFormatDateString(oDate), this.getFormatDateString(new Date())]
            } else if (val === 'currentMonth') {
                var oDate = new Date();
                oDate.setDate(1);
                res = [this.getFormatDateString(oDate), this.getFormatDateString(new Date())]

            } else if (val === 'currentYear') {
                var oDate = new Date();
                oDate.setMonth(0);
                oDate.setDate(1);
                res = [this.getFormatDateString(oDate), this.getFormatDateString(new Date())]
            } else {
                res = ['', '']
            }
            return res;
        },
        getFormatDateString: function(date) {
            var y = date.getFullYear();
            var m = date.getMonth() + 1;
            var d = date.getDate();
            return y + '-' + this.toDou(m) + '-' + this.toDou(d);
        },
        toDou: function(n) {
            return n >= 10 ? n + '' : '0' + n;
        },
        remoteCodeSearch: function(selector) {
            function remote(search, cb) {
                API.METHODS.getData('/api/stock/new_search', { ccode: search }, function(res) {
                    if (res.status == 0) {
                        var items = $.map(res.data, function(item, index) {
                            return {
                                id: item.ccode,
                                name: item.ccode + '  ' + item.cname
                            };
                        });
                        cb && cb(items);
                    }
                }, 'get')
            }

            var class_id = 'dts_search_box' + parseInt(Math.random() * 100000000);
            $(selector).wrap(`<div class='searchBox ${class_id}'></div>`);
            var inputEle = $(selector)[0];

            $('.' + class_id).append('<ul class="selectList"></ul>')
            $('.' + class_id + ' .selectList')


            function input_logic() {
                var input = inputEle.value
                if (input.length >= 2) {
                    remote(input, callBack);
                } else {
                    $('.' + class_id + ' .selectList').removeClass('active').html('');
                }
            }

            $(selector).on('focus', input_logic);
            $(selector).on('input', input_logic);
            // 搜索框只接受数字输入
            // $(selector).on('keyup',function(){
            //     this.value=this.value.replace(/\D/g,'')
            // })

            function callBack(res) {
                var display = '';
                if (res && res.length > 0) {
                    display = '';
                    for (var i = 0; i < res.length; i++) {
                        display += `<li class="item" data-value="${res[i].id}">${res[i].name}</li>`
                    };
                    $('.' + class_id + ' .selectList').addClass('active')
                } else {
                    $('.' + class_id + ' .selectList').removeClass('active')
                }
                $('.' + class_id + ' .selectList').html(display);
                $(document).on('click', function(e) {
                    var target = e.target;
                    var have = false;
                    $('.' + class_id + ' .selectList li').each(function(index, item) {
                        if (item === target) {
                            have = true;
                        }
                    })
                    if (have) {
                        var text = target.innerHTML;
                        inputEle.value = text || '';
                        // inputEle.setAttribute('data-value', $(target).attr('data-value'));
                    }
                    $('.' + class_id + ' .selectList').removeClass('active');
                })
            }

        }
    }
}();