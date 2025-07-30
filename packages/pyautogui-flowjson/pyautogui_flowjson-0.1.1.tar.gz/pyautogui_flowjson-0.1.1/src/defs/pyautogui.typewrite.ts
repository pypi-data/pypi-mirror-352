import path from 'node:path'
import z from 'zod'
import { def, execPyFile, KEYBOARD_KEYS, lfJoin } from '../utils'

export const typewriteDef = def({
  name: 'typewrite',
  description: lfJoin(
    '模拟按键输入文本字符串的过程，message 中的每个字符执行一个按键按下，然后释放。',
    '也可用于粘贴文本，message 为要粘贴的字符串。',
    '不能用于执行键盘快捷键',
    '示例：',
    '1. 键盘输入 你好',
    `${JSON.stringify(
      {
        message: '你好',
      },
      null,
      2
    )}`
  ),
  argsSchema: {
    message: z
      .union([z.string(), z.array(z.string())])
      .describe(
        lfJoin(
          '如果是一个字符串，则是需要按下的字符。',
          '如果是一个数组，则是按键名称的列表，按键顺序按下。',
          `有效的名称: ${KEYBOARD_KEYS.join(', ')}`
        )
      ),
    interval: z
      .number()
      .optional()
      .describe(lfJoin('每个按键之间等待的时间，以秒为单位', '默认为 0')),
  },
  async requestHandler(arg) {
    // TODO Linux 下 貌似 pyperclip.copy 调用 有关 会阻塞node进程 后续换成vnc测试下
    const res = await execPyFile(
      `src/defs/${path.basename(__filename, path.extname(__filename))}.py`,
      arg
    )
    return res
  },
})
