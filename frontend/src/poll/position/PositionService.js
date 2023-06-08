import axios from 'axios'
const API_URL = 'http://localhost:8000/api'
// axios.defaults.baseURL = API_URL

export default class PositionsService {
    // constructor() {}

    getPositions() {
        const url = `${API_URL}/positions/`
        return axios.get(url).then(response => response.data)
    }

    getPositionsByURL(link) {
        const url = `${API_URL}${link}`
        return axios.get(url).then(response => response.data)
    }

    getPosition(pk) {
        const url = `${API_URL}/position/${pk}`
        return axios.get(url).then(response => response.data)
    }

    deletePosition(position) {
        const url = `${API_URL}/position/${position.pk}`
        return axios.delete(url)
    }

    createPosition(position) {
        const url = `${API_URL}/position/`
        return axios.post(url, position)
    }

    updatePosition(position) {
        const url = `${API_URL}/position/${position.pk}`
        return axios.put(url, position)
    }
}