import  React from  'react';
import { BrowserRouter, Route, Routes } from  'react-router-dom'

import  HomePage  from  './poll/HomePage'
import  Login  from  './account/Login'
import  Register  from  './account/Register'

import  NationList  from  './geo/nation/NationList'
import  NationCreateUpdate  from  './geo/nation/NationCreateUpdate'
import  RegionList  from  './geo/region/RegionList'
import  RegionCreateUpdate  from  './geo/region/RegionCreateUpdate'
import  ConstituencyList  from  './geo/constituency/ConstituencyList'
import  ConstituencyCreateUpdate  from  './geo/constituency/ConstituencyCreateUpdate'
import  StationList  from  './geo/station/StationList'
import  StationCreateUpdate  from  './geo/station/StationCreateUpdate'

import  AgentList  from  './people/agent/AgentList'
import  AgentCreateUpdate  from  './people/agent/AgentCreateUpdate'
import  CandidateList  from  './people/candidate/CandidateList'
import  CandidateCreateUpdate  from  './people/candidate/CandidateCreateUpdate'
import  PartyList  from  './people/party/PartyList'
import  PartyCreateUpdate  from  './people/party/PartyCreateUpdate'

import  EventList  from  './poll/event/EventList'
import  EventCreateUpdate  from  './poll/event/EventCreateUpdate'
import  OfficeList  from  './poll/office/OfficeList'
import  OfficeCreateUpdate  from  './poll/office/OfficeCreateUpdate'
import  PositionList  from  './poll/position/PositionList'
import  PositionCreateUpdate  from  './poll/position/PositionCreateUpdate'
import  ResultList  from  './poll/result/ResultList'
import  ResultCreateUpdate  from  './poll/result/ResultCreateUpdate'
import  ResultApprovalList  from  './poll/result_approval/ResultApprovalList'
import  ResultApprovalCreateUpdate  from  './poll/result_approval/ResultApprovalCreateUpdate'

// import  'https://maxcdn.bootstrapcdn.com/bootstrap/4.0.0/js/bootstrap.min.js';


import './App.css';

//import 'https://maxcdn.bootstrapcdn.com/bootstrap/4.0.0/css/bootstrap.min.css';

const  BaseLayout  = () => (
  <div  className="container-fluid">

    <nav className="navbar navbar-expand-lg navbar-light bg-light">
      <h2 className="navbar-brand">Kabanga</h2>
      <button  className="navbar-toggler" type="button" data-bs-toggle="collapse"  data-bs-target="#navbarNavAltMarkup"  aria-controls="navbarNavAltMarkup"  aria-expanded="false"  aria-label="Toggle navigation">
        <span  className="navbar-toggler-icon"></span>
      </button>
      <div  className="collapse navbar-collapse" id="navbarNavAltMarkup">

        <ul className="navbar-nav mr-auto">

          <li className="nav-item active">
            <a className="nav-link" href="/">Home <span className="sr-only">(current)</span></a>
          </li>

          <li className="nav-item">
            <a className="nav-link" href="/results">Polls</a>
          </li>

          <li className="nav-item">
            <a className="nav-link" href="/result_approvals">Poll Approvals</a>
          </li>

          <li className="nav-item dropdown">
            <a className="nav-link dropdown-toggle" href="#geo" id="electionDropDown" role="button" data-bs-toggle="dropdown" aria-haspopup="true" aria-expanded="false">
              Reports
            </a>
            <div className="dropdown-menu" aria-labelledby="electionDropDown">
              <a className="dropdown-item" href="/agents">Constituency Parliament Collation Results</a>
              <a className="dropdown-item" href="/candidates">Regional Parliament Collation Results</a>
              <a className="dropdown-item" href="/parties">National Parliament Collation Results</a>
              <div className="dropdown-divider"></div>
              <a className="dropdown-item" href="/events">Constituency Presidential Collation Results</a>
              <a className="dropdown-item" href="/offices">Regional Presidential Collation Results</a>
              <a className="dropdown-item" href="/positions">National Presidential Collation Results</a>
            </div>
          </li>

          <li className="nav-item dropdown">
            <a className="nav-link dropdown-toggle" href="#geo" id="electionDropDown" role="button" data-bs-toggle="dropdown" aria-haspopup="true" aria-expanded="false">
              Election
            </a>
            <div className="dropdown-menu" aria-labelledby="electionDropDown">
              <a className="dropdown-item" href="/agents">Agents</a>
              <a className="dropdown-item" href="/candidates">Candidates</a>
              <div className="dropdown-divider"></div>
              <a className="dropdown-item" href="/parties">Parties</a>
              <a className="dropdown-item" href="/events">Events</a>
              <a className="dropdown-item" href="/offices">Offices</a>
              <a className="dropdown-item" href="/positions">Positions</a>
            </div>
          </li>

          <li className="nav-item dropdown">
            <a className="nav-link dropdown-toggle" href="#geo" id="geoDropDown" role="button" data-bs-toggle="dropdown" aria-haspopup="true" aria-expanded="false">
              Geo
            </a>
            <div className="dropdown-menu" aria-labelledby="geoDropDown">
              <a className="dropdown-item" href="/stations">Polling Stations</a>
              <a className="dropdown-item" href="/constituencies">Constituencies</a>
              <a className="dropdown-item" href="/regions">Regions</a>
              <a className="dropdown-item" href="/nations">Nations</a>
            </div>
          </li>

        </ul>

      </div>
    </nav>



    <div  className="content">
      <Routes>
        <Route  path="/"  exact  element={<HomePage />}  />
        <Route  path="/login"  exact  element={<Login />}  />
        <Route  path="/register"  exact  element={<Register />}  />

        <Route  path="/nations"  exact  element={<NationList />}  />
        <Route  path="/nation/:pk"  element={<NationCreateUpdate />}  />
        <Route  path="/nation/"  exact  element={<NationCreateUpdate />}  />
        <Route  path="/regions"  exact  element={<RegionList />}  />
        <Route  path="/region/:pk"  element={<RegionCreateUpdate />}  />
        <Route  path="/region/"  exact  element={<RegionCreateUpdate />}  />
        <Route  path="/constituencies"  exact  element={<ConstituencyList />}  />
        <Route  path="/constituency/:pk"  element={<ConstituencyCreateUpdate />}  />
        <Route  path="/constituency/"  exact  element={<ConstituencyCreateUpdate />}  />
        <Route  path="/stations"  exact  element={<StationList />}  />
        <Route  path="/station/:pk"  element={<StationCreateUpdate />}  />
        <Route  path="/station/"  exact  element={<StationCreateUpdate />}  />

        <Route  path="/agents"  exact  element={<AgentList />}  />
        <Route  path="/agent/:pk"  element={<AgentCreateUpdate />}  />
        <Route  path="/agent/"  exact  element={<AgentCreateUpdate />}  />
        <Route  path="/candidates"  exact  element={<CandidateList />}  />
        <Route  path="/candidate/:pk"  element={<CandidateCreateUpdate />}  />
        <Route  path="/candidate/"  exact  element={<CandidateCreateUpdate />}  />
        <Route  path="/parties"  exact  element={<PartyList />}  />
        <Route  path="/party/:pk"  element={<PartyCreateUpdate />}  />
        <Route  path="/party/"  exact  element={<PartyCreateUpdate />}  />

        <Route  path="/events"  exact  element={<EventList />}  />
        <Route  path="/event/:pk"  element={<EventCreateUpdate />}  />
        <Route  path="/event/"  exact  element={<EventCreateUpdate />}  />
        <Route  path="/offices"  exact  element={<OfficeList />}  />
        <Route  path="/office/:pk"  element={<OfficeCreateUpdate />}  />
        <Route  path="/office/"  exact  element={<OfficeCreateUpdate />}  />
        <Route  path="/positions"  exact  element={<PositionList />}  />
        <Route  path="/position/:pk"  element={<PositionCreateUpdate />}  />
        <Route  path="/position/"  exact  element={<PositionCreateUpdate />}  />
        <Route  path="/results"  exact  element={<ResultList />}  />
        <Route  path="/result/:pk"  element={<ResultCreateUpdate />}  />
        <Route  path="/result/"  exact  element={<ResultCreateUpdate />}  />
        <Route  path="/result_approvals"  exact  element={<ResultApprovalList />}  />
        <Route  path="/result_approval/:pk"  element={<ResultApprovalCreateUpdate />}  />
        <Route  path="/result_approval/"  exact  element={<ResultApprovalCreateUpdate />}  />

      </Routes>
    </div>
  </div>
)


function App() {
  return (
    <BrowserRouter>
      <BaseLayout />
    </BrowserRouter>
  );
}

export default App;
