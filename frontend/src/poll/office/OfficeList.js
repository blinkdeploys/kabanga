import  React, { Component } from  'react';
import  OfficeService  from  './OfficeService';

const  officeService  =  new  OfficeService();

class OfficeList extends Component {

    constructor(props) {
        super(props)
        this.state = {
            office: [],
            nextPageURL: '',
        }
        this.nextPage = this.nextPage.bind(this)
        this.handleDelete = this.handleDelete.bind(this)
    }

    componentDidMount() {
        var self = this
        officeService.getOffices().then(function (office) {
            self.setState({ office: office.data, nextPageURL: office.nextlink})
        })
    }

    handleDelete(e, pk) {
        var self = this
        officeService.deleteOffice({pk: pk}).then(() => {
            var newArr = self.state.office.filter(function(obj) {
                return obj.pk !== pk
            })
            self.setState({office: newArr})
        })
    }

    nextPage(){
        var self = this
        officeService.getOfficesByURL(this.state.nextPageURL).then((office) => {
            self.setState({ office: office.data, nextPageURL: office.nextlink})
        })
    }

    render() {
    
        return (
        <div  className="office--list">
            <table  className="table">
                <thead  key="thead">
                <tr>
                    <th>#</th>
                    <th>Office Designation</th>
                    <th>Level</th>
                    <th>Actions</th>
                </tr>
                </thead>
                <tbody>
                    {this.state?.office?.map( c  =>
                    <tr  key={c.pk}>
                        <td>{c.pk}</td>
                        <td>
                            <a href={"/office/" + c.pk}>
                                {c.title}
                            </a>
                        </td>
                        <td>
                            {c.level}
                        </td>
                        <td>
                            <button className="btn" onClick={(e)=>  this.handleDelete(e,c.pk) }> Delete</button>
                        </td>
                    </tr>)}
                </tbody>
            </table>
            <button  className="btn btn-primary"  onClick=  {  this.nextPage  }>Next</button>
        </div>
        );
    }
}
export default OfficeList