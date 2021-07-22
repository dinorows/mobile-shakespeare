import React, { useState, useEffect, useRef } from 'react';

import Container from 'react-bootstrap/Container';
import Button from 'react-bootstrap/Button';
import Form from 'react-bootstrap/Form';

const dialog = {
    "actors": [
        { "name": "A", "id": "A" },
        { "name": "B", "id": "B" },
    ],
    "dialogue": [
        {
            "id": 1,
            "actor": "A",
            "zh": "小姐，您要买什么衣服",
        },
        {
            "id": 2,
            "actor": "B",
            "zh": "我想买一件衬衫"
        },
        {
            "id": 3,
            "actor": "A",
            "zh": "您喜欢什么颜色的？黄的还是红的？",
        },
        {
            "id": 4,
            "actor": "B",
            "zh": "我喜欢穿红的。我还想买一条裤子。"
        },
        {
            "id": 5,
            "actor": "A",
            "zh": "多大的？大号的、中号的、还是小号的？",
        },
        {
            "id": 6,
            "actor": "B",
            "zh": "中号的。不要太贵的，也不要太便宜的。"
        },
        {
            "id": 7,
            "actor": "A",
            "zh": "这条裤子怎么样？",
        },
        {
            "id": 8,
            "actor": "B",
            "zh": "颜色很好。如果长短合适的话，我就买。"
        },
        {
            "id": 9,
            "actor": "A",
            "zh": "您试一下。",
        },
        {
            "id": 10,
            "actor": "B",
            "zh": "不用试。可以。"
        },
        {
            "id": 11,
            "actor": "A",
            "zh": "这件衬衫呢？",
        },
        {
            "id": 12,
            "actor": "B",
            "zh": "也不错。一共多少钱？。"
        },
        {
            "id": 13,
            "actor": "A",
            "zh": "衬衫二十一块五，裤子三十二块九毛九，一共是五十四块四毛九分。",
        },
        {
            "id": 14,
            "actor": "A",
            "zh": "好，这是一百块钱。"
        },
        {
            "id": 15,
            "actor": "B",
            "zh": "找您四十五块五毛一。"
        },
        {
            "id": 16,
            "actor": "A",
            "zh": "谢谢。",
        },

    ]
}

function Chat() {
    const [messages, setMessages] = useState([{ id: 0, message: "Hello! 你好！", user: false },]);

    const [userEntry, setUserEntry] = useState("");
    const [messageId, setMessageId] = useState(1);

    const messagesEndRef = useRef(null)

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" })
    }

    useEffect(() => {
        scrollToBottom()
    }, [messages]);

    function renderChat(msg) {
        return (
            <div key={msg.id} className='d-flex flex-column'>
                {msg.user ?
                    <div className='p-1 align-self-end'>
                        <Button variant='light'>
                            {msg.message}
                        </Button>
                    </div> :
                    <div className='p-1 align-self-start'>
                        <Button>
                            {msg.message}
                        </Button>
                    </div>
                }
            </div>
        )
    }

    async function processMsg(e) {
        e.preventDefault();

        let newMessages = [...messages];
        let newId = messageId;

        newMessages.push({ id: newId, message: userEntry, user: true });
        newId += 1;
        setMessages(newMessages);
        setMessageId(newId);
        e.target[0].value = "";

        let response = "No response";
        try {
            response = await fetch("http://localhost:5000/next-en/" + userEntry);

            if (response.ok) {

                let serverResponse = await response.json();
                response = serverResponse[1];
            } else {
                alert("launch: failure on send!");
            }

        } catch (error) {
            console.log(error);
            alert("exception on get");
        }

        newMessages.push({ id: newId, message: response, user: false });
        newId += 1;
        setMessages(newMessages);
        setMessageId(newId);
        scrollToBottom();
    }

    function handleUserChange(e) {
        setUserEntry(e.target.value);
    }

    return (
        <Container>
            <div className='d-flex flex-column'>
                <h3 className='py-3 align-self-start'>
                    Husky Chat Bot
                </h3>
            </div>
            <div className='py-3' style={{
                height: '600px',
                'overflowY': 'scroll'
            }}>
                {messages && messages.map((msg) => (
                    renderChat(msg)
                ))}
                <div ref={messagesEndRef} />
            </div>
            <div>
                <Form inline className='w-100 py-1 d-flex justify-content-between align-items-center'
                    id='chatbox'
                    onSubmit={processMsg}>
                    <Form.Group style={{ flex: 1 }} controlId='submitControl'>
                        <Form.Control required
                            type='text' placeholder='Type Message here...'
                            onChange={handleUserChange}
                        />
                    </Form.Group>
                    <Button variant='primary' type='submit'>
                        Send
                    </Button>
                </Form>
                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-mic" viewBox="0 0 16 16">
                    <path d="M3.5 6.5A.5.5 0 0 1 4 7v1a4 4 0 0 0 8 0V7a.5.5 0 0 1 1 0v1a5 5 0 0 1-4.5 4.975V15h3a.5.5 0 0 1 0 1h-7a.5.5 0 0 1 0-1h3v-2.025A5 5 0 0 1 3 8V7a.5.5 0 0 1 .5-.5z" />
                    <path d="M10 8a2 2 0 1 1-4 0V3a2 2 0 1 1 4 0v5zM8 0a3 3 0 0 0-3 3v5a3 3 0 0 0 6 0V3a3 3 0 0 0-3-3z" />
                </svg>
            </div>
        </Container>
    )
}

export default Chat;