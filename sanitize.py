import re

logs = [
"17/06/09 20:10:40 INFO executor.CoarseGrainedExecutorBackend: Registered signal handlers for [TERM, HUP, INT]",
"17/06/09 20:10:40 INFO spark.SecurityManager: Changing view acls to: yarn,curi",
"17/06/09 20:10:40 INFO spark.SecurityManager: Changing modify acls to: yarn,curi",
"17/06/09 20:10:40 INFO spark.SecurityManager: SecurityManager: authentication disabled; ui acls disabled; users with view permissions: Set(yarn, curi); users with modify permissions: Set(yarn, curi)",
"17/06/09 20:10:41 INFO spark.SecurityManager: Changing view acls to: yarn,curi",
"17/06/09 20:10:41 INFO spark.SecurityManager: Changing modify acls to: yarn,curi",
"17/06/09 20:10:41 INFO spark.SecurityManager: SecurityManager: authentication disabled; ui acls disabled; users with view permissions: Set(yarn, curi); users with modify permissions: Set(yarn, curi)",
"17/06/09 20:10:41 INFO slf4j.Slf4jLogger: Slf4jLogger started",
"17/06/09 20:10:41 INFO Remoting: Starting remoting",
"17/06/09 20:10:41 INFO Remoting: Remoting started; listening on addresses :[akka.tcp://sparkExecutorActorSystem@mesos-slave-07:55904]",
"17/06/09 20:10:41 INFO util.Utils: Successfully started service 'sparkExecutorActorSystem' on port 55904.]",
]

def sanitize_log(log):
    UUID_REGEX = r"[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}"
    HEX_REGEX = r"0x[0-9a-fA-F]+"
    TIMESTAMP_REGEX = r"\d{4}-\d{2}-\d{2}[ T]\d{2}:\d{2}:\d{2}(?:\.\d+)?|\d{2}/\d{2}/\d{2} \d{2}:\d{2}:\d{2}"
    HOST_NODE_REGEX = r"\b[a-zA-Z0-9]+(?:-[a-zA-Z0-9]+)*-\d+\b"
    IP_PORT_REGEX = r"\b(?:\d{1,3}\.){3}\d{1,3}(?::\d+)?\b"
    STANDALONE_NUMS_REGEX = r"\b\d+\b"

    # strip UUIDs
    p = re.compile(UUID_REGEX)
    log = p.sub('<UUID>', log)

    # strip hexadecimal
    p = re.compile(HEX_REGEX)
    log = p.sub('<HEX>', log)

    # strip timestamp
    p = re.compile(TIMESTAMP_REGEX)
    log = p.sub('<TIMESTAMP>', log)

    # strip hostnames/nodes
    p = re.compile(HOST_NODE_REGEX)
    log = p.sub('<HOST>', log)
    
    # strip ip addresses/port
    p = re.compile(IP_PORT_REGEX)
    log = p.sub('<IP>', log)

    # strip standalone numbers
    p = re.compile(STANDALONE_NUMS_REGEX)
    log = p.sub('<NUM>', log)

    return log
 