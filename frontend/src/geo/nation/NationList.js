import  React, { Component } from  'react';
import  NationService  from  './NationService';

const  nationService  =  new  NationService();

class NationList extends Component {

    constructor(props) {
        super(props)
        this.state = {
            nation: [],
            nextPageURL: '',
        }
        this.nextPage = this.nextPage.bind(this)
        this.handleDelete = this.handleDelete.bind(this)
    }

    componentDidMount() {
        var self = this
        nationService.getNations().then(function (result) {
            self.setState({ nation: result.data, nextPageURL: result.nextlink})
        })
    }

    handleDelete(e, pk) {
        var self = this
        nationService.deleteNation({pk: pk}).then(() => {
            var newArr = self.state.nation.filter(function(obj) {
                return obj.pk !== pk
            })
            self.setState({nation: newArr})
        })
    }

    nextPage(){
        var self = this
        nationService.getNationByURL(this.state.nextPageURL).then((result) => {
            self.setState({ nation: result.data, nextPageURL: result.nextlink})
        })
    }

    render() {
        console.log(this.state?.nation)

        return (
        <div  className="nation--list">
            <table  className="table">
                <thead  key="thead">
                <tr>
                    <th>#</th>
                    <th>Code</th>
                    <th>Nations</th>
                    <th>Actions</th>
                </tr>
                </thead>
                <tbody >
                    {this.state?.nation?.map( c  =>
                    <tr  key={c.pk}>
                        <td>{c.pk}</td>
                        <td>{c.code}</td>
                        <td>
                            <a href={"/nation/" + c.pk}>
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
export default NationList