import axios from 'axios'
const API_URL = 'http://localhost:8000/api'
// axios.defaults.baseURL = API_URL

export default class ResultsService {
    // constructor() {}

    getResults() {
        const url = `${API_URL}/results/`
        return axios.get(url).then(response => response.data)
    }

    getResultsByURL(link) {
        const url = `${API_URL}${link}`
        return axios.get(url).then(response => response.data)
    }

    getResult(pk) {
        const url = `${API_URL}/result/${pk}`
        return axios.get(url).then(response => response.data)
    }

    deleteResult(result) {
        const url = `${API_URL}/result/${result.pk}`
        return axios.delete(url)
    }

    createResult(result) {
        const url = `${API_URL}/result/`
        return axios.post(url, result)
    }

    updateResult(result) {
        const url = `${API_URL}/result/${result.pk}`
        return axios.put(url, result)
    }
}