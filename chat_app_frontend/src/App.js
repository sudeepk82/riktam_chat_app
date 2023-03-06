import './App.css';
import { Component } from 'react';
import axios from 'axios';
import LoginPage from './LoginPageComponent/LoginPage';
import ChatApplication from './ChatApplicationComponent/ChatApplication';

class App extends Component {
  constructor(props) {
    super(props);

    this.state = {
      isAuthenticated: false,
      currentUser: {},
    }

  }


  handleLogin(email, password) {
    console.log(email, password)
    axios.post("/users/login/", { "username": email, "password": password })
      .then((res) => {
        if (res.status === 200) {
          console.log("Logged in", res);
          this.setState({ isAuthenticated: true, currentUser: res.data.data });
        }
      });
  }

  handleLogout() {
    axios.get("/users/" + this.props.currentUserId + "/logout/")
      .then((res) => {
        if (res.status === 200) {
          this.setState({ isAuthenticated: false, currentUser: {} });
        }
      })
  }


  render() {
    return (
      <div className="App">
        {
          !this.state.isAuthenticated ?
            (
              <LoginPage handleLogin={(username, password) => this.handleLogin(username, password)} />
            ) : (
              <ChatApplication currentUser={this.state.currentUser} handleLogout={() => this.handleLogout()} />
            )
        }
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

export default App;
