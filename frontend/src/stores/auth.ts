import { defineStore } from 'pinia'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    userId: '',
    userName: '',
    userRole: '' as 'director' | 'college_leader' | 'evaluation_team' | 'evaluation_office' | 'president_office' | 'teaching_office' | '',
    token: '',
    teachingOfficeId: ''
  }),
  
  getters: {
    isLoggedIn: (state) => {
      // 检查state中的token或localStorage中的token
      const storedToken = localStorage.getItem('token')
      return !!state.token || !!storedToken
    },
    roleName: (state) => {
      const roleMap = {
        director: '教研室',
        teaching_office: '教研室',
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
        teaching_office: '#66bb6a',
        college_leader: '#ab47bc',
        evaluation_team: '#ff7043',
        evaluation_office: '#ffa726',
        president_office: '#9c27b0'
      }
      return colorMap[state.userRole as keyof typeof colorMap] || '#1a237e'
    }
  },
  
  actions: {
    setRole(role: 'director' | 'college_leader' | 'evaluation_team' | 'evaluation_office' | 'president_office' | 'teaching_office') {
      this.userRole = role
      localStorage.setItem('userRole', role)
    },
    
    setAuth(data: { token: string; user: any }) {
      this.token = data.token
      this.userId = data.user.id
      this.userName = data.user.name
      this.userRole = data.user.role
      this.teachingOfficeId = data.user.teaching_office_id || ''
      
      // 保存到localStorage
      localStorage.setItem('token', data.token)
      localStorage.setItem('userId', data.user.id)
      localStorage.setItem('userName', data.user.name)
      localStorage.setItem('userRole', data.user.role)
      if (data.user.teaching_office_id) {
        localStorage.setItem('teachingOfficeId', data.user.teaching_office_id)
      }
    },
    
    loadFromStorage() {
      const token = localStorage.getItem('token')
      const userId = localStorage.getItem('userId')
      const userName = localStorage.getItem('userName')
      const role = localStorage.getItem('userRole')
      const teachingOfficeId = localStorage.getItem('teachingOfficeId')
      
      if (token) this.token = token
      if (userId) this.userId = userId
      if (userName) this.userName = userName
      if (role) this.userRole = role as any
      if (teachingOfficeId) this.teachingOfficeId = teachingOfficeId
    },
    
    logout() {
      this.$reset()
      localStorage.removeItem('token')
      localStorage.removeItem('userId')
      localStorage.removeItem('userName')
      localStorage.removeItem('userRole')
      localStorage.removeItem('teachingOfficeId')
      localStorage.removeItem('viewMode')
    }
  }
})
