const path = require('path');
const VueLoaderPlugin = require('vue-loader/lib/plugin')

module.exports = {
  entry: './src/index.js',
  output: {
    filename: 'bundle.js',
    path: path.resolve(__dirname, 'dist')
  },
  module:{
    rules:[
      {test: /\.css$/,use: ['vue-style-loader','style-loader', 'css-loader']},
      {test: /\.(js)$/,use: {loader: 'babel-loader',options: {presets: ['@babel/preset-env']}}},
      {test: /\.vue$/,loader: 'vue-loader'}
    ]
  },
  plugins: [
    // make sure to include the plugin!
    new VueLoaderPlugin()
  ]
};