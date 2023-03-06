import { Component } from "react";

export default class LoginPage extends Component {
    constructor(props) {
        super(props);
        this.state = {
            email: "",
            password: ""
        }
    }

    handleEmailChange(email) {
        this.setState({ email: email });
    }

    handlePasswordChange(password) {
        this.setState({ password: password });
    }



    render() {
        return (
            <div
                style={{
                    "width": "50%",
                    "height": "70%",
                    "position": "absolute",
                    "top": "15%",
                    "left": "25%",
                    "margin": "none",
                    "padding": "none",
                    "textAlign": "justify"
                }}
            >
                <label htmlFor="email">E-Mail</label> <br />
                <input type="email" name="email" placeholder="E-Mail"
                    onChange={(e) => this.handleEmailChange(e.target.value)}
                    // onChange={(e) => console.log(e.target.value)}
                    style={{
                        "width": "100%",
                        "padding": "none",
                        "margin": "none"
                    }}
                /><br />
                <label htmlFor="password">Password</label><br />
                <input type="password" name="password" placeholder="Password"
                    onChange={(e) => this.handlePasswordChange(e.target.value)}
                    style={{
                        "width": "100%",
                        "padding": "none",
                        "margin": "none"
                    }}
                /><br />
                <button onClick={() => this.props.handleLogin(this.state.email, this.state.password)}>Log In</button>
                {/* <button onClick={() => console.log(this.state.email, this.state.password)}>Log In</button> */}
            </div>
        );
    }
}