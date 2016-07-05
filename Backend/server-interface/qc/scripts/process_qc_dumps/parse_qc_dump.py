# Copyright 2016 The Eyra Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# File author/s:
#     Matthias Petursson <oldschool01123@gmail.com>

# Quick and dirty script to parse marosijo module dumps and present their data.
# Based on scripts from earlier commits, parse_qc_dump.sh and combine_qc_dump_with_recinfo.sh
# written by Robert Kjaran <robert@kjaran.com>

import os
import json
import MySQLdb
import sys

# mv out of qc/scripts/process_qc_dumps directory and do relative imports from there.
newPath = os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir, os.path.pardir, os.pardir))
sys.path.append(newPath)
from config import dbConst
sys.path.remove(newPath)
del newPath

_db = MySQLdb.connect(**dbConst)
_warnings = 0

def log(arg, category=None):
    """
    Logs arg to stderr. To avoid writing to stdout (used in piping this scripts output to file)

    category is 'warning' or None
    """
    global _warnings
    if category == 'warning':
        _warnings += 1
    print(arg, file=sys.stderr)

def run(dump_path):
    print('# sessionId\ttokenId\taccuracy\tonlyInsOrSub\tcorrect\tsub\tins\tdel\tstartdel\tenddel\textraInsertions\tempty\tdistance\terror\trecordingId\tfilename\ttoken\tsessionId')

    cur = _db.cursor()

    for dump in os.listdir(dump_path):
        log('Processing dump: {}'.format(dump))
        dump = os.path.join(dump_path, dump)
        with open(dump, 'r') as f:
            reports = f.read().splitlines() # might be more than one, if a timeout occurred and recording was resumed
            for report in reports:
                if report == '':
                    # robustness to extra newlines
                    continue
                report = json.loads(report)
                
                session_id = dump.split('/')[-1].replace('session_','')

                for rec in report['perRecordingStats']:
                    stats = rec['stats']

                    if 'error' in stats:
                        # the new version of the reports, with correct recordingId and error
                        recording_id = rec['recordingId']
                        error = stats['error']
                        cur.execute('SELECT id FROM token WHERE id = (\
                                       SELECT tokenId FROM recording\
                                       WHERE id = %s)',
                                    (recording_id,))
                        try:
                            token_id = cur.fetchone()[0] #fetchone returns tuple
                        except TypeError as e:
                            log('Error: no prompt found with recordingId: {}'.format(recording_id))
                            raise
                    else:
                        # backwards compatibility for the old reports, which had the tokenId
                        # titled as recording id and no error column
                        token_id = rec['recordingId']
                        error = 'no_error'
                        cur.execute('SELECT id FROM recording WHERE tokenId = %s AND sessionId = %s',
                                    (token_id, session_id))
                        recIds = cur.fetchall()
                        if not recIds:
                            raise ValueError('Error: no recording id found with prompt {} and session {}.'.format(
                                   token_id, session_id))
                        recording_id = recIds[0]
                        if len(recIds) > 1:
                            log('Warning: same prompt read twice with old report configuration. Cannot\
                                   find all recording ids. Using recId: {} for all.'.format(recording_id), 'warning')
                    # grab recording filename
                    cur.execute('SELECT filename FROM recording WHERE id = %s',
                                (recording_id,))
                    try:
                        filename = cur.fetchone()[0]
                    except TypeError as e:
                        log('Error: no filename for recording with id: {}'.format(recording_id))
                        raise
                    # grab token
                    cur.execute('SELECT inputToken FROM token WHERE id = %s',
                                (token_id,))
                    try:
                        token = cur.fetchone()[0]
                    except TypeError as e:
                        log('Error: no inputToken for token with id: {}'.format(token_id))
                        raise
                    # now we should have all we need to print the correct line for this recording
                    print('{session_id}\t{token_id}\t{accuracy}\t{onlyInsOrSub}\t{correct}\t{sub}\
                           \t{ins}\t{dels}\t{startdel}\t{enddel}\t{extraInsertions}\t{empty}\t{distance}\
                           \t{error}\t{recordingId}\t{filename}\t{token}\t{session_id}'.format(
                            session_id=session_id, token_id=token_id, accuracy=stats['accuracy'],
                            onlyInsOrSub=stats['onlyInsOrSub'], correct=stats['correct'],
                            sub=stats['sub'], ins=stats['ins'], dels=stats['del'],
                            startdel=stats['startdel'], enddel=stats['enddel'],
                            extraInsertions=stats['extraInsertions'], empty=stats['empty'],
                            distance=stats['distance'], error=error, recordingId=recording_id,
                            filename=filename, token=token))
    log('Finished with {} warnings.'.format(_warnings))

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description="""
        Quick and dirty script to parse Marosijo module dumps and present their data.
        Writes to stdout. """)
    parser.add_argument('dump_path', type=str, help='Path to the Marosijo dumps.')
    args = parser.parse_args()

    run(args.dump_path)