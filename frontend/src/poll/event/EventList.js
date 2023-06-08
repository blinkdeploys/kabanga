import  React, { Component } from  'react';
import  EventService  from  './EventService';

const  eventService  =  new  EventService();

class EventList extends Component {

    constructor(props) {
        super(props)
        this.state = {
            event: [],
            nextPageURL: '',
        }
        this.nextPage = this.nextPage.bind(this)
        this.handleDelete = this.handleDelete.bind(this)
    }

    componentDidMount() {
        var self = this
        eventService.getEvents().then(function (event) {
            self.setState({ event: event.data, nextPageURL: event.nextlink})
        })
    }

    handleDelete(e, pk) {
        var self = this
        eventService.deleteEvent({pk: pk}).then(() => {
            var newArr = self.state.event.filter(function(obj) {
                return obj.pk !== pk
            })
            self.setState({event: newArr})
        })
    }

    nextPage(){
        var self = this
        eventService.getEventsByURL(this.state.nextPageURL).then((event) => {
            self.setState({ event: event.data, nextPageURL: event.nextlink})
        })
    }

    render() {
    
        return (
        <div  className="event--list">
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
                    {this.state?.event?.map( c  =>
                    <tr  key={c.pk}>
                        <td>{c.pk}</td>
                        <td>
                            <a href={"/event/" + c.pk}>
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
export default EventList