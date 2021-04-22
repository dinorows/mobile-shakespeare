var express = require('express');
var app = express();
var similarity = require('sentence-similarity')
var similarityScore = require('similarity-score')
require('@tensorflow/tfjs');
const use = require('@tensorflow-models/universal-sentence-encoder');

 
const s1 = ['白英爱，你周末喜欢做什么?']
const s2 = ['白英爱，你周末一般喜欢干嘛?']
 
const winkOpts = { f: similarityScore.winklerMetaphone, options : {threshold: 0} }



app.get('/', function (req, res) {
  res.send('Hello World!');
});

app.get('/ss', function (req, res) {
    res.send(similarity(s1, s2, winkOpts));
  });


app.listen(3000, function () {
    // console.log('Example app listening on port 3000!');
    console.log(similarity(s1, s2, winkOpts));
      // Load the model.
	use.load().then(model => {
        // Embed an array of sentences.
        const sentences = [
          '白英爱，你喜欢做什么?',
          '你周末喜欢干嘛?'
        ];
        model.embed(sentences).then(embeddings => {
        // `embeddings` is a 2D tensor consisting of the 512-dimensional embeddings for each sentence.
        // So in this example `embeddings` has the shape [2, 512].
        embeddings.print(true /* verbose */);
        });
      });
});
