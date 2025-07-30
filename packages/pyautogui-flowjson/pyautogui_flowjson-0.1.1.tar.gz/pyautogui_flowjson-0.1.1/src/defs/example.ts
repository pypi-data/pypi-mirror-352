import { randomUUID } from 'node:crypto'
import z from 'zod'
import { def, getContent, lfJoin } from '../utils'

type RecordType = {
  name?: string
  content: string
}

// 记录
const recordMap = new Map<string, RecordType>([
  ['999', { name: '小王', content: '今天天气不错' }],
])

export const SaveRecordDef = def({
  name: 'save-record',
  description: lfJoin(
    'save 记录',
    '示例：',
    '1. 保存记录  123',
    `${JSON.stringify(
      {
        content: 123,
      },
      null,
      2
    )}`
  ),
  argsSchema: {
    name: z.string().optional().describe('记录 的 name'),
    content: z.string().describe('记录 的 content'),
  },
  async requestHandler({ name, content }) {
    const id = randomUUID()
    recordMap.set(id, { name, content })
    return getContent({
      msg: '操作成功',
      res: {
        id,
        ...recordMap.get(id),
      },
    })
  },
})

export const GetRecordDef = def({
  name: 'get-record',
  description: lfJoin(
    'get 记录',
    '示例：',
    '1. 获取记录 id为 999 的内容',
    `${JSON.stringify(
      {
        id: '999',
      },
      null,
      2
    )}`
  ),
  argsSchema: {
    id: z.string().optional().describe('记录 的 id'),
    name: z.string().optional().describe('记录 的 name'),
  },
  async requestHandler({ id, name }) {
    if (!id && !name) throw new Error('参数 id 和 name 至少要有一个')
    if (id) {
      if (!recordMap.get(id)) return getContent('未能检索预测数据')
      return getContent(`操作成功 ${JSON.stringify(recordMap.get(id))}`)
    }
    // 使用name获取
    const record: RecordType | undefined = Object.values(recordMap).find(
      (item) => item.name === name
    )
    if (!record) return getContent('未能检索预测数据')
    return getContent({
      msg: '操作成功',
      res: record,
    })
  },
})
