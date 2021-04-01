import React, { Component } from 'react';
import CssBaseline from '@material-ui/core/CssBaseline';
import Appbar from './components/Appbar.js';
import { script } from './script.js';
import './App.css';

// Docs at https://lucasbassetti.com.br/react-simple-chatbot/
import ChatBot from 'react-simple-chatbot';

function getScript({ previousValue, steps }) {
  let i = script.findIndex((e) =>
    e.toLowerCase().replace(/[!"#$%&()*+,-./:;<=>?@[\]^_`{|}~]/g, '') === previousValue.toLowerCase()
  );
  if (i === -1) {
    return 'Cannot find line.';
  } else if (i === script.length) {
    return 'End of script';
  } else {
    return script[i + 1];
  }
}

const steps = [
  {
    id: '1',
    message: 'Say a line from Hamlet',
    trigger: '2',
  },
  {
    id: '2',
    user: true,
    trigger: '3',
  },
  {
    id: '3',
    message: getScript,
    trigger: '2'
  }
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