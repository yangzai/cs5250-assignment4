'''
CS5250 Assignment 4, Scheduling policies simulator
Sample skeleton program
Author: Minh Ho
Input file:
    input.txt
Output files:
    FCFS.txt
    RR.txt
    SRTF.txt
    SJF.txt

Apr 10th Revision 1:
    Update FCFS implementation, fixed the bug when there are idle time slices between processes
    Thanks Huang Lung-Chen for pointing out
Revision 2:
    Change requirement for future_prediction SRTF => future_prediction shortest job first(SJF), the simpler non-preemptive version.
    Let initial guess = 5 time units.
    Thanks Lee Wei Ping for trying and pointing out the difficulty & ambiguity with future_prediction SRTF.
'''
import sys

input_file = 'input.txt'


class Process:
    last_scheduled_time = 0

    def __init__(self, id, arrive_time, burst_time):
        self.id = id
        self.arrive_time = arrive_time
        self.burst_time = burst_time

    # for printing purpose
    def __repr__(self):
        return ('[id %d : arrive_time %d,  burst_time %d]' % (self.id, self.arrive_time, self.burst_time))


def FCFS_scheduling(process_list):
    # store the (switching time, proccess_id) pair
    schedule = []
    current_time = 0
    waiting_time = 0
    for process in process_list:
        if current_time < process.arrive_time:
            current_time = process.arrive_time
        schedule.append((current_time, process.id))
        waiting_time = waiting_time + (current_time - process.arrive_time)
        current_time = current_time + process.burst_time
    average_waiting_time = waiting_time / float(len(process_list))
    return schedule, average_waiting_time


# Input: process_list, time_quantum (Positive Integer)
# Output_1 : Schedule list contains pairs of (time_stamp, proccess_id) indicating the time switching to that proccess_id
# Output_2 : Average Waiting Time
def RR_scheduling(process_list, time_quantum):
    schedule = []
    current_time = 0
    waiting_time = 0
    count = index = 0
    length = len(process_list)
    rem_bt = [p.burst_time for p in process_list]

    while count < length:
        if index >= length:
            index = 0
            continue
        if not rem_bt[index]:
            index += 1
            continue

        process = process_list[index]

        if current_time < process.arrive_time:
            if index == count:
                current_time = process.arrive_time
            else:
                index = 0
                continue
        if not len(schedule) or schedule[-1][1] != process.id:
            schedule.append((current_time, process.id))

        run_time = min(rem_bt[index], time_quantum)
        current_time += run_time
        rem_bt[index] -= run_time

        if not rem_bt[index]:
            waiting_time += current_time - process.arrive_time - process.burst_time
            count += 1

        index += 1

    average_waiting_time = waiting_time / float(length)
    return schedule, average_waiting_time


def SRTF_scheduling(process_list):
    schedule = []
    current_time = 0
    waiting_time = 0
    count = index = 0
    length = len(process_list)
    rem_bt = [p.burst_time for p in process_list]

    # for i in range(length - 1):
    while count < length:
        # print(rem_bt)
        # nxt = process_list[index + 1]

        # index = rem_bt.index(min([t for t in rem_bt[:i + 1] if t]))
        candidate_burst = [t for t in rem_bt[:index + 1] if t]

        if not len(candidate_burst):
            index += 1
            continue

        srtf_index = rem_bt.index(min(candidate_burst))
        # index = rem_bt.index(min([t for t in rem_bt if t and t <= current_time]))
        process = process_list[srtf_index]

        if current_time < process.arrive_time:
            current_time = process.arrive_time

        if not len(schedule) or schedule[-1][1] != process.id:
            schedule.append((current_time, process.id))

        run_time = rem_bt[srtf_index]

        if index < length - 1:  # nxt exist
            nxt = process_list[index + 1]
            run_time = min(run_time, nxt.arrive_time - current_time)

            if current_time >= nxt.arrive_time:
                index += 1

        current_time += run_time
        rem_bt[srtf_index] -= run_time

        if not rem_bt[srtf_index]:
            waiting_time += current_time - process.arrive_time - process.burst_time
            count += 1

    # print(rem_bt)
    # remainder_bt_index_sorted = sorted([(rem_bt[i], i) for i in range(length) if rem_bt[i]])
    #
    # for bt, i in remainder_bt_index_sorted:
    #     # print(i, bt)
    #     print("this")
    #     process = process_list[i]
    #     schedule.append((current_time, process.id))
    #     print(current_time, process.id)
    #     current_time += bt
    #     waiting_time += current_time - process.arrive_time - process.burst_time

    average_waiting_time = waiting_time / float(length)
    return schedule, average_waiting_time


def SJF_scheduling(process_list, alpha):
    schedule = []
    current_time = 0
    waiting_time = 0
    length = len(process_list)
    # rem_bt = [p.burst_time for p in process_list]
    uncompleted = [True] * length

    predict = dict((id_, 5) for id_ in set(p.id for p in process_list))

    for count in range(length):
        candidate_indices = [i for i in range(length) if uncompleted[i] and process_list[i].arrive_time <= current_time]
        if not len(candidate_indices):
            current_time = process_list[count].arrive_time
            candidate_indices = [i for i in range(length) if
                                 uncompleted[i] and process_list[i].arrive_time <= current_time]

        index, _ = min(((i, predict[process_list[i].id]) for i in candidate_indices),
                       key=lambda x: x[1])
        # print(index)
        # id_, burst = min(predict.items(), key=lambda x: x[1])

        process = process_list[index]
        if current_time < process.arrive_time:
            current_time = process.arrive_time
        schedule.append((current_time, process.id))
        waiting_time = waiting_time + (current_time - process.arrive_time)
        current_time = current_time + process.burst_time

        predict[process.id] = alpha * process.burst_time + (1 - alpha) * predict[process.id]
        uncompleted[index] = False

    average_waiting_time = waiting_time / float(length)
    return schedule, average_waiting_time


def read_input():
    result = []
    with open(input_file) as f:
        for line in f:
            array = line.split()
            if (len(array) != 3):
                print("wrong input format")
                exit()
            result.append(Process(int(array[0]), int(array[1]), int(array[2])))
    return result


def write_output(file_name, schedule, avg_waiting_time):
    with open(file_name, 'w') as f:
        for item in schedule:
            f.write(str(item) + '\n')
        f.write('average waiting time %.2f \n' % (avg_waiting_time))


def main(argv):
    process_list = read_input()
    print("printing input ----")
    for process in process_list:
        print(process)
    print("simulating FCFS ----")
    FCFS_schedule, FCFS_avg_waiting_time = FCFS_scheduling(process_list)
    write_output('FCFS.txt', FCFS_schedule, FCFS_avg_waiting_time)
    print("simulating RR ----")
    RR_schedule, RR_avg_waiting_time = RR_scheduling(process_list, time_quantum=2)
    write_output('RR.txt', RR_schedule, RR_avg_waiting_time)
    print("simulating SRTF ----")
    SRTF_schedule, SRTF_avg_waiting_time = SRTF_scheduling(process_list)
    write_output('SRTF.txt', SRTF_schedule, SRTF_avg_waiting_time)
    print("simulating SJF ----")
    SJF_schedule, SJF_avg_waiting_time = SJF_scheduling(process_list, alpha=0.5)
    write_output('SJF.txt', SJF_schedule, SJF_avg_waiting_time)


if __name__ == '__main__':
    main(sys.argv[1:])
