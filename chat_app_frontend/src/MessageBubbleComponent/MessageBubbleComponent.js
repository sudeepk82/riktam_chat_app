import { Component } from "react";
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { solid, regular } from '@fortawesome/fontawesome-svg-core/import.macro'

export default class MessageBubbleComponent extends Component {
    constructor(props) {
        super(props);
        this.state = {
        };
    }

    likeMessage() {
        // this.props.handleLike(this.props.message.id);
        let msgData = {
            "msgId": this.props.message.id,
            "userId": this.props.user.id
        }
        this.props.wsClient.send(JSON.stringify({ "event_name": "like_message", "data": msgData }));
    }

    render() {
        return (
            <div
                style={{
                    "textAlign": this.props.message.author.id === this.props.user.id ? "right" : "left",
                    "margin": 0,
                }}
            >
                <span style={{ "fontSize": "12px" }}>{this.props.message.author.name} </span><br />
                {this.props.message.msg_text}<br />
                {
                    this.props.message.like_users.includes(this.props.user.id) ?
                        <FontAwesomeIcon onClick={() => this.likeMessage()} icon={solid("thumbs-up")} /> :
                        <FontAwesomeIcon onClick={() => this.likeMessage()} icon={regular("thumbs-up")} />

                }
                <span style={{ "fontSize": "14px" }}>
                    {this.props.message.like_users.length}
                </span><br />

            </div>
        );
    }
}