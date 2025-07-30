import path from 'node:path'
import z from 'zod'
import { PICTURE_DESCRIBE } from '../types'
import { def, execPyFile, lfJoin, VERIFICATION_CODE_TYPE } from '../utils'

export const vCodeDef = def({
  name: 'verification-code',
  description: lfJoin(
    '识别验证码',
    '示例：',
    '1. 填充类 验证码 识别 /a.png',
    `${JSON.stringify(
      {
        type: 'fill',
        source: '/a.png',
      },
      null,
      2
    )}`,
    '2. 点击类 验证码 识别 https://b.png',
    `${JSON.stringify(
      {
        type: 'click',
        source: 'https://b.png',
      },
      null,
      2
    )}`,
    '3. 滑动类 验证码 识别 https://target.png https://background.png 精准匹配',
    `${JSON.stringify(
      {
        type: 'scroll',
        source: 'https://target.png',
        backgroundSource: 'https://background.png',
        simple_target: false,
      },
      null,
      2
    )}`
  ),
  argsSchema: {
    type: z
      .enum([...VERIFICATION_CODE_TYPE.keys()] as ['fill', 'click', 'scroll'])
      .describe(
        lfJoin(
          `验证码 类型: ${Array.from(
            VERIFICATION_CODE_TYPE.entries(),
            ([key, description]) => `${key}: ${description}`
          ).join('、')}`
        )
      ),
    source: z.string().describe(lfJoin('图片 ', PICTURE_DESCRIBE)),
    backgroundSource: z
      .string()
      .optional()
      .describe(
        lfJoin(
          '当验证码类型为 scroll 时 必填 表示背景图片',
          PICTURE_DESCRIBE,
          '当验证码类型为 fill、click 时 无需填写'
        )
      ),
    simple_target: z
      .boolean()
      .optional()
      .default(true)
      .describe(
        lfJoin(
          '当验证码类型为 scroll 时，true 表示使用简单模式匹配，只返回目标位置信息',
          '其验证码类型下 此参数无效'
        )
      ),
  },
  async requestHandler(arg) {
    const res = await execPyFile(
      `src/defs/${path.basename(__filename, path.extname(__filename))}.py`,
      arg
    )
    return res
  },
})
