import React from "react";

import Comm from "./Comm";

class Liquid extends React.Component {

    constructor(props) {
        super(props);

        this.state = {
            currentData: []
        };

        this.comm = new Comm();
        this.comm.setOnMessage( this.handler )
        this.comm.setOnConnect( this.connected )
        this.comm.connect();

        console.log("Liquid constructor");
    }

    connected()
    {
        this.comm.sendMessage("status");
        console.log("Liquid connected");
    }

    handler(data) {
        this.setState( data );
        console.log("Liquid handler");
    }

    render() {

        console.log(this.state.currentData);
        return (
            <div>
                100
            </div>
        );
    }
}

export default Liquid;