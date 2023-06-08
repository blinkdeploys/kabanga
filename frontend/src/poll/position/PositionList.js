import  React, { Component } from  'react';
import  PositionService  from  './PositionService';

const  positionService  =  new  PositionService();

class PositionList extends Component {

    constructor(props) {
        super(props)
        this.state = {
            position: [],
            nextPageURL: '',
        }
        this.nextPage = this.nextPage.bind(this)
        this.handleDelete = this.handleDelete.bind(this)
    }

    componentDidMount() {
        var self = this
        positionService.getPositions().then(function (position) {
            self.setState({ position: position.data, nextPageURL: position.nextlink})
        })
    }

    handleDelete(e, pk) {
        var self = this
        positionService.deletePosition({pk: pk}).then(() => {
            var newArr = self.state.position.filter(function(obj) {
                return obj.pk !== pk
            })
            self.setState({position: newArr})
        })
    }

    nextPage(){
        var self = this
        positionService.getPositionsByURL(this.state.nextPageURL).then((position) => {
            self.setState({ position: position.data, nextPageURL: position.nextlink})
        })
    }

    render() {
    
        return (
        <div  className="position--list">
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
                    {this.state?.position?.map( c  =>
                    <tr  key={c.pk}>
                        <td>{c.pk}</td>
                        <td>
                            <a href={"/position/" + c.pk}>
                                {c.first_name} {c.last_name}
                            </a>
                        </td>
                        <td>{c.phone}</td>
                        <td>{c.email}</td>
                        <td>{c.address}</td>
                        <td>{c.description}</td>
                        <td>
                            <button  onClick={(e)=>  this.handleDelete(e,c.pk) }> Delete</button>
                        </td>
                    </tr>)}
                </tbody>
            </table>
            <button  className="btn btn-primary"  onClick=  {  this.nextPage  }>Next</button>
        </div>
        );
    }
}
export default PositionList