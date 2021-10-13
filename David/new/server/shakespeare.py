from flask import Flask, flash, request, jsonify, render_template, redirect, url_for, g, session, send_from_directory, \
    abort
from flask_cors import CORS
from flask_api import status

from datetime import date, datetime, timedelta
# from dateutil.parser import parse
import pytz
import os
import sys
import time
import uuid
import json
import random
import array
import string
import pathlib
import io
from uuid import UUID
from snownlp import SnowNLP
from bson.objectid import ObjectId

from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from transformers import pipeline
classifier = pipeline("zero-shot-classification",
                      model="joeddav/xlm-roberta-large-xnli")


# straight mongo access
# from pymongo import MongoClient
# from motor.motor_asyncio import AsyncIOMotorClient

# mongo
# mongo_client = MongoClient('mongodb://localhost:27017/')

# pip install -U sentence-transformers

app = Flask(__name__)
CORS(app)
basedir = os.path.abspath(os.path.dirname(__file__))

# Here are my datasets
acts = dict()
actors = dict()
zh_embeddings = dict()
en_embeddings = dict()

# local collections: 
collections = (acts, actors, zh_embeddings, en_embeddings)
prefixes = ('ac', 'at', 'ez', 'ee')
cnames = ('acts', 'actors', 'zh_embeddings', 'en_embeddings')


def tryexcept(requesto, key, default):
    lhs = None
    try:
        lhs = requesto.json[key]
        # except Exception as e:
    except:
        lhs = default
    return lhs


# test
@app.route("/test401", methods=["GET"])
def test_401():
    # from Flask import Response
    # return Response("{'a':'b'}", status=401, mimetype='application/json')
    return jsonify(("Authentication is required and has failed!", status.HTTP_401_UNAUTHORIZED))


####################################
# Acts
####################################

# endpoint to create new act
BASE_URL = None


@app.route("/act", methods=["POST"])
def add_act():
    global acts

    name = request.json['name']
    act = request.json['act']

    # ubd
    for k, g in acts.items():
        if name.lower() == g['name'].lower():
            # https://www.flaskapi.org/api-guide/status-codes/
            print("Duplicate name in acts: ", name)
            return jsonify(("Duplicate name in acts!", status.HTTP_409_CONFLICT))

    # debugging
    acts.clear()
    print("acts:", acts)
    print()

    myact = dict(name=name, act=json.loads(act), _id=str(ObjectId()))
    acts[myact['_id']] = myact
    print("acts:", acts)

    # Debugging: Verify the data gets here!
    # The secret is to write the file as bytes, in order to print hanzi instead
    # of "\u6211\u8981\u4e00\u74f6\u53ef\u4e50\uff0c\u53ef\u4ee5\u5417" for zh
    # and "W\u01d2 y\u00e0o y\u00ec p\u00edng k\u011bl\u00e8, k\u011by\u01d0 ma" for pinyin
    # For some reason, printing hanzi to screen does not work on my console :-(
    with open('shakespeare.csv', 'wb') as f:
        # f.write('迪诺\n'.encode('utf8'))
        # f.write(bytes(j['dialogue'][0]['zh'], 'utf-8'))
        # f.write('\n'.encode('utf8'))
        # f.write(j['dialogue'][0]['zh'].encode('utf-8'))
        # f.write('\n'.encode('utf8'))

        f.write(act.encode('utf8'))
        j = json.loads(act)
        f.write('\n'.encode('utf8'))
        f.write(j['dialogue'][0]['zh'].encode('utf-8'))
        f.write('\n'.encode('utf8'))
        f.write(json.dumps(acts).encode('utf-8'))
        f.write('\n'.encode('utf8'))

        # iterating over chinese sentences, 1st attempt, quite fucked up ;-)
        # for ak,av in acts.items():
        #     for dk,dv in av['act'].items():
        #             #print(dk,dv)
        #             #print(av['act']['dialogue'])
        #             for d in av['act']['dialogue']:
        #                 #print(s)
        #                 for sk,sv in d.items():
        #                     #print(d['zh'])
        #                     f.write(d['zh'].encode('utf-8'))
        #                     f.write('\n'.encode('utf8'))

        # iterating over chinese sentences:
        for ak, av in acts.items():  # iterate over all acts
            for i, d in enumerate(av['act']['dialogue']):  # iterate over all sentences
                # print(d) # print all items
                # print(d['zh']) # print chinese sentence
                f.write((str(i) + ": ").encode('utf-8'))
                f.write(d['zh'].encode('utf-8'))
                f.write('\n'.encode('utf8'))

    return jsonify(act)


# endpoint to show all act names
@app.route("/acts", methods=["GET"])
def get_acts():
    global acts
    # return jsonify([v for k,v in acts.items()])
    return jsonify(acts)


# endpoint to get act from id
@app.route("/act-fom-id/<id>", methods=["GET"])
def act_from_id(id):
    return jsonify(acts[id])


# endpoint to get act from name
@app.route("/act-fom-name/<name>", methods=["GET"])
def act_from_name(name):
    return jsonify([v['dialogue'] for k, v in acts.items() if v['name'] == name])


####################################
# Actors
####################################

# endpoint to create new actor
@app.route("/actor", methods=["POST"])
def add_actor():
    name = request.json['name']

    # ubd
    for k, g in actors.items():
        if name.lower() == g['name'].lower():
            # https://www.flaskapi.org/api-guide/status-codes/
            print("Duplicate name in actors: ", name)
            return jsonify(("Duplicate name in actors!", status.HTTP_409_CONFLICT))

    # group = dict(name=name, moniker=moniker, miles = 0, active=True, uuid=uuid.uuid1())
    actor = dict(name=name, _id=str(ObjectId()))
    actors[actor['_id']] = actor

    return jsonify(actor)


# endpoint to show all actor names
@app.route("/actors", methods=["GET"])
def get_actors():
    return jsonify([v for k, v in actors.items()])


# endpoint to get actor from id
@app.route("/actor-from-id/<id>", methods=["GET"])
def actor_from_id(id):
    return jsonify(actors[id])


@app.route("/test", methods=["POST"])
def test():
    return jsonify("hello world!")


#############################################
# Smart dialogue based on sentence similarity
#############################################

@app.route("/", methods=["GET"])
def home():
    return """Smart dialogue based on BERT embeddings:<br />
        <br />
        Mock:<br/>
        /mock-l1v1l5d1<br/>
        Bootstrap:<br/>
        /bootstrap<br />
        Acts:<br />
        /acts<br />
        Actors:<br />
        /actors<br />
    """


# cosine between two sentences
def cosine(s1, s2):
    return cosine_similarity([s1], [s2])


# show BERT embeddings
@app.route("/embeddings-en", methods=["GET"])
def my_embeddings_en():
    return jsonify(en_embeddings)


@app.route("/embeddings-zh", methods=["GET"])
def my_embeddings_zh():
    return jsonify(zh_embeddings)


# find next sentence in dialogue based on closest BERT embedding
# by looking at the cosine of the sentence with every other sentence,
# finding the one closest to 1, then returning the sentence right after.
# Note: replace spaces with _ 
@app.route("/next-en/<s>", methods=["GET"])
def next_en(s):
    global en_embeddings, acts, actors

    # restore spaces
    s = s.replace('_', ' ')

    # compute encoding
    e = model.encode(s)
    print(s, e[0:10])

    best_index = 0
    best_cosine = cosine(e, en_embeddings[0]['embedding'])
    print(0, best_cosine)

    for i in range(1, len(en_embeddings)):
        new_cosine = cosine(e, en_embeddings[i]['embedding'])
        print(i, new_cosine)
        if 1 - abs(new_cosine) < 1 - abs(best_cosine):
            best_index = i
            best_cosine = new_cosine

    print("closest sentence:")
    print(best_index, best_cosine, en_embeddings[best_index]['sentence'])

    if best_index == len(en_embeddings) - 1:
        print("end of dialogue!")
        return jsonify("end of dialogue!")
    else:
        print("next sentence in the dialogue:")
        print(best_index + 1, en_embeddings[best_index + 1]['sentence'])
        sequence_to_classify = zh_embeddings[best_index + 1]['sentence'].decode("utf-8")
        candidate_labels = ["happiness", "sadness", "fear", "disgust", "anger", "surprise"]
        print(classifier(sequence_to_classify, candidate_labels))
        return jsonify((best_index + 1, en_embeddings[best_index + 1]['sentence']))


@app.route("/next-zh/<s>", methods=["GET"])
def next_zh(s):
    global zh_embeddings, acts, actors

    # restore spaces
    s = s.replace('_', ' ')

    # compute encoding
    e = model.encode(s)
    print(s, e[0:10])

    best_index = 0
    best_cosine = cosine(e, zh_embeddings[0]['embedding'])
    print(0, best_cosine)

    for i in range(1, len(zh_embeddings)):
        new_cosine = cosine(e, zh_embeddings[i]['embedding'])
        print(i, new_cosine)
        if 1 - abs(new_cosine) < 1 - abs(best_cosine):
            best_index = i
            best_cosine = new_cosine

    print("closest sentence:")
    print(best_index, best_cosine, zh_embeddings[best_index]['sentence'].decode("utf-8"))

    if best_index == len(zh_embeddings) - 1:
        print("end of dialogue!")
        return jsonify("end of dialogue!")
    else:
        print("next sentence in the dialogue:")
        print(best_index + 1, zh_embeddings[best_index + 1]['sentence'].decode("utf-8"))
        sequence_to_classify = zh_embeddings[best_index + 1]['sentence'].decode("utf-8")
        candidate_labels = ["高兴", "难过", "恐惧", "恶心", "生气", "惊讶"]
        print(classifier(sequence_to_classify, candidate_labels))
        classifier(sequence_to_classify, candidate_labels)
        return jsonify((best_index + 1, zh_embeddings[best_index + 1]['sentence'].decode("utf-8")))


@app.route("/next", methods=["POST"])
def next():
    global en_embeddings, zh_embeddings, acts, actors

    sentence = request.json['sentence']
    language = request.json['language']
    zh = (language == 'chinese')

    # compute encoding
    e = model.encode(sentence)
    print(sentence, e[0:10])

    best_index = 0
    best_cosine = cosine(e, zh_embeddings[0]['embedding']) if zh else cosine(e, en_embeddings[0]['embedding'])
    print(0, best_cosine)

    for i in range(1, len(zh_embeddings if zh else en_embeddings)):
        new_cosine = cosine(e, zh_embeddings[i]['embedding'] if zh else en_embeddings[i]['embedding'])
        print(i, new_cosine)
        if 1 - abs(new_cosine) < 1 - abs(best_cosine):
            best_index = i
            best_cosine = new_cosine

    print("closest sentence:")
    print(best_index, best_cosine,
          zh_embeddings[best_index]['sentence'] if zh else en_embeddings[best_index]['sentence'])

    if best_index == len(zh_embeddings if zh else en_embeddings) - 1:
        print("end of dialogue!")
        return jsonify("end of dialogue!")
    else:
        print("next sentence in the dialogue:")
        print(best_index + 1,
              zh_embeddings[best_index + 1]['sentence'] if zh else en_embeddings[best_index + 1]['sentence'])
        return jsonify(
            zh_embeddings[best_index + 1]['sentence'].decode("utf-8") if zh else en_embeddings[best_index + 1][
                'sentence'])


# compute and store the BERT embeddings for all sentences in dialogue of each act
model = None


@app.route("/bootstrap", methods=["GET"])
def bootstrap():
    global model
    if not model:
        model = SentenceTransformer('stsb-roberta-large')
        print("loaded stsb-roberta-large!")

    print("evaluating embeddings for all acts...")
    if 0 < len(zh_embeddings):
        print("clearing old embeddings...")
        zh_embeddings.clear()
        en_embeddings.clear()

    # for a in acts:
    #     for i,s in enumerate(a['dialogue']):
    #         e = model.encode(s['zh'])
    #         print(i, e)
    #         print()
    #         embedding = dict(act=a['_id'], sentence_id=s['id'], embedding=e, _id=str(ObjectId()))
    #         embeddings[s['zh']] = embedding

    # iterating over sentences in dialogue:
    print("embeddings:")
    for ak, av in acts.items():  # iterate over all acts
        for i, d in enumerate(av['act']['dialogue']):  # iterate over all sentences
            # generate english embedding
            print(d['en'])
            e1 = model.encode(d['en'])
            print(i, e1[0:10])
            en_embedding = dict(act=av['_id'], sentence=d['en'], rank=i, embedding=e1, _id=str(ObjectId()))
            en_embeddings[i] = en_embedding

            # generate chinese embedding
            print(d['zh'])
            # e2 = model.encode(d['zh'].encode('utf-8'))
            e2 = model.encode(d['zh'])
            print(i, e2[0:10])
            print()
            zh_embedding = dict(act=av['_id'], sentence=d['zh'].encode('utf-8'), rank=i, embedding=e2,
                                _id=str(ObjectId()))
            zh_embeddings[i] = zh_embedding

    print("done!")
    return jsonify("done!")


####################################
# Mocking
####################################

# example
jsonString = """{"menu": {
  "id": "file",
  "value": "File",
  "popup": {
    "menuitem": [
      {"value": "New", "onclick": "CreateNewDoc()"},
      {"value": "Open", "onclick": "OpenDoc()"},
      {"value": "Close", "onclick": "CloseDoc()"}
    ]
  }
}}"""
jsonData = json.loads(jsonString)
# type(jsonData)
# print(jsonData['menu'])

# Integrated Chinese Level 1 Volume I, Lesson 5 Dialogue 1
# M1:    谁呀, Shéi ya, who is it, L5-1-1.mp3
# M2:   是我，王朋，还有李友, Shì wǒ, Wáng Péng, hái yǒu Lǐ Yǒu, It’s me Wang Peng, Li You is here, too, L5-1-2.mp3
# M1:  请进，请进，快进来, Qǐng jìn, qǐng jìn, kuài jìn lai, Please come in, please come in, come on in, L5-1-3-1.mp3
# M1:  来，我介绍一下，这是我姐姐，高小音, Lái, wǒ jièshào yí xià, zhè shì wǒ jiějie, Gāo Xiǎoyīn, Let me introduce you to one another, this is my sister, Gao Xiaoyin, L5-1-3-2.mp3, L5-1-3-3  .mp3
# M2/F1:   小音，你好, 认识你很高兴, Xiǎoyīn, nǐ hǎo, Rènshi nǐ hěn gāoxìng, How do you do, Xiaoyin, pleased to meet you, L5-1-4-1.mp3, L5-1-4-2.mp3,
# F2:   认识你们我也很高兴, Rènshi nǐmen wǒ yě hěn gāoxìng, Pleased to meet you, too, L5-1-5.mp3
# F1：你们家很大，也很漂亮, Nǐmen jiā hěn dà, yě hěn piàoliang, Your home is very big, and very beautiful, too, L5-1-6-1.mp3, L5-1-6-2.mp3
# F2:   是吗，请坐，请坐, Shì ma? Qǐng zuò, qǐng zuò, Really, have a seat, please, L5-1-7.mp3
# M1:   小音，你在哪儿工作, Xiǎoyīn, nǐ zài nǎr gōngzuò, Xiaoyin, where do you work, L5-1-8.mp3
# F2:   我在学校工作, Wǒ zài xuéxiào gōngzuò, I work at a school, L5-1-9-1.mp3 
# F2:   你们想喝点儿什么, 喝茶还是喝咖啡, Nǐmen xiǎng hē diǎnr shénme, Hē chá háishi hē kāfēi, What would you like to drink, tea or coffee, L5-1-9-2.mp3, L5-1-9-3.mp3
# M1:   我喝茶吧, Wǒ hē chá ba, I’ll have tea, L5-1-10.mp3 
# F1:   我要一瓶可乐，可以吗, Wǒ yào yì píng kělè, kěyǐ ma, I’d like a bottle of cola, is that OK, L5-1-11.mp3 
# F2:   对不起，我们家没有可乐, Duìbuqǐ, wǒmen jiā méi yǒu kělè, I’m sorry, we don’t have cola, L5-1-12.mp3 
# F1:   那给我一杯水吧, nà gěi wǒ yī bēi shuǐ ba, Then please give me a glass of water, L5-1-13.mp3 

# L1V1L5D1
l1v1l5d1 = """{
"title": "Integrated Chinese Level 1 Volume I, Lesson 5 Dialogue 1", 
"actors": [
    {"name": "Li You", "id": "F1"},
    {"name": "Wang Peng", "id": "M1"},
    {"name": "Gao Xiaoyin", "id": "F2"}
],
"dialogue": [
    {"id": 1,
    "actor": "F1",
    "zh": "谁呀",
    "py": "Shéi ya?",
    "en": "who is it?",
    "mp3": "L5-1-1.mp3"
    },
    {"id": 2,
    "actor": "M1",
    "zh": "是我，王朋，还有李友",
    "py": "Shì wǒ, Wáng Péng, hái yǒu Lǐ Yǒu.",
    "en": "It’s me Wang Peng, Li You is here, too.",
    "mp3": "L5-1-2.mp3"
    },
    {"id": 3,
    "actor": "F1",
    "zh": "请进，请进，快进来",
    "py": "Qǐng jìn, qǐng jìn, kuài jìn lai",
    "en": "Please come in, please come in, come on in",
    "mp3": "L5-1-3-1.mp3"
    },
    {"id": 4,
    "actor": "M1",
    "zh": "来，我介绍一下，这是我姐姐，高小音",
    "py": "Lái, wǒ jièshào yí xià, zhè shì wǒ jiějie, Gāo Xiǎoyīn",
    "en": "",
    "mp3": ["L5-1-3-2.mp3", "L5-1-3-3.mp3"]
    },
    {"id": 5,
    "actor": "F1",
    "zh": "小音，你好, 认识你很高兴",
    "py": "Xiǎoyīn, nǐ hǎo, Rènshi nǐ hěn gāoxìng",
    "en": "How do you do, Xiaoyin, pleased to meet you",
    "mp3": ["L5-1-4-1.mp3", "L5-1-4-2.mp3"]
    },
    {"id": 6,
    "actor": "F2",
    "zh": "你们家很大，也很漂亮,",
    "py": "Nǐmen jiā hěn dà, yě hěn piàoliang",
    "en": "Your home is very big, and very beautiful, too,",
    "mp3": ["L5-1-6-1.mp3", "L5-1-6-2.mp3"]
    },
    {"id": 7,
    "actor": "F1",
    "zh": "是吗，请坐，请坐",
    "py": "Shì ma? Qǐng zuò, qǐng zuò,",
    "en": "Really, have a seat, please,",
    "mp3": "L5-1-7.mp3"
    },
    {"id": 8,
    "actor": "F1",
    "zh": "小音，你在哪儿工作?",
    "py": "Xiǎoyīn, nǐ zài nǎr gōngzuò?",
    "en": "Xiaoyin, where do you work?",
    "mp3": "L5-1-8.mp3"
    },
    {"id": 9,
    "actor": "F2",
    "zh": "我在学校工作",
    "py": "Wǒ zài xuéxiào gōngzuò",
    "en": "I work at a school",
    "mp3": "L5-1-9-1.mp3"
    },
    {"id": 10,
    "actor": "F1",
    "zh": "你们想喝点儿什么, 喝茶还是喝咖啡?",
    "py": "Nǐmen xiǎng hē diǎnr shénme, Hē chá háishi hē kāfēi?",
    "en": "What would you like to drink, tea or coffee?",
    "mp3": ["L5-1-9-2.mp3", "L5-1-9-3.mp3"]
    },
    {"id": 11,
    "actor": "M1",
    "zh": "我喝茶吧",
    "py": "Wǒ hē chá ba",
    "en": "I’ll have tea",
    "mp3": "L5-1-10.mp3"
    },
    {"id": 12,
    "actor": "F2",
    "zh": "我要一瓶可乐，可以吗",
    "py": "Wǒ yào yì píng kělè, kěyǐ ma",
    "en": "I’d like a bottle of cola, is that OK",
    "mp3": "L5-1-11.mp3 "
    },
    {"id": 13,
    "actor": "F1",
    "zh": "对不起，我们家没有可乐",
    "py": "Duìbuqǐ, wǒmen jiā méi yǒu kělè",
    "en": "I’m sorry, we don’t have cola",
    "mp3": "L5-1-12.mp3"
    },
    {"id": 14,
    "actor": "F2",
    "zh": "那给我一杯水吧",
    "py": "nà gěi wǒ yī bēi shuǐ ba",
    "en": "Then please give me a glass of water",
    "mp3": "L5-1-13.mp3"
    }
]
}"""

l1v1l10d1 = """{
"title": "Integrated Chinese Level 1 Volume I, Lesson 10 Dialogue 1", 
"actors": [
    {"name": "Li You", "id": "F1"},
    {"name": "Wang Peng", "id": "M1"}
],
"dialogue": [
    {"id": 1,
    "actor": "M1",
    "zh": "李友，寒假回家吗？",
    "py": "Li Yǒu, hán jià nǐ huí jiā mā?",
    "en": "Li You, are you going home during winter vacation?",
    "mp3": "L10-1-1.mp3"
    },
    {"id": 2,
    "actor": "F1",
    "zh": "对，我要回家",
    "py": "Duì, wo yào huí jiā.",
    "en": "Yes i'm going home",
    "mp3": "L10-1-2.mp3"
    },
    {"id": 3,
    "actor": "M1",
    "zh": "飞机票你买了吗",
    "py": "Feī jī piào ni mǎi le ma?",
    "en": "Have you bought the plane ticket?",
    "mp3": "L10-1-3.mp3"
    },
    {"id": 4,
    "actor": "F1",
    "zh": "已经买了。是二十一号的。",
    "py": "Yǐ jīng mǎi le. Shì èr shí yī hào de.",
    "en": "",
    "mp3": "L10-1-4.mp3"
    },
	{"id": 5,
    "actor": "M1",
    "zh": "飞机是几点的？",
    "py": "Feī jī shì jǐ diǎn de?",
    "en": "What time is the plane?",
    "mp3": "L10-1-5.mp3"
    },
    {"id": 6,
    "actor": "F1",
    "zh": "晚上八点的",
    "py": "Wǎn shàng bā diǎn de.",
    "en": "At eight o'clock in the evening",
    "mp3": "L10-1-6.mp3"
    },
    {"id": 7,
    "actor": "M1",
    "zh": "你怎么去机场?",
    "py": "Nǐ zěn me qù jī chǎng?",
    "en": "How do you get to the airport?",
    "mp3": "L10-1-7.mp3"
    },
    {"id": 8,
    "actor": "F1",
    "zh": "我想坐公共汽车或者坐地铁.你知道怎么走吗?",
    "py": "Wǒ xiǎng zuò gōnggòng qìchē huòzhě zuò dìtiě. Nǐ zhī dào zěn me zǒu ma?",
    "en": "I want to take the bus or the subway. Do you know how to go?",
    "mp3": "L10-1-8.mp3"
    },
    {"id": 9,
    "actor": "M1",
    "zh": "你先坐一路汽车，坐三站下车，然后换地铁。先做红线，再换绿线，最后换蓝线。",
    "py": "Nǐ xiān zuò yīlù qìchē, zuò sān zhàn xià chē, ránhòu huàn dìtiě. Xiān zuò hóngxiàn, zài huàn lǜ xiàn, zuìhòu huàn lán xiàn.",
    "en": "You first take Bus No. 1. Get off after three stops. Then take the subway. First take the red line, then change to the green line, and finally change to the blue line",
    "mp3": "L10-1-9.mp3"
    },
    {"id": 10,
    "actor": "F1",
    "zh": "不行，不行，太麻烦了。我还是打车吧。",
    "py": "Bù xíng, bù xíng, tài má fán le. Wǒ hái shì dǎ chē ba. Chū zū qì chē tài guì, wǒ kāi chē sòng nǐ qù ba.",
    "en": "No, no, too much trouble. I'll take a taxi",
    "mp3": "L10-1-10.mp3"
    },
    {"id": 11,
    "actor": "M1",
    "zh": "出租汽车太贵.我开车送你去吧",
    "py": "Chūzū qìchē tài guì. Wǒ kāichē sòng nǐ qù ba",
    "en": "The taxi is too expensive. I'll drive you there",
    "mp3": "L10-1-11.mp3"
    },
    {"id": 12,
    "actor": "F1",
    "zh": "谢谢你。",
    "py": "Xièxie nǐ.",
    "en": "Thank you.",
    "mp3": "L10-1-12.mp3 "
    },
    {"id": 13,
    "actor": "M1",
    "zh": "四点半，没问题，我在办公室等你。不用客气。",
    "py": "Sì diǎn bàn, méi wèntí, wǒ zài bàngōngshì děng nǐ. Bùyòng kèqì",
    "en": "4:30, no problem, I'll wait for you in the office. Don’t mention it",
    "mp3": "L10-1-13.mp3"
    }
]
}"""


@app.route("/mock-l1v1l5d1", methods=["GET"])
def mock_l1v1l5d1():
    json_data_all = []
    with app.test_client() as c:
        # 1. actors
        json_data = []
        json_data_all.append("@@@ actors")
        rv = c.post('/actor', json={
            'name': 'Li You'
        })
        json_data.append(rv.get_json())
        rv = c.post('/actor', json={
            'name': 'Wang Peng'
        })
        json_data.append(rv.get_json())
        rv = c.post('/actor', json={
            'name': 'Gao Xiaoyin'
        })
        json_data.append(rv.get_json())
        json_data_all.append(actors)

        # 2. acts
        json_data = []
        json_data_all.append("@@@ acts")
        rv = c.post('/act', json={
            'name': 'l1v1l5d1', 'act': l1v1l5d1
        })
        json_data.append(rv.get_json())
        json_data_all.append(acts)

    return jsonify(json_data_all)


if __name__ == '__main__':
    app.config['JSON_AS_ASCII'] = False
    app.run(debug=True)
