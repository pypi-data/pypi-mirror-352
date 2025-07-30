export type SA = Array<string | SA>

export function lfJoin(...args: SA) {
  // @ts-expect-error
  const arr: string[] = args.flat(Infinity)
  return arr.join('\n')
}
