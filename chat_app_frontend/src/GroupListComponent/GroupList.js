import axios from "axios";
import { Component } from "react"

export default class GroupList extends Component {
    constructor(props) {
        super(props);
        this.state = {
            showGrpForm: false,
            newGroupName: "",
            newGroupDesc: "",
            userGroups: [],
        }
    }

    componentDidMount() {
        this.fetchUserGroups();
    }

    fetchUserGroups() {
        axios.get("/users/" + this.props.currentUser.id)
            .then((res) => {
                this.setState({ userGroups: res.data.chat_groups })
            })
    }

    render() {
        let grpForm = (
            <div id="add-grp-form">
                <input type="text" name="grp-name" placeholder="Group Name"
                    onChange={(e) => this.setState({ newGroupName: e.target.value })} />
                <input type="text" name="grp-desc" placeholder="Group Description"
                    onChange={(e) => this.setState({ newGroupDesc: e.target.value })} />
                <button
                    onClick={() => { this.setState({ showGrpForm: false }); this.props.groupCreateHandle(this.state.newGroupName, this.state.newGroupDesc); this.fetchUserGroups() }}
                >Create</button>
                <button onClick={() => this.setState({ showGrpForm: false })}>Cancel</button>
            </div>
        );
        return (
            <section style={{ "width": "25%", "position": "absolute", "left": 0, "border": "1px solid red", "height": "100%" }}>
                <h3>Groups:</h3>
                <button style={{ "display": "inline" }}
                    onClick={() => this.setState({ showGrpForm: true })}
                >New Group</button>
                {this.state.showGrpForm ? grpForm : null}
                <ul style={{ "textDecoration": "none", "listStyle": "none", "padding": "1%", "textAlign": "left" }}>
                    {
                        this.props.groups.map((group) => {
                            if (this.state.userGroups.includes(group.id))
                                return (
                                    <li key={group.id}
                                        style={{ "width": "100%", "display": "block" }}
                                        onClick={() => this.props.createChatRoom(group)}>
                                        <div>{group.name}</div>
                                    </li>
                                )
                            else
                                return ""
                        })
                    }
                </ul>
            </section >
        )
    }
}