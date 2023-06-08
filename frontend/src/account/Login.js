import  React, { Component } from  'react';
import  LoginService  from  './AccountServices';
import { useParams } from "react-router-dom"

function withParams(Component) {
    return props => <Component {...props} params={useParams()} />;
}
  
const  loginService  =  new  LoginService();


class Login extends Component {

    constructor(props) {
        super(props)
        this.handleSubmit = this.handleSubmit.bind(this);
        this.state = {
            context: {
                username: 'username',
                password: '*******',
                // email: 'email address',
            }
        }
        this.onInputChange = this.onInputChange.bind(this);
    }

    componentDidMount(){
        // const { match: { params } } =  this.props;
        const { params } =  this.props;

        if(params  &&  params.pk)
        {
            loginService.getUserToken(params.pk).then((c)=>{
                this.setState({
                    username: c?.username || '',
                    password: c?.password || '',
                    // email: c?.email || '',
                })
            })
        }
    }

    handleCreate(){
        loginService.createConstituency({
            "username":  this.state.username,
            "password":  this.state.password,
            "email":  this.state.email,
            "phone":  this.state.phone,
            "address":  this.state.address,
            "description":  this.state.description
        }).then((result)=>{
            alert("Constituency created!");
        }).catch(()=>{
            alert('There was an error! Please re-check your form.');
        });
    }

    handleUpdate(pk){
        loginService.updateConstituency({
            "pk":  pk,
            "username":  this.state.username,
            "password":  this.state.password,
            "email":  this.state.email,
            "phone":  this.state.phone,
            "address":  this.state.address,
            "description":  this.state.description
        }).then((result)=>{
            alert("Constituency updated!");
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
        const constituency = this.state
        const context = constituency.context
        return (
          <form onSubmit={this.handleSubmit}>
            <div className='container'>
                <div className='row align-items-center'>
                    <div className='col'></div>
                    <div className='col align-self-center'>
                        <div className="form-group">
                            <label>Username:</label>
                            <input className="form-control"
                                type="text"
                                name="username"
                                value={constituency.username || ''}
                                onChange={this.onInputChange}
                                placeholder={context.userName} />
                        
                            <label>Password:</label>
                            <input
                                className="form-control"
                                type="password" name="password"
                                value={constituency.password || ''}
                                onChange={this.onInputChange}
                                placeholder={context.password} />
                        
                            {/*<label>Email:</label>
                            <input className="form-control"
                                type="text" name="email"
                                value={constituency.email || ''}
                                onChange={this.onInputChange}
                                placeholder={context.email} />*/}
                        
                            <div className="py-3">
                                <input className="btn btn-primary" type="submit" value="Login" />
                                <a className="btn" href={"/"}>Cancel</a>
                            </div>
                        </div>
                    </div>
                    <div className='col'></div>
                </div>
            </div>
          </form>
        );
    }
}
export default withParams(Login)