import request from '../utils/request'

export const getSystemStats = () => {
    return request({
        url: '/admin/stats',
        method: 'get'
    })
}

export const getSystemLogs = (lines: number = 500) => {
    return request({
        url: '/admin/logs',
        method: 'get',
        params: { lines }
    })
}

export const resetUserPassword = (userId: number) => {
    return request({
        url: `/admin/users/${userId}/password`,
        method: 'put'
    })
}

export const updateUserStatus = (userId: number, isActive: boolean) => {
    return request({
        url: `/admin/users/${userId}/status`,
        method: 'put',
        data: { is_active: isActive }
    })
}
