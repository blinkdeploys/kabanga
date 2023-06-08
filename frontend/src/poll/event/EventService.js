import axios from 'axios'
const API_URL = 'http://localhost:8000/api'
// axios.defaults.baseURL = API_URL

export default class EventsService {
    // constructor() {}

    getEvents() {
        const url = `${API_URL}/events/`
        return axios.get(url).then(response => response.data)
    }

    getEventsByURL(link) {
        const url = `${API_URL}${link}`
        return axios.get(url).then(response => response.data)
    }

    getEvent(pk) {
        const url = `${API_URL}/event/${pk}`
        return axios.get(url).then(response => response.data)
    }

    deleteEvent(event) {
        const url = `${API_URL}/event/${event.pk}`
        return axios.delete(url)
    }

    createEvent(event) {
        const url = `${API_URL}/event/`
        return axios.post(url, event)
    }

    updateEvent(event) {
        const url = `${API_URL}/event/${event.pk}`
        return axios.put(url, event)
    }
}