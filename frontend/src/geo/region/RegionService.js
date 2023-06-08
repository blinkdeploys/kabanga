import axios from 'axios'
const API_URL = 'http://localhost:8000/api'
// axios.defaults.baseURL = API_URL

export default class RegionService {
    // constructor() {}

    getRegions() {
        const url = `${API_URL}/regions/`
        return axios.get(url).then(response => response.data)
    }

    getRegionsByURL(link) {
        const url = `${API_URL}${link}`
        return axios.get(url).then(response => response.data)
    }

    getRegion(pk) {
        const url = `${API_URL}/region/${pk}`
        return axios.get(url).then(response => response.data)
    }

    deleteRegion(region) {
        const url = `${API_URL}/region/${region.pk}`
        return axios.delete(url)
    }

    createRegion(region) {
        const url = `${API_URL}/region/`
        return axios.post(url, region)
    }

    updateRegion(region) {
        const url = `${API_URL}/region/${region.pk}`
        return axios.put(url, region)
    }
}