import axios from 'axios'
const API_URL = 'http://localhost:8000/api'
// axios.defaults.baseURL = API_URL

export default class AgentService {
    // constructor() {}

    getAgents() {
        const url = `${API_URL}/agents/`
        return axios.get(url).then(response => response.data)
    }

    getAgentsByURL(link) {
        const url = `${API_URL}${link}`
        return axios.get(url).then(response => response.data)
    }

    getAgent(pk) {
        const url = `${API_URL}/agent/${pk}`
        return axios.get(url).then(response => response.data)
    }

    deleteAgent(agent) {
        const url = `${API_URL}/agent/${agent.pk}`
        return axios.delete(url)
    }

    createAgent(agent) {
        const url = `${API_URL}/agent/`
        return axios.post(url, agent)
    }

    updateAgent(agent) {
        const url = `${API_URL}/agent/${agent.pk}`
        return axios.put(url, agent)
    }
}