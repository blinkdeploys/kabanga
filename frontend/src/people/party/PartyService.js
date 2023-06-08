import axios from 'axios'
const API_URL = 'http://localhost:8000/api'
// axios.defaults.baseURL = API_URL

export default class PartyService {
    // constructor() {}

    getParties() {
        const url = `${API_URL}/parties/`
        return axios.get(url).then(response => response.data)
    }

    getPartiesByURL(link) {
        const url = `${API_URL}${link}`
        return axios.get(url).then(response => response.data)
    }

    getParty(pk) {
        const url = `${API_URL}/party/${pk}`
        return axios.get(url).then(response => response.data)
    }

    deleteParty(party) {
        const url = `${API_URL}/party/${party.pk}`
        return axios.delete(url)
    }

    createParty(party) {
        const url = `${API_URL}/party/`
        return axios.post(url, party)
    }

    updateParty(party) {
        const url = `${API_URL}/party/${party.pk}`
        return axios.put(url, party)
    }
}