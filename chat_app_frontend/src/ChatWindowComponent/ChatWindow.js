import axios from "axios";
import { Component } from "react";
import { w3cwebsocket } from "websocket";
import MessageBubbleComponent from "../MessageBubbleComponent/MessageBubbleComponent";


class ChatWindow extends Component {
    constructor(props) {
        super(props);
        this.state = {
            messages: [],
            members: [],
            msg_counter: 0,
            msg: "",
            users: [],
            showUserAddForm: false,
        }
    }

    componentDidUpdate(prevProps) {
        if (this.props.group) {
            if (prevProps.group)
                if (this.props.group.id !== prevProps.group.id) {
                    this.chatroomClient.close()
                    this.setupSocketAndFetchMessages();
                } else { }
            else
                this.setupSocketAndFetchMessages();
            this.chatroomClient.onmessage = (message) => {
                message = JSON.parse(message.data);
                if (message.event_name === "message_received") {
                    this.setState({ messages: [...this.state.messages, message.data] });
                    this.setState({ msg: '' });
                }
                if (message.event_name === "message_liked") {
                    axios.get("/groups/" + this.props.group.id + "/messages")
                        .then((res) => {
                            this.setState({ messages: res.data.data });
                        })
                }
                if (message.event_name === "error_alert")
                    alert(message.message)
            };
        }
    }

    setupSocketAndFetchMessages = () => {
        this.chatroomClient = new w3cwebsocket("ws://" + process.env.REACT_APP_SITE_HOST + "/ws/" + this.props.group.id + "/")
        this.chatroomClient.onopen = () => {
            console.log("Connection opened to chat client for group", this.props.group.id);
        };

        if (this.props.group) {
            axios.get("/groups/" + this.props.group.id + "/messages")
                .then((res) => {
                    this.setState({ messages: res.data.data })
                })
        } else {
            this.setState({ messages: [] })
        }

    }

    sendMessage = () => {
        if (this.state.msg) {

            let msgObject = {
                "msg_text": this.state.msg,
                "sender": this.props.currentUser.id,
                "group": this.props.group.id,
                "like_users": []
            }
            this.chatroomClient.send(JSON.stringify({ "event_name": "send_message", "data": msgObject }));
        }

    }

    likeMessage = (msgId) => {
        let msgData = {
            "msgId": msgId,
            "userId": this.props.currentUser.id
        }
        this.chatroomClient.send(JSON.stringify({ "event_name": "like_message", "data": msgData }));
    }

    openUserAddForm() {
        axios.get("/users")
            .then((res) => {
                this.setState({ users: res.data })
            })
        this.setState({ showUserAddForm: true })
    }

    addUserToGroup(userId) {
        let userData = {
            "userId": userId,
            "groupId": this.props.group.id
        }
        this.props.groupClient.send(JSON.stringify({ "event_name": "add_user", "data": userData }))
        this.setState({ showUserAddForm: false })
    }

    render() {
        let userForm = (
            <div>
                {
                    this.state.users.map((user) => {
                        if (!user.chat_groups.includes(this.props.group.id)) {
                            return (
                                <li key={user.id} style={{ "textDecoration": "none", "listStyle": "none" }}>
                                    {user.first_name} {user.last_name}
                                    <button onClick={() => this.addUserToGroup(user.id)}>Add</button>
                                </li>
                            )
                        }
                        else
                            return ""
                    })
                }
                <button onClick={() => this.setState({
                    showUserAddForm: false
                })}>Close</button>
            </div>
        );
        return (
            this.props.group === undefined ?

                (
                    <div className="chat-window"
                        style={{
                            "width": '50%',
                            "border": "1px solid black",
                            "position": "absolute",
                            "left": "25%",
                            "height": "100%"
                        }}
                    />
                ) : (
                    <div className="chat-window"
                        style={{
                            "width": '50%',
                            "border": "1px solid black",
                            "position": "absolute",
                            "left": "25%",
                            "height": "100%"
                        }}

                    >
                        {this.props.group.name}
                        <button
                            style={{
                                "position": "absolute",
                                "right": 0,
                                "top": 0
                            }}
                            onClick={() => this.openUserAddForm()}
                        >Add User</button>
                        {this.state.showUserAddForm ? userForm : null}

                        <section className="message-board" style={{ height: "90%", overflow: "scroll" }}>
                            <ul style={{ "textDecoration": "none", "listStyle": "none", "padding": "1%" }}>
                                {
                                    this.state.messages.map((msg) => (
                                        < MessageBubbleComponent key={msg.id} user={this.props.currentUser} message={msg} wsClient={this.chatroomClient} />
                                    ))
                                }
                            </ul>
                        </section>

                        <input type="text" placeholder="Enter your message here..."
                            style={{
                                "width": "90%",
                                "position": "absolute",
                                "left": 0,
                                "bottom": 0,
                                "height": "10%",
                            }}
                            value={this.state.msg}
                            onChange={(e) => this.setState({ msg: e.target.value })}
                        />
                        <button
                            onClick={() => this.sendMessage()}
                            style={{
                                "width": "10%",
                                "position": "absolute",
                                "bottom": 0,
                                "right": 0,
                                "border": "none",
                                "boxShadow": "none",
                                "height": "10%",
                            }}
                        >SEND</button>
                    </div>
                )
        );
    }

}

export default ChatWindow;