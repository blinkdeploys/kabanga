import axios from 'axios'
const API_URL = 'http://localhost:8000/api'
// axios.defaults.baseURL = API_URL

export default class CandidateService {
    // constructor() {}

    getCandidates() {
        const url = `${API_URL}/candidates/`
        return axios.get(url).then(response => response.data)
    }

    getCandidatesByURL(link) {
        const url = `${API_URL}${link}`
        return axios.get(url).then(response => response.data)
    }

    getCandidate(pk) {
        const url = `${API_URL}/candidate/${pk}`
        return axios.get(url).then(response => response.data)
    }

    deleteCandidate(candidate) {
        const url = `${API_URL}/candidate/${candidate.pk}`
        return axios.delete(url)
    }

    createCandidate(candidate) {
        const url = `${API_URL}/candidate/`
        return axios.post(url, candidate)
    }

    updateCandidate(candidate) {
        const url = `${API_URL}/candidate/${candidate.pk}`
        return axios.put(url, candidate)
    }
}