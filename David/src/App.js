import React, { Component } from 'react';
import CssBaseline from '@material-ui/core/CssBaseline';
import Appbar from './components/Appbar.js';
import './App.css';

// Docs at https://lucasbassetti.com.br/react-simple-chatbot/
import ChatBot from 'react-simple-chatbot';
const obj = {'hi':'welcome',
           'Gregory, on my word, we’ll not carry coals.': 'No, for then we should be colliers.',
           'No, for then we should be colliers.':'I mean, if we be in choler, we’ll draw.',
           'I mean, if we be in choler, we’ll draw.': 'Ay, while you live, draw your neck out o’ the collar.',
           'Ay, while you live, draw your neck out o’ the collar.':'I strike quickly, being moved.',
           'I strike quickly, being moved.': 'But thou art not quickly moved to strike.',
           'But thou art not quickly moved to strike.': 'A dog of the house of Montague moves me.',
           'A dog of the house of Montague moves me.': 'To move is to stir; and to be valiant is to stand: therefore, if thou art moved, thou runn’st away.',
           'To move is to stir; and to be valiant is to stand: therefore, if thou art moved, thou runn’st away.': 'A dog of that house shall move me to stand.I will take the wall of any man or maid of Montague’s.',
           'A dog of that house shall move me to stand.I will take the wall of any man or maid of Montague’s.': 'That shows thee a weak slave, for the weakest goes to the wall.',
           'That shows thee a weak slave, for the weakest goes to the wall.': 'True, and therefore women, being the weaker vessels, are ever thrust to the wall: therefore I will push Montague’s men from the wall, and thrust his maids to the wall.',
           'True, and therefore women, being the weaker vessels, are ever thrust to the wall: therefore I will push Montague’s men from the wall, and thrust his maids to the wall.': 'The quarrel is between our masters and us their men.',
           'The quarrel is between our masters and us their men.': '’Tis all one, I will show myself a tyrant: when I have fought with the men I will be civil with the maids, I will cut off their heads.',
           '’Tis all one, I will show myself a tyrant: when I have fought with the men I will be civil with the maids, I will cut off their heads.': 'The heads of the maids?',
           'The heads of the maids?': 'Ay, the heads of the maids, or their maidenheads; take it in what sense thou wilt.',
           'Ay, the heads of the maids, or their maidenheads; take it in what sense thou wilt.': 'They must take it in sense that feel it.',
           'They must take it in sense that feel it.': 'Me they shall feel while I am able to stand: and ’tis known I am a pretty piece of flesh.',
           'Me they shall feel while I am able to stand: and ’tis known I am a pretty piece of flesh.': '’Tis well thou art not fish; if thou hadst, thou hadst been poor John. Draw thy tool; here comes of the house of Montagues.'}
      
const steps = [
  {
    id: '1',
    message: 'Please say a sentence in Romeo and Juliet by William SHakespeare',
    trigger: '2',
  },
  {
    id: '2',
    user: true,
    validator: (value) => {
      if (obj[(String(value))] === undefined) {
        return 'Please say a sentence in Romeo and Juliet';
      }
      return true;
    },
    trigger: '3',
  },
  {
    id: '3',
    message: ({ previousValue, steps }) => obj[previousValue],
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