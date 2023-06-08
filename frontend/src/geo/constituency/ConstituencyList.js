import  React, { Component } from  'react';
import  ConstituencyService  from  './ConstituencyService';

const  constituencyService  =  new  ConstituencyService();

class ConstituencyList extends Component {

    constructor(props) {
        super(props)
        this.state = {
            constituency: [],
            nextPageURL: '',
        }
        this.nextPage = this.nextPage.bind(this)
        this.handleDelete = this.handleDelete.bind(this)
    }

    componentDidMount() {
        var self = this
        constituencyService.getConstituencies().then(function (result) {
            self.setState({ constituency: result.data, nextPageURL: result.nextlink})
        })
    }

    handleDelete(e, pk) {
        var self = this
        constituencyService.deleteConstituency({pk: pk}).then(() => {
            var newArr = self.state.constituency.filter(function(obj) {
                return obj.pk !== pk
            })
            self.setState({constituency: newArr})
        })
    }

    nextPage(){
        var self = this
        constituencyService.getConstituenciesByURL(this.state.nextPageURL).then((result) => {
            self.setState({ constituency: result.data, nextPageURL: result.nextlink})
        })
    }

    render() {
    
        return (
        <div  className="constituency--list">
            <table  className="table">
                <thead  key="thead">
                <tr>
                    <th>#</th>
                    <th>Constituencies</th>
                    <th>Region</th>
                    <th>Actions</th>
                </tr>
                </thead>
                <tbody>
                    {this.state?.constituency?.map( c  =>
                    <tr  key={c.pk}>
                        <td>{c.pk}</td>
                        <td>
                            <a href={"/constituency/" + c.pk}>
                                {c.title}
                            </a>
                        </td>
                        <td>{c.region.title}</td>
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
export default ConstituencyList