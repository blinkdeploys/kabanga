import axios from 'axios'
const API_URL = 'http://localhost:8000/api'
// axios.defaults.baseURL = API_URL

export default class StationService {
    // constructor() {}

    getStations() {
        const url = `${API_URL}/stations/`
        return axios.get(url).then(response => response.data)
    }

    getStationsByURL(link) {
        const url = `${API_URL}${link}`
        return axios.get(url).then(response => response.data)
    }

    getStation(pk) {
        const url = `${API_URL}/station/${pk}`
        return axios.get(url).then(response => response.data)
    }

    deleteStation(station) {
        const url = `${API_URL}/station/${station.pk}`
        return axios.delete(url)
    }

    createStation(station) {
        const url = `${API_URL}/station/`
        return axios.post(url, station)
    }

    updateStation(station) {
        const url = `${API_URL}/station/${station.pk}`
        return axios.put(url, station)
    }
}