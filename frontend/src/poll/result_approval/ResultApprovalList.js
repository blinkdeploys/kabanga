import  React, { Component } from  'react';
import  ResultApprovalService  from  './ResultApprovalService';

const  resultApprovalService  =  new  ResultApprovalService();

class ResultApprovalList extends Component {

    constructor(props) {
        super(props)
        this.state = {
            resultApproval: [],
            nextPageURL: '',
        }
        this.nextPage = this.nextPage.bind(this)
        this.handleDelete = this.handleDelete.bind(this)
    }

    componentDidMount() {
        var self = this
        resultApprovalService.getResultApprovals().then(function (result) {
            self.setState({ resultApproval: result.data, nextPageURL: result.nextlink})
        })
    }

    handleDelete(e, pk) {
        var self = this
        resultApprovalService.deleteResultApproval({pk: pk}).then(() => {
            var newArr = self.state.resultApproval.filter(function(obj) {
                return obj.pk !== pk
            })
            self.setState({resultApproval: newArr})
        })
    }

    nextPage(){
        var self = this
        resultApprovalService.getResultApprovalsByURL(this.state.nextPageURL).then((result) => {
            self.setState({ resultApproval: result.data, nextPageURL: result.nextlink})
        })
    }

    render() {
    
        return (
        <div  className="resultApproval--list">
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
                    {this.state?.resultApproval?.map( c  =>
                    <tr  key={c.pk}>
                        <td>{c.pk}</td>
                        <td>
                            <a href={"/result_approval/" + c.pk}>
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
export default ResultApprovalList