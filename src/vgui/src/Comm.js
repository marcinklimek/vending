import {Component} from "react";

class Comm extends Component {

    // single websocket instance for the own application and constantly trying to reconnect.

    constructor(props) {
        console.log("Comm constructor");

        super(props);
        this.state = {
            data: null,
            onConnect: null,
            onMessage: null,
        };
    }

    componentDidMount() {
        console.log("Comm componentDidMount");
        this.connect();
    }

    timeout = 50; // Initial timeout duration as a class variable

    /**
     * @function connect
     * This function establishes the connect with the websocket and also ensures constant reconnection if connection closes
     */
    connect = () => {
        console.log("connect");

        var ws = new WebSocket("ws://localhost:8888/ws");

        if ( this.state.onMessage != null )
            ws.onmessage = this.state.onMessage;

        let that = this; // cache the this
        var connectInterval;

        // websocket onopen event listener
        ws.onopen = () => {
            console.log("connected websocket main component");
            console.log(this.state.onMessage);
            console.log("X");
            this.setState({ ws: ws });

            that.timeout = 250; // reset timer to 250 on open of websocket connection 
            clearTimeout(connectInterval); // clear Interval on on open of websocket connection

            if ( this.onConnect != null )
                this.onConnect();


        };

        // websocket onclose event listener
        ws.onclose = e => {
            console.log(
                `Socket is closed. Reconnect will be attempted in ${Math.min(
                    10000 / 1000,
                    (that.timeout) / 1000
                )} second.`,
                e.reason
            );

            connectInterval = setTimeout(this.check, that.timeout); //call check function after timeout
        };

        // websocket onerror event listener
        ws.onerror = err => {
            console.error(
                "Socket encountered error: ",
                err.message,
                "Closing socket"
            );

            ws.close();
        };

    };

    /**
     * utilited by the @function connect to check if the connection is close, if so attempts to reconnect
     */
    check = () => {
        const { ws } = this.state;
        if (!ws || ws.readyState === WebSocket.CLOSED) this.connect(); //check if websocket instance is closed, if so call `connect` function.
    };

    setOnMessage = handler =>
    {
        this.setState( { onMessage: handler});
    }

    setOnConnect = handler =>
    {
        this.setState( { onConnect: handler});
    }

    sendMessage = msg => {
        this.state.ws.send(msg);
    }
}

export default Comm;