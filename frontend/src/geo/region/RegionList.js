import  React, { Component } from  'react';
import  RegionService  from  './RegionService';

const  regionService  =  new  RegionService();

class RegionList extends Component {

    constructor(props) {
        super(props)
        this.state = {
            region: [],
            nextPageURL: '',
        }
        this.nextPage = this.nextPage.bind(this)
        this.handleDelete = this.handleDelete.bind(this)
    }

    componentDidMount() {
        var self = this
        regionService.getRegions().then(function (result) {
            self.setState({ region: result.data, nextPageURL: result.nextlink})
        })
    }

    handleDelete(e, pk) {
        var self = this
        regionService.deleteRegion({pk: pk}).then(() => {
            var newArr = self.state.region.filter(function(obj) {
                return obj.pk !== pk
            })
            self.setState({region: newArr})
        })
    }

    nextPage(){
        var self = this
        regionService.getRegionsByURL(this.state.nextPageURL).then((result) => {
            self.setState({ region: result.data, nextPageURL: result.nextlink})
        })
    }

    render() {
    
        return (
        <div  className="region--list">
            <table  className="table">
                <thead  key="thead">
                <tr>
                    <th>#</th>
                    <th>Regions</th>
                    <th>Actions</th>
                </tr>
                </thead>
                <tbody>
                    {this.state?.region?.map( c  =>
                    <tr  key={c.pk}>
                        <td>{c.pk}</td>
                        <td>
                            <a href={"/region/" + c.pk}>
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
export default RegionList