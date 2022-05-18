from . import handlers 

handlers = [
    (r"/", handlers.test.TestHandler),
    #图形验证码
    (r"/api/imgcode/get", handlers.imgcode.GetHandler),#获取图形验证码
    (r"/api/imgcode/valid", handlers.imgcode.ValidHandler),#验证图形验证码

    #用户
    (r"/api/user/login", handlers.user.LoginHandler),#登录
    (r"/api/user/logout", handlers.user.LogoutHandler),#退出
    (r"/api/user/check", handlers.user.CheckHandler),#判断是否登录

    #交易
    (r"/api/stock/order", handlers.stock.OrderHandler),#股票下单
    # (r"/stock/batch/order", handlers.stock.BatchOrderHandler),#股票批量下单（平头寸）
    (r"/api/stock/cancel", handlers.stock.CancelHandler),#撤单

    #查询
    (r"/api/query/position", handlers.query.PositionHandler),#查询交易底仓
    (r"/api/query/public/position", handlers.query.PublicPositionHandler),#查询交易底仓(公共券池)
    (r"/api/query/cash", handlers.query.CashHandler),#查询交易头寸
    (r"/api/query/dorder", handlers.query.DorderHandler),#查询当日委托记录
    (r"/api/query/dcancel", handlers.query.DcancelHandler),#查询当日可撤单列表

    (r"/api/query/profit", handlers.query.ProfitHandler),#查询盈亏报表
    (r"/api/query/order", handlers.query.OrderHandler),#查询委托记录
    (r"/api/query/fill", handlers.query.FillHandler),#查询成交记录

    #导出
    (r"/api/export/profit", handlers.importdata.ProfitHandler),#导出盈亏报表
    (r"/api/export/order", handlers.importdata.OrderHandler),#导出委托
    (r"/api/export/fill", handlers.importdata.FillHandler),#导出成交

    #其他
    (r"/api/stock/search", handlers.query.SearchHandler),#股票搜索
    (r"/api/stock/bscount", handlers.query.StockBscountHandler),#获取单个股票的最大可买卖数量
    (r"/api/faccount/list", handlers.query.FaccountListHandler),#获取资金账户列表
    (r"/api/query/configinfo", handlers.query.ConfiginfoHandler),#获取配置信息
    (r"/api/query/traderinfo", handlers.user.UserinfoHandler),#获取配置信息
    (r"/api/stock/new_search", handlers.query.NewSearchHandler),#股票搜索(新版)
    (r"/api/quote/get", handlers.query.QuoteHandler),


]





