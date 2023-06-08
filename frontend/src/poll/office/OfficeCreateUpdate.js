import  React, { Component } from  'react';
import  OfficeService  from  './OfficeService';
import { useParams } from "react-router-dom"

function withParams(Component) {
    return props => <Component {...props} params={useParams()} />;
}
  
const  officeService  =  new  OfficeService();


class OfficeCreateUpdate extends Component {

    constructor(props) {
        super(props)
        this.handleSubmit = this.handleSubmit.bind(this);
        this.state = {
            context: {
                title: 'office title',
                level: 'office level',
            }
        }
        this.onInputChange = this.onInputChange.bind(this);
    }

    componentDidMount(){
        // const { match: { params } } =  this.props;
        const { params } =  this.props;

        if(params  &&  params.pk)
        {
            officeService.getOffice(params.pk).then((c)=>{
                this.setState({
                    title: c?.title || '',
                    level: c?.level || '',
                })
            })
        }
    }

    handleCreate(){
        officeService.createOffice({
            "title":  this.state.title,
            "level":  this.state.level,
        }).then((office)=>{
            alert("Office created!");
        }).catch(()=>{
            alert('There was an error! Please re-check your form.');
        });
    }

    handleUpdate(pk){
        officeService.updateOffice({
            "pk":  pk,
            "title":  this.state.title,
            "level":  this.state.level,
        }).then((office)=>{
            alert("Office updated!");
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
        const office = this.state
        const context = office.context
        return (
          <form onSubmit={this.handleSubmit}>
            <div className="form-group">
                <label>First Name:</label>
                <input className="form-control"
                    type="text"
                    name="title"
                    value={office.title || ''}
                    onChange={this.onInputChange}
                    placeholder={context.title} />
            
                <label>Last Name:</label>
                <input
                    className="form-control"
                    type="text" name="level"
                    value={office.level || ''}
                    onChange={this.onInputChange}
                    placeholder={context.level} />
            
                <input className="btn btn-primary" type="submit" value="Submit" />
                <a className="btn" href={"/"}>Cancel</a>
            </div>
          </form>
        );
    }
}
export default withParams(OfficeCreateUpdate)