var path = require('path')
var styles = path.resolve(__dirname, './frontend/assets/scss/app.scss');

const { VueLoaderPlugin } = require('vue-loader');
const CssExtractPlugin = require("mini-css-extract-plugin");
const FriendlyErrorsWebpackPlugin = require("friendly-errors-webpack-plugin")


module.exports = {
    entry: ['./frontend/index.ts', styles],
    output: {
        path: path.resolve(__dirname, './app/static/'),
        publicPath: '/static/',
    },
    resolve: {
        extensions: [".js", ".json", ".ts", ".tsx", ".js", ".vue"],
        alias: {
            vue: 'vue/dist/vue.js'
        }
    },
    module: {
        rules: [
            {
                test: /\.vue$/,
                loader: 'vue-loader',
                options: {
                    esModule: true
                },
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
                test: /\.js$/,
                enforce: "pre",
                loader: "source-map-loader"
            },
            {
                test: /\.tsx?$/,
                loader: "ts-loader",
                exclude: /node_modules/,
                options: {
                    appendTsSuffixTo: [/\.vue$/],
                },
            },
            {
                test: /\.pug$/,
                loader: "pug-plain-loader",
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
    plugins: [
        new VueLoaderPlugin(),
        new FriendlyErrorsWebpackPlugin(),
        new CssExtractPlugin({
            filename: "styles.css",
        })
    ],
    devtool: "inline-source-map"
};
