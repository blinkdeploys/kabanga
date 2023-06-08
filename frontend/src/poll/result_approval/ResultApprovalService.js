import axios from 'axios'
const API_URL = 'http://localhost:8000/api'
// axios.defaults.baseURL = API_URL

export default class ResultApprovalService {
    // constructor() {}

    getResultApprovals() {
        const url = `${API_URL}/result_approvals/`
        return axios.get(url).then(response => response.data)
    }

    getResultApprovalsByURL(link) {
        const url = `${API_URL}${link}`
        return axios.get(url).then(response => response.data)
    }

    getResultApproval(pk) {
        const url = `${API_URL}/result_approval/${pk}`
        return axios.get(url).then(response => response.data)
    }

    deleteResultApproval(resultApproval) {
        const url = `${API_URL}/result_approval/${resultApproval.pk}`
        return axios.delete(url)
    }

    createResultApproval(resultApproval) {
        const url = `${API_URL}/result_approval/`
        return axios.post(url, resultApproval)
    }

    updateResultApproval(resultApproval) {
        const url = `${API_URL}/result_approval/${resultApproval.pk}`
        return axios.put(url, resultApproval)
    }
}