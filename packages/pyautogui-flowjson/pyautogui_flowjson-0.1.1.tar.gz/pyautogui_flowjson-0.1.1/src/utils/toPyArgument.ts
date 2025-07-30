export function toPyStrArg(obj: object) {
  return Object.entries(obj)
    .filter(([_, v]) => v !== undefined) // 过滤掉值为 undefined 的键值对
    .map(([k, v]) => `${k}=${typeof v === 'string' ? `"${v}"` : v}`) // 转换为 "key=value" 格式
    .join(', ')
}
