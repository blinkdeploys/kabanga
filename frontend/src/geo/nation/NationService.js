import axios from 'axios'
const API_URL = 'http://localhost:8000/api'
// axios.defaults.baseURL = API_URL

export default class NationsService {
    // constructor() {}

    getNations() {
        const url = `${API_URL}/nations/`
        return axios.get(url).then(response => response.data)
    }

    getNationsByURL(link) {
        const url = `${API_URL}${link}`
        return axios.get(url).then(response => response.data)
    }

    getNation(pk) {
        const url = `${API_URL}/nation/${pk}`
        return axios.get(url).then(response => response.data)
    }

    deleteNation(nation) {
        const url = `${API_URL}/nation/${nation.pk}`
        return axios.delete(url)
    }

    createNation(nation) {
        const url = `${API_URL}/nation/`
        return axios.post(url, nation)
    }

    updateNation(nation) {
        const url = `${API_URL}/nation/${nation.pk}`
        return axios.put(url, nation)
    }
}