import axios from 'axios'
const API_URL = 'http://localhost:8000/api'
// axios.defaults.baseURL = API_URL

export default class LoginService {
    // constructor() {}

    getUserToken() {
        const url = `${API_URL}/api-token-auth/`
        return axios.get(url).then(response => response.data)
    }

    /*
    getConstituenciesByURL(link) {
        const url = `${API_URL}${link}`
        return axios.get(url).then(response => response.data)
    }
    
    getConstituency(pk) {
        const url = `${API_URL}/constituency/${pk}`
        return axios.get(url).then(response => response.data)
    }
    
    deleteConstituency(constituency) {
        const url = `${API_URL}/constituency/${constituency.pk}`
        return axios.delete(url)
    }
    
    createConstituency(constituency) {
        const url = `${API_URL}/constituency/`
        return axios.post(url, constituency)
    }
    
    updateConstituency(constituency) {
        const url = `${API_URL}/constituency/${constituency.pk}`
        return axios.put(url, constituency)
    }
    */
}