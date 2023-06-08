import  React, { Component } from  'react';
import  StationService  from  './StationService';

const  stationService  =  new  StationService();

class StationList extends Component {

    constructor(props) {
        super(props)
        this.state = {
            station: [],
            nextPageURL: '',
        }
        this.nextPage = this.nextPage.bind(this)
        this.handleDelete = this.handleDelete.bind(this)
    }

    componentDidMount() {
        var self = this
        stationService.getStations().then(function (result) {
            self.setState({ station: result.data, nextPageURL: result.nextlink})
        })
    }

    handleDelete(e, pk) {
        var self = this
        stationService.deleteStation({pk: pk}).then(() => {
            var newArr = self.state.station.filter(function(obj) {
                return obj.pk !== pk
            })
            self.setState({station: newArr})
        })
    }

    nextPage(){
        var self = this
        stationService.getStationsByURL(this.state.nextPageURL).then((result) => {
            self.setState({ station: result.data, nextPageURL: result.nextlink})
        })
    }

    render() {
    
        return (
        <div  className="station--list">
            <table  className="table">
                <thead  key="thead">
                <tr>
                    <th>#</th>
                    <th>Code</th>
                    <th>Polling Station</th>
                    <th>Constituency</th>
                    <th>Actions</th>
                </tr>
                </thead>
                <tbody>
                    {this.state?.station?.map( c  =>
                    <tr  key={c.pk}>
                        <td>{c.pk}</td>
                        <td>{c.code}</td>
                        <td>
                            <a href={"/station/" + c.pk}>
                                {c.title}
                            </a>
                        </td>
                        <td>{c.constituency.title}</td>
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
export default StationList