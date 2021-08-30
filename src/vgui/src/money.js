import React, {useState} from "react";

import Comm from "./Comm";

class Money extends React.Component {

    constructor(props) {
        super(props);

        this.state = {
            money: 0
        };

        this.comm = new Comm(this.handler);
    }

    handler = (data) => {
        const status = JSON.parse(data.data);
        this.setState({money:status.money});
    }

    render() {
        return (
            <div>
                {this.state.money}
            </div>
        );
    }
}

export default Money;