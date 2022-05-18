var webpackDevConfig = {
    // devtool:'eval-source-map',
    devServer: {
        historyApiFallback: true,
        contentBase: "./",
        publicPath: '/dist/',
        compress: false,
        quiet: false, //控制台中不输出打包的信息
        noInfo: false,
        hot: false, //开启热点
        inline: true, //开启页面自动刷新
        lazy: false, //不启动懒加载
        progress: true, //显示打包的进度
        host: '127.0.0.1',
        port: '9090', //设置端口号
        //其实很简单的，只要配置这个参数就可以了
        proxy: {
            // '/api/*': {
            // 	target: 'http://team.dts.youlikj.com/',
            // 	secure: false,
            // 	changeOrigin: true
            // },
            '/api/': {
                //target: 'http://beta.dts.youlikj.com/',
				target: 'http://127.0.0.1:9091/',
                secure: false,
                changeOrigin: true
            },
        }

    }
}

module.exports = webpackDevConfig;
