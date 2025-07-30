import { execPyFile } from '../src/utils';
(async () => {
  const res = await execPyFile('src/defs/pyautogui.typewrite.py', {
    message: '你好',
  })
  console.log(res)
})()
