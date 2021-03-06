'''@file build_cluster.py
this file will be ran for all machines to build the cluster'''

import os
import sys
import socket
from time import sleep
from nabu.distributed import cluster
from train_asr import train_asr
from train_lm import train_lm
import tensorflow as tf

def main(_):
    '''main function'''

    #unbuffer stdout
    sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', 0)

    cluster_dir = FLAGS.expdir + '/cluster'

    port = 1024
    machine_file = '%s/%s-%d' % (cluster_dir, socket.gethostname(), port)

    #look for an available port
    while (os.path.exists(machine_file)
           and not cluster.port_available(port)):

        port += 1
        machine_file = '%s/%s-%d' % (cluster_dir, socket.gethostname(), port)

    #report that the machine is ready
    with open(machine_file, 'w') as fid:
        fid.write(FLAGS.job_name)

    #wait untill the main process has given a go
    print 'waiting for cluster to be ready...'

    #read the task_index in the created file
    task_index = ''
    while (task_index == FLAGS.job_name
           or not os.path.exists(cluster_dir + '/ready')):

        with open(machine_file) as fid:
            task_index = fid.read()

        sleep(1)

    print 'cluster is ready'

    print 'task index is %s' % task_index

    #start the training process
    if FLAGS.type == 'asr':
        train_asr(clusterfile=cluster_dir + '/cluster',
                  job_name=FLAGS.job_name,
                  task_index=int(task_index),
                  ssh_tunnel=FLAGS.ssh_tunnel == 'True',
                  expdir=FLAGS.expdir)
    else:
        train_lm(clusterfile=cluster_dir + '/cluster',
                 job_name=FLAGS.job_name,
                 task_index=int(task_index),
                 ssh_tunnel=FLAGS.ssh_tunnel == 'True',
                 expdir=FLAGS.expdir)

    #delete the file to notify that the porcess has finished
    os.remove(machine_file)

if __name__ == '__main__':

    tf.app.flags.DEFINE_string('job_name', None, 'One of ps, worker')
    tf.app.flags.DEFINE_string('expdir', '.',
                               'the experimental directory')
    tf.app.flags.DEFINE_string('type', 'asr',
                               'one of asr or lm, the training type')
    tf.app.flags.DEFINE_string(
        'ssh_tunnel', 'False',
        'wheter or not communication should happen through an ssh tunnel')
    FLAGS = tf.app.flags.FLAGS

    tf.app.run()
