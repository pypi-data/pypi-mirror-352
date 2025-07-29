const path = require('path');

module.exports = {
    entry: {
        index: './assets/src/index.js',
    },
    module: {
        rules: [
            {
                test: /\.css$/i,
                use: ["style-loader", "css-loader"],
            },
        ],
    },
    output: {
        filename: '[name].bundle.js',
        path: path.resolve(__dirname, './src/djangocms_fomantic_ui/static/djangocms_fomantic_ui/webpack'),
        clean: true,
    },
    mode: 'production',
};