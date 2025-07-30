import z from 'zod'
import { PICTURE_DESCRIBE } from '../types'
import { def, execPyFile, lfJoin, POINT_OPERATION } from '../utils'

const getScreenshotSchema = () => ({
  uri: z.string().describe(lfJoin('图片', PICTURE_DESCRIBE)),
  confidence: z
    .number()
    .optional()
    .describe(lfJoin('从当前屏幕中查询图片的 相似度', '默认值 0.95')),
})

const getShotSchema = (
  describe = lfJoin('“target 图片”（解析后作为最终“点位操作” 所使用的坐标）')
) => z.object(getScreenshotSchema()).describe(describe)

export const imgPointOperationDef = def({
  name: 'img-point-operation',
  description: lfJoin(
    '在屏幕中查询图片的位置 并做 “点位操作”',
    `有效的点位操作类型: ${Array.from(
      POINT_OPERATION.entries(),
      ([key, description]) => `${key}: ${description}`
    ).join('、')}`,
    '示例：',
    '1. 点击图片 /a.png',
    `${JSON.stringify(
      {
        position: { uri: '/a.png' },
        action: { type: 'click' },
      },
      null,
      2
    )}`,
    `2. 移动到图片 https://x.png 相似度0.9 => ${JSON.stringify(
      {
        position: { uri: 'https://x.png', confidence: 0.9 },
        action: { type: 'moveTo' },
      },
      null,
      2
    )}`,
    `3. 双击图片 /a.png 包含图片 /b.jpg 排除图片 /c.jpeg => ${JSON.stringify(
      {
        position: { uri: '/a.png' },
        includes: [{ uri: '/b.jpg' }],
        excludes: [{ uri: '/c.jpeg' }],
        action: { type: 'doubleClick' },
      },
      null,
      2
    )}`
  ),
  argsSchema: {
    action: z.object({
      type: z
        .string()
        .describe(
          lfJoin(
            '点位操作类型',
            `有效的点位操作类型: ${Array.from(
              POINT_OPERATION.entries(),
              ([key, description]) => `${key}: ${description}`
            ).join('、')}`
          )
        ),
      // TODO arguments 暂时不扩展了
    }),
    position: getShotSchema(),
    includes: z
      .array(getShotSchema(lfJoin('每一个 “includes 图片”')))
      .optional()
      .default([])
      .describe(
        lfJoin(
          '额外 “includes 图片”（作为辅助 “目标图片” 判断的信息）这里表示 所有的 “includes 图片” 都应该存在'
        )
      ),
    excludes: z
      .array(getShotSchema(lfJoin('每一个 “excludes 图片”')))
      .optional()
      .default([])
      .describe(
        lfJoin(
          '额外 “excludes 图片”（作为辅助 “目标图片” 判断的信息）这里表示 所有的 “excludes 图片” 都应该不存在'
        )
      ),
  },
  async requestHandler(arg) {
    const res = await execPyFile('src/defs/img.point.operation.py', arg)
    return res
  },
})

export const imgEnsureDef = def({
  name: 'img-ensure',
  description: lfJoin(
    '等到 图片出现、确保 图片存在',
    '一般用于 执行某些异步操作后 等待的时间（确保图片存在）',
    '没有找到会一直等待 找到则结束',
    '示例：',
    '1. 等待 图片出现 /a.png 超时时间1分钟',
    `${JSON.stringify(
      {
        uri: '/a.png',
        timeout: 60,
      },
      null,
      2
    )}`
  ),
  argsSchema: {
    ...getScreenshotSchema(),
    timeout: z
      .number()
      .optional()
      .default(30)
      .describe(lfJoin('等待的超时时间', '默认值 30 秒')),
  },
  async requestHandler(arg) {
    const res = await execPyFile('src/defs/img.ensure.py', arg)
    return res
  },
})

/**
 * TODO 扩增参数
 * 后续支持 2张图片 获取 左上角 右下角 然后ocr
 * 后续支持 截取当前屏幕 + 2点位（左上角 右下角） 然后ocr
 */
export const imgOcrDef = def({
  name: 'img-ocr',
  description: lfJoin(
    '图片 ocr',
    '示例：',
    '1. ocr https://a.png',
    `${JSON.stringify(
      {
        uri: 'https://a.png',
      },
      null,
      2
    )}`
  ),
  argsSchema: {
    uri: getScreenshotSchema().uri,
  },
  async requestHandler(arg) {
    const res = await execPyFile('src/defs/img.ocr.py', arg)
    return res
  },
})
