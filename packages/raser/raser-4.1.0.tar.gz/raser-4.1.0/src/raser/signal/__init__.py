import sys

def main(kwargs):    
    label = kwargs['label']
    scan_number = kwargs['scan']
    job_number = kwargs['job']
    mem = kwargs['mem']

    if label == 'signal':
        if scan_number != None:
            from util import batchjob
            scan_number = kwargs['scan']
            args = sys.argv
            command_tail_list = args[args.index('signal')+1:]
            for i in command_tail_list:
                if i == '-s':
                    index = command_tail_list.index(i)
                    command_tail_list.remove(command_tail_list[index+1]) # remove scan number
                    command_tail_list.remove(i) # remove '-s'
                    break
            for i in range(scan_number):
                args = ['signal', '--job', str(i)] + command_tail_list
                command = ' '.join(args) 
                print(command)
                destination = 'signal'
                batchjob.main(destination, command, mem, is_test=False)
        elif job_number != None:
            from . import gen_signal_scan
            gen_signal_scan.main(kwargs)
        else:
            from . import gen_signal_main
            gen_signal_main.main(kwargs)