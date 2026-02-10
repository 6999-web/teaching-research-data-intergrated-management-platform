import { defineStore } from 'pinia'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    userId: '',
    userName: '',
    userRole: '' as 'director' | 'college_leader' | 'evaluation_team' | 'evaluation_office' | 'president_office' | '',
    token: '',
    teachingOfficeId: ''
  }),
  
  getters: {
    isLoggedIn: (state) => !!state.token || !!state.userName,
    roleName: (state) => {
      const roleMap = {
        director: '教研室',
        college_leader: '二级学院负责人',
        evaluation_team: '评教小组',
        evaluation_office: '评教小组办公室',
        president_office: '校长办公会'
      }
      return roleMap[state.userRole as keyof typeof roleMap] || ''
    },
    roleColor: (state) => {
      const colorMap = {
        director: '#66bb6a',
        college_leader: '#ab47bc',
        evaluation_team: '#ff7043',
        evaluation_office: '#ffa726',
        president_office: '#9c27b0'
      }
      return colorMap[state.userRole as keyof typeof colorMap] || '#1a237e'
    }
  },
  
  actions: {
    setRole(role: 'director' | 'college_leader' | 'evaluation_team' | 'evaluation_office' | 'president_office') {
      this.userRole = role
      localStorage.setItem('userRole', role)
    },
    
    loadFromStorage() {
      const role = localStorage.getItem('userRole')
      const userName = localStorage.getItem('userName')
      if (role) {
        this.userRole = role as any
      }
      if (userName) {
        this.userName = userName
      }
    },
    
    logout() {
      this.$reset()
      localStorage.removeItem('userRole')
      localStorage.removeItem('userName')
      localStorage.removeItem('viewMode')
    }
  }
})
