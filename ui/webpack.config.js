var webpack = require('webpack');
const path = require('path');

module.exports = {
    entry: './app/main.ts',

    devtool: 'inline-source-map',

    module: {
        rules: [
            {
                test: /\.ts$/,
                loader: 'ts-loader',
                exclude: /node_modules/
            },
            {
                test: /\.scss$/,
                loader: 'sass-loader',
                exclude: /node_modules/
            }
        ]
    },

    output: {
        path: path.resolve(__dirname, 'web'),
        filename: 'app.bundle.js'
    },

    resolve: {
        extensions: ['.js', '.ts', '.sccs']
    },

    performance: { hints: false }
};
