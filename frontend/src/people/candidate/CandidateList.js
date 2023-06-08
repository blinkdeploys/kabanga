import  React, { Component } from  'react';
import  CandidateService  from  './CandidateService';

const  candidateService  =  new  CandidateService();

class CandidateList extends Component {

    constructor(props) {
        super(props)
        this.state = {
            candidate: [],
            nextPageURL: '',
        }
        this.nextPage = this.nextPage.bind(this)
        this.handleDelete = this.handleDelete.bind(this)
    }

    componentDidMount() {
        var self = this
        candidateService.getCandidates().then(function (result) {
            self.setState({ candidate: result.data, nextPageURL: result.nextlink})
        })
    }

    handleDelete(e, pk) {
        var self = this
        candidateService.deleteCandidate({pk: pk}).then(() => {
            var newArr = self.state.candidate.filter(function(obj) {
                return obj.pk !== pk
            })
            self.setState({candidate: newArr})
        })
    }

    nextPage(){
        var self = this
        candidateService.getCandidatesByURL(this.state.nextPageURL).then((result) => {
            self.setState({ candidate: result.data, nextPageURL: result.nextlink})
        })
    }

    render() {
    
        return (
        <div  className="candidate--list">
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
                    {this.state?.candidate?.map( c  =>
                    <tr  key={c.pk}>
                        <td>{c.pk}</td>
                        <td>
                            <a href={"/candidate/" + c.pk}>
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
export default CandidateList