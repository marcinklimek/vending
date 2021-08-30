import React from "react";
import Comm from "./Comm";

class Liquid extends React.Component {

    constructor(props) {
        super(props);

        this.state = {
            liquid: 0
        };

        this.comm = new Comm(this.handler);
    }

    handler = (data) => {
        const status = JSON.parse(data.data);
        this.setState({liquid:status.liquid});
    }

    render() {
        return (
            <div>
                {this.state.liquid}
            </div>
        );
    }
}

export default Liquid;