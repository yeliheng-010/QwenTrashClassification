import request from '../utils/request'

// 词典数据类型定义
export interface DictionaryItem {
    id?: number
    item_name: string
    category: string
    description?: string
    created_at?: string
}

// -------------------------------------------------------------------
// 公开接口
// -------------------------------------------------------------------

/**
 * 搜索本地分类词典
 * @param keyword 关键词
 * @returns 匹配的词条列表
 */
export const searchDictionary = (keyword: string) => {
    return request({
        url: '/dictionary/search',
        method: 'get',
        params: { keyword }
    })
}

// -------------------------------------------------------------------
// 管理员接口
// -------------------------------------------------------------------

/**
 * 获取全量词库列表 (管理员)
 * @returns 所有词条
 */
export const getDictionaryItems = () => {
    return request({
        url: '/dictionary/admin',
        method: 'get'
    })
}

/**
 * 新增词条 (管理员)
 * @param data 词条数据
 * @returns 新增的词条
 */
export const createDictionaryItem = (data: DictionaryItem) => {
    return request({
        url: '/dictionary/admin',
        method: 'post',
        data
    })
}

/**
 * 修改词条 (管理员)
 * @param id 词条ID
 * @param data 修改的数据
 * @returns 修改后的词条
 */
export const updateDictionaryItem = (id: number, data: DictionaryItem) => {
    return request({
        url: `/dictionary/admin/${id}`,
        method: 'put',
        data
    })
}

/**
 * 删除词条 (管理员)
 * @param id 词条ID
 */
export const deleteDictionaryItem = (id: number) => {
    return request({
        url: `/dictionary/admin/${id}`,
        method: 'delete'
    })
}
