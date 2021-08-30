import {Component} from "react";

class Comm extends Component {

    constructor(props) {
        console.log("Comm constructor");

        super(props);

        this.state = {
            ws: undefined
        };

        this.timeout = 50; // Initial timeout duration as a class variable

        this.onMessage = props;

        this.resetValues();
        this.connect();
    }

    resetValues = () => {
        this.onMessage( {data: "{\"money\":0, \"liquid\":0}"} );
    }

    connect = () => {
        let ws = new WebSocket("ws://localhost:8888/ws");
        ws.onmessage = this.onMessage;

        let that = this; // cache the this
        let connectInterval; // timer id

        // websocket onopen event listener
        ws.onopen = () => {
            this.setState({ws:ws});
            clearTimeout(connectInterval); // clear Interval on on open of websocket connection
        };

        // websocket onclose event listener
        ws.onclose = e => {
            console.log(
                `Socket is closed. Reconnect will be attempted in ${(that.timeout) / 1000} seconds.`,
                e.reason
            );

            this.resetValues();
            connectInterval = setTimeout(this.check, that.timeout); //call check function after timeout
        };

        // websocket onerror event listener
        ws.onerror = err => {
            console.error(
                "Socket encountered error: ",
                err.message,
                "Closing socket"
            );

            this.resetValues();
            ws.close();
        };

    };

    check = () => {
        const { ws } = this.state;
        if (!ws || ws.readyState === WebSocket.CLOSED) this.connect(); //check if websocket instance is closed, if so call `connect` function.
    };
}

export default Comm;