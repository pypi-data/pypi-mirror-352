import { dayjs } from '@zeroer/general-tools'
import path from 'node:path'
import {
  createLogger,
  format,
  LeveledLogMethod,
  Logger,
  transports,
} from 'winston'
const { combine, timestamp, printf } = format

export const logger = createLogger({
  format: combine(
    timestamp(),
    // 自定义日志格式
    printf(({ level, message, timestamp }) => {
      // @ts-expect-error
      return `${dayjs(timestamp).format(
        'YYYY-MM-DD HH:mm:ss'
      )} [node:${level}] ${message}`
    })
  ),
  transports: [
    new transports.File({
      filename: path.resolve(__dirname, '../../logs/app.log'),
    }),
  ],
})

// 中间件
function StringifyMiddleware(oig: LeveledLogMethod) {
  return function (message: string, ...meta: any[]): Logger {
    return oig.call(
      // @ts-expect-error
      this,
      typeof message === 'string' ? message : JSON.stringify(message),
      // @ts-expect-error
      ...meta
    )
  } as LeveledLogMethod
}
logger.error = StringifyMiddleware(logger.error)
logger.info = StringifyMiddleware(logger.info)
logger.warn = StringifyMiddleware(logger.warn)
logger.debug = StringifyMiddleware(logger.debug)
