from flask import Flask, flash, request, jsonify, render_template, redirect, url_for, g, session, send_from_directory, abort
from flask_cors import CORS
from flask_api import status

from datetime import date, datetime, timedelta
#from dateutil.parser import parse
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
from bson.objectid import ObjectId

from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

# straight mongo access
#from pymongo import MongoClient
#from motor.motor_asyncio import AsyncIOMotorClient

# mongo
#mongo_client = MongoClient('mongodb://localhost:27017/')

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
    #from Flask import Response
    #return Response("{'a':'b'}", status=401, mimetype='application/json')
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

    #ubd
    for k,g in acts.items():
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
    with open('shakespeare.csv','wb') as f:
        # f.write('??????\n'.encode('utf8'))
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
        for ak,av in acts.items(): # iterate over all acts
            for i,d in enumerate(av['act']['dialogue']): # iterate over all sentences
                #print(d) # print all items
                #print(d['zh']) # print chinese sentence
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
    return jsonify([v['dialogue'] for k,v in acts.items() if v['name'] == name])


####################################
# Actors
####################################

# endpoint to create new actor
@app.route("/actor", methods=["POST"])
def add_actor():
    name = request.json['name']

    #ubd
    for k,g in actors.items():
        if name.lower() == g['name'].lower():
            # https://www.flaskapi.org/api-guide/status-codes/
            print("Duplicate name in actors: ", name)
            return jsonify(("Duplicate name in actors!", status.HTTP_409_CONFLICT))

    #group = dict(name=name, moniker=moniker, miles = 0, active=True, uuid=uuid.uuid1())
    actor = dict(name=name, _id=str(ObjectId()))
    actors[actor['_id']] = actor

    return jsonify(actor)

# endpoint to show all actor names
@app.route("/actors", methods=["GET"])
def get_actors():
    return jsonify([v for k,v in actors.items()])

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
    print(best_index, best_cosine, zh_embeddings[best_index]['sentence'])

    if best_index == len(zh_embeddings) - 1:
        print("end of dialogue!")
        return jsonify("end of dialogue!")
    else:
        print("next sentence in the dialogue:")
        print(best_index + 1, zh_embeddings[best_index + 1]['sentence'])
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
    print(best_index, best_cosine, zh_embeddings[best_index]['sentence'] if zh else en_embeddings[best_index]['sentence'])

    if best_index == len(zh_embeddings if zh else en_embeddings) - 1:
        print("end of dialogue!")
        return jsonify("end of dialogue!")
    else:
        print("next sentence in the dialogue:")
        print(best_index + 1, zh_embeddings[best_index + 1]['sentence'] if zh else en_embeddings[best_index + 1]['sentence'])
        return jsonify(zh_embeddings[best_index + 1]['sentence'].decode("utf-8") if zh else en_embeddings[best_index + 1]['sentence'])


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
    for ak,av in acts.items(): # iterate over all acts
        for i,d in enumerate(av['act']['dialogue']): # iterate over all sentences
            # generate english embedding
            print(d['en'])
            e1 = model.encode(d['en'])
            print(i, e1[0:10])
            en_embedding = dict(act=av['_id'], sentence=d['en'], rank=i, embedding=e1, _id=str(ObjectId()))
            en_embeddings[i] = en_embedding

            # generate chinese embedding
            print(d['zh'])
            #e2 = model.encode(d['zh'].encode('utf-8'))
            e2 = model.encode(d['zh'])
            print(i, e2[0:10])
            print()
            zh_embedding = dict(act=av['_id'], sentence=d['zh'].encode('utf-8'), rank=i, embedding=e2, _id=str(ObjectId()))
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
#type(jsonData)
#print(jsonData['menu'])

# Integrated Chinese Level 1 Volume I, Lesson 5 Dialogue 1
# M1:    ??????, Sh??i ya, who is it, L5-1-1.mp3
# M2:   ??????????????????????????????, Sh?? w??, W??ng P??ng, h??i y??u L?? Y??u, It???s me Wang Peng, Li You is here, too, L5-1-2.mp3
# M1:  ???????????????????????????, Q??ng j??n, q??ng j??n, ku??i j??n lai, Please come in, please come in, come on in, L5-1-3-1.mp3
# M1:  ???????????????????????????????????????????????????, L??i, w?? ji??sh??o y?? xi??, zh?? sh?? w?? ji??jie, G??o Xi??oy??n, Let me introduce you to one another, this is my sister, Gao Xiaoyin, L5-1-3-2.mp3, L5-1-3-3  .mp3
# M2/F1:   ???????????????, ??????????????????, Xi??oy??n, n?? h??o, R??nshi n?? h??n g??ox??ng, How do you do, Xiaoyin, pleased to meet you, L5-1-4-1.mp3, L5-1-4-2.mp3,
# F2:   ???????????????????????????, R??nshi n??men w?? y?? h??n g??ox??ng, Pleased to meet you, too, L5-1-5.mp3
# F1?????????????????????????????????, N??men ji?? h??n d??, y?? h??n pi??oliang, Your home is very big, and very beautiful, too, L5-1-6-1.mp3, L5-1-6-2.mp3
# F2:   ????????????????????????, Sh?? ma? Q??ng zu??, q??ng zu??, Really, have a seat, please, L5-1-7.mp3
# M1:   ???????????????????????????, Xi??oy??n, n?? z??i n??r g??ngzu??, Xiaoyin, where do you work, L5-1-8.mp3
# F2:   ??????????????????, W?? z??i xu??xi??o g??ngzu??, I work at a school, L5-1-9-1.mp3 
# F2:   ????????????????????????, ?????????????????????, N??men xi??ng h?? di??nr sh??nme, H?? ch?? h??ishi h?? k??f??i, What would you like to drink, tea or coffee, L5-1-9-2.mp3, L5-1-9-3.mp3
# M1:   ????????????, W?? h?? ch?? ba, I???ll have tea, L5-1-10.mp3 
# F1:   ??????????????????????????????, W?? y??o y?? p??ng k??l??, k??y?? ma, I???d like a bottle of cola, is that OK, L5-1-11.mp3 
# F2:   ?????????????????????????????????, Du??buq??, w??men ji?? m??i y??u k??l??, I???m sorry, we don???t have cola, L5-1-12.mp3 
# F1:   ?????????????????????, n?? g??i w?? y?? b??i shu?? ba, Then please give me a glass of water, L5-1-13.mp3 

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
    "zh": "??????",
    "py": "Sh??i ya?",
    "en": "who is it?",
    "mp3": "L5-1-1.mp3"
    },
    {"id": 2,
    "actor": "M1",
    "zh": "??????????????????????????????",
    "py": "Sh?? w??, W??ng P??ng, h??i y??u L?? Y??u.",
    "en": "It???s me Wang Peng, Li You is here, too.",
    "mp3": "L5-1-2.mp3"
    },
    {"id": 3,
    "actor": "F1",
    "zh": "???????????????????????????",
    "py": "Q??ng j??n, q??ng j??n, ku??i j??n lai",
    "en": "Please come in, please come in, come on in",
    "mp3": "L5-1-3-1.mp3"
    },
    {"id": 4,
    "actor": "M1",
    "zh": "???????????????????????????????????????????????????",
    "py": "L??i, w?? ji??sh??o y?? xi??, zh?? sh?? w?? ji??jie, G??o Xi??oy??n",
    "en": "",
    "mp3": ["L5-1-3-2.mp3", "L5-1-3-3.mp3"]
    },
    {"id": 5,
    "actor": "F1",
    "zh": "???????????????, ??????????????????",
    "py": "Xi??oy??n, n?? h??o, R??nshi n?? h??n g??ox??ng",
    "en": "How do you do, Xiaoyin, pleased to meet you",
    "mp3": ["L5-1-4-1.mp3", "L5-1-4-2.mp3"]
    },
    {"id": 6,
    "actor": "F2",
    "zh": "??????????????????????????????,",
    "py": "N??men ji?? h??n d??, y?? h??n pi??oliang",
    "en": "Your home is very big, and very beautiful, too,",
    "mp3": ["L5-1-6-1.mp3", "L5-1-6-2.mp3"]
    },
    {"id": 7,
    "actor": "F1",
    "zh": "????????????????????????",
    "py": "Sh?? ma? Q??ng zu??, q??ng zu??,",
    "en": "Really, have a seat, please,",
    "mp3": "L5-1-7.mp3"
    },
    {"id": 8,
    "actor": "F1",
    "zh": "????????????????????????????",
    "py": "Xi??oy??n, n?? z??i n??r g??ngzu???",
    "en": "Xiaoyin, where do you work?",
    "mp3": "L5-1-8.mp3"
    },
    {"id": 9,
    "actor": "F2",
    "zh": "??????????????????",
    "py": "W?? z??i xu??xi??o g??ngzu??",
    "en": "I work at a school",
    "mp3": "L5-1-9-1.mp3"
    },
    {"id": 10,
    "actor": "F1",
    "zh": "????????????????????????, ??????????????????????",
    "py": "N??men xi??ng h?? di??nr sh??nme, H?? ch?? h??ishi h?? k??f??i?",
    "en": "What would you like to drink, tea or coffee?",
    "mp3": ["L5-1-9-2.mp3", "L5-1-9-3.mp3"]
    },
    {"id": 11,
    "actor": "M1",
    "zh": "????????????",
    "py": "W?? h?? ch?? ba",
    "en": "I???ll have tea",
    "mp3": "L5-1-10.mp3"
    },
    {"id": 12,
    "actor": "F2",
    "zh": "??????????????????????????????",
    "py": "W?? y??o y?? p??ng k??l??, k??y?? ma",
    "en": "I???d like a bottle of cola, is that OK",
    "mp3": "L5-1-11.mp3 "
    },
    {"id": 13,
    "actor": "F1",
    "zh": "?????????????????????????????????",
    "py": "Du??buq??, w??men ji?? m??i y??u k??l??",
    "en": "I???m sorry, we don???t have cola",
    "mp3": "L5-1-12.mp3"
    },
    {"id": 14,
    "actor": "F2",
    "zh": "?????????????????????",
    "py": "n?? g??i w?? y?? b??i shu?? ba",
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
    "zh": "???????????????????????????",
    "py": "Li Y??u, h??n ji?? n?? hu?? ji?? m???",
    "en": "Li You, are you going home during winter vacation?",
    "mp3": "L10-1-1.mp3"
    },
    {"id": 2,
    "actor": "F1",
    "zh": "??????????????????",
    "py": "Du??, wo y??o hu?? ji??.",
    "en": "Yes i'm going home",
    "mp3": "L10-1-2.mp3"
    },
    {"id": 3,
    "actor": "M1",
    "zh": "?????????????????????",
    "py": "Fe?? j?? pi??o ni m??i le ma?",
    "en": "Have you bought the plane ticket?",
    "mp3": "L10-1-3.mp3"
    },
    {"id": 4,
    "actor": "F1",
    "zh": "????????????????????????????????????",
    "py": "Y?? j??ng m??i le. Sh?? ??r sh?? y?? h??o de.",
    "en": "",
    "mp3": "L10-1-4.mp3"
    },
	{"id": 5,
    "actor": "M1",
    "zh": "?????????????????????",
    "py": "Fe?? j?? sh?? j?? di??n de?",
    "en": "What time is the plane?",
    "mp3": "L10-1-5.mp3"
    },
    {"id": 6,
    "actor": "F1",
    "zh": "???????????????",
    "py": "W??n sh??ng b?? di??n de.",
    "en": "At eight o'clock in the evening",
    "mp3": "L10-1-6.mp3"
    },
    {"id": 7,
    "actor": "M1",
    "zh": "???????????????????",
    "py": "N?? z??n me q?? j?? ch??ng?",
    "en": "How do you get to the airport?",
    "mp3": "L10-1-7.mp3"
    },
    {"id": 8,
    "actor": "F1",
    "zh": "????????????????????????????????????.??????????????????????",
    "py": "W?? xi??ng zu?? g??ngg??ng q??ch?? hu??zh?? zu?? d??ti??. N?? zh?? d??o z??n me z??u ma?",
    "en": "I want to take the bus or the subway. Do you know how to go?",
    "mp3": "L10-1-8.mp3"
    },
    {"id": 9,
    "actor": "M1",
    "zh": "????????????????????????????????????????????????????????????????????????????????????????????????????????????",
    "py": "N?? xi??n zu?? y??l?? q??ch??, zu?? s??n zh??n xi?? ch??, r??nh??u hu??n d??ti??. Xi??n zu?? h??ngxi??n, z??i hu??n l?? xi??n, zu??h??u hu??n l??n xi??n.",
    "en": "You first take Bus No. 1. Get off after three stops. Then take the subway. First take the red line, then change to the green line, and finally change to the blue line",
    "mp3": "L10-1-9.mp3"
    },
    {"id": 10,
    "actor": "F1",
    "zh": "??????????????????????????????????????????????????????",
    "py": "B?? x??ng, b?? x??ng, t??i m?? f??n le. W?? h??i sh?? d?? ch?? ba. Ch?? z?? q?? ch?? t??i gu??, w?? k??i ch?? s??ng n?? q?? ba.",
    "en": "No, no, too much trouble. I'll take a taxi",
    "mp3": "L10-1-10.mp3"
    },
    {"id": 11,
    "actor": "M1",
    "zh": "??????????????????.?????????????????????",
    "py": "Ch??z?? q??ch?? t??i gu??. W?? k??ich?? s??ng n?? q?? ba",
    "en": "The taxi is too expensive. I'll drive you there",
    "mp3": "L10-1-11.mp3"
    },
    {"id": 12,
    "actor": "F1",
    "zh": "????????????",
    "py": "Xi??xie n??.",
    "en": "Thank you.",
    "mp3": "L10-1-12.mp3 "
    },
    {"id": 13,
    "actor": "M1",
    "zh": "???????????????????????????????????????????????????????????????",
    "py": "S?? di??n b??n, m??i w??nt??, w?? z??i b??ng??ngsh?? d??ng n??. B??y??ng k??q??",
    "en": "4:30, no problem, I'll wait for you in the office. Don???t mention it",
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