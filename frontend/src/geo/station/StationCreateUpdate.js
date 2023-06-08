import  React, { Component } from  'react';
import  StationService  from  './StationService';
import { useParams } from "react-router-dom"

function withParams(Component) {
    return props => <Component {...props} params={useParams()} />;
}
  
const  stationService  =  new  StationService();


class StationCreateUpdate extends Component {

    constructor(props) {
        super(props)
        this.handleSubmit = this.handleSubmit.bind(this);
        this.state = {
            context: {
                title: 'title',
                constituency: 'constituency',
            }
        }
        this.onInputChange = this.onInputChange.bind(this);
    }

    componentDidMount(){
        // const { match: { params } } =  this.props;
        const { params } =  this.props;

        if(params  &&  params.pk)
        {
            stationService.getStation(params.pk).then((c)=>{
                this.setState({
                    title: c?.title || '',
                    constituency: c?.constituency || '',
                })
            })
        }
    }

    handleCreate(){
        stationService.createStation({
            "title":  this.state.title,
            "constituency":  this.state.constituency,
        }).then((result)=>{
            alert("Station created!");
        }).catch(()=>{
            alert('There was an error! Please re-check your form.');
        });
    }

    handleUpdate(pk){
        stationService.updateStation({
            "pk":  pk,
            "title":  this.state.title,
            "constituency":  this.state.constituency,
        }).then((result)=>{
            alert("Station updated!");
        }).catch(()=>{
            alert('There was an error! Please re-check your form.');
        });
    }    

    handleSubmit(event) {
        // const { match: { params } } =  this.props;
        const { params } =  this.props;
        if(params  &&  params.pk){
            this.handleUpdate(params.pk);
        } else {
            this.handleCreate();
        }
        event.preventDefault();
    }

    onInputChange(event) {
        this.setState({
            [event.target.name]: event.target.value
        })
    }

    render() {
        const station = this.state
        const context = station.context
        return (
          <form onSubmit={this.handleSubmit}>
            <div className="form-group">
                <label>First Name:</label>
                <input className="form-control"
                    type="text"
                    name="title"
                    value={station.title || ''}
                    onChange={this.onInputChange}
                    placeholder={context.title} />
            
                <label>Last Name:</label>
                <input
                    className="form-control"
                    type="text" name="constituency"
                    value={station.constituency || ''}
                    onChange={this.onInputChange}
                    placeholder={context.constituency} />
            
                <label>Phone:</label>
                <input className="form-control"
                    type="text" name="phone"
                    value={station.phone || ''}
                    onChange={this.onInputChange}
                    placeholder={context.phone} />
            
                <label>Email:</label>
                <input className="form-control"
                    type="text" name="email"
                    value={station.email || ''}
                    onChange={this.onInputChange}
                    placeholder={context.email} />
            
                <label>Address:</label>
                <input className="form-control"
                    type="text" name="address"
                    value={station.address || ''}
                    onChange={this.onInputChange}
                    placeholder={context.address} />
            
                <label>Description:</label>
                <textarea className="form-control"
                    name="description"
                    value={station.description || ''}
                    onChange={this.onInputChange}
                    placeholder={context.description} ></textarea>
              
                <input className="btn btn-primary" type="submit" value="Submit" />
                <a className="btn" href={"/"}>Cancel</a>
            </div>
          </form>
        );
    }
}
export default withParams(StationCreateUpdate)