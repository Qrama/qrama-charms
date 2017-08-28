import re


def metrics_replica(measurement):
    if measurement == 'Check failed to run: not running with --replSet ()':
        return []
    else:
        measurement = measurement.replace('\n', '')
        output = []
        outputs = {
            'health': {'name': 'health', 'unit': 'string'},
            'ping': {'name': 'ping_to_master', 'unit': 'ms'},
            'delay': {'name': 'delay_to_primary', 'unit': 's'},
            'name': {'name': 'name', 'unit': 'string'}
        }
        ids = re.search(r'member_[0-9]+\.id ([0-9]+?) ', measurement).groups()
        for m_id in ids:
            outputs['name']['value'] = re.search(r'member_{}\.name (.+?) '.format(m_id), measurement).groups()[0]
            outputs['name']['id'] = m_id
            outputs['health']['value'] = re.search(r'member_{}\.health (.+?) '.format(m_id), measurement).groups()[0]
            outputs['health']['id'] = m_id
            outputs['ping']['value'] = re.search(r'member_{}\.pingMs (.+?) '.format(m_id), measurement).groups()[0]
            outputs['ping']['id'] = m_id
            outputs['delay']['value'] = re.search(r'member_{}\.secondsBehindPrimary ([0-9]+?) '.format(m_id), measurement).groups()[0]
            outputs['delay']['id'] = m_id
            output.extend(outputs.values())
        return output


def metrics(measurement):
    measurement = measurement.replace('\n', '')
    outputs = [
        {'name': 'asserts warnings', 'unit': 'amount', 'value': re.search(r'asserts\.warnings ([0-9]+?) ', measurement).groups()[0]},
        {'name': 'asserts errors', 'unit': 'amount', 'value': re.search(r'asserts\.errors ([0-9]+?) ', measurement).groups()[0]},
        {'name': 'asserts regular', 'unit': 'amount', 'value': re.search(r'asserts\.regular ([0-9]+?) ', measurement).groups()[0]},
        {'name': 'asserts user', 'unit': 'amount', 'value': re.search(r'asserts\.user ([0-9]+?) ', measurement).groups()[0]},
        {'name': 'asserts rollovers', 'unit': 'amount', 'value': re.search(r'asserts\.rollovers ([0-9]+?) ', measurement).groups()[0]},
        {'name': 'backgroundFlushing flushes', 'unit': 'amount', 'value': re.search(r'backgroundFlushing\.flushes ([0-9]+?) ', measurement).groups()[0]},
        {'name': 'backgroundFlushing total_ms', 'unit': 'ms', 'value': re.search(r'backgroundFlushing\.total_ms ([0-9]+?) ', measurement).groups()[0]},
        {'name': 'backgroundFlushing average_ms', 'unit': 'ms', 'value': re.search(r'backgroundFlushing\.average_ms ([0-9\.]+?) ', measurement).groups()[0]},
        {'name': 'backgroundFlushing last_ms', 'unit': 'ms', 'value': re.search(r'backgroundFlushing\.last_ms ([0-9]+?) ', measurement).groups()[0]},
        {'name': 'connections current', 'unit': 'amount', 'value': re.search(r'connections\.current ([0-9]+?) ', measurement).groups()[0]},
        {'name': 'connections available', 'unit': 'amount', 'value': re.search(r'connections\.available ([0-9]+?) ', measurement).groups()[0]},
        {'name': 'connections totalCreated', 'unit': 'amount', 'value': re.search(r'connections\.totalCreated ([0-9]+?) ', measurement).groups()[0]},
        {'name': 'cursors timedOut', 'unit': 'amount', 'value': re.search(r'cursors\.timedOut ([0-9]+?) ', measurement).groups()[0]},
        {'name': 'cursors open noTimeout', 'unit': 'amount', 'value': re.search(r'cursors\.open\.noTimeout ([0-9]+?) ', measurement).groups()[0]},
        {'name': 'cursors open total', 'unit': 'amount', 'value': re.search(r'cursors\.open\.total ([0-9]+?) ', measurement).groups()[0]},
        {'name': 'journal commits', 'unit': 'amount', 'value': re.search(r'journal\.commits ([0-9]+?) ', measurement).groups()[0]},
        {'name': 'journaled_MB', 'unit': 'MB', 'value': re.search(r'journaled_MB ([0-9\.]+?) ', measurement).groups()[0]},
        {'name': 'journal timeMs writeToDataFiles', 'unit': 'ms', 'value': re.search(r'journal\.timeMs\.writeToDataFiles ([0-9]+?) ', measurement).groups()[0]},
        {'name': 'journal writeToDataFilesMB', 'unit': 'MB', 'value': re.search(r'journal\.writeToDataFilesMB ([0-9\.]+?) ', measurement).groups()[0]},
        {'name': 'journal compression', 'unit': 'ratio', 'value': re.search(r'journal\.compression ([0-9\.]+?) ', measurement).groups()[0]},
        {'name': 'journal commitsInWriteLock', 'unit': 'amount', 'value': re.search(r'journal\.commitsInWriteLock ([0-9]+?)', measurement).groups()[0]},
        {'name': 'journal timeMs dt', 'unit': 'ms', 'value': re.search(r'journal\.timeMs\.dt ([0-9]+?)', measurement).groups()[0]},
        {'name': 'journal timeMs prepLogBuffer', 'unit': 'ms', 'value': re.search(r'journal\.timeMs\.prepLogBuffer ([0-9]+?)', measurement).groups()[0]},
        {'name': 'journal timeMs writeToJournal', 'unit': 'ms', 'value': re.search(r'journal\.timeMs\.writeToJournal ([0-9]+?)', measurement).groups()[0]},
        {'name': 'journal timeMs remapPrivateView', 'unit': 'ms', 'value': re.search(r'journal\.timeMs\.remapPrivateView ([0-9]+?)', measurement).groups()[0]},
        {'name': 'mem heap usage bytes', 'unit': 'B', 'value': re.search(r'mem\.heap_usage_bytes ([0-9]+?)', measurement).groups()[0]},
        {'name': 'mem pageFaults', 'unit': 'amount', 'value': re.search(r'mem\.pageFaults ([0-9]+?)', measurement).groups()[0]},
        {'name': 'lock totalTime', 'unit': 's', 'value': re.search(r'lock\.totalTime ([0-9]+?)', measurement).groups()[0]},
        {'name': 'lock queue total', 'unit': 'amount', 'value': re.search(r'lock\.queue_total ([0-9]+?)', measurement).groups()[0]},
        {'name': 'lock queue readers', 'unit': 'amount', 'value': re.search(r'lock\.queue_readers ([0-9]+?)', measurement).groups()[0]},
        {'name': 'lock queue writers', 'unit': 'amount', 'value': re.search(r'lock\.queue_writers ([0-9]+?)', measurement).groups()[0]},
        {'name': 'lock clients total', 'unit': 'amount', 'value': re.search(r'lock\.clients_total ([0-9]+?) ', measurement).groups()[0]},
        {'name': 'lock clients readers', 'unit': 'amount', 'value': re.search(r'lock\.clients_readers ([0-9]+?) ', measurement).groups()[0]},
        {'name': 'lock clients writers', 'unit': 'amount', 'value': re.search(r'lock\.clients_writers ([0-9]+?) ', measurement).groups()[0]},
        {'name': 'indexes missRatio', 'unit': 'ratio', 'value': re.search(r'indexes\.missRatio ([0-9]+?) ', measurement).groups()[0]},
        {'name': 'indexes hits', 'unit': 'amount', 'value': re.search(r'indexes\.hits ([0-9]+?) ', measurement).groups()[0]},
        {'name': 'indexes misses', 'unit': 'amount', 'value': re.search(r'indexes\.misses ([0-9]+?) ', measurement).groups()[0]},
        {'name': 'indexes accesses', 'unit': 'amount', 'value': re.search(r'indexes\.accesses ([0-9]+?) ', measurement).groups()[0]},
        {'name': 'indexes resets', 'unit': 'amount', 'value': re.search(r'indexes\.resets ([0-9]+?) ', measurement).groups()[0]},
        {'name': 'network bytesIn', 'unit': 'B', 'value': re.search(r'network\.bytesIn ([0-9]+?) ', measurement).groups()[0]},
        {'name': 'network bytesOut', 'unit': 'B', 'value': re.search(r'network\.bytesOut ([0-9]+?) ', measurement).groups()[0]},
        {'name': 'network numRequests', 'unit': 'amount', 'value': re.search(r'network\.numRequests ([0-9\.]+?) ', measurement).groups()[0]},
        {'name': 'opcounters insert', 'unit': 'amount', 'value': re.search(r'opcounters\.insert ([0-9]+?) ', measurement).groups()[0]},
        {'name': 'opcounters query', 'unit': 'amount', 'value': re.search(r'opcounters\.query ([0-9\.]+?) ', measurement).groups()[0]},
        {'name': 'opcounters update', 'unit': 'amount', 'value': re.search(r'opcounters\.update ([0-9\.]+?) ', measurement).groups()[0]},
        {'name': 'opcounters delete', 'unit': 'amount', 'value': re.search(r'opcounters\.delete ([0-9]+?)', measurement).groups()[0]},
        {'name': 'opcounters getmore', 'unit': 'amount', 'value': re.search(r'opcounters\.getmore ([0-9]+?)', measurement).groups()[0]},
        {'name': 'opcounters command', 'unit': 'amount', 'value': re.search(r'opcounters\.command ([0-9]+?)', measurement).groups()[0]},
        {'name': 'opcountersRepl insert', 'unit': 'amount', 'value': re.search(r'opcountersRepl\.insert ([0-9]+?)', measurement).groups()[0]},
        {'name': 'opcountersRepl query', 'unit': 'amount', 'value': re.search(r'opcountersRepl\.query ([0-9]+?)', measurement).groups()[0]},
        {'name': 'opcountersRepl update', 'unit': 'amount', 'value': re.search(r'opcountersRepl\.update ([0-9]+?)', measurement).groups()[0]},
        {'name': 'opcountersRepl delete', 'unit': 'amount', 'value': re.search(r'opcountersRepl\.delete ([0-9]+?)', measurement).groups()[0]},
        {'name': 'opcountersRepl getmore', 'unit': 'amount', 'value': re.search(r'opcountersRepl\.getmore ([0-9]+?)', measurement).groups()[0]},
        {'name': 'opcountersRepl command', 'unit': 'amount', 'value': re.search(r'opcountersRepl\.command ([0-9]+?)', measurement).groups()[0]},
        {'name': 'mem residentMb', 'unit': 'MB', 'value': re.search(r'mem\.residentMb ([0-9]+?)', measurement).groups()[0]},
        {'name': 'mem virtualMb', 'unit': 'MB', 'value': re.search(r'mem\.virtualMb ([0-9]+?)', measurement).groups()[0]},
        {'name': 'mem mapped', 'unit': 'amount', 'value': re.search(r'mem\.mapped ([0-9]+?) ', measurement).groups()[0]},
        {'name': 'mem mappedWithJournal', 'unit': 'amount', 'value': re.search(r'mem\.mappedWithJournal ([0-9]+?) ', measurement).groups()[0]},
        {'name': 'metrics document deleted', 'unit': 'amount', 'value': re.search(r'metrics\.document\.deleted ([0-9]+?) ', measurement).groups()[0]},
        {'name': 'metrics document inserted', 'unit': 'amount', 'value': re.search(r'metrics\.document\.inserted ([0-9]+?) ', measurement).groups()[0]},
        {'name': 'metrics document returned', 'unit': 'amount', 'value': re.search(r'metrics\.document\.returned ([0-9]+?) ', measurement).groups()[0]},
        {'name': 'metrics document updated', 'unit': 'amount', 'value': re.search(r'metrics\.document\.updated ([0-9]+?) ', measurement).groups()[0]},
        {'name': 'metrics getLastError wtime num', 'unit': 'amount', 'value': re.search(r'metrics\.getLastError\.wtime_num ([0-9]+?) ', measurement).groups()[0]},
        {'name': 'metrics getLastError wtime totalMillis', 'unit': 'ms', 'value': re.search(r'metrics\.getLastError\.wtime_totalMillis ([0-9]+?) ', measurement).groups()[0]},
        {'name': 'metrics getLastError wtimeouts', 'unit': 'amount', 'value': re.search(r'metrics\.getLastError\.wtimeouts ([0-9]+?) ', measurement).groups()[0]},
        {'name': 'metrics operation fastmod', 'unit': 'amount', 'value': re.search(r'metrics\.operation\.fastmod ([0-9\.]+?) ', measurement).groups()[0]},
        {'name': 'metrics operation idhack', 'unit': 'amount', 'value': re.search(r'metrics\.operation\.idhack ([0-9]+?) ', measurement).groups()[0]},
        {'name': 'metrics operation scanAndOrder', 'unit': 'amount', 'value': re.search(r'metrics\.operation\.scanAndOrder ([0-9\.]+?) ', measurement).groups()[0]},
        {'name': 'metrics queryExecutor scanned', 'unit': 'amount', 'value': re.search(r'metrics\.queryExecutor\.scanned ([0-9\.]+?) ', measurement).groups()[0]},
        {'name': 'metrics queryExecutor scannedObjects', 'unit': 'amount', 'value': re.search(r'metrics\.queryExecutor\.scannedObjects ([0-9]+?)', measurement).groups()[0]},
        {'name': 'metrics record moves', 'unit': 'amount', 'value': re.search(r'metrics\.record\.moves ([0-9]+?)', measurement).groups()[0]},
        {'name': 'metrics repl apply batches num', 'unit': 'amount', 'value': re.search(r'metrics\.repl\.apply\.batches_num ([0-9]+?)', measurement).groups()[0]},
        {'name': 'metrics repl apply batches totalMillis', 'unit': 'ms', 'value': re.search(r'metrics\.repl\.apply\.batches_totalMillis ([0-9]+?)', measurement).groups()[0]},
        {'name': 'metrics repl apply ops', 'unit': 'amount', 'value': re.search(r'metrics\.repl\.apply\.ops ([0-9]+?)', measurement).groups()[0]},
        {'name': 'metrics repl buffer count', 'unit': 'amount', 'value': re.search(r'metrics\.repl\.buffer\.count ([0-9]+?)', measurement).groups()[0]},
        {'name': 'metrics repl buffer maxSizeBytes', 'unit': 'B', 'value': re.search(r'metrics\.repl\.buffer\.maxSizeBytes ([0-9]+?)', measurement).groups()[0]},
        {'name': 'metrics repl buffer sizeBytes', 'unit': 'B', 'value': re.search(r'metrics\.repl\.buffer\.sizeBytes ([0-9]+?)', measurement).groups()[0]},
        {'name': 'metrics repl network bytes', 'unit': 'B', 'value': re.search(r'metrics\.repl\.network\.bytes ([0-9]+?)', measurement).groups()[0]},
        {'name': 'metrics repl network getmores num', 'unit': 'amount', 'value': re.search(r'metrics\.repl\.network\.getmores_num ([0-9]+?)', measurement).groups()[0]},
        {'name': 'metrics repl network getmores totalMillis', 'unit': 'ms', 'value': re.search(r'metrics\.repl\.network\.getmores_totalMillis ([0-9]+?)', measurement).groups()[0]},
        {'name': 'metrics repl network ops', 'unit': 'amount', 'value': re.search(r'metrics\.repl\.network\.ops ([0-9]+?) ', measurement).groups()[0]},
        {'name': 'metrics repl network readersCreated', 'unit': 'amount', 'value': re.search(r'metrics\.repl\.network\.readersCreated ([0-9\.]+?) ', measurement).groups()[0]},
        {'name': 'metrics repl preload docs num', 'unit': 'amount', 'value': re.search(r'metrics\.repl\.preload\.docs_num ([0-9\.]+?) ', measurement).groups()[0]},
        {'name': 'metrics repl preload docs totalMillis', 'unit': 'ms', 'value': re.search(r'metrics\.repl\.preload\.docs_totalMillis ([0-9]+?)', measurement).groups()[0]},
        {'name': 'metrics repl preload indexes num', 'unit': 'amount', 'value': re.search(r'metrics\.repl\.preload\.indexes_num ([0-9]+?)', measurement).groups()[0]},
        {'name': 'metrics repl preload indexes totalMillis', 'unit': 'ms', 'value': re.search(r'metrics\.repl\.preload\.indexes_totalMillis ([0-9]+?)', measurement).groups()[0]},
        {'name': 'metrics storage freelist search bucketExhauseted', 'unit': 'amount', 'value': re.search(r'metrics\.storage\.freelist\.search_bucketExhauseted ([0-9]+?)', measurement).groups()[0]},
        {'name': 'metrics storage freelist search requests', 'unit': 'amount', 'value': re.search(r'metrics\.storage\.freelist\.search_requests ([0-9]+?)', measurement).groups()[0]},
        {'name': 'metrics storage freelist search scanned', 'unit': 'amount', 'value': re.search(r'metrics\.storage\.freelist\.search_scanned ([0-9]+?)', measurement).groups()[0]},
        {'name': 'metrics ttl deletedDocuments', 'unit': 'amount', 'value': re.search(r'metrics\.ttl\.deletedDocuments ([0-9]+?)', measurement).groups()[0]},
        {'name': 'metrics ttl passes', 'unit': 'amount', 'value': re.search(r'metrics\.ttl\.passes ([0-9]+?)', measurement).groups()[0]}
    ]
    for db in re.search(r'databaseSizes\.([^\.]*)\.dataSize', measurement).groups():
        outputs.extend([
            {'name': 'db: {} collections'.format(db), 'unit': 'amount', 'value': re.search(r'databaseSizes\.{}\.collections ([0-9]+?) '.format(db), measurement).groups()[0]},
            {'name': 'db {} objects'.format(db), 'unit': 'amount', 'value': re.search(r'databaseSizes\.{}\.objects ([0-9]+?) '.format(db), measurement).groups()[0]},
            {'name': 'databaseSizes {} avgObjSize'.format(db), 'unit': 'B', 'value': re.search(r'databaseSizes\.{}\.avgObjSize ([0-9]+?) '.format(db), measurement).groups()[0]},
            {'name': 'databaseSizes {} dataSize'.format(db), 'unit': 'B', 'value': re.search(r'databaseSizes\.{}\.dataSize ([0-9]+?) '.format(db), measurement).groups()[0]},
            {'name': 'databaseSizes {} storageSize'.format(db), 'unit': 'B', 'value': re.search(r'databaseSizes\.{}\.storageSize ([0-9]+?) '.format(db), measurement).groups()[0]},
            {'name': 'databaseSizes {} numExtents'.format(db), 'unit': 'amount', 'value': re.search(r'databaseSizes\.{}\.numExtents ([0-9]+?) '.format(db), measurement).groups()[0]},
            {'name': 'databaseSizes {} indexes'.format(db), 'unit': 'amount', 'value': re.search(r'databaseSizes\.{}\.indexes ([0-9]+?) '.format(db), measurement).groups()[0]},
            {'name': 'databaseSizes {} indexSize'.format(db), 'unit': 'B', 'value': re.search(r'databaseSizes\.{}\.indexSize ([0-9]+?) '.format(db), measurement).groups()[0]},
            {'name': 'databaseSizes {} fileSize'.format(db), 'unit': 'B', 'value': re.search(r'databaseSizes\.{}\.fileSize ([0-9]+?) '.format(db), measurement).groups()[0]}
        ])
    return outputs
