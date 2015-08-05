#*****************************************************
# OpenMQ queue stats monitor.
# Updates gmond with stats of IN/OUT Queue dst metrics
# DW 2012-08-14
#*****************************************************

import commands
import datetime
import memcache
import time
descriptors = list()

def get_metrics(queue,type):
        mc = memcache.Client(['127.0.0.1:11211'])
        epoch_time = int(time.mktime(time.gmtime()))
        id = int(epoch_time / 60)

        metrics = mc.get(queue + str(id))
        if metrics:
                #print "metrics found in memcache: " + str(metrics)
                return metrics
        else:
                if type == "q":
                        cmd = "/var/lib/glassfish/imq/bin/imqcmd metrics dst -n %s -t q -u admin -passfile /etc/mq.pass -msp 1|egrep \"^[0-9]+\"" % (queue)
                elif type == "t":
                        cmd = "/var/lib/glassfish/imq/bin/imqcmd metrics dst -n %s -t t -u admin -passfile /etc/mq.pass -msp 1|egrep \"^[0-9]+\"" % (queue)

                metrics = commands.getoutput(cmd)
                mc.set(queue + str(id), metrics)
                #print "metrics not found in memcache, fetch from imqcmd: " + str(metrics)
                return metrics


def metric_init(params):
        cmd ="/var/lib/glassfish/imq/bin/imqcmd -u admin -passfile /etc/mq.pass list dst |egrep \"Queue\"|awk '{print $1}'"
        x = commands.getoutput(cmd)
        queues = x.split()
        for queue in queues:
                # create descriptors
                d_in =  { 'name': 'openmq_in_' + queue,
                          'call_back': q_in,
                          'time_max': 60,
                          'value_type': 'uint',
                          'units': 'Msgs',
                          'slope': 'positive',
                          'format': '%u',
                          'description': 'Messages IN Queue ' + queue,
                          'groups': 'OpenMQ'}

                descriptors.append(d_in)

                d_out = { 'name': 'openmq_out_' + queue,
                          'call_back': q_out,
                          'time_max': 60,
                          'value_type': 'uint',
                          'units': 'Msgs',
                          'slope': 'positive',
                          'format': '%u',
                          'description': 'Messages OUT Queue ' + queue,
                          'groups': 'OpenMQ'}

                descriptors.append(d_out)

                d_bl = { 'name': 'openmq_bl_' + queue,
                          'call_back': q_bl,
                          'time_max': 60,
                          'value_type': 'uint',
                          'units': 'Msgs',
                          'slope': 'both',
                          'format': '%u',
                          'description': 'Message backlog ' + queue,
                          'groups': 'OpenMQ'}

                descriptors.append(d_bl)

        cmd ="/var/lib/glassfish/imq/bin/imqcmd -u admin -passfile /etc/mq.pass list dst |egrep \"Topic\"|awk '{print $1}'"
        x = commands.getoutput(cmd)
        topics = x.split()
        for topic in topics:
                # create descriptors
                d_in =  { 'name': 'openmq_in_' + topic,
                          'call_back': t_in,
                          'time_max': 60,
                          'value_type': 'uint',
                          'units': 'Msgs',
                          'slope': 'positive',
                          'format': '%u',
                          'description': 'Messages IN Topic ' + topic,
                          'groups': 'OpenMQ'}

                descriptors.append(d_in)

                d_out = { 'name': 'openmq_out_' + topic,
                          'call_back': t_out,
                          'time_max': 60,
                          'value_type': 'uint',
                          'units': 'Msgs',
                          'slope': 'positive',
                          'format': '%u',
                          'description': 'Messages OUT Topic ' + topic,
                          'groups': 'OpenMQ'}

                descriptors.append(d_out)

                d_bl = { 'name': 'openmq_bl_' + topic,
                          'call_back': t_bl,
                          'time_max': 60,
                          'value_type': 'uint',
                          'units': 'Msgs',
                          'slope': 'both',
                          'format': '%u',
                          'description': 'Message backlog Topic ' + topic,
                          'groups': 'OpenMQ'}

                descriptors.append(d_bl)

        return descriptors

def q_in(name):
        name = name.replace('openmq_in_', '')
        vals =  get_metrics(name,"q").split()
        #print " Q:" + name + " IN:" + vals[0]
        return int(vals[0])

def q_out(name):
        name = name.replace('openmq_out_', '')
        vals =  get_metrics(name,"q").split()
        #print " Q:" + name + " OUT:" + vals[1]
        return int(vals[1])

def q_bl(name):
        name = name.replace('openmq_bl_', '')
        vals =  get_metrics(name,"q").split()
        return int(vals[4])

def t_in(name):
        name = name.replace('openmq_in_', '')
        vals =  get_metrics(name,"t").split()
        #print " Q:" + name + " IN:" + vals[0]
        return int(vals[0])

def t_out(name):
        name = name.replace('openmq_out_', '')
        vals =  get_metrics(name,"t").split()
        #print " Q:" + name + " OUT:" + vals[1]
        return int(vals[1])

def t_bl(name):
        name = name.replace('openmq_bl_', '')
        vals =  get_metrics(name,"t").split()
        #print "TOPIC BL:" + name + " " + vals[4]
        return int(vals[4])

def metric_cleanup():
    '''Clean up the metric module.'''
    pass

#This code is for debugging and unit testing
if __name__ == '__main__':
        metric_init("test")
        for d in descriptors:
                print d
        t_bl("electricityEvents")

#        v = d['call_back'](d['name'])
#        print 'value for %s is %u' % (d['name'],  v)
