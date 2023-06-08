import  React, { Component } from  'react';
import  PartyService  from  './PartyService';

const  partyService  =  new  PartyService();

class PartyList extends Component {

    constructor(props) {
        super(props)
        this.state = {
            party: [],
            nextPageURL: '',
        }
        this.nextPage = this.nextPage.bind(this)
        this.handleDelete = this.handleDelete.bind(this)
    }

    componentDidMount() {
        var self = this
        partyService.getParties().then(function (result) {
            self.setState({ party: result.data, nextPageURL: result.nextlink})
        })
    }

    handleDelete(e, pk) {
        var self = this
        partyService.deleteParty({pk: pk}).then(() => {
            var newArr = self.state.party.filter(function(obj) {
                return obj.pk !== pk
            })
            self.setState({party: newArr})
        })
    }

    nextPage(){
        var self = this
        partyService.getPartiesByURL(this.state.nextPageURL).then((result) => {
            self.setState({ party: result.data, nextPageURL: result.nextlink})
        })
    }

    render() {
    
        return (
        <div  className="party--list">
            <table  className="table">
                <thead  key="thead">
                <tr>
                    <th>#</th>
                    <th>Abbreviations</th>
                    <th>Political Parties</th>
                    <th>Actions</th>
                </tr>
                </thead>
                <tbody>
                    {this.state?.party?.map( c  =>
                    <tr  key={c.pk}>
                        <td>{c.pk}</td>
                        <td>{c.code}</td>
                        <td>
                            <a href={"/party/" + c.pk}>
                                {c.title}
                            </a>
                        </td>
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
export default PartyList