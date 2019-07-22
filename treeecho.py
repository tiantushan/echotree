import re


target_file = './ansible_hosts_prod'
#target_file_object = open(target_file, 'r')

class HandleVar(object):
    """处理ansible_hosts最终形成几个变量列表"""
    def __init__(self):
        # all_group_list 存储一个二维列表，[['zujian_ALL',
        #  'cgw_ALL', 'payment_ALL'], ['cgw_ALL', 'cgw_sd', '
        # cgw_bj']], 列表中的每一项也是一个列表，每个列表的第一个值，
        # 是具有子组的父组名字，例如[zujian_ALL:children] ，就是指
        # zujian_ALL 这个名字
        self.all_group_list = []

        # 这个变量最终存储的是一个值不重复的一维列表，他是all_group_list
        # 变量去除重复元素后形成的，如下
        # ['zujian_ALL', 'cgw_ALL', 'payment_ALL', 'cgw_sd']
        self.merge_list = []

        # 存储的是没有父组的 孤儿组名字，如[tts_sd],这个组没有其他组包含它
        self.all_single_list = []


    def handle_line(self):
        """处理ansible_hosts每一行，把含有children的父组及其子组放进一个二维列表"""
        # 打开文件对象
        target_file_object = open(target_file, 'r')
        with target_file_object as open_file_object:
            # 临时变量，当其形成一个完整的父子组名称列表时，就把该列表追加到all_group_list
            # 并即可清空该临时列表，以便把形成下一个完整的父子组列表
            tmp_list = []

            # 当找到以:children 结尾的组时，那他的子组也会和它一起追加到列表，
            # 但是当ansible_hosts不标准时，没有找到children则下面的其他组加入
            # 到列表则没意义，当key为False时，则不加入
            key = False

            # 当第一次形成列表时，则 46 47 48行不应执行，因为第一次他就空列表
            round_num = 1

            for line_num, line_content in enumerate(open_file_object):
                res = re.search(r' *\[(\w+(-\w+)*):children\]', line_content)
                if res:
                    if round_num != 1:

                        ##################################################
                        # 若调试可以把下行注释去掉
                        # print(tmp_list)

                        # 追加列表到all_group_list
                        self.all_group_list.append(tmp_list)
                        # 完成了一个父子组列表，应重新初始化，以便容纳下一个父子组
                        tmp_list = []

                    # 父组名称
                    match_word = res.group(1)
                    key = True
                    # 父组名称放在列表第一个元素
                    tmp_list.append(match_word)
                    #print(line_num+1, match_word)
                    #print(tmp_list)
                    round_num += 1

                # 开始匹配:children 父组下面的子组名称
                child_group_object = re.search(r'(^\w+_(\w_)+\w+)|(^\w+(-\w+)+)|(^\w+)', line_content)
                if child_group_object and key:
                    child_group_name = child_group_object.group()
                    tmp_list.append(child_group_name)
                    #print(tmp_list)
                    #print(line_num, line_con)
            # 最后一次的临时列表也加入all_group_list
            if round_num != 1:
                #print(tmp_list)
                self.all_group_list.append(tmp_list)

            ##################################################
            # 若调试可以把下行注释去掉
            # print(self.all_group_list)
###handle_line()


    def merge_list_fun(self):
        """处理合成merge_list"""

        #merge_list这个变量最终存储的是一个值不重复的一维列表，他是all_group_list
        #变量去除重复元素后形成的，如下
        #['zujian_ALL', 'cgw_ALL', 'payment_ALL', 'cgw_sd']

        for v in self.all_group_list:
            # 列表合并
            self.merge_list.extend(v)

        # 一下几行代码去除重复元素
        tmp_list = []
        for v in self.merge_list:
            if v not in tmp_list:
                tmp_list.append(v)
        self.merge_list = tmp_list

        #################################################
        # 若调试可以把下行注释去掉
        # print(self.merge_list)



###merge_list_fun()

    def single_group(self):
        """处理孤儿的组，类似[tts_sd]这样无父亲组"""
        target_file_object = open(target_file, 'r')
        with target_file_object as open_file_object:
            for line_num, line_content in enumerate(open_file_object):
                res = re.search(r' *\[(\w+)\]', line_content)
                if res:
                    match_group = res.group(1)
                    #print(match_word)
                    if match_group not in self.merge_list:
                        self.all_single_list.append(match_group)
                        #print(match_word)

            ########################################################
            # 若调试可以把下行注释去掉
            # print(self.all_single_list)
                    


###single_group()


class Chain(object):
    """类对象实例化组为对象，然后串联实例形成一个单向链表"""
    def __init__(self, master, instance_object):
        # 组的名字
        self.master = master

        # container包含的元素也是Chain对象实例
        self.container = []

        # 打印开关
        self.echo_key = True

        # 传入HandleVar对象实例
        self.instance_object = instance_object

        # Chain对象池
        self.obj_pool = []
    def add_container(self, member):
        # member是Chain对象实例
        self.container.append(member)

    # def init_obj(self):
    #     # 组成一个Chain对象实例列表，存入obj_pool对象池
    #     for obj in self.instance_object.merge_list:
    #         obj = Chain(obj, self.instance_object)
    #         self.obj_pool.append(obj)


##init_obj()

    def merge_chain(self):
        """形成单向链表"""
        # 循环merge_list列表，per是组名字
        for per in self.instance_object.merge_list:
            # 循环二维列表，ss也是列表
            for ss in self.instance_object.all_group_list:
                # 排除第一个元素
                if per in ss[1:]:
                    # 列表第一个元素
                    per_head = ss[0]
                    #print(per_head, per)

                    # 循环对象池
                    for tt in self.obj_pool:
                        # print('##',tt.master)

                        # 若per和对象池某个元素的master属性相等
                        # 则将该tt对象加入父组实例的container属性
                        if per == tt.master:
                            #print(per, tt.master)
                            for head in self.obj_pool:
                                #print(head.master)
                                # 匹配到父组对象的master属性，则将
                                # 子组对象放进 父组对象的container里
                                if per_head == head.master:
                                    head.add_container(tt)
                                    tt.echo_key = False

##merge_chain()

    def print_obj(self, obj, num=0):
        """打印对象master值"""

        # 第一次调用，且该对象的显示开关关闭
        if num == 0 and obj.echo_key == False:
            return

        # 非第一次调用，意味着已经进入递归函数，不关心obj.echo_key真假
        else:
            if not num:
                print(obj.master + ':')
            else:
                print(num * '\t', ':' + obj.master )
            num += 1
            for tmp in obj.container:
                if isinstance(tmp, Chain):
                    self.print_obj(tmp, num)

    def loop(self):
        # 遍历对象池
        for obj in self.obj_pool:
            self.print_obj(obj)

        # 遍历孤儿组列表
        for obj in self.instance_object.all_single_list:
            print(obj + ':')

##loop()
def main():
    handle_var = HandleVar()
    handle_var.handle_line()
    handle_var.merge_list_fun()
    handle_var.single_group()
    chain = Chain(handle_var,handle_var)
    for obj in handle_var.merge_list:
        obj = Chain(obj, handle_var)
        chain.obj_pool.append(obj)
    chain.merge_chain()
    chain.loop()

if __name__ == '__main__':
    main()








