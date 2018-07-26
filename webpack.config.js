var path = require('path')
var styles = path.resolve(__dirname, './frontend/assets/scss/app.scss');

const { VueLoaderPlugin } = require('vue-loader');
const CssExtractPlugin = require("mini-css-extract-plugin");

module.exports = {
    entry: ['./frontend/main.js', styles],
    output: {
        path: path.resolve(__dirname, './app/static/'),
        publicPath: '/static/',
    },
    module: {
        rules: [
            {
                test: /\.vue$/,
                use: 'vue-loader'
            },
            {
                test: /\.scss$/,
                exclude: styles,
                use: [
                    'vue-style-loader',
                    'css-loader',
                    'sass-loader'
                ],
            },
            {
                test: /\.(png|jpg|gif)$/,
                loader: 'file-loader',
                options: {
                    name: '[name].[ext]?[hash]',
                    outputPath: 'images/',
                }
            },
            {
                test: styles,
                use: [
                    CssExtractPlugin.loader,
                    'css-loader',
                    'sass-loader',
                ],
            },
            {
                test: /\.(woff(2)?|ttf|eot|svg)(\?v=\d+\.\d+\.\d+)?$/,
                use: [{
                    loader: 'file-loader',
                    options: {
                        name: '[name].[ext]',
                        outputPath: 'fonts/'
                    }
                }]
            }
        ]
    },
    resolve: {
        alias: {
            vue: 'vue/dist/vue.js'
        }
    },
    plugins: [
        new VueLoaderPlugin(),
        new CssExtractPlugin({
            filename: "styles.css",
        })
    ]
}
