import { CallToolResult } from '@modelcontextprotocol/sdk/types.js'
import path from 'node:path'
import { Options, PythonShell } from 'python-shell'
import pkg from '../../package.json'
import { getContent } from './getContent'
import { lfJoin } from './lfJoin'
// 初衷: js 与 py 互操作

export const absCwdpath = path.resolve(__dirname, '../../')

/**
 * 判断路径是否是绝对路径
 * 如果是绝对路径，直接返回
 * 否则，转换为绝对路径并返回
 */
export const getAbsPath = (p: string, basePath: string = absCwdpath) => {
  return path.isAbsolute(p) ? p : path.resolve(basePath, p)
}

export const PythonShellOptions: Options = {
  pythonPath: path.resolve(absCwdpath, '.venv/bin/python3'),
  env: {
    ...process.env,
    // 是否通过node调用
    isNodeExec: '1',
  },
}

/**
 * 执行 py 文件 拿到对象结果
 */
export const execPyFile = async <R = CallToolResult>(
  p: string,
  arg: object = {}
): Promise<R> => {
  const res = await PythonShell.run(getAbsPath(p), {
    ...PythonShellOptions,
    env: {
      ...PythonShellOptions.env,
      // js py 互操作 传参
      [pkg.jspy_identifier]: JSON.stringify(arg),
    },
  })

  for (const v of res) {
    try {
      if (!v?.includes(pkg.jspy_identifier)) continue
      const res = JSON.parse(v)
      const callToolResult = await getContent(res[pkg.jspy_identifier])
      // @ts-expect-error
      return callToolResult
    } catch (err) {}
  }
  const callToolResult = await getContent(
    `execPyFile err: ${lfJoin(res.map((v) => String(v)))}`,
    true
  )
  // @ts-expect-error
  return callToolResult
}
