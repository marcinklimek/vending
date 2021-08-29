import React from "react";

import Comm from "./Comm";

class Money extends React.Component {

    constructor(props) {
        super(props);

        this.state = {
            currentData: []
        };

        this.comm = new Comm();
        this.comm.setOnMessage( this.handler )
        this.comm.setOnConnect( this.connected )
    }

    connected()
    {
        this.comm.sendMessage("status");
    }

    handler(data) {
        this.setState( data );
    }

    render() {

        console.log(this.state.currentData);
        return (
            <div>
                41
            </div>
        );
    }
}

export default Money;