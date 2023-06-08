import  React, { Component } from  'react';
import  PositionService  from  './PositionService';
import { useParams } from "react-router-dom"

function withParams(Component) {
    return props => <Component {...props} params={useParams()} />;
}
  
const  positionService  =  new  PositionService();


class PositionCreateUpdate extends Component {

    constructor(props) {
        super(props)
        this.handleSubmit = this.handleSubmit.bind(this);
        this.state = {
            context: {
                firstName: 'first name',
                lastName: 'last name',
                phone: 'phone number',
                email: 'email address',
                address: 'address',
                description: 'description',
            }
        }
        this.onInputChange = this.onInputChange.bind(this);
    }

    componentDidMount(){
        // const { match: { params } } =  this.props;
        const { params } =  this.props;

        if(params  &&  params.pk)
        {
            positionService.getPosition(params.pk).then((c)=>{
                this.setState({
                    firstName: c?.first_name || '',
                    lastName: c?.last_name || '',
                    email: c?.email || '',
                    phone: c?.phone || '',
                    address: c?.address || '',
                    description: c?.description || '',
                })
            })
        }
    }

    handleCreate(){
        positionService.createPosition({
            "first_name":  this.state.firstName,
            "last_name":  this.state.lastName,
            "email":  this.state.email,
            "phone":  this.state.phone,
            "address":  this.state.address,
            "description":  this.state.description
        }).then((position)=>{
            alert("Position created!");
        }).catch(()=>{
            alert('There was an error! Please re-check your form.');
        });
    }

    handleUpdate(pk){
        positionService.updatePosition({
            "pk":  pk,
            "first_name":  this.state.firstName,
            "last_name":  this.state.lastName,
            "email":  this.state.email,
            "phone":  this.state.phone,
            "address":  this.state.address,
            "description":  this.state.description
        }).then((position)=>{
            alert("Position updated!");
        }).catch(()=>{
            alert('There was an error! Please re-check your form.');
        });
    }    

    handleSubmit(position) {
        // const { match: { params } } =  this.props;
        const { params } =  this.props;
        if(params  &&  params.pk){
            this.handleUpdate(params.pk);
        } else {
            this.handleCreate();
        }
        position.prpositionDefault();
    }

    onInputChange(position) {
        this.setState({
            [position.target.name]: position.target.value
        })
    }

    render() {
        const position = this.state
        const context = position.context
        return (
          <form onSubmit={this.handleSubmit}>
            <div className="form-group">
                <label>First Name:</label>
                <input className="form-control"
                    type="text"
                    name="firstName"
                    value={position.firstName || ''}
                    onChange={this.onInputChange}
                    placeholder={context.firstName} />
            
                <label>Last Name:</label>
                <input
                    className="form-control"
                    type="text" name="lastName"
                    value={position.lastName || ''}
                    onChange={this.onInputChange}
                    placeholder={context.lastName} />
            
                <label>Phone:</label>
                <input className="form-control"
                    type="text" name="phone"
                    value={position.phone || ''}
                    onChange={this.onInputChange}
                    placeholder={context.phone} />
            
                <label>Email:</label>
                <input className="form-control"
                    type="text" name="email"
                    value={position.email || ''}
                    onChange={this.onInputChange}
                    placeholder={context.email} />
            
                <label>Address:</label>
                <input className="form-control"
                    type="text" name="address"
                    value={position.address || ''}
                    onChange={this.onInputChange}
                    placeholder={context.address} />
            
                <label>Description:</label>
                <textarea className="form-control"
                    name="description"
                    value={position.description || ''}
                    onChange={this.onInputChange}
                    placeholder={context.description} ></textarea>
              
                <input className="btn btn-primary" type="submit" value="Submit" />
                <a className="btn" href={"/"}>Cancel</a>
            </div>
          </form>
        );
    }
}
export default withParams(PositionCreateUpdate)