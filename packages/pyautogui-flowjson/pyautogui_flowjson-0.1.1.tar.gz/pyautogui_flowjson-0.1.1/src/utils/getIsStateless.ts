import express from 'express'
import { headersKey } from '../types'

/**
 * 获取 是否无状态
 *
 * 服务端启动时 环境变量优先，否则依赖前端请求头（存在认为是无状态的 否则就是有状态的）
 */
export function getIsStateless(req: express.Request) {
  if (process.env.STATELESS !== undefined) return Boolean(process.env.STATELESS)
  return Boolean(req.headers[headersKey.stateless])
}
