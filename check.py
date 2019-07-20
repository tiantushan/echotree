import re


target_file = './ansible_hosts'

#target_file_object = open(target_file, 'r')
all_group_list = []
merge_list = []
all_single_list = []
def handle_line():
    target_file_object = open(target_file, 'r')
    with target_file_object as f:
        tmp_list = []
        key = False
        round_num = 1
        for line_num, line_con in enumerate(f):
            res = re.search(r' *\[(\w+):children\]', line_con)
            if res:
                if round_num != 1:
                    print(tmp_list)
                    all_group_list.append(tmp_list)
                    tmp_list = []

                match_word = res.group(1)
                key = True
                tmp_list.append(match_word)
                #print(line_num+1, match_word)
                #print(tmp_list)
                round_num += 1

                #tmp_list = []
            resu = re.search(r'(^\w+)', line_con)
            if resu and key:
                match_word = resu.group(1)
                tmp_list.append(match_word)
                #print(tmp_list)
                #print(line_num, line_con)
        if round_num != 1:
            print(tmp_list)
            all_group_list.append(tmp_list)
        print(all_group_list)
handle_line()

def merge_list_fun():
    global merge_list
    for v in all_group_list:
        merge_list.extend(v)
    tmp_list = []
    for v in merge_list:
        if v not in tmp_list:
            tmp_list.append(v)
    merge_list = tmp_list
    print(merge_list)

merge_list_fun()

def single_group():
    target_file_object = open(target_file, 'r')
    with target_file_object as f:
        for line_num, line_con in enumerate(f):
            res = re.search(r' *\[(\w+)\]', line_con)
            if res:
                match_word = res.group(1)
                #print(match_word)
                if match_word not in merge_list:
                    all_single_list.append(match_word)
                    #print(match_word)
        print(all_single_list)
                    


single_group()

obj_pool = []
class Chain(object):
    def __init__(self, master):
        self.master = master
        self.container = []
        self.echo_key = True
    def add_container(self, member):
        self.container.append(member)

def init_obj():
    for obj in merge_list:
        ob = Chain(obj)
        obj_pool.append(ob)

    # for var in obj_pool:
    #     print(var.master)

init_obj()

def merge_chain():
    for per in merge_list:
        for ss in all_group_list:
            if per in ss[1:]:
                per_head = ss[0]
                #print(per_head, per)
                for tt in obj_pool:
                    # print('##',tt.master)
                    if per == tt.master:
                        #print(per, tt.master)
                        for head in obj_pool:
                    #       print(head.master)
                            if per_head == head.master:
                                head.add_container(tt)
                                tt.echo_key = False

merge_chain()

def print_obj(obj, num=0):
    if num == 0 and obj.echo_key == False:
        return
    else:
        if not num:
            print(obj.master + ':')
        else:
            print(num * '\t', ':' + obj.master )
        num += 1
        for tmp in obj.container:
            if isinstance(tmp, Chain):
                print_obj(tmp, num)

def loop():
    for obj in obj_pool:
        print_obj(obj)
    for obj in all_single_list:
        print(obj + ':')

loop()









