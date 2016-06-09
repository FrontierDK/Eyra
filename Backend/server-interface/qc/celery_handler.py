# Copyright 2016 Matthias Petursson
# Apache 2.0

import redis
import datetime
import time
import json
import os

#: Relative imports
from celery import Celery
from . import celery_config

# this code is generated by setupActiveModules.py script
# @@CELERYQCBASETASKIMPORTS
from .modules.MarosijoModule.MarosijoModule import MarosijoTask
# @@/CELERYQCBASETASKIMPORTS

host = celery_config.const['host']
port = celery_config.const['port']
broker_db = celery_config.const['broker_db']
backend_db = celery_config.const['backend_db']

broker = 'redis://{}:{}/{}'.format(host, port, broker_db)

celery = Celery(broker=broker)
celery.conf.update(
    CELERY_RESULT_BACKEND='redis://{}:{}/{}'.format(host, port, backend_db)
)

# connect to redis
_redis = redis.StrictRedis(host=host, port=port, db=backend_db)

def isSessionOver(sessionId) -> bool:
    """
    Returns True if session(Id) is over. 

    Finds out by using celery_config.const['session_timeout'] and checking
    if the time since client last queried this session is more than said
    timeout. If so, the session is over.
    """
    try:
        prevTime = datetime.datetime.strptime(
            _redis.get('session/{}/timestamp'.format(sessionId)).decode('utf-8'), 
            "%Y-%m-%d %H:%M:%S.%f")
    except AttributeError:
        # redis get is None
        print('Error, timestamp not in redis datastore, sessionId: %s' % sessionId)
        raise
    except ValueError:
        # datetime parse failed
        print('Error, timestamp not on correct format, sessionId: %s' % sessionId)
        raise

    if (datetime.datetime.now() - prevTime).seconds\
        > celery_config.const['session_timeout']:
        return True
    return False


# this code is used as template for the setupActiveModules.py script
# should be commented out here
# @@CELERYQCPROCESSTEMPLATE
# @celery.task(base=MarosijoTask, name='celery.qcProcSessionMarosijoModule')
# def qcProcSessionMarosijoModule(name, sessionId, slistIdx=0, batchSize=5) -> None:
#     """
#     Goes through the list of recordings for this session in the redis database
#     located at: 'session/sessionId/recordings', containing a list of all current
#     recordings of this session, in the backend continuing from
#     slistIdx. 

#     Performs qcProcSessionMarosijoModule.processBatch which does the processing, 
#     it must take exactly 3 arguments, the first being the name used for identification
#     in the redis datastore (e.g. 'report/name/sessionId'), and
#     the second is sessionId, third is a list of indices of recordings to process (empty
#     if no new recordings to process). 
#     processBatch is responsible for putting the results on the correct format in the
#     report in the redis datastore. Obviously, processBatch needs to be a
#     synchronous function. If processBatch returns False, stop this particular task chain.

#     Only processes batchSize recs at a time, until calling itself recursively
#     with the updated slistIdx (and by that placing itself at the back
#     of the celery queue), look at instagram, that's how they do it xD
#     """

#     if isSessionOver(sessionId):
#         # make sure to delete the report once the session is over (sparking a new task chain
#         # if user returns to session)
#         _redis.delete('session/{}/processing'.format(sessionId)) # remove processing flag

#         reportPath = 'report/{}/{}'.format(name, sessionId)
#         try:
#             report = _redis.get(reportPath).decode('utf-8')
#             # We also dump the report onto disk (mainly for debugging)
#             dumpPath = '{}/{}'.format(celery_config.const['qc_report_dump_path'],
#                                       reportPath)
#             os.makedirs(os.path.dirname(dumpPath), exist_ok=True)
#             with open(dumpPath, 'at') as rf:
#                 print(report, file=rf)

#             _redis.delete(reportPath)
#         except AttributeError as e:
#             print('Error, no report in database.\
#                    Probably due to a timeout before report was made.\
#                    Session id: {}, module: {}'.format(sessionId, name))
#         return

#     _redis.set('session/{}/processing'.format(sessionId), 'true')

#     # make sure not to go out of bounds on the recsInfo list
#     recsInfo = _redis.get('session/{}/recordings'.format(sessionId))
#     if recsInfo:
#         recsInfo = json.loads(recsInfo.decode('utf-8'))
#     # indices of next batch of recordings to process (argument to processBatch)
#     indices = []
#     for i in range(slistIdx, slistIdx+batchSize):
#         # only add indices if they are within bounds of recsInfo
#         if i < len(recsInfo):
#             indices.append(i)
#     # new index in list for next task in this task chain
#     newSListIdx = slistIdx+len(indices)

#     # stall if this task executes too rapidly
#     prevTime = datetime.datetime.now()
#     result = qcProcSessionMarosijoModule.processBatch(name, sessionId, indices)
#     curTime = datetime.datetime.now()
#     if prevTime is not None:
#         diff = (curTime - prevTime).microseconds
#         if diff < celery_config.const['task_min_proc_time']:
#             time.sleep(celery_config.const['task_delay'])

#     if result:
#         # continue the task chain
#         qcProcSessionMarosijoModule.apply_async(
#            args=[name, sessionId, newSListIdx, batchSize])
#     else:
#         _redis.delete('session/{}/processing'.format(sessionId)) # remove processing flag

# @@/CELERYQCPROCESSTEMPLATE

# this code is generated by setupActiveModules.py script
# be careful modifying this, it is overwritten on a setupActiveModules.py run
# @@CELERYQCPROCESSTASKS
@celery.task(base=MarosijoTask, name='celery.qcProcSessionMarosijoModule')
def qcProcSessionMarosijoModule(name, sessionId, slistIdx=0, batchSize=5) -> None:
    """
    Goes through the list of recordings for this session in the redis database
    located at: 'session/sessionId/recordings', containing a list of all current
    recordings of this session, in the backend continuing from
    slistIdx. 

    Performs qcProcSessionMarosijoModule.processBatch which does the processing, 
    it must take exactly 3 arguments, the first being the name used for identification
    in the redis datastore (e.g. 'report/name/sessionId'), and
    the second is sessionId, third is a list of indices of recordings to process (empty
    if no new recordings to process). 
    processBatch is responsible for putting the results on the correct format in the
    report in the redis datastore. Obviously, processBatch needs to be a
    synchronous function. If processBatch returns False, stop this particular task chain.

    Only processes batchSize recs at a time, until calling itself recursively
    with the updated slistIdx (and by that placing itself at the back
    of the celery queue), look at instagram, that's how they do it xD
    """

    if isSessionOver(sessionId):
        # make sure to delete the report once the session is over (sparking a new task chain
        # if user returns to session)
        _redis.delete('session/{}/processing'.format(sessionId)) # remove processing flag

        reportPath = 'report/{}/{}'.format(name, sessionId)
        try:
            report = _redis.get(reportPath).decode('utf-8')
            # We also dump the report onto disk (mainly for debugging)
            dumpPath = '{}/{}'.format(celery_config.const['qc_report_dump_path'],
                                      reportPath)
            os.makedirs(os.path.dirname(dumpPath), exist_ok=True)
            with open(dumpPath, 'at') as rf:
                print(report, file=rf)

            _redis.delete(reportPath)
        except AttributeError as e:
            print('Error, no report in database.\
                   Probably due to a timeout before report was made.\
                   Session id: {}, module: {}'.format(sessionId, name))
        return

    _redis.set('session/{}/processing'.format(sessionId), 'true')

    # make sure not to go out of bounds on the recsInfo list
    recsInfo = _redis.get('session/{}/recordings'.format(sessionId))
    if recsInfo:
        recsInfo = json.loads(recsInfo.decode('utf-8'))
    # indices of next batch of recordings to process (argument to processBatch)
    indices = []
    for i in range(slistIdx, slistIdx+batchSize):
        # only add indices if they are within bounds of recsInfo
        if i < len(recsInfo):
            indices.append(i)
    # new index in list for next task in this task chain
    newSListIdx = slistIdx+len(indices)

    # stall if this task executes too rapidly
    prevTime = datetime.datetime.now()
    result = qcProcSessionMarosijoModule.processBatch(name, sessionId, indices)
    curTime = datetime.datetime.now()
    if prevTime is not None:
        diff = (curTime - prevTime).microseconds
        if diff < celery_config.const['task_min_proc_time']:
            time.sleep(celery_config.const['task_delay'])

    if result:
        # continue the task chain
        qcProcSessionMarosijoModule.apply_async(
           args=[name, sessionId, newSListIdx, batchSize])
    else:
        _redis.delete('session/{}/processing'.format(sessionId)) # remove processing flag



# @@/CELERYQCPROCESSTASKS
