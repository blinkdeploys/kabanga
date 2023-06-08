import  React, { Component } from  'react';
import  ResultService  from  './ResultService';

const  resultService  =  new  ResultService();

class ResultList extends Component {

    constructor(props) {
        super(props)
        this.state = {
            result: [],
            nextPageURL: '',
        }
        this.nextPage = this.nextPage.bind(this)
        this.handleDelete = this.handleDelete.bind(this)
    }

    componentDidMount() {
        var self = this
        resultService.getResults().then(function (result) {
            self.setState({ result: result.data, nextPageURL: result.nextlink})
        })
    }

    handleDelete(e, pk) {
        var self = this
        resultService.deleteResult({pk: pk}).then(() => {
            var newArr = self.state.result.filter(function(obj) {
                return obj.pk !== pk
            })
            self.setState({result: newArr})
        })
    }

    nextPage(){
        var self = this
        resultService.getResultsByURL(this.state.nextPageURL).then((result) => {
            self.setState({ result: result.data, nextPageURL: result.nextlink})
        })
    }

    render() {
    
        return (
        <div  className="result--list">
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
                    {this.state?.result?.map( c  =>
                    <tr  key={c.pk}>
                        <td>{c.pk}</td>
                        <td>
                            <a href={"/result/" + c.pk}>
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
export default ResultList