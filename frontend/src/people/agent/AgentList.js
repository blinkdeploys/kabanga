import  React, { Component } from  'react';
import  AgentService  from  './AgentService';

const  agentService  =  new  AgentService();

class AgentList extends Component {

    constructor(props) {
        super(props)
        this.state = {
            agent: [],
            nextPageURL: '',
        }
        this.nextPage = this.nextPage.bind(this)
        this.handleDelete = this.handleDelete.bind(this)
    }

    componentDidMount() {
        var self = this
        agentService.getAgents().then(function (result) {
            self.setState({ agent: result.data, nextPageURL: result.nextlink})
        })
    }

    handleDelete(e, pk) {
        var self = this
        agentService.deleteAgent({pk: pk}).then(() => {
            var newArr = self.state.agent.filter(function(obj) {
                return obj.pk !== pk
            })
            self.setState({agent: newArr})
        })
    }

    nextPage(){
        var self = this
        agentService.getAgentsByURL(this.state.nextPageURL).then((result) => {
            self.setState({ agent: result.data, nextPageURL: result.nextlink})
        })
    }

    render() {
    
        return (
        <div  className="agent--list">
            <table  className="table">
                <thead  key="thead">
                <tr>
                    <th>#</th>
                    <th>Full Name</th>
                    <th>Phone</th>
                    <th>Email</th>
                    <th>Address</th>
                    <th>Description</th>
                    <th>Actions</th>
                </tr>
                </thead>
                <tbody>
                    {this.state?.agent?.map( c  =>
                    <tr  key={c.pk}>
                        <td>{c.pk}</td>
                        <td>
                            <a href={"/agent/" + c.pk}>
                                {c.first_name} {c.last_name}
                            </a>
                        </td>
                        <td>{c.phone}</td>
                        <td>{c.email}</td>
                        <td>{c.address}</td>
                        <td>{c.description}</td>
                        <td>
                            <button  className="btn" onClick={(e)=>  this.handleDelete(e,c.pk) }> Delete</button>
                        </td>
                    </tr>)}
                </tbody>
            </table>
            <button  className="btn btn-primary"  onClick=  {  this.nextPage  }>Next</button>
        </div>
        );
    }
}
export default AgentList