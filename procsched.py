import json
import random as rd
import logging as lg
import numpy as np
import matplotlib.pyplot as plt


def load_config():
    '''
    从`config.json`文件中加载配置信息
    
    Returns
    -------
    + config: dict 配置信息，包括进程平均运行时间、时间片大小、样本数量等
    '''
    with open('config.json', 'r', encoding='utf-8') as fp:
        cfg = json.load(fp)
    
    print('config = ', cfg)
    return cfg


def gen_proc_seq(cfg: dict):
    '''
    生成进程序列，包括进程到达时间和进程运行时间

    Parameters
    ----------
    + cfg: dict 进程序列的配置信息

    Returns
    -------
    + arri_time: list 进程到达时间列表
    + run_time: list 进程运行时间列表
    '''
    arri_time = [0, cfg['latest_arri']]
    for _ in range(cfg['count'] - 2):
        arri_time.append(rd.randint(0, cfg['latest_arri']))
    arri_time.sort()

    run_time = []
    for _ in range(cfg['count']):
        x = 0
        while x <= 0:
            x = int(rd.gauss(cfg['avg_runtime'], cfg['diff_runtime']))
        
        run_time.append(x)
    
    lg.info('arri_time = ' + arri_time.__str__())
    lg.info('run_time = ' + run_time.__str__())
    return arri_time, run_time


def FCFS(at: list, rt: list):
    '''
    先来先服务算法

    Parameters
    ----------
    + at: list 进程到达时间列表
    + rt: list 进程运行时间列表

    Returns
    -------
    + turna_time: list 进程周转时间列表
    '''
    clock = 0
    turna_time = []
    count = len(at)

    for i in range(count):
        lg.debug('proc{i}_start_time: {c}'.format(i=i, c=clock))
        
        clock += rt[i]
        turna_time.append(clock - at[i])
        lg.debug('proc{i}_term_time: {c}'.format(i=i, c=clock))

        if i < count - 1 and clock < at[i+1]:
            clock = at[i+1]

    return turna_time


def SRTN(at: list, rt: list):
    '''
    最短剩余时间优先算法

    Parameters
    ----------
    + at: list 进程到达时间列表
    + rt: list 进程运行时间列表

    Returns
    -------
    + turna_time: list 进程周转时间列表
    '''
    clock = 0
    act_proc = []
    remain_time = rt[:]
    count = len(at)
    turna_time = [0] * count

    for i in range(count):
        insed = False
        for j in range(len(act_proc)):
            if remain_time[i] < remain_time[act_proc[j]]:
                act_proc.insert(j, i)
                insed = True
                break
        if not insed:
            act_proc.append(i)

        lg.debug('porc{i}_start_time = {c}'.format(i=i, c=clock))
        lg.debug('act_proc = ' + act_proc.__str__())
        lg.debug('act_proc_remain_time = {t}'.format(t=[remain_time[p] for p in act_proc]))

        if i < count - 1:
            while act_proc and clock + remain_time[act_proc[0]] <= at[i+1]:
                clock += remain_time[act_proc[0]]
                turna_time[act_proc[0]] = clock - at[act_proc[0]]
                lg.debug('porc{i}_term_time = {c}'.format(i=act_proc.pop(0), c=clock))
            
            if act_proc:
                remain_time[act_proc[0]] -= (at[i+1] - clock)
            
            clock = at[i+1]
                    
    for p in act_proc:
        clock += remain_time[p]
        turna_time[p] = clock - at[p]
        lg.debug('porc{i}_term_time = {c}'.format(i=p, c=clock))
    
    return turna_time


def HRRF(at: list, rt: list):
    '''
    最高响应比优先算法

    Parameters
    ----------
    + at: list 进程到达时间列表
    + rt: list 进程运行时间列表

    Returns
    -------
    + turna_time: list 进程周转时间列表
    '''
    clock = 0
    act_proc = []
    remain_time = rt[:]
    count = len(at)
    turna_time = [0] * count

    rr = lambda x : (clock - at[x] + remain_time[x]) / rt[x]

    for i in range(count):
        act_proc.append(i)
        act_proc.sort(key=rr, reverse=True)
        lg.debug('porc{i}_start_time = {c}'.format(i=i, c=clock))
        lg.debug('act_proc = ' + act_proc.__str__())
        lg.debug('act_proc_response_rate = {t}'.format(t=[rr(p) for p in act_proc]))

        if i < count - 1:
            while act_proc and clock + remain_time[act_proc[0]] <= at[i+1]:
                clock += remain_time[act_proc[0]]
                turna_time[act_proc[0]] = clock - at[act_proc[0]]
                lg.debug('porc{i}_term_time = {c}'.format(i=act_proc.pop(0), c=clock))
                act_proc.sort(key=rr, reverse=True)
            
            if act_proc:
                remain_time[act_proc[0]] -= (at[i+1] - clock)
            
            clock = at[i+1]
    
    while act_proc:
        clock += remain_time[act_proc[0]]
        turna_time[act_proc[0]] = clock - at[act_proc[0]]
        lg.debug('porc{i}_term_time = {c}'.format(i=act_proc.pop(0), c=clock))
        act_proc.sort(key=rr, reverse=True)
    
    return turna_time


def RR(at: list, rt: list, ss: int):
    '''
    时间片轮转法

    Parameters
    ----------
    + at: list 进程到达时间列表
    + rt: list 进程运行时间列表
    + ss: int 时间片大小

    Returns
    -------
    + turna_time: list 进程周转时间列表
    '''
    clock = 0
    act_proc = []
    remain_time = rt[:]
    count = len(at)
    turna_time = [0] * count
    
    i = 0
    while i < count or act_proc:
        if act_proc:
            if remain_time[act_proc[0]] <= ss:
                clock += remain_time[act_proc[0]]
                turna_time[act_proc[0]] = clock - at[act_proc[0]]
                lg.debug('porc{i}_term_time = {c}'.format(i=act_proc.pop(0), c=clock))
            else:
                clock += ss
                remain_time[act_proc[0]] -= ss
                lg.debug('proc{i}_reamin_time = {t}'.format(i=act_proc[0], t=remain_time[act_proc[0]]))
                act_proc.append(act_proc.pop(0))
        else:
            clock = at[i]

        while i < count and clock >= at[i]:
            act_proc.insert(0, i)
            lg.debug('porc{i}_start_time = {c}'.format(i=i, c=clock))
            lg.debug('act_proc = ' + act_proc.__str__())
            i += 1
    
    return turna_time


def MLFQ(at: list, rt: list, ss: int, ql: int):
    '''
    多级反馈队列算法

    Parameters
    ----------
    + at: list 进程到达时间列表
    + rt: list 进程运行时间列表
    + ss: int 第0级时间片大小
    + ql: int 进程队列级数

    Returns
    -------
    + turna_time: list 进程周转时间列表
    '''
    clock = 0
    proc_lists = [[] for _ in range(ql)]
    remain_time = rt[:]
    count = len(at)
    turna_time = [0] * count
    time_slice = [0] * ql

    not_empty = lambda ls : bool([True for e in ls if e])
    
    i = 0
    while i < count or not_empty(proc_lists):
        if not_empty(proc_lists):
            lvl = 0
            while not proc_lists[lvl]:
                lvl += 1
            cur_proc = proc_lists[lvl][0]

            if time_slice[lvl] == 0:
                time_slice[lvl] = ss * (2 ** lvl)
            time_slice[lvl] = min(time_slice[lvl], remain_time[cur_proc])
            
            if lvl > 0 and i < count and clock + time_slice[lvl] > at[i]:
                remain_time[cur_proc] -= (at[i] - clock)
                time_slice[lvl] -= (at[i] - clock)
                clock = at[i]
            else:
                clock += time_slice[lvl]
                remain_time[cur_proc] -= time_slice[lvl]
                time_slice[lvl] = 0
                lg.debug('proc{i}_reamin_time = {t}'.format(i=cur_proc, t=remain_time[cur_proc]))

                if remain_time[cur_proc] == 0:
                    turna_time[cur_proc] = clock - at[cur_proc]
                    lg.debug('porc{i}_term_time = {c}'.format(i=proc_lists[lvl].pop(0), c=clock))
                else:
                    if lvl < ql - 1:
                        proc_lists[lvl+1].append(proc_lists[lvl].pop(0))
                    else:
                        proc_lists[lvl].append(proc_lists[lvl].pop(0))
        else:
            clock = at[i]

        while i < count and clock >= at[i]:
            proc_lists[0].insert(0, i)
            lg.debug('porc{i}_start_time = {c}'.format(i=i, c=clock))
            lg.debug('proc_lists = ' + proc_lists.__str__())
            i += 1
    
    return turna_time


def calc_result(rt: list, tt: list):
    '''
    计算进程调度算法的运行结果

    Parameters
    ----------
    + rt: list 进程运行时间列表
    + tt: list 进程周转时间列表

    Returns
    -------
    + result: dict 计算结果，包括平均周转时间、平均响应比、最大等待时间
    '''
    count = len(rt)
    res = {
        'avg_turna_time' : sum(tt) / count,
        'avg_resp_rate' : sum(tt[i]/rt[i] for i in range(count)) / count,
        'max_wait_time' : max(tt[i] - rt[i] for i in range(count)),
    }
    lg.info('result = ' + res.__str__())
    return res


def summary(att: list, arr: list, mwt: list):
    '''
    对计算结果进行汇总，求平均值

    Parameters
    ----------
    + att: list 平均周转时间列表
    + arr: list 平均响应比列表
    + mwt: list 最大等待时间列表

    Returns
    -------
    + results: dict 汇总结果，包括平均周转时间、平均响应比、最大等待时间
    '''
    count = len(att)
    res = {
        'avg_turna_time' : sum(att) / count,
        'avg_resp_rate' : sum(arr) / count,
        'max_wait_time' : sum(mwt) / count,
    }
    return res


def draw_chart(res: dict, rt1: float, rt2: float):
    '''
    根据汇总结果绘制图表

    Parameters
    ----------
    + res: lsit 汇总结果，包括平均周转时间、平均响应比、最大等待时间
    + rt1: float 第二个属性即平均响应比的显示比率
    + rt2: float 第三个属性即最大等待时间的显示比率
    '''
    xs = np.arange(len(res))
    names = res.keys()
    data = {
        'avg_turna_time' : np.array([r['avg_turna_time'] for r in res.values()]),
        'avg_resp_rate' : np.array([r['avg_resp_rate'] for r in res.values()]),
        'max_wait_time' : np.array([r['max_wait_time'] for r in res.values()])
    }

    plt.figure(figsize=(8, 5), dpi=120)
    # plt.axes([0.05, 0.05, 0.9, 0.9])
    plt.margins(y=0.3)

    plt.bar(xs + 0.00, data['avg_turna_time'], 0.25, label = 'avg_turna_time')
    plt.bar(xs + 0.25, data['avg_resp_rate'] * rt1, 0.25, label = 'avg_resp_rate')
    plt.bar(xs + 0.50, data['max_wait_time'] * rt2, 0.25, label = 'max_wait_time')
    
    for x in xs:
        plt.text(x + 0.00, data['avg_turna_time'][x], '{:.0f}'.format(data['avg_turna_time'][x]), ha='center')
        plt.text(x + 0.25, data['avg_resp_rate'][x] * rt1, '{:.2f}'.format(data['avg_resp_rate'][x]), ha='center')
        plt.text(x + 0.50, data['max_wait_time'][x] * rt2, '{:.0f}'.format(data['max_wait_time'][x]), ha='center')

    plt.title('performence of process dispatch algorithm')
    plt.xticks(xs + 0.25, names)
    plt.legend(loc='upper right')
    plt.show()


def main():
    '''
    主程序
    根据配置生成进程序列、运行进程调度算法，然后计算运行结果，并绘制图表
    '''
    lg.basicConfig(level=lg.WARNING)

    config = load_config()
    algos = ['FCFS', 'SRTN', 'HRRF', 'RR', 'MLFQ']
    results = {a : [] for a in algos}
   
    for _ in range(config['sample_size']):
        arri_time, run_time = gen_proc_seq(config['proc'])

        turna_times = dict()
        turna_times['FCFS'] = FCFS(arri_time, run_time)
        turna_times['SRTN'] = SRTN(arri_time, run_time)
        turna_times['HRRF'] = HRRF(arri_time, run_time)
        turna_times['RR'] = RR(arri_time, run_time, config['algo']['slice_size'])
        turna_times['MLFQ'] = MLFQ(arri_time, run_time, config['algo']['slice_size'], config['algo']['queue_level'])

        for a in algos:
            results[a].append(calc_result(run_time, turna_times[a]))
    
    for a in algos:
        results[a] = summary(
            [r['avg_turna_time'] for r in results[a]],
            [r['avg_resp_rate'] for r in results[a]],
            [r['max_wait_time'] for r in results[a]]
        )
    
    print('results = ', results)
    draw_chart(results, config['proc']['avg_runtime'], 0.5)


main()