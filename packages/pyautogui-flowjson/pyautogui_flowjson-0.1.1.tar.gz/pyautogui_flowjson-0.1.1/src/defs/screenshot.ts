import path from 'node:path'
import { def, execPyFile, lfJoin } from '../utils'

export const screenshotDef = def({
  name: 'screenshot',
  description: lfJoin('获取当前屏幕截图 返回 屏幕截图地址 存储到临时文件夹下'),
  argsSchema: {},
  async requestHandler(arg) {
    const res = await execPyFile(
      `src/defs/${path.basename(__filename, path.extname(__filename))}.py`,
      arg
    )
    return res
  },
})
