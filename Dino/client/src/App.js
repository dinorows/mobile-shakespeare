import React, { useRef, useState } from "react";
import SpeechRecognition, { useSpeechRecognition } from "react-speech-recognition";
import pinyin from "pinyin";
//import nodejieba from "nodejieba";
import microPhoneIcon from "./microphone.svg";
import usIcon from "./us.svg";
import cnIcon from "./cn.svg";
import pinyinIcon from "./pinyin.jpg";
import './App.css';

function App() {
  const { transcript, resetTranscript } = useSpeechRecognition({ });
  const [mypinyin, setMyPinyin] = useState('');
  const [reply, setReply] = useState('');
  const [zh, setZh] = useState(false);
  const [isListening, setIsListening] = useState(false);
  const microphoneRef = useRef(null);

  const handleEnglish = () => {
    setZh(false);
    setIsListening(true);
    microphoneRef.current.classList.add("listening");
    SpeechRecognition.startListening({
      continuous: true,
	    language: 'en-US'
    });
  };

  const handleChinese = () => {
    setZh(true);
    setIsListening(true);
    microphoneRef.current.classList.add("listening");
    SpeechRecognition.startListening({
      continuous: true,
	    language: 'zh-CN'
    });
  };

  const handlePinyin = () => {
    setIsListening(false);
    //microphoneRef.current.classList.remove("listening");
    //SpeechRecognition.stopListening();

    if (!zh) {
      return;
    }

    //const jcut = nodejieba.cut(transcript);
    //console.log(jcut);
    if ( 0 < transcript.length) {
      const pnyn = pinyin(transcript, {
        group: true,
        style: pinyin.STYLE_TONE,
      });
      console.log(pnyn);
      resetTranscript();
      setMyPinyin(pnyn);
    }
    else if ( 0 < reply.length) {
      const pnyn = pinyin(reply, {
        group: true,
        style: pinyin.STYLE_TONE,
      });
      console.log(pnyn);
      setReply('');
      setMyPinyin(pnyn);
    }
  };

  const replyDialogue = () => {
    setIsListening(false);
    microphoneRef.current.classList.remove("listening");
    SpeechRecognition.stopListening();

    // call server
    const postSentence = async (s, l) => {
      const paramdict = {
        'sentence': s,
        'language': l,
      }

      try {
        const config = {
            method: 'POST',
            headers: {
                'Accept': 'application/json',
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(paramdict)
        }
        const response = await fetch("http://localhost:5000/next", config);

        if (response.ok) {
            console.log("launch: success on send.");
        } else {
            alert("launch: failure on send!");
        }

        try {
          const serversaid = await response.json();
          console.log("launch: on reply:")
          console.log(serversaid);

          // refresh UI
          resetTranscript();
          setReply(serversaid);

        } catch (err) {
          console.log(err);
          alert("exception on launch/reply!");
        }

      } catch (error) {
        console.log(error);
        alert("exception on launch/send");
      }
    };

    postSentence(transcript, zh? "chinese": "english");
  };

  const stopListening = () => {
    setIsListening(false);
    microphoneRef.current.classList.remove("listening");
    SpeechRecognition.stopListening();
  };

  const handleReset = () => {
    stopListening();
    resetTranscript();
    setMyPinyin('');
    setReply('');
  };

  return (
    <div className="microphone-wrapper">

      <h1>HuskyChat</h1>
      <h4>Northeastern University 2021</h4>
      <h6>Xinru He, William Cui, Ann Cai, Dino Konstantopoulos</h6>

      {!SpeechRecognition.browserSupportsSpeechRecognition() &&
        <div className="mircophone-container">
          Browser does not Support Speech Recognition!
        </div>
      }

      {SpeechRecognition.browserSupportsSpeechRecognition() &&
        <div className="mircophone-container">
          <div
              className="microphone-icon-container"
              ref={microphoneRef}
              onClick={handleEnglish}
            >
              <img src={usIcon} alt='microphone' className="microphone-icon" />
          </div>

          <div
              className="microphone-icon-container"
              ref={microphoneRef}
              onClick={handleChinese}
            >
              <img src={cnIcon} alt='microphone' className="microphone-icon" />
          </div>

          <div
              className="microphone-icon-container"
              //ref={microphoneRef}
              onClick={handlePinyin}
            >
              <img src={pinyinIcon} alt='microphone' className="microphone-icon" />
          </div>

          <div className="microphone-status">
              {isListening ? "Listening........." : "Click to talk"}
          </div>

          {isListening && (
            <button className="microphone-stop btn" onClick={replyDialogue}>
            Chatbot
          </button>
          )}

        </div>
      }

      {transcript && (
        <div className="microphone-result-container">
        <div className="microphone-result-text">{transcript}</div>
        <button className="microphone-reset btn" onClick={handleReset}>
          Reset
        </button>
      </div>
      )}
      {mypinyin && (
        <div className="microphone-result-container">
        <div className="microphone-result-text">{mypinyin}</div>
        <button className="microphone-reset btn" onClick={handleReset}>
          Reset
        </button>
      </div>
      )}
      {reply && (
        <div className="microphone-result-container">
        <div className="microphone-result-text">{reply}</div>
        <button className="microphone-reset btn" onClick={handleReset}>
          Reset
        </button>
      </div>
      )}

    </div>
  );
}

export default App;
