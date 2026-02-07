import { defineStore } from 'pinia'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    userId: '',
    userName: 'admin',
    userRole: 'director' as 'teacher' | 'director' | 'college_leader' | 'academic_affairs',
    token: '',
    teachingOfficeId: ''
  }),
  
  getters: {
    isLoggedIn: (state) => !!state.token || !!state.userName,
    roleName: (state) => {
      const roleMap = {
        teacher: '普通教师',
        director: '教研室负责人',
        college_leader: '二级学院负责人',
        academic_affairs: '学校教务处负责人'
      }
      return roleMap[state.userRole] || ''
    },
    roleColor: (state) => {
      const colorMap = {
        teacher: '#42a5f5',
        director: '#66bb6a',
        college_leader: '#ab47bc',
        academic_affairs: '#ff7043'
      }
      return colorMap[state.userRole] || '#2c4a6d'
    }
  },
  
  actions: {
    setRole(role: 'teacher' | 'director' | 'college_leader' | 'academic_affairs') {
      this.userRole = role
      localStorage.setItem('userRole', role)
    },
    
    loadFromStorage() {
      const role = localStorage.getItem('userRole')
      if (role) {
        this.userRole = role as any
      }
    },
    
    logout() {
      this.$reset()
      localStorage.removeItem('userRole')
    }
  }
})
