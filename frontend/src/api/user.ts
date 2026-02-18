import request from '../utils/request'

export const updatePassword = (data: any) => {
    return request({
        url: '/users/password',
        method: 'put',
        data
    })
}

export const getUserInfo = () => {
    return request({
        url: '/users/me',
        method: 'get'
    })
}

export const updateUserInfo = (data: any) => {
    return request({
        url: '/users/me/info',
        method: 'put',
        data
    })
}
