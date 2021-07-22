import React, { Component } from 'react';
import CssBaseline from '@material-ui/core/CssBaseline';
import Appbar from './components/Appbar.js';
import { script } from './script.js';
import { dialogue } from './dialogue.js';
import './App.css';

// Docs at https://lucasbassetti.com.br/react-simple-chatbot/
import ChatBot from 'react-simple-chatbot';

require('@tensorflow/tfjs');
const use = require('@tensorflow-models/universal-sentence-encoder');

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

class TFJS extends Component {
  constructor(props) {
    super(props);

    this.state = {
      trigger: false,
    }

    this.triggerNext = this.triggerNext.bind(this);
  }

  triggerNext() {
    this.setState({ trigger: true }, () => {
      this.props.triggerNextStep();
    });
  }

  async componentDidMount() {
    const { steps } = this.props;
    console.log(steps);
    const search = steps.search.value;

    const ret = await getDialogue(search);
    console.log(ret);
    this.triggerNext({ value: ret, trigger: '4' });
  }

  render() {
    return (<div></div>);
  }
}

async function getDialogue(previousValue) {
  const model = await use.load();

  // let comp = [previousValue].concat(dialogue);
  // const embeddings = await model.embed(comp);
  // embeddings.print(true /* verbose */);
  // let arr = embeddings.arraySync();
  let dist = 0;

  let response = 'a';


  // var index = scores.indexOf(Math.min.apply(Math, scores));
  // var response;

  // if (index === scores.length) {
  //   response = "No more dialogue."
  // } else {
  //   response = dialogue[index + 1];
  // }

  return response;
}

const steps = [
  {
    id: '1',
    message: 'Say a line from Hamlet',
    trigger: 'search',
  },
  {
    id: 'search',
    user: true,
    trigger: '3',
  },
  {
    id: '3',
    component: <TFJS />,
    // asMessage: true,
    // replace: true,
    waitAction: true,
    trigger: 'search'
  },
  {
    id: '4',
    message: 'Done',
    trigger: 'search'
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