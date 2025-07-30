from concurrent.futures import ThreadPoolExecutor

# 创建一个最多同时运行6个任务的线程池
executor = ThreadPoolExecutor(max_workers=6)
