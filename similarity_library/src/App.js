import React, { Component } from 'react';
// import CssBaseline from '@material-ui/core/CssBaseline';
// import Appbar from './components/Appbar.js';
import './App.css';
import ChatBot from 'react-simple-chatbot';
// var express = require('express');
// var app = express();
var similarity = require('sentence-similarity')
var similarityScore = require('similarity-score')

// Docs at https://lucasbassetti.com.br/react-simple-chatbot/

const obj = {
           '你好':'你好',
           '白英爱你周末喜欢做什么': '我喜欢打球看电视你呢',
           '我喜欢打球看电视你呢':'我喜欢唱歌跳舞还喜欢听音乐',
           '我喜欢唱歌跳舞还喜欢听音乐': '你也喜欢看书对不对',
           '你也喜欢看书对不对':'对有的时候也喜欢看书',
           '对有的时候也喜欢看书': '你喜不喜欢看电影',
           '你喜不喜欢看电影': '喜欢，我周末常常看电影',
           '喜欢，我周末常常看电影': '那我们今天晚上去看一个外国电影怎么样',
           '那我们今天晚上去看一个外国电影怎么样': '我请客',
           '我请客': '为什么你请客',
           '为什么你请客': '因为昨天你请我吃饭所以今天我请你看电影',
           '因为昨天你请我吃饭所以今天我请你看电影': '那你也请王朋李友好吗',
           '那你也请王朋李友好吗': '好'}
const data = {}
const steps = [
  {
    id: '1',
    message: '请开始对话',
    trigger: '2',
  },
  {
    id: '2',
    user: true,
    validator: (value) => {
      for (const s1 of Object.keys(obj)) {
        const winkOpts = { f: similarityScore.winklerMetaphone, options : {threshold: 0} }
        const score = similarity([s1], [value], winkOpts).matchScore[0]
        console.log(score)
        if (score >= 0.4) {
          data.str = obj[s1]
          return true
        }
      }
      return '你能再说一次吗';
    },
    trigger: '3',
  },
  {
    id: '3',
    message: ({ previousValue, steps }) => data.str,
    trigger: '2',
  },
];

class App extends Component {
  render() {
    return (
      <div>
        <ChatBot headerTitle="Speech Recognition" recognitionEnable={true} steps={steps} />
	    </div>
    );
  }
}

export default App; 