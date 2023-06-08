import axios from 'axios'
const API_URL = 'http://localhost:8000/api'
// axios.defaults.baseURL = API_URL

export default class OfficesService {
    // constructor() {}

    getOffices() {
        const url = `${API_URL}/offices/`
        return axios.get(url).then(response => response.data)
    }

    getOfficesByURL(link) {
        const url = `${API_URL}${link}`
        return axios.get(url).then(response => response.data)
    }

    getOffice(pk) {
        const url = `${API_URL}/office/${pk}`
        return axios.get(url).then(response => response.data)
    }

    deleteOffice(office) {
        const url = `${API_URL}/office/${office.pk}`
        return axios.delete(url)
    }

    createOffice(office) {
        const url = `${API_URL}/office/`
        return axios.post(url, office)
    }

    updateOffice(office) {
        const url = `${API_URL}/office/${office.pk}`
        return axios.put(url, office)
    }
}