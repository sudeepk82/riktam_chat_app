import axios from 'axios';
import { Component } from 'react';
import { w3cwebsocket } from 'websocket';
import '../App.css';
import ChatWindow from '../ChatWindowComponent/ChatWindow';
import GroupList from '../GroupListComponent/GroupList';
import UserList from '../UserListComponent/UserList';

class ChatApplication extends Component {
    constructor(props) {
        super(props);

        this.state = {
            received_event: {},
            groups: [],
            users: [],
            chatClient: undefined,
            chatGroup: undefined,
        }

        this.client = new w3cwebsocket('ws://' + process.env.SITE_HOST + '/ws/chat_app_groups/');
    }

    componentDidMount() {
        this.client.onopen = () => {
            console.log("Websocket client connected.", this.client);
        };
        this.getGroups();
        this.getUsers();

        this.client.onmessage = (message) => {
            message = JSON.parse(message.data);
            if (message.event_name === "new_group") {
                console.log("Created group", message.data);
                // this.getUsers(message.data.id);
                this.setState({ groups: [...this.state.groups, message.data] })
                this.getGroups();
            }
            if (message.event_name === "updated_group_members") {
                this.getUsers(this.state.chatGroup.id);
                this.getGroups();
            }
            if (message.event_name === "error_alert")
                console.log(message.message)
        };

    }

    getGroups = () => {
        axios.get("/groups").then((res) => {
            this.setState({ groups: res.data });
        })
    }

    getUsers = (groupId = undefined) => {
        if (groupId) {
            axios.get("/groups/" + groupId + "/members")
                .then((res) => this.setState({ users: res.data.data }))
        } else {
            axios.get("/users").then((res) => {
                this.setState({ users: res.data });
            })
        }
    }

    handleCreateGroup = (grpName, grpDesc) => {
        let group_obj = {
            "name": grpName,
            "admin": this.props.currentUser.id,
            "description": grpDesc,
        }
        this.client.send(JSON.stringify({ "event_name": "create_group", "data": group_obj }));
    }

    // handleAddUserToGroup = (userId) => {
    //     this.client.send(JSON.stringify({ "event_name": "add_user", "data": { "userId": userId, "groupId": this.state.chatGroup } }));
    //     this.client.onmessage = (message) => {
    //         message = JSON.parse(message.data);
    //         console.log(message);
    //     }
    // }

    createChatRoom = (group) => {
        this.getUsers(group.id);
        this.setState({ chatGroup: group });
    }

    render() {
        return (
            <div className="chat-app"
                style={{ "width": "100%", "position": "absolute", "left": 0, "border": "1px solid red", "height": "100%" }}
            >
                <header className="main-header" style={{ "height": "10 %" }}>
                    <h1>Sample Chat Application</h1>
                </header>
                <button
                    style={{
                        position: 'absolute',
                        top: 0,
                        right: 0
                    }}
                    onClick={() => { this.props.handleLogout() }}
                >Log out</button>
                <div className='app-container' style={{ "width": "100%", "position": "absolute", "left": 0, "bottom": 0, "border": "1px solid red", "height": "90%" }}>
                    <GroupList currentUser={this.props.currentUser} groups={this.state.groups} groupCreateHandle={(name, desc) => this.handleCreateGroup(name, desc)} createChatRoom={(grp) => this.createChatRoom(grp)} />
                    <ChatWindow currentUser={this.props.currentUser} group={this.state.chatGroup} groupClient={this.client} />
                    <UserList currentUser={this.props.currentUser} users={this.state.users} group={this.state.chatGroup} />
                </div>
            </div>
        );
    }
}

// function App() {
//   return (
//     <div className="App">
//       <header className="App-header">
//         Sample Chat Application
//       </header>
//     </div>
//   );
// }

export default ChatApplication;
